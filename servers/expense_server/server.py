
from pathlib import Path
import asyncio

import aiosqlite
from mcp.server.fastmcp import FastMCP


# Initialize MCP Server
mcp = FastMCP("Expense Management Server")

# Database path
BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "expenses.db"


# Initialize Database
async def initialize_database():

    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                date TEXT NOT NULL
            )
        """)

        await db.commit()




# Tool 1: Add Expense
@mcp.tool()
async def add_expense(
    amount: float,
    category: str,
    description: str,
    date: str
) -> str:
    """Add a new expense to the expense tracker."""

    if amount <= 0:
        return "Error: Amount must be greater than zero."

    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute("""
            INSERT INTO expenses
            (amount, category, description, date)
            VALUES (?, ?, ?, ?)
        """, (amount, category, description, date))

        await db.commit()

    return f"Successfully added expense of Rs. {amount}"


# Tool 2: View Expenses
@mcp.tool()
async def view_expenses() -> list[dict]:
    """Retrieve all expenses from the database."""

    async with aiosqlite.connect(DB_PATH) as db:

        db.row_factory = aiosqlite.Row

        async with db.execute(
            "SELECT * FROM expenses ORDER BY date DESC"
        ) as cursor:

            rows = await cursor.fetchall()

    return [dict(row) for row in rows]


# Tool 3: Delete Expense
@mcp.tool()
async def delete_expense(expense_id: int) -> str:
    """Delete an expense using its ID."""

    async with aiosqlite.connect(DB_PATH) as db:

        cursor = await db.execute(
            "DELETE FROM expenses WHERE id = ?",
            (expense_id,)
        )

        await db.commit()

        deleted = cursor.rowcount

    if deleted == 0:
        return "Expense not found."

    return f"Expense {expense_id} deleted successfully."


# Start MCP Server
if __name__ == "__main__":

    asyncio.run(initialize_database())

    mcp.run(transport="stdio")
