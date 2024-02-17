# from flask import Flask, request, jsonify
# from google.cloud import vision
# import os

# app = Flask(__name__)

# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Users\\Public\\Documents\\Avinash\\Projects\\Points\\Point4\\knowfood-service-account-credentials.json"
# os.environ["GOOGLE_API_KEY"] = ""


# import google.generativeai as genai
# genai.configure()
# # model = genai.GenerativeModel('gemini-pro')
# # response = model.generate_content("""
# # """)


# query = """This is supposed to contain ingredients. Extract each individual ingredient separately and return as a JSON under key "ingredients". If any ingredients are mentioned in brackets, mention them as actual ingredients. If it says may contain, add those under a different key "mayContain", not under other ingredients.
# # 165\na\ningredients: corn flour (processed with lime).\nvegetable oil (palm and/or soybean and/or\ncanola oil), seasoning [salt, maltodextrin,\ncitric acid, sugar, monosodium glutamate\nhydrolyzed soy protein, onion powder, yeast\nextract, red 40 lake, yellow 6 lake, natural and\nartificial flavors, sodium bicarbonate, soybean\noil, chili pepper (chile), disodium inosinate,\ndisodium guanylate, tbhq (antioxidant)]\ncontains soy. made in a facility that may also\nuse milk, egg, wheat and peanuts.\ndistributed by:\nbarcel usa llc.\n301 south northpoint,\nsuite 100, coppell tx,\n75019, usa.\nmade in mexico\nwww.takis.us\ntm\nbarcel®\na company of\ngrupo\nbimbo\nsmartlabel\nscan for info or call\n1-800-432-8266\nc
# """


# model = genai.GenerativeModel('gemini-pro')
# response = model.generate_content(
#     query,
#     generation_config=genai.types.GenerationConfig(
#         candidate_count=1,
#         temperature=0.5,)
# )



# print(response.text)

# def detect_text(content):
#     """Detects text in the image content."""
#     client = vision.ImageAnnotatorClient()
#     image = vision.Image(content=content)
#     response = client.text_detection(image=image)
#     texts = response.text_annotations
#     alltext = [text.description for text in texts]
#     return alltext

# @app.route('/detect-text', methods=['POST'])
# def process_image():
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part'})

#     file = request.files['file']

#     if file.filename == '':
#         return jsonify({'error': 'No selected file'})

#     if file:
#         content = file.read()
#         text = detect_text(content)
#         return jsonify({'text': text})
    



# # if __name__ == '__main__':
# #     app.run(debug=True)





from flask import Flask, request, jsonify
from google.cloud import vision
import os
import google.generativeai as genai
#from ast import literal_eval
import json
import re

app = Flask(__name__)

# Set Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Users\\Public\\Documents\\Avinash\\Projects\\Points\\Point4\\knowfood-service-account-credentials.json"
os.environ["GOOGLE_API_KEY"] = ""

# Configure generative AI
genai.configure()

@app.route('/get-ingredients', methods=['POST'])
def get_ingredients():
    data = request.get_data().decode('utf-8').replace('\\n', '\n')
    ingredientsRawText = data#data.get('ingredientsRawText', '').decode('utf-8')
    #print(type(ingredientsRawText))
    #print(ingredientsRawText)
    #return jsonify({'response': 'success'})
    #ingredientsRawText = "165\nA\nINGREDIENTS: CORN FLOUR (PROCESSED WITH LIME).\nVEGETABLE OIL (PALM AND/OR SOYBEAN AND/OR\nCANOLA OIL), SEASONING [SALT, MALTODEXTRIN,\nCITRIC ACID, SUGAR, MONOSODIUM GLUTAMATE\nHYDROLYZED SOY PROTEIN, ONION POWDER, YEAST\nEXTRACT, RED 40 LAKE, YELLOW 6 LAKE, NATURAL AND\nARTIFICIAL FLAVORS, SODIUM BICARBONATE, SOYBEAN\nOIL, CHILI PEPPER (CHILE), DISODIUM INOSINATE,\nDISODIUM GUANYLATE, TBHQ (ANTIOXIDANT)]\nCONTAINS SOY. MADE IN A FACILITY THAT MAY ALSO\nUSE MILK, EGG, WHEAT AND PEANUTS.\nDISTRIBUTED BY:\nBARCEL USA LLC.\n301 SOUTH NORTHPOINT,\nSUITE 100, COPPELL TX,\n75019, USA.\nMADE IN MEXICO\nwww.takis.us\nTM\nBARCEL®\nA COMPANY OF\nGRUPO\nBIMBO\nsmartlabel\nScan for info or call\n1-800-432-8266\nC"
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
    return jsonify({'response': json.loads(response)})

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
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file:
        content = file.read()
        text = detect_text(content)
        return jsonify({'text': text})

if __name__ == '__main__':
    app.run(debug=True)
