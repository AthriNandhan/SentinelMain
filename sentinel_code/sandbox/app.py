from flask import Flask, request, jsonify
import sqlite3
import os
import vulnerable_code

app = Flask(__name__)

DB_NAME = "production.db"
FLAG = "SECRET_FLAG_DATA_123"

def setup_db():
    """Initialize the database with sample data."""
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, active INTEGER, data TEXT)")
    
    # Insert normal user
    cursor.execute("INSERT INTO users (username, password, active, data) VALUES ('alice', 'password123', 1, 'Public Profile Data')")
    
    # Insert admin user with FLAG
    cursor.execute("INSERT INTO users (username, password, active, data) VALUES ('admin', 'admin123', 1, ?)", (FLAG,))
    
    conn.commit()
    conn.close()

# Initialize DB on startup
setup_db()

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json(force=True)
        # Pass the raw JSON string to the vulnerable function as it expects
        # In a real app, this might be request.data or similar
        import json
        payload = json.dumps(data)
        
        # find the function to call automatically
        import inspect
        
        # Get all functions defined in the vulnerable_code module
        functions = inspect.getmembers(vulnerable_code, inspect.isfunction)
        
        result = None
        handler = None
        
        # Try finding a generic handle first
        if hasattr(vulnerable_code, 'handle'):
            handler = vulnerable_code.handle
        elif functions:
            # Just grab the first defined function that isn't a builtin/import
            for name, func in functions:
                if func.__module__ == 'vulnerable_code':
                    handler = func
                    break
        
        if handler:
            result = handler(payload)
        else:
            raise AttributeError('vulnerable_code module has no handler function defined')
        
        if result:
            return jsonify({"status": "success", "data": result})
        else:
            return jsonify({"status": "failure", "data": None})
            
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=False)
