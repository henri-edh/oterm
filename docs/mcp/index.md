### Model Context Protocol support

`oterm` has support for Anthropic's open-source [Model Context Protocol](https://modelcontextprotocol.io). While Ollama does not yet directly support the protocol, `oterm` attempts to bridge [MCP servers](https://github.com/modelcontextprotocol/servers) with Ollama.

To add an MCP server to `oterm`, simply add the server shim to oterm's `config.json`. For example for the [git](https://github.com/modelcontextprotocol/servers/tree/main/src/git) MCP server you would add something like the following to the `mcpServers` section of the `oterm` configuration file:

```json
{
  ...
  "mcpServers": {
    "git": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--mount",
        "type=bind,src=/Users/ggozad/dev/open-source/oterm,dst=/oterm",
        "mcp/git"
      ]
    }
  }
}
```
### Supported MCP Features
#### Tools
By transforming MCP tools into Ollama tools `oterm` provides full support.

!!! note
    A lot of the smaller LLMs are not as capable with tools as larger ones you might be used to. If you experience issues with tools, try reducing the number of tools you attach to a chat, increase the context size, or use a larger LLM.


![Tool support](../img/mcp_tools.svg)
oterm using the `git` MCP server to access its own repo.

#### Prompts
`oterm` supports MCP prompts. Use the "Use MCP prompt" command to invoke a form with the prompt. Submitting will insert the prompt messages into the chat.

![Prompt support](../img/mcp_prompts.svg)
oterm displaying a test MCP prompt.
