from adapters import CanonicalRequest, ADAPTERS

def demo_retriever_A():
    req = CanonicalRequest(
        agent_kind="retriever",
        inputs={"query":"請求レポート 手順", "top_k": 2},
        context={"locale":"ja-JP"},
        telemetry={"trace_id":"demo-001"}
    )
    res = ADAPTERS["retriever_A"](req)
    print("[Retriever A] ->", res.outputs)

def demo_retriever_B():
    req = CanonicalRequest(
        agent_kind="retriever",
        inputs={"query":"サービス 概要", "top_k": 3},
        context={"locale":"ja-JP"},
        telemetry={"trace_id":"demo-002"}
    )
    res = ADAPTERS["retriever_B"](req)
    print("[Retriever B] ->", res.outputs)

def demo_tool_C():
    req = CanonicalRequest(
        agent_kind="tool",
        inputs={"expr":"3+4"},
        telemetry={"trace_id":"demo-003"}
    )
    res = ADAPTERS["tool_C"](req)
    print("[Tool C] ->", res.outputs)

if __name__ == "__main__":
    print("=== Adapter Demos (Canonical -> Legacy -> Canonical) ===")
    demo_retriever_A()
    demo_retriever_B()
    demo_tool_C()

