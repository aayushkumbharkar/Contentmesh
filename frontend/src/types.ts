export type Node = {id:string;kind:string;label:string;[key:string]:unknown};
export type Edge = {id:string;source:string;target:string;type:string};
export type Graph = {nodes:Node[];edges:Edge[]};
export type Path = {nodes:string[];edges:string[]};
export type Run = {id:string;session_id:string;status:string;answer:string;evidence:Node[];paths:Path[];steps:{id:string;agent:string;status:string;summary:string;input_ids:string[];output_ids:string[]}[];usage:Record<string,unknown>};
export const colors:Record<string,string> = {Entity:'#58d6d1',Evidence:'#e9bc74',Memory:'#a58bff',Session:'#77a5ff',Agent:'#e896bf',AgentRun:'#e896bf',Task:'#9fb5cc',Decision:'#b4d982',Run:'#82afe9',Workspace:'#ffffff'};
