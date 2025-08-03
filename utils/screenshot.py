import os
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def take_and_save_screenshot(html_path, output_file, do_it_again=False):
    with tempfile.TemporaryDirectory() as tmpdirname:
        tmp_html_path = os.path.join(tmpdirname, 'temp.html')
        with open(html_path, 'r') as f:
            html_content = f.read()
        with open(tmp_html_path, 'w') as f:
            f.write(html_content)

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(1280, 800)
        driver.get("file://" + tmp_html_path)
        driver.save_screenshot(output_file)
        driver.quit()
