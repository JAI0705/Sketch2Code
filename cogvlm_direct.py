import os
import json
import base64
import traceback
import time
import argparse
from PIL import Image
from tqdm import tqdm
import requests

from utils.utils import extract_title, read_html, remove_html_comments, cleanup_response, gemini_encode_image
from utils.prompt_utils import get_direct_prompt_combined
from utils.screenshot import take_and_save_screenshot
# from metrics.layout_similarity import layout_similarity

def cogvlm_call(prompt, image_path):
    try:
        with open(image_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode("utf-8")

        headers = {
            "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
            "Content-Type": "application/json",
        }

        body = {
            "model": "gryphe/mythomax-l2-13b",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded}"}}
                    ]
                }
            ]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
        response.raise_for_status()
        return cleanup_response(response.json()["choices"][0]["message"]["content"])

    except Exception as e:
        print("⚠️ CogVLM call failed:", str(e))
        traceback.print_exc()
        return ""

def generate(sketch_path, html_path, out_dir, img_id):
    html = remove_html_comments(read_html(html_path))
    topic = extract_title(html)
    prompt = get_direct_prompt_combined(topic)

    output_html = cogvlm_call(prompt, sketch_path)

    if not output_html:
        return False, {}

    html_file = os.path.join(out_dir, f"{img_id}.html")
    with open(html_file, 'w') as f:
        f.write(output_html)

    image_file = os.path.join(out_dir, f"{img_id}.png")
    take_and_save_screenshot(html_file, output_file=image_file, do_it_again=True)

    return True, {
        "id": img_id,
        "filename": html_file
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", default="sketch2code_dataset_v1/sketches")
    parser.add_argument("--html_dir", default="sketch2code_dataset_v1/webpages")
    parser.add_argument("--out_dir", default="output_cogvlm")
    parser.add_argument("--limit", type=int, default=3)
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    all_sketches = sorted([f for f in os.listdir(args.input_dir) if f.endswith(".png")])[:args.limit]
    available_html_ids = set([f.split('.')[0] for f in os.listdir(args.html_dir) if f.endswith(".html")])

    examples = []
    for file in all_sketches:
        base = file.split("_")[0]
        if base in available_html_ids:
            examples.append((file, f"{base}.html"))

    results = []
    for sketch_file, html_file in tqdm(examples):
        sketch_path = os.path.join(args.input_dir, sketch_file)
        html_path = os.path.join(args.html_dir, html_file)
        print(f"Saved HTML: {html_path}")

        img_id = sketch_file.split("_")[0]

        success, res = generate(sketch_path, html_path, args.out_dir, img_id)
        if success:
            results.append(res)

    with open(os.path.join(args.out_dir, "results.json"), "w") as f:
        json.dump(results, f, indent=4)
