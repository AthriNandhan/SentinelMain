import sys
import os

# Add path like verify_setup.py
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from app.core.config import settings
    print(f"GROQ_KEY_LEN: {len(settings.GROQ_API_KEY)}")
    print("Environment loaded successfully.")
except Exception as e:
    print(f"Error loading settings: {e}")
