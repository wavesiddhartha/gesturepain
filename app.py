import os
import json
import base64
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load local environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes (to support front-end to backend calls)

NVIDIA_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY")

def clean_json_response(text):
    """Clean markdown code blocks and whitespace from response to ensure valid JSON."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

@app.route('/api/generate', methods=['POST'])
def generate_drawing():
    try:
        if not NVIDIA_API_KEY:
            return jsonify({"error": "NVIDIA API Key not configured. Please set NVIDIA_API_KEY in your .env file."}), 500
            
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"error": "Missing image parameter"}), 400

        image_b64 = data['image']
        # Strip header if it exists (e.g. data:image/png;base64,)
        if "," in image_b64:
            image_b64 = image_b64.split(",")[1]

        # Prepare request to Kimi K2.6
        headers = {
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json"
        }

        prompt = (
            "Analyze the scribble drawing provided in the image. Identify the subject (e.g., cat, face, house, tree, flower, animal, complex object) "
            "and create an advanced, high-fidelity, clean vector line art/sketch version of it. "
            "Do not oversimplify: capture key features, details, and shapes using curved lines (like C and S commands in SVG path syntax) to create a beautiful, "
            "artistically complete representation consisting of multiple detailed lines/paths (e.g., 20 to 50 paths if complex).\n"
            "Your output must be a single, valid JSON object with exactly two keys:\n"
            "1. \"label\": A short string identifying the subject (e.g., \"A detailed cat portrait\", \"A beautiful mountain landscape\").\n"
            "2. \"paths\": A JSON array of detailed SVG path 'd' strings. The paths must represent the complete, detailed line-art drawing. "
            "Scale and position the paths to center and fit beautifully inside a 1280x720 canvas resolution.\n\n"
            "Ensure the output contains ONLY the raw JSON object. Do not include any explanations, introductory text, "
            "or markdown backticks. Just output the JSON."
        )

        payload = {
            "model": "moonshotai/kimi-k2.6",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_b64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            "max_tokens": 2048,
            "temperature": 0.10,  # Lower temperature for faster generation
            "top_p": 0.70,
            "chat_template_kwargs": {"thinking": False}  # Disable thinking mode to get instant results
        }

        print("Sending request to Kimi AI via NVIDIA API...")
        response = requests.post(NVIDIA_API_URL, headers=headers, json=payload)
        
        if response.status_code != 200:
            print(f"NVIDIA API Error: Status {response.status_code}, Response: {response.text}")
            return jsonify({"error": f"NVIDIA API returned error status {response.status_code}"}), 502

        res_json = response.json()
        raw_text = res_json['choices'][0]['message']['content']
        print(f"Received raw text from Kimi AI: {raw_text[:500]}...")

        # Parse the output
        cleaned_text = clean_json_response(raw_text)
        try:
            parsed_data = json.loads(cleaned_text)
            return jsonify(parsed_data)
        except json.JSONDecodeError as je:
            print(f"JSON Decode Error parsing Kimi output: {cleaned_text}")
            # Attempt to extract json object if it wrapped it in text
            start = cleaned_text.find('{')
            end = cleaned_text.rfind('}')
            if start != -1 and end != -1:
                try:
                    parsed_data = json.loads(cleaned_text[start:end+1])
                    return jsonify(parsed_data)
                except Exception:
                    pass
            return jsonify({"error": "Failed to parse Kimi AI drawing instructions", "raw_output": raw_text}), 500

    except Exception as e:
        print(f"Error handling request: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate_text', methods=['POST'])
def generate_drawing_from_text():
    try:
        if not NVIDIA_API_KEY:
            return jsonify({"error": "NVIDIA API Key not configured. Please set NVIDIA_API_KEY in your .env file."}), 500
            
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "Missing prompt parameter"}), 400

        text_prompt = data['prompt']

        headers = {
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json"
        }

        system_instruction = (
            f"Generate a beautiful, clean, highly detailed minimalist line art/vector illustration of: '{text_prompt}'. "
            "If the prompt is a math question, expression, or equation (like '2+2=' or '3+5'), solve it first, and draw both the equation and the answer beautifully "
            "(e.g., for '2+2=', draw the characters '2 + 2 = 4' in a stylized, neat vector line font style).\n"
            "Your output must be a single, valid JSON object with exactly two keys:\n"
            "1. \"label\": A short string identifying the subject (e.g., \"A detailed butterfly\", \"The equation 2 + 2 = 4\").\n"
            "2. \"paths\": A JSON array of detailed SVG path 'd' strings. The paths must represent the complete, detailed line-art drawing. "
            "Scale and position the paths to center and fit beautifully inside a 1280x720 canvas resolution.\n\n"
            "Ensure the output contains ONLY the raw JSON object. Do not include any explanations, introductory text, "
            "or markdown backticks. Just output the JSON."
        )

        payload = {
            "model": "moonshotai/kimi-k2.6",
            "messages": [
                {
                    "role": "user",
                    "content": system_instruction
                }
            ],
            "max_tokens": 2048,
            "temperature": 0.20,
            "top_p": 0.70,
            "chat_template_kwargs": {"thinking": False}
        }

        print(f"Sending text prompt to Kimi AI: {text_prompt}...")
        response = requests.post(NVIDIA_API_URL, headers=headers, json=payload)
        
        if response.status_code != 200:
            print(f"NVIDIA API Error: Status {response.status_code}, Response: {response.text}")
            return jsonify({"error": f"NVIDIA API returned error status {response.status_code}"}), 502

        res_json = response.json()
        raw_text = res_json['choices'][0]['message']['content']
        print(f"Received raw text from Kimi AI: {raw_text[:500]}...")

        # Parse the output
        cleaned_text = clean_json_response(raw_text)
        try:
            parsed_data = json.loads(cleaned_text)
            return jsonify(parsed_data)
        except json.JSONDecodeError as je:
            print(f"JSON Decode Error parsing Kimi output: {cleaned_text}")
            start = cleaned_text.find('{')
            end = cleaned_text.rfind('}')
            if start != -1 and end != -1:
                try:
                    parsed_data = json.loads(cleaned_text[start:end+1])
                    return jsonify(parsed_data)
                except Exception:
                    pass
            return jsonify({"error": "Failed to parse Kimi AI drawing instructions", "raw_output": raw_text}), 500

    except Exception as e:
        print(f"Error handling request: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run server locally on port 5001
    app.run(host='0.0.0.0', port=5001, debug=True)
