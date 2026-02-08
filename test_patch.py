"""Test script to verify patch works"""
import sys
from pathlib import Path

# Add paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "PageIndex"))

# Import and patch
from pageindex_ollama import patch_pageindex_for_ollama, ChatGPT_API_ollama

print("Testing patch...")
result = patch_pageindex_for_ollama()
print(f"Patch result: {result}")

# Check if patched
from pageindex import utils
print(f"utils.ChatGPT_API: {utils.ChatGPT_API}")
print(f"Is patched: {utils.ChatGPT_API is ChatGPT_API_ollama}")

# Try to call it
try:
    response = utils.ChatGPT_API(model="llama3.1:8b", prompt="Say hello", api_key=None)
    print(f"Response: {response[:50]}...")
except Exception as e:
    print(f"Error: {e}")

