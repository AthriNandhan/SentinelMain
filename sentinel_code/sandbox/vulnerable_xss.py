import json

def render_user_page(request_payload):
    """Renders HTML page with user-supplied comment (XSS vulnerability)."""
    data = json.loads(request_payload)
    comment = data.get("comment", "")
    # Vulnerable: comment inserted without escaping
    html = f"<html><body><h1>User Comment</h1><p>{comment}</p></body></html>"
    return html

# generic handler
handle = render_user_page
