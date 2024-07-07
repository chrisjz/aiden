import os

COGNITIVE_API_URL_BASE = f'{os.environ.get("COGNITIVE_API_PROTOCOL", "http")}://{os.environ.get("COGNITIVE_API_HOST", "localhost")}:{os.environ.get("COGNITIVE_API_PORT", "11434")}'
COGNITIVE_API_URL_CHAT = f"{COGNITIVE_API_URL_BASE}/api/chat"
VISION_API_URL_BASE = f'{os.environ.get("VISION_API_PROTOCOL", "http")}://{os.environ.get("VISION_API_HOST", "localhost")}:{os.environ.get("VISION_API_PORT", "11434")}'
