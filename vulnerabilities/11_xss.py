from fastapi.responses import HTMLResponse
import json

def generate_search_results(request_payload):
    """
    VULNERABILITY: Cross-Site Scripting (XSS) via Unescaped Templates
    Demonstrates returning user input directly into an HTML response.
    """
    try:
        data = json.loads(request_payload)
        query = data.get("comment", data.get("q", ""))
        
        # Simulate searching a database
        results = ["Item 1", "Item 2"]
        result_items = "".join([f"<li>{item}</li>" for item in results])
        
        # VULNERABLE: Reflects unescaped user input directly into the HTML
        # An attacker can send q="<script>alert(1)</script>"
        html_content = f"""
        <html>
            <head><title>Search</title></head>
            <body>
                <h1>Search results for: {query}</h1>
                <ul>{result_items}</ul>
            </body>
        </html>
        """
        
        # Mocking the exploit flag for the test harness
        data_res = html_content
        if "<script>" in query.lower() or "javascript:" in query.lower() or "onerror=" in query.lower() or "onload=" in query.lower():
            data_res += "\n<!-- XSS Executed! SECRET_FLAG_DATA_123 -->"
        
        # Simulating returning an HTML response as JSON data so test_harness can read it
        return {"status": "success", "data": data_res}
        
    except Exception as e:
        return {"status": "error", "data": f"Error: {str(e)}"}
