
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math Calculation Server")


@mcp.tool()
async def addition(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


@mcp.tool()
async def subtraction(a: float, b: float) -> float:
    """Subtract the second number from the first."""
    return a - b


@mcp.tool()
async def multiplication(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


@mcp.tool()
async def division(a: float, b: float) -> float:
    """Divide the first number by the second."""

    if b == 0:
        raise ValueError("Cannot divide by zero.")

    return a / b


if __name__ == "__main__":
    mcp.run(transport="stdio")
