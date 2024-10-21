---
license: odc-by
tags:
- code
---

The Sketch2Code dataset consists of 731 human-drawn sketches paired with 484 real-world webpages from the [Design2Code dataset](https://huggingface.co/datasets/SALT-NLP/Design2Code), serving to benchmark Vision-Language Models (VLMs) on converting rudimentary sketches into web design prototypes.

Each example consists of a pair of source HTML and rendered webpage screenshot (stored in `webpages/` directory under name `{webpage_id}.html` and `{webpage_id}.png`), as well as 1 to 3 sketches drawn by human annotators (stored in `sketches/` directory under name `{webpage_id}_{sketch_id}.png`).

Note that all images in these webpages are replaced by a blue placeholder image (rick.jpg).

Please refer to our [Project Page](https://salt-nlp.github.io/Sketch2Code-Project-Page/) for more detailed information.


### Example Usage
You can download the full dataset through this [link](https://huggingface.co/datasets/SALT-NLP/Sketch2Code/resolve/main/sketch2code_dataset_v1.zip?download=true). After unzipping, all 731 sketches (`{webpage_id}_{sketch_id}.png`) and 484 webpage screenshots + HTMLs (`{webpage_id}.html` and `{webpage_id}.png`) will be appear flattened under `sketch2code_dataset_v1_cleaned/`. We also include `rick.jpg` which is used to render the image placeholder in the HTML code.

Alternatively, you may access the data online through `huggingface_hub`. Below is a sample script to access the data via `huggingface_hub` and generate predictions using Llava-1.6-8b:
``` python
import os
import re
import torch

from PIL import Image
from tqdm import tqdm
from transformers import LlavaNextProcessor, LlavaNextForConditionalGeneration
from huggingface_hub import HfApi, hf_hub_download

def extract_html(code):
    # re.DOTALL allows the dot (.) to match newlines as well
    matches = re.findall(r'```(.*?)```', code, re.DOTALL)
    if matches:
        return matches[-1]  # Return the last match found
    else:
        return None
    
def cleanup_response(response):
    if not response:
        return None
    if '<!DOCTYPE' not in response and '<html>' not in response:
        # invalid html, return none
        return None
    ## simple post-processing
    if response[ : 3] == "```":
        response = response[3 :].strip()
    if response[-3 : ] == "```":
        response = response[ : -3].strip()
    if response[ : 4] == "html":
        response = response[4 : ].strip()

    ## strip anything before '<!DOCTYPE'
    if '<!DOCTYPE' in response:
        response = response.split('<!DOCTYPE', 1)[1]
        response = '<!DOCTYPE' + response
		
    ## strip anything after '</html>'
    if '</html>' in response:
        response = response.split('</html>')[0] + '</html>'
    return response


def llava_call(model, processor, user_message, image, history=None):
    def parse_resp(text_output):
        idx = text_output.rfind("assistant")

        if idx > -1:
            return text_output[idx+len("assistant"):].strip()
        else:
            return text_output
    
    if not history:
        conversation = [
            {

            "role": "user",
            "content": [
                {"type": "text", "text": user_message},
                {"type": "image"},
                ],
            },
        ]
    else:
        conversation = history
        conversation.append({
            "role": "user",
            "content": [
                {"type": "text", "text": user_message},
            ],
        })
    prompt = processor.apply_chat_template(conversation, add_generation_prompt=True)
    inputs = processor(images=image, text=prompt, return_tensors="pt").to(model.device)
    output = parse_resp(processor.decode(model.generate(**inputs, max_new_tokens=4096, do_sample=True, temperature=0.5, repetition_penalty=1.1)[0], skip_special_tokens=True))
    
    conversation.append({
        "role": "assistant",
        "content": [
            {"type": "text", "text": output}
        ]
    })

    return output, conversation


api = HfApi(token="your_hf_access_token")
repo_id = "SALT-NLP/Sketch2Code"

files = api.list_repo_files(repo_id, repo_type="dataset")
sketch_files = [file for file in files if file.startswith('sketches/')][:5]    # running only the first 5 sketches


prompt = '''You are an expert web developer who specializes in HTML and CSS. A user will provide you with a sketch design of the webpage following the wireframing conventions, where images are represented as boxes with an "X" inside, and texts are replaced with curly lines. You need to return a single html file that uses HTML and CSS to produce a webpage that strictly follows the sketch layout. Include all CSS code in the HTML file itself. If it involves any images, use "rick.jpg" as the placeholder name. You should try your best to figure out what text should be placed in each text block. In you are unsure, you may use "lorem ipsum..." as the placeholder text. However, you must make sure that the positions and sizes of these placeholder text blocks matches those on the provided sketch.

Do your best to reason out what each element in the sketch represents and write a HTML file with embedded CSS that implements the design. Do not hallucinate any dependencies to external files. Pay attention to things like size and position of all the elements, as well as the overall layout. You may assume that the page is static and ignore any user interactivity.

Here is a sketch design of a webpage. Could you write a HTML+CSS code of this webpage for me?

Please format your code as
```
{{HTML_CSS_CODE}}
```
Remember to use "rick.jpg" as the placeholder for any images'''

model_name = "llava-hf/llama3-llava-next-8b-hf"
processor = LlavaNextProcessor.from_pretrained(model_name)
model = LlavaNextForConditionalGeneration.from_pretrained(
    model_name, 
    device_map="auto", 
    load_in_8bit=True,
    torch_dtype=torch.float16
)

for sketch_file in tqdm(sketch_files):
    sketch_path = hf_hub_download(repo_id=repo_id, repo_type="dataset", filename=sketch_file)
    sketch = Image.open(sketch_path)
    
    agent_resp, _ = llava_call(model, processor, prompt, sketch)
    html_response = cleanup_response(extract_html(agent_resp))
    
    if not html_response:
        html_response = "Error: HTML not Generated"
    
    output_path = sketch_path.split('/')[-1].replace(".png", ".html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_response)
    
    print(f"Output saved to {output_path}")
```