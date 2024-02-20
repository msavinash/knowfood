from flask import Flask, request, jsonify
from google.cloud import vision
import os
import google.generativeai as genai
#from ast import literal_eval
import json
import re
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Set Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ""
os.environ["GOOGLE_API_KEY"] = ""

# Configure generative AI
genai.configure()

@app.route('/get-ingredients', methods=['POST'])
def get_ingredients():
    data = request.get_data().decode('utf-8').replace('\\n', '\n')
    ingredientsRawText = data
    prompt = """This is supposed to contain ingredients. Extract each individual ingredient separately and return as a JSON under key "ingredients". If any ingredients are mentioned in brackets, mention them as actual ingredients. If it says may contain, add those under a different key "mayContain", not under other ingredients."""
    prompt += ingredientsRawText.lower()
    #print(prompt)

    if not ingredientsRawText:
        return jsonify({'error': 'Query not provided'})

    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.5,)
    )
    from pprint import pprint
    pprint(response.candidates)
    response = response.text
    jsonStart = response.find('{')
    jsonEnd = response.rfind('}')
    response = response[jsonStart:jsonEnd+1]
    # print(response)
    return jsonify(json.loads(response))

def detect_text(content):
    """Detects text in the image content."""
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    alltext = [text.description for text in texts]
    return alltext

@app.route('/detect-text', methods=['POST'])
def process_image():
    print(request.files)
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 500

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 500

    if file:
        content = file.read()
        text = detect_text(content)
        return jsonify({'text': text})

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
