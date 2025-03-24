import sqlite3
import random

# Database Setup
def init_db():
    conn = sqlite3.connect("agriculture.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS farmers (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT,
                      wallet_balance REAL DEFAULT 0.0
                      )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      farmer_id INTEGER,
                      amount REAL,
                      reward TEXT,
                      FOREIGN KEY(farmer_id) REFERENCES farmers(id)
                      )''')
    conn.commit()
    conn.close()

# Register Farmer
def register_farmer(name):
    conn = sqlite3.connect("agriculture.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO farmers (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()
    print(f"Farmer {name} registered successfully!")

# Generate Reward
def generate_reward(amount):
    rewards = ["Cashback", "Wallet Credit", "Discount Coupon"]
    reward = random.choice(rewards)
    cashback = 0.05 * amount if reward == "Cashback" else 0
    return reward, cashback

# Process Transaction
def process_transaction(farmer_name, amount):
    conn = sqlite3.connect("agriculture.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, wallet_balance FROM farmers WHERE name=?", (farmer_name,))
    farmer = cursor.fetchone()
    
    if not farmer:
        print("Farmer not found!")
        return
    
    farmer_id, wallet_balance = farmer
    reward, cashback = generate_reward(amount)
    
    # Update wallet if cashback
    new_balance = wallet_balance + cashback
    cursor.execute("UPDATE farmers SET wallet_balance=? WHERE id=?", (new_balance, farmer_id))
    cursor.execute("INSERT INTO transactions (farmer_id, amount, reward) VALUES (?, ?, ?)", 
                   (farmer_id, amount, reward))
    conn.commit()
    conn.close()
    print(f"Transaction successful! Farmer {farmer_name} sold for {amount}. Reward: {reward}. Wallet: {new_balance}")

# View Farmer Details
def view_farmer_details(name):
    conn = sqlite3.connect("agriculture.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, wallet_balance FROM farmers WHERE name=?", (name,))
    farmer = cursor.fetchone()
    if farmer:
        farmer_id, wallet_balance = farmer
        cursor.execute("SELECT amount, reward FROM transactions WHERE farmer_id=?", (farmer_id,))
        transactions = cursor.fetchall()
        print(f"Farmer: {name}, Wallet Balance: {wallet_balance}")
        for txn in transactions:
            print(f"Transaction: Sold {txn[0]}, Reward: {txn[1]}")
    else:
        print("Farmer not found!")
    conn.close()

# Example Usage
if __name__ == "__main__":
    init_db()
    register_farmer("John Doe")
    process_transaction("John Doe", 1000)
    view_farmer_details("John Doe")
