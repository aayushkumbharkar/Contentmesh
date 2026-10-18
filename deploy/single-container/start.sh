#!/bin/sh
set -e
mkdir -p "$DATA_DIR"
redis-server --loadmodule /opt/falkordb/falkordb.so --bind 127.0.0.1 --port 6379 \
  --protected-mode yes --appendonly yes --dir "$DATA_DIR" --daemonize yes \
  --logfile "$DATA_DIR/falkordb.log"
i=0; until redis-cli -h 127.0.0.1 ping >/dev/null 2>&1; do i=$((i+1)); [ $i -gt 60 ] && exit 1; sleep 0.5; done
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-7860}"
