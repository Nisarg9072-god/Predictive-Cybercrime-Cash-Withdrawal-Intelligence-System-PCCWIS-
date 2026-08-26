from agent.graph.graph import get_compiled_graph

def test_graph_compilation():
    graph = get_compiled_graph()
    assert graph is not None
