import asyncio

from nl_sql.mcp_server import mcp


def test_registers_semantic_tools():
    tools = asyncio.run(mcp.list_tools())
    names = {tool.name for tool in tools}
    assert names == {
        "list_metrics",
        "get_metric_definition",
        "compile_metric_query",
        "explain_query",
    }
