from mcp.server.fastmcp import Context, FastMCP
from mcp.server.fastmcp.prompts.base import AssistantMessage, Message, UserMessage

mcp = FastMCP("Oracle")


@mcp.resource("config://app")
def get_config() -> str:
    return "Oracle MCP server"


@mcp.tool()
async def oracle(query: str, ctx: Context) -> str:
    return "Oracle says: oterm"


@mcp.prompt(name="Oracle prompt", description="Prompt to ask the oracle a question.")
async def oracle_prompt(question: str) -> str:
    return f"Oracle: {question}"


@mcp.prompt()
def debug_error(error: str) -> list[Message]:
    return [
        UserMessage(f"I'm seeing this error: {error}"),
        AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]


if __name__ == "__main__":
    mcp.run(transport="stdio")
