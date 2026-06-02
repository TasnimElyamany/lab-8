#!/usr/bin/env python3
"""Part 7: a minimal MCP server exposing two tools. Run: python mcp_server.py"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("orders")
_ORDERS = {"A100": "shipped", "B200": "processing"}

@mcp.tool()
def lookup_order(order_id: str) -> str:
    """Return the status of a customer order."""
    return _ORDERS.get(order_id, "unknown")

@mcp.tool()
def calculate(expr: str) -> float:
    """Evaluate a simple arithmetic expression (digits and + - * / . ( ) only)."""
    if not all(ch in "0123456789.+-*/() " for ch in expr):
        raise ValueError("only arithmetic allowed")
    return float(eval(expr, {"__builtins__": {}}, {}))

if __name__ == "__main__":
    mcp.run()  # stdio transport by default
