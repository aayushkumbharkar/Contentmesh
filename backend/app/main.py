"""Same-origin local API. Graph namespaces isolate workspace records."""
import json
import os
import logging
from datetime import datetime, timezone
from typing import Annotated
from fastapi import FastAPI, HTTPException, Path, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from redis.exceptions import RedisError
from app.graph import GraphStore, GraphUnavailable
from app.orchestration import run_workflow
from app.provider import synthesize
from app.memory import update_memory as revise_memory

app = FastAPI(title='ContextMesh', version='0.1.0')
store = GraphStore()
Workspace = Annotated[str, Path(pattern=r'^[a-z0-9][a-z0-9-]{0,63}$')]

class SessionInput(BaseModel):
    title: str = Field(default='New investigation', min_length=1, max_length=120)

class NoteInput(BaseModel):
    text: str = Field(min_length=1, max_length=6000)

@app.exception_handler(GraphUnavailable)
@app.exception_handler(RedisError)
def database_error(request: Request, exc: RedisError):
    logging.error('Database request failed: %s', type(exc).__name__)
    return JSONResponse(status_code=503, content={'detail': 'Graph database unavailable. Please retry when healthy.'})

@app.exception_handler(ValueError)
def validation_error(request: Request, exc: ValueError):
    return JSONResponse(status_code=422, content={'detail': 'Invalid graph operation or request.'})

@app.get('/api/health')
def health():
    if not store.health():
        raise HTTPException(503, 'Graph database unavailable')
    return {'status': 'ok', 'database': 'FalkorDB'}

@app.post('/api/workspaces/{w}/seed')
def seed(w: Workspace):
    return store.seed(w)

@app.get('/api/workspaces/{w}/graph')
def graph(w: Workspace):
    return store.graph(w)

@app.get('/api/workspaces/{w}/sessions')
def sessions(w: Workspace):
    return {'sessions': store.nodes(w, 'Session')}

@app.post('/api/workspaces/{w}/sessions', status_code=201)
def create_session(w: Workspace, body: SessionInput):
    workspace = store.put_node(w, 'Workspace', {'id': 'workspace', 'label': w})
    node = store.put_node(w, 'Session', {'label': body.title, 'created_at': datetime.now(timezone.utc).isoformat()})
    store.link(w, workspace['id'], node['id'], 'HAS_SESSION')
    return node

@app.get('/api/workspaces/{w}/memories')
def memories(w: Workspace):
    return {'memories': store.nodes(w, 'Memory')}

@app.patch('/api/workspaces/{w}/memories/{node_id}')
def update_memory(w: Workspace, node_id: str, body: NoteInput):
    old = store.get_node(w, node_id)
    if not old or old['kind'] != 'Memory':
        raise HTTPException(404, 'Memory not found')
    return revise_memory(store, w, node_id, body.text)

@app.post('/api/workspaces/{w}/sessions/{session_id}/runs')
def run(w: Workspace, session_id: str, body: NoteInput):
    session = store.get_node(w, session_id)
    if not session or session['kind'] != 'Session':
        raise HTTPException(404, 'Session not found in this workspace')
    if not body.text.strip():
        raise HTTPException(422, 'Note cannot be blank')
    return run_workflow(store, w, session_id, body.text, provider=synthesize)

@app.get('/api/workspaces/{w}/runs')
def runs(w: Workspace):
    results = []
    for node in store.nodes(w, 'Run'):
        if node.get('result'):
            try:
                results.append(json.loads(node['result']))
            except (ValueError, TypeError):
                logging.warning('Run record has invalid result: %s', node['id'])
        else:
            results.append({'id': node['id'], 'session_id': node.get('session_id', ''), 'status': node.get('status', 'unknown'), 'answer': node.get('error', 'Run is incomplete; inspect persisted graph activity.'), 'evidence': [], 'paths': [], 'steps': [], 'usage': {}})
    return {'runs': results}

@app.get('/api/workspaces/{w}/nodes/{node_id}/neighborhood')
def neighborhood(w: Workspace, node_id: str, hops: int = Query(2, ge=1, le=4)):
    if not store.get_node(w, node_id):
        raise HTTPException(404, 'Node not found')
    return store.neighborhood(w, node_id, hops)

@app.get('/api/workspaces/{w}/paths')
def paths(w: Workspace, source: str, target: str, max_hops: int = Query(4, ge=1, le=4)):
    return {'paths': store.paths(w, source, target, max_hops)}


# Optional bundled frontend for a single-service HTTP deployment.
if os.getenv("FRONTEND_DIST"):
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=os.environ["FRONTEND_DIST"], html=True), name="frontend")
