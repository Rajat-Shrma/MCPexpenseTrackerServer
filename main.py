from fastmcp import FastMCP
import os 
import sqlite3
mcp = FastMCP(name='ExpenseTracker')

DB_NAME = os.path.join(os.path.dirname(__file__),"expenses.db")
CATEGORIES = os.path.join(os.path.dirname(__file__),"category.json")

def delete():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS expenses")

    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(
        database=DB_NAME
    )
    conn.row_factory = sqlite3.Row

    return conn

def create_db():
    conn = get_db_connection()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS expenses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT DEFAULT '',
        subcategory TEXT DEFAULT '',
        note TEXT DEFAULT ''   
        )
    """)
    conn.commit()
    conn.close()

create_db()

@mcp.tool()
def input_expense(date, amount: float, category : str , subcategory : str = "", note : str=""):
    """
    Docstring for input_expense
    
    :param date: Date of expense, Dates must be in YYYY-MM-DD format
    :param amount: Money spent
    :type amount: float
    :param category: Categories the expense
    :type category: str
    :param subcategory: subcategory of the expense
    :type subcategory: str
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
    return {'status':'Expense Added', 'id': cur.lastrowid}
    

@mcp.tool()
def list_expense(start_date, end_date):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM expenses WHERE date BETWEEN ? AND ? ORDER BY id ASC", (start_date,end_date))
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@mcp.tool()
def summarize(start_date, end_data, category=None):
    ''' Summarize expenses by category within an inclusive date range.'''

    conn = get_db_connection()
    cur = conn.cursor()
    query = """
    SELECT category, SUM(amount) AS total_amount 
    FROM expenses
    WHERE date BETWEEN ? AND ?
                """
    
    params = [start_date,end_data]

    if category:
        params.append(category)
        query += " AND category = ?"
        
    query += " GROUP BY category ORDER BY category ASC"

    cur.execute(query, params)

    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@mcp.tool()
def update_expense(
    id : int,
    date : str = None,
    amount : float = None,
    category : str = None,
    subcategory : str = None,
    note : str = None

):
    """
    Update fields of an existing expense.
    Only provided fields will be updated.

    :param expense_id: ID of the expense to update
    """

    conn= get_db_connection()
    cur = conn.cursor()
    
    fields = []
    params = []

    if date is not None:
        fields.append("date = ?")
        params.append(date)

    if amount is not None:
        fields.append("amount = ?")
        params.append(amount)

    if category is not None:
        fields.append("category = ?")
        params.append(category)

    if subcategory is not None:
        fields.append("subcategory = ?")
        params.append(subcategory)

    if note is not None:
        fields.append("note = ?")
        params.append(note)

    if not fields:
        return {"status": "No fields provided to update"}
    
    params.append(id)

    query = f"""    
        UPDATE expenses SET {", ".join(fields)}
        WHERE id = ?
"""
    cur.execute(query, params)
    conn.commit()
    if cur.rowcount == 0:
        conn.close()
        return {"status":"Expense not found."}
    
    cur.execute("SELECT * FROM expenses WHERE id = ?",(id,))
    row = cur.fetchone()
    conn.close()
    return {
        "status": "Expense updated",
        "expense":dict(row)
    }

@mcp.tool()
def delete_expense(expense_id: int):
    """
    Delete an expense by ID.

    :param expense_id: ID of the expense to delete
    """

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
    row = cur.fetchone()

    if row is None:
        conn.close()
        return {"status": "Expense not found"}

    cur.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()

    return {
        "status": "Expense deleted",
        "deleted_expense": dict(row)
    }



@mcp.resource("expense://categories", mime_type = 'application/json')
def category_selection():
    """ Returns the expense category and subcategory from the category.json file each expense should have a category and a subcategory for proper tabulation"""
    with open(CATEGORIES, 'r', encoding='utf-8') as f:
        return f.read()