import sqlite3

DB_NAME = "sales.db"

def connect():
    return sqlite3.connect(DB_NAME)

def create_tables():
    conn = connect()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name TEXT, price REAL, quantity INTEGER)""")
    c.execute("""CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER, product_id INTEGER, 
        quantity INTEGER, total_price REAL, 
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    conn.commit()
    conn.close()

def add_new_product(name, price, qty):
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)", (name, price, qty))
    conn.commit()
    conn.close()

def update_product(p_id, name, price, qty):
    conn = connect()
    c = conn.cursor()
    c.execute("UPDATE products SET name=?, price=?, quantity=? WHERE id=?", (name, price, qty, p_id))
    conn.commit()
    conn.close()

def delete_product(p_id):
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM products WHERE id=?", (p_id,))
    conn.commit()
    conn.close()

def get_inventory():
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    data = c.fetchall()
    conn.close()
    return data

def process_bulk_sale(cart_items):
    conn = connect()
    c = conn.cursor()
    try:
        c.execute("SELECT MAX(invoice_id) FROM sales")
        res = c.fetchone()[0]
        invoice_id = (res + 1) if res else 1
        final_items = []; grand_total = 0
        for item in cart_items:
            c.execute("SELECT name, price, quantity FROM products WHERE id = ?", (item['id'],))
            product = c.fetchone()
            if not product or product[2] < item['qty']: raise ValueError("Stock Error")
            total = product[1] * item['qty']
            grand_total += total
            c.execute("UPDATE products SET quantity = ? WHERE id = ?", (product[2] - item['qty'], item['id']))
            c.execute("INSERT INTO sales (invoice_id, product_id, quantity, total_price) VALUES (?, ?, ?, ?)", 
                      (invoice_id, item['id'], item['qty'], total))
            final_items.append({'name': product[0], 'qty': item['qty'], 'price': product[1], 'total': total})
        conn.commit()
        return True, invoice_id, final_items, grand_total
    except:
        conn.rollback()
        return False, "Error in sale", None, None
    finally: conn.close()

def get_sales_stats():
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT p.name, SUM(s.quantity) FROM sales s JOIN products p ON s.product_id = p.id GROUP BY p.id ORDER BY SUM(s.quantity) DESC")
    data = c.fetchall()
    conn.close()
    return data
 
def get_all_sales_detailed():
    conn = connect()
    c = conn.cursor()
    # جلب تفاصيل المبيعات مع اسم المنتج من جدول المنتجات
    query = """
        SELECT s.date, p.name, s.quantity, s.total_price, s.invoice_id
        FROM sales s
        JOIN products p ON s.product_id = p.id
        ORDER BY s.date DESC
    """
    c.execute(query)
    data = c.fetchall()
    conn.close()
    return data

def create_expense_table():
    conn = connect()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT,
                    amount REAL,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    description TEXT)""")
    conn.commit()
    conn.close()

# 2. دالة إضافة مصروف جديد
def add_expense(category, amount, description):
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO expenses (category, amount, description) VALUES (?, ?, ?)", 
              (category, amount, description))
    conn.commit()
    conn.close()

# 3. دالة جلب كل المصروفات
def get_expenses():
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT * FROM expenses ORDER BY date DESC")
    data = c.fetchall()
    conn.close()
    return data