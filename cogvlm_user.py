# cogvlm_user.py
import os
import json
import base64
import traceback
import time
import argparse
from PIL import Image
from tqdm import tqdm
import requests

from utils.prompt_utils import get_direct_prompt_combined
from utils.utils import cleanup_response
from utils.screenshot import take_and_save_screenshot


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
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{encoded}"
                        }
                    }
                ]}
            ]
        }

        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
        res.raise_for_status()

        output = res.json()["choices"][0]["message"]["content"]
        return cleanup_response(output)
    except Exception as e:
        print("⚠️ CogVLM call failed:", str(e))
        traceback.print_exc()
        return ""


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--upload_dir", default="user_uploads")
    parser.add_argument("--out_dir", default="user_outputs")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    files = [f for f in os.listdir(args.upload_dir) if f.endswith(".png")]

    for f in tqdm(files):
        sketch_path = os.path.join(args.upload_dir, f)
        base_name = os.path.splitext(f)[0]
        prompt = get_direct_prompt_combined("This is a custom UI sketch. Convert it into clean HTML/CSS code.")

        output_html = cogvlm_call(prompt, sketch_path)

        if not output_html:
            print(f"Failed to generate HTML for {f}")
            continue

        html_path = os.path.join(args.out_dir, base_name + ".html")
        with open(html_path, "w") as f_html:
            f_html.write(output_html)

        screenshot_path = os.path.join(args.out_dir, base_name + ".png")
        take_and_save_screenshot(html_path, output_file=screenshot_path, do_it_again=True)

        print(f"✅ HTML created: {html_path}")
