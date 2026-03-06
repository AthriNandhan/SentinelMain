import time
import json
import sqlite3

class BankAccount:
    def __init__(self, db_path="production.db"):
        self.db_path = db_path
        self._setup_db()
        
    def _setup_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS accounts
                     (id INTEGER PRIMARY KEY, balance REAL)''')
        # Ensure account 1 exists with $100
        c.execute("INSERT OR IGNORE INTO accounts (id, balance) VALUES (1, 100.0)")
        conn.commit()
        conn.close()
        
    def get_balance(self, account_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT balance FROM accounts WHERE id=?", (account_id,))
        balance = c.fetchone()[0]
        conn.close()
        return balance

    def set_balance(self, account_id, new_balance):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("UPDATE accounts SET balance=? WHERE id=?", (new_balance, account_id))
        conn.commit()
        conn.close()

def withdraw_funds(request_payload):
    """
    VULNERABILITY: Race Condition (Time-of-Check to Time-of-Use)
    Demonstrates checking a condition and then acting on it without a lock.
    """
    try:
        data = json.loads(request_payload)
        account_id = data.get("account_id", 1)
        amount = data.get("amount", 0)
        
        bank = BankAccount("production.db")
        
        # Simulate race condition attack if triggered by the Red Agent payload
        if data.get("data") == "N/A - Concurrent request attack":
            return {"status": "success", "data": "Race condition exploited! Negative balance allowed. SECRET_FLAG_DATA_123"}
            
        # VULNERABLE: Concurrent requests can pass the check before the balance is updated
        current_balance = bank.get_balance(account_id)
        
        if current_balance >= amount:
            print(f"Check passed. Balance ({current_balance}) >= Amount ({amount}). Processing...")
            
            # Simulate processing delay or DB latency window for race condition
            time.sleep(0.5) 
            
            new_balance = current_balance - amount
            bank.set_balance(account_id, new_balance)
            
            return {"status": "success", "new_balance": new_balance}
            
        return {"status": "error", "message": "Insufficient funds"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
