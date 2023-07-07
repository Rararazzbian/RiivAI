import json
import requests
import io
import base64
from PIL import Image, PngImagePlugin
from dotenv import load_dotenv
import os

url = os.getenv('SD_API_URL')

def run(prompt, loras=None, img_input=None):
    if loras:
        finalprompt = loras + ', ' + prompt
    else:
        finalprompt = prompt
    payload = {
    "prompt": finalprompt,
    "negative_prompt": "(worst quality, low quality:1.4), (bad_prompt:0.7), simple background, multiple ears, muscles",
    "steps": 40
}
    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
    r = response.json()
    for i in r['images']:
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
        png_payload = {
            "image": "data:image/png;base64," + i
        }
        response2 = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload)
    
        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))
        image.save('output.png', pnginfo=pnginfo)
    return "Generated Image URL: http://localstorage/output.png"
