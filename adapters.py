import os, json, re, requests
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ValidationError

BASE_URL = os.environ.get("LEGACY_BASE_URL", "http://localhost:8000")

# Canonical Schemas
class CanonicalRequest(BaseModel):
    agent_kind: str                      # "retriever" | "tool" | "writer" | ...
    inputs: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)
    policy: Dict[str, Any] = Field(default_factory=dict)
    telemetry: Dict[str, Any] = Field(default_factory=dict)

class CanonicalResponse(BaseModel):
    agent_kind: str
    outputs: Dict[str, Any]
    errors: Optional[List[str]] = None

# Adapters (Legacy call inside)
def retriever_A_adapter(req: CanonicalRequest) -> CanonicalResponse:
    """Legacy A: POST /legacyA/search  {q,lang,limit} -> {hits:[{text,score}]}"""
    q = req.inputs.get("query", "")
    top_k = int(req.inputs.get("top_k", 3))
    lang = req.context.get("locale", "ja")
    payload = {"q": q, "lang": lang, "limit": top_k}
    r = requests.post(f"{BASE_URL}/legacyA/search", json=payload, timeout=5)
    r.raise_for_status()
    data = r.json()
    snippets = [h.get("text","") for h in data.get("hits", [])]
    return CanonicalResponse(agent_kind="retriever", outputs={"snippets": snippets}, errors=[])

def retriever_B_adapter(req: CanonicalRequest) -> CanonicalResponse:
    """Legacy B: POST /legacyB/graphql {query:'{ search(text:"...", topK:n){ passage, score } }'} -> {"data":{"search":[...]}}"""
    q = req.inputs.get("query", "")
    top_k = int(req.inputs.get("top_k", 3))
    gql = f'{{ search(text:"{q}", topK: {top_k}){{ passage, score }} }}'
    r = requests.post(f"{BASE_URL}/legacyB/graphql", json={"query": gql}, timeout=5)
    r.raise_for_status()
    data = r.json()
    hits = data.get("data", {}).get("search", [])
    snippets = [h.get("passage","") for h in hits]
    return CanonicalResponse(agent_kind="retriever", outputs={"snippets": snippets}, errors=[])

def tool_C_adapter(req: CanonicalRequest) -> CanonicalResponse:
    """Legacy C: POST /legacyC/calc {a,b,op} -> {res}"""
    expr = str(req.inputs.get("expr", ""))
    m = re.search(r"(-?\d+(?:\.\d+)?)\s*([+\-*/×÷])\s*(-?\d+(?:\.\d+)?)", expr)
    if not m:
        return CanonicalResponse(agent_kind="tool", outputs={"result": "（計算対象が見つかりませんでした）"}, errors=[])
    a, op, b = m.groups()
    op = "×" if op == "*" else "÷" if op == "/" else op
    payload = {"a": float(a), "b": float(b), "op": op}
    r = requests.post(f"{BASE_URL}/legacyC/calc", json=payload, timeout=5)
    r.raise_for_status()
    data = r.json()  # {"res": 7}
    val = data.get("res")
    result_str = f"{a}{op}{b} = {val}"
    return CanonicalResponse(agent_kind="tool", outputs={"result": result_str}, errors=[])

ADAPTERS = {
    "retriever_A": retriever_A_adapter,
    "retriever_B": retriever_B_adapter,
    "tool_C":      tool_C_adapter,
}