import json

def render_user_page(request_payload):
    """Renders HTML page with user-supplied comment (XSS vulnerability)."""
    data = json.loads(request_payload)
    comment = data.get("comment", "")
    
    # Vulnerable: comment inserted without escaping
    html = f"<html><body><h1>User Comment</h1><p>{comment}</p></body></html>"
    
    # Simulate XSS exploit success if payload contains typical script tags or handlers
    if "<script" in comment.lower() or "javascript:" in comment.lower() or "onload" in comment.lower() or "onerror" in comment.lower() or "xss" in comment.lower():
        html += "\n<!-- EXPLOIT SUCCESS: SECRET_FLAG_DATA_123 -->"
         
    return html

# generic handler
handle = render_user_page
