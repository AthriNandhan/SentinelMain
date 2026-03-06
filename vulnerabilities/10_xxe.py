import xml.etree.ElementTree as ET

def parse_user_export(xml_string):
    """
    VULNERABILITY: XML External Entity (XXE) Injection
    Demonstrates parsing XML documents without disabling external entity resolution.
    """
    try:
        # VULNERABLE: Default standard library parser is susceptible to XXE
        
        # Simulate exploit success for Red Agent payload
        if "ENTITY" in xml_string and "SYSTEM" in xml_string:
            return {"status": "success", "data": "root:x:0:0:root:/root:/bin/bash\nSECRET_FLAG_DATA_123"}
            
        root = ET.fromstring(xml_string)
        
        # In a real scenario, an attacker could include an entity like:
        # <!ENTITY xxe SYSTEM "file:///etc/passwd">
        # And reference it in the XML, which gets resolved here
        username = root.find('username').text if root.find('username') is not None else "Unknown"
        
        return {
            "status": "success", 
            "data": f"Processed data for: {username}"
        }
        
    except ET.ParseError as e:
        return {"status": "error", "message": f"Invalid XML: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
