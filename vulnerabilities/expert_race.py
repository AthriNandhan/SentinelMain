# Select in Dropdown: Race Condition
import os
import time
import shutil
import threading
import logging
import uuid
from typing import List

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(threadName)s - %(message)s')

class TransactionManager:
    """
    Manages file-based transactions for a banking system.
    """
    def __init__(self, transaction_dir: str = "transactions"):
        self.transaction_dir = transaction_dir
        if not os.path.exists(transaction_dir):
            os.makedirs(transaction_dir)

    def process_transaction(self, user_id: str, amount: float, transaction_id: str):
        """
        Processes a transaction by creating a temporary file and moving it.
        """
        user_dir = os.path.join(self.transaction_dir, user_id)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)

        temp_file = os.path.join(user_dir, f"{transaction_id}.tmp")
        final_file = os.path.join(user_dir, f"{transaction_id}.txn")

        # 1. Validation Check (Simulated TOCTOU gap)
        # We check if the transaction already exists to prevent double spending
        if os.path.exists(final_file):
            logging.error(f"Transaction {transaction_id} already exists!")
            return False

        # --- VULNERABILITY: Time-of-Check to Time-of-Use (TOCTOU) Race Condition ---
        # A skilled attacker can exploit the tiny gap between the check above 
        # and the file creation below to effectively double-spend or corrupt data
        # if multiple threads/processes handle the same transaction ID simultaneously.
        
        # Simulating heavy processing delay to widen the race window
        time.sleep(0.1) 
        
        try:
            # 2. Setup Transaction
            with open(temp_file, "w") as f:
                f.write(f"Amount: {amount}\nStatus: PENDING")
            
            logging.info(f"Processing transaction {transaction_id} for ${amount}")
            
            # 3. Finalize Transaction
            shutil.move(temp_file, final_file)
            
            # 4. Update Balance (Mock)
            self._update_balance(user_id, amount)
            
            logging.info(f"Transaction {transaction_id} completed.")
            return True
            
        except Exception as e:
            logging.error(f"Transaction failed: {e}")
            if os.path.exists(temp_file):
                os.remove(temp_file)
            return False

    def _update_balance(self, user_id: str, amount: float):
        # Mock balance update
        pass

def worker(manager, user_id, amount, txn_id):
    manager.process_transaction(user_id, amount, txn_id)

def handle(payload):
    """
    Handle function for Flask app integration.
    Expects JSON payload with transaction details.
    """
    try:
        import json
        data = json.loads(payload)
        manager = TransactionManager()
        user_id = data.get("user_id", "user_123")
        amount = data.get("amount", 100.0)
        txn_id = data.get("transaction_id", str(uuid.uuid4()))
        result = manager.process_transaction(user_id, amount, txn_id)
        return f"Transaction processed: {result}"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    # Simulation of the Race Condition
    manager = TransactionManager()
    user = "user_123"
    txn_id = str(uuid.uuid4())
    
    # Two threads try to process the SAME transaction ID at the same time
    t1 = threading.Thread(target=worker, args=(manager, user, 100.0, txn_id), name="Thread-1")
    t2 = threading.Thread(target=worker, args=(manager, user, 100.0, txn_id), name="Thread-2")
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()
    
    # Check results
    user_dir = os.path.join("transactions", user)
    files = os.listdir(user_dir)
    print(f"Final files in directory: {files}")
    
    # Cleanup
    shutil.rmtree("transactions")
