#!/usr/bin/env python3
import asyncio, json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    params = StdioServerParameters(command="python", args=["mcp_server.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # STEP 1: discover server capabilities + tool descriptions
            tools = await session.list_tools()
            print("STEP 1 discover:", [t.name for t in tools.tools])
            # STEP 2: (in a full agent) these descriptions would be added to the model prompt.
            # STEP 3: the model output would be parsed for a tool-invocation request. Here we simulate that.
            requested = {"name": "lookup_order", "arguments": {"order_id": "A100"}}
            print("STEP 3 parsed request:", requested)
            # STEP 4: invoke the requested tool through MCP
            result = await session.call_tool(requested["name"], requested["arguments"])
            print("STEP 4 invoke ->", result.content[0].text)
            # STEP 5: tool output is sent back to the model (printed here)
            print("STEP 5 return-to-model:", result.content[0].text)

if __name__ == "__main__":
    asyncio.run(main())
