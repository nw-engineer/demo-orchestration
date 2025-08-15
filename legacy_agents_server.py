from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import re, random

app = FastAPI(title="Legacy AI Agents (Dummy)")

# Legacy A: Retriever (REST/JSON, q/lang/limit -> hits)
class ASearchIn(BaseModel):
    q: str
    lang: str = "ja"
    limit: int = 3

class AHit(BaseModel):
    text: str
    score: float

class ASearchOut(BaseModel):
    hits: List[AHit]

@app.post("/legacyA/search", response_model=ASearchOut)
def legacy_a_search(inp: ASearchIn):
    seed = ["請求レポートはテンプレA。月末締め。", "第1営業日に提出。", "サービス概要はパンフB。3章構成。"]
    q = inp.q
    
    filtered = [s for s in seed if any(k in q for k in ["請求","手順","サービス","概要"])] or seed
    hits = [AHit(text=s, score=round(random.uniform(0.7, 0.95), 2)) for s in filtered[:inp.limit]]
    return ASearchOut(hits=hits)

# Legacy B: Retriever (GraphQL風, query string → data.search)
class GQLIn(BaseModel):
    query: str

@app.post("/legacyB/graphql")
def legacy_b_graphql(inp: GQLIn):
    q = inp.query
    m_text = re.search(r'text:"([^"]+)"', q)
    m_k = re.search(r'topK:\s*(\d+)', q)
    text = m_text.group(1) if m_text else ""
    k = int(m_k.group(1)) if m_k else 3
    seed = ["月末締め運用ルール", "テンプレAの利用方法", "パンフB要約（3章）"]
    filtered = [s for s in seed if any(w in text for w in ["請求","手順","サービス","概要"])] or seed
    res = [{"passage": s, "score": round(random.uniform(0.68, 0.9), 2)} for s in filtered[:k]]
    return {"data": {"search": res}}

# Legacy C: Tool（計算）(REST/JSON, a/b/op -> res)
class CalcIn(BaseModel):
    a: float
    b: float
    op: str  # "+", "-", "*", "/"

class CalcOut(BaseModel):
    res: float

@app.post("/legacyC/calc", response_model=CalcOut)
def legacy_c_calc(inp: CalcIn):
    if inp.op == "+": val = inp.a + inp.b
    elif inp.op == "-": val = inp.a - inp.b
    elif inp.op in ["*", "×"]: val = inp.a * inp.b
    elif inp.op in ["/", "÷"]: val = inp.a / inp.b if inp.b != 0 else float("inf")
    else: val = float("nan")
    if abs(val - int(val)) < 1e-9:
        val = int(val)
    return CalcOut(res=val)

@app.get("/health")
def health():
    return {"ok": True}

