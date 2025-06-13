# app.py

from flask import Flask, request, jsonify, render_template
from retrieval import retrieve_chunks
from utils import build_prompt, ask_chatgpt
from dotenv import load_dotenv
import os
import logging

# Load API key từ .env
load_dotenv()

# Thiết lập Flask
app = Flask(__name__, static_folder="static", template_folder="templates")
logging.basicConfig(level=logging.INFO)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json(force=True)

        question = data.get("question", "").strip()
        if not question:
            return jsonify({"error": "❌ Thiếu câu hỏi"}), 400

        # Các tham số truy vấn
        top_k = int(data.get("top_k", 10))
        temperature = float(data.get("temperature", 0.35))
        max_tokens = int(data.get("max_tokens", 1200))
        top_p = float(data.get("top_p", 0.98))

        app.logger.info(f"🔍 Người dùng hỏi: {question}")

        # RAG pipeline
        chunks = retrieve_chunks(question, top_k=top_k)
        prompt = build_prompt(question, chunks)
        answer = ask_chatgpt(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p
        )

        return jsonify({
            "answer": answer,
            "retrieved_context": chunks
        })

    except Exception as e:
        app.logger.error(f"❌ Lỗi xử lý câu hỏi: {e}")
        return jsonify({"error": str(e)}), 500

# Quan trọng: đảm bảo Flask nhận PORT do Render cung cấp
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
