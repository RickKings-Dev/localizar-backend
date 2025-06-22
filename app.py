from flask import Flask, request, jsonify
import base64
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_OWNER = os.getenv('REPO_OWNER')
REPO_NAME = os.getenv('REPO_NAME')
UPLOAD_PATH = os.getenv('UPLOAD_PATH', '')

app = Flask(__name__)

@app.route("/upload", methods=["POST"])
def upload_image():
    data = request.json
    image_data = data.get("image")

    if not image_data:
        return jsonify({"error": "Imagem não fornecida"}), 400

    try:
        # Remove o prefixo data URL (ex: "data:image/png;base64,")
        header, encoded = image_data.split(",", 1)
        binary_data = base64.b64decode(encoded)

        # Nome do arquivo com timestamp UTC
        filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.png"
        path = f"{UPLOAD_PATH}/{filename}" if UPLOAD_PATH else filename

        url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{path}"

        payload = {
            "message": f"Upload automático {filename}",
            "content": base64.b64encode(binary_data).decode("utf-8")
        }

        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json"
        }

        response = requests.put(url, json=payload, headers=headers)

        if response.status_code in [200, 201]:
            return jsonify({"status": "ok", "path": path})
        else:
            return jsonify({"error": response.json()}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
