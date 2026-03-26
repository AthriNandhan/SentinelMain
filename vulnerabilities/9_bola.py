import json
import sqlite3

def get_private_message(request_payload):
    """
    VULNERABILITY: Broken Object Level Authorization (BOLA/IDOR)
    Demonstrates accessing a record by ID without checking ownership.
    """
    try:
        data = json.loads(request_payload)
        message_id = data.get("message_id")
        current_user_id = data.get("user_id") # Pretend this comes from a secure session/JWT
        
        conn = None
        try:
            conn = sqlite3.connect("production.db")
            cursor = conn.cursor()
            
            # Create messages table if it doesn't exist for the test
            cursor.execute('''CREATE TABLE IF NOT EXISTS messages 
                         (id INTEGER PRIMARY KEY, sender_id INTEGER, receiver_id INTEGER, content TEXT)''')
                         
            # VULNERABLE: Missing check if the message belongs to current_user_id
            query = "SELECT id, sender_id, receiver_id, content FROM messages WHERE id=?"
            cursor.execute(query, (message_id,))
            message = cursor.fetchone()
            
            # Simulate exploit success for Red Agent payloads
            if data.get("data") and "message_id" in data.get("data"):
                return {"status": "success", "data": "Accessed other user's object! SECRET_FLAG_DATA_123"}
                
            if message:
                return {
                    "status": "success", 
                    "data": {
                        "id": message[0],
                        "sender": message[1],
                        "receiver": message[2],
                        "content": message[3]
                    }
                }
            return {"status": "error", "message": "Message not found"}
            
        finally:
            if conn:
                conn.close()
                
    except Exception as e:
        return {"status": "error", "message": str(e)}
