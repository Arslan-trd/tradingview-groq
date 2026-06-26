from flask import Flask, request, jsonify
from groq import Groq
import os
import json

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            raw = request.data.decode("utf-8")
            try:
                data = json.loads(raw)
            except:
                data = {"message": raw}

        alert_text = json.dumps(data, indent=2) if isinstance(data, dict) else str(data)

        prompt = f"""You are an expert forex and trading analyst helping a beginner trader.

A TradingView alert just fired with this data:
{alert_text}

Please provide:
1. Is this a good trade? YES / NO / WAIT
2. Entry suggestion
3. Stop Loss
4. Take Profit
5. Risk warning

Keep it simple and beginner-friendly."""

        response = client.chat.completions.create(
            model="llama3-70b-8192",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        analysis = response.choices[0].message.content
        return jsonify({"status": "ok", "analysis": analysis}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "running", "message": "TradingView → Groq AI webhook is live ✅"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
