"""Quick script to list available Gemini models for this API key."""
import google.generativeai as genai
import os, sys

# Try env var first, then fall back to streamlit secrets file
api_key = os.environ.get("GEMINI_API_KEY", "")
if not api_key:
    # Try reading from streamlit secrets toml manually
    import toml
    for p in [".streamlit/secrets.toml", "../.streamlit/secrets.toml"]:
        if os.path.exists(p):
            secrets = toml.load(p)
            api_key = secrets.get("GEMINI_API_KEY", "")
            break

if not api_key:
    print("ERROR: No GEMINI_API_KEY found in env or secrets.toml")
    sys.exit(1)

genai.configure(api_key=api_key)

print("Available models supporting generateContent:")
print("-" * 60)
for m in genai.list_models():
    methods = [s.name for s in m.supported_generation_methods] if hasattr(m, 'supported_generation_methods') else []
    if "generateContent" in methods:
        print(f"  {m.name}")
