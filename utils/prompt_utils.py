def get_direct_prompt_combined(topic):
    return f"""You are a helpful HTML generator. Based on the layout of this UI sketch image, generate the HTML code to implement it. 
The layout is related to "{topic}". 
Generate only the HTML code, without any explanation or extra formatting. Wrap the content in <html>...</html>."""

def get_direct_prompt_combined(title):
    prompt = f"""You are an expert front-end developer. Given the following sketch representing a web UI titled "{title}", generate a clean, well-structured HTML and inline CSS code that replicates the layout and design of the sketch as closely as possible. Ensure that the code is responsive and uses modern best practices.

Only output valid HTML code. Do not explain or add any extra text.
"""
    return prompt
