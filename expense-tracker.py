from fastmcp import FastMCP
import os 
import sqlite3
mcp = FastMCP(name='ExpenseTracker')

DB_NAME = "expenses.db"

def get_db_connection():
    conn = sqlite3.connect(
        database=DB_NAME
    )
    conn.row_factory = sqlite3.Row

    return conn

def create_db():
    conn = get_db_connection()
    conn.execute("""
    CREATE TABLE IF NOT EXIST expenses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT DEFAULT '',
        category TEXT DEFAULT '',
        note TEXT DEFAULT ''   
        )
    """)

create_db()

@mcp.tool()
def input_expense(date, amount: str, category : str , subcategory : str = "", note : str=""):
    """
    Docstring for input_expense
    
    :param date: Date of expense
    :param amount: Money spent
    :type amount: str
    :param category: Categories the expense
    :type category: str
    :param note: A short note to remeber the spending.
    :type note: str
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO expenses(date, amount, category, subcategory, note) VALUES(?,?,?,?,?)
    """,(date, amount, category, subcategory, note))
    
    conn.commit()
    conn.close()
    return {'status':'ok', 'id': cur.lastrowid}
    

@mcp.tool()
def list_expense():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM expenses ORDER BY id ASC")
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

