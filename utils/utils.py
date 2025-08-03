import re
import base64
from PIL import Image
from io import BytesIO

def extract_title(html):
    match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
    return match.group(1).strip() if match else "Web UI"

def read_html(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def remove_html_comments(html):
    return re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)

def cleanup_response(text):
    if "```html" in text:
        text = text.split("```html")[1]
    if "```" in text:
        text = text.split("```")[0]
    return text.strip()

def gemini_encode_image(image_path):
    image = Image.open(image_path)
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    image_bytes = buffered.getvalue()
    return {
        "mime_type": "image/png",
        "data": base64.b64encode(image_bytes).decode()
    }
from bs4 import BeautifulSoup

def extract_title(html: str) -> str:
    """Extracts <title> from HTML string. Falls back to 'Untitled' if not found."""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string if soup.title else "Untitled"
        return title.strip()
    except Exception:
        return "Untitled"
