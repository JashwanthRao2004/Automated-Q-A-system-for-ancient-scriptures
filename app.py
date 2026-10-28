from flask import Flask, request, jsonify, render_template_string
from gita_bot_core import gita_bot_response

app = Flask(__name__)

# --- Ultra-Dynamic Spiritual UI ---
HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitaBot | Divine Consciousness</title>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600&family=Outfit:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --saffron: #FF9933;
            --deep-gold: #D4AF37;
            --glass-white: rgba(255, 255, 255, 0.75);
            --user-bg: rgba(255, 153, 51, 0.2);
        }

        * { box-sizing: border-box; }

        body {
            font-family: 'Outfit', sans-serif;
            margin: 0;
            height: 100vh;
            overflow: hidden;
            display: flex;
            justify-content: center;
            align-items: center;
            /* Dynamic Aurora Background */
            background: linear-gradient(135deg, #FFF5E6 0%, #FFEDD5 25%, #FFFBF5 50%, #FFFAF0 100%);
            background-size: 400% 400%;
            animation: auroraFlow 15s ease infinite;
        }

        @keyframes auroraFlow {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        /* Animated Floating Circles in Background */
        .circle {
            position: absolute;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(255,153,51,0.1) 0%, rgba(255,255,255,0) 70%);
            z-index: -1;
            filter: blur(40px);
            animation: float 20s infinite alternate;
        }

        @keyframes float {
            from { transform: translate(0, 0); }
            to { transform: translate(100px, 150px); }
        }

        #app-window {
            width: 95%;
            max-width: 550px;
            height: 85vh;
            background: var(--glass-white);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.5);
            border-radius: 32px;
            display: flex;
            flex-direction: column;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.1);
            position: relative;
            z-index: 1;
        }

        #header {
            padding: 30px 20px 20px;
            text-align: center;
        }

        #header h1 {
            font-family: 'Cinzel', serif;
            margin: 0;
            font-size: 1.8rem;
            color: #5D4037;
            letter-spacing: 3px;
        }

        #header p { font-size: 0.8rem; color: #8D6E63; margin-top: 5px; letter-spacing: 1px; }

        #chat-flow {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 15px;
            scrollbar-width: none;
        }
        #chat-flow::-webkit-scrollbar { display: none; }

        .msg {
            max-width: 85%;
            padding: 14px 20px;
            border-radius: 22px;
            line-height: 1.6;
            font-size: 1rem;
            animation: fadeInUp 0.4s ease forwards;
        }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .bot {
            align-self: flex-start;
            background: white;
            color: #333;
            border-bottom-left-radius: 4px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        }

        .user {
            align-self: flex-end;
            background: var(--user-bg);
            color: #5D4037;
            font-weight: 500;
            border-bottom-right-radius: 4px;
            border: 1px solid rgba(255,153,51,0.2);
        }

        #chips-container {
            display: flex;
            gap: 10px;
            padding: 10px 20px;
            overflow-x: auto;
            scrollbar-width: none;
        }
        #chips-container::-webkit-scrollbar { display: none; }

        .chip {
            background: white;
            border: 1px solid #FFE0B2;
            padding: 8px 18px;
            border-radius: 25px;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            white-space: nowrap;
            color: #8D6E63;
        }
        .chip:hover {
            background: var(--saffron);
            color: white;
            transform: translateY(-3px);
            box-shadow: 0 8px 15px rgba(255, 153, 51, 0.2);
        }

        #input-area {
            padding: 25px;
            display: flex;
            gap: 12px;
            align-items: center;
        }

        input {
            flex: 1;
            background: white;
            border: 1px solid #EEE;
            padding: 14px 20px;
            border-radius: 20px;
            outline: none;
            font-size: 1rem;
            transition: 0.3s;
            box-shadow: 0 2px 10px rgba(0,0,0,0.02);
        }
        input:focus { border-color: var(--saffron); box-shadow: 0 0 0 4px rgba(255, 153, 51, 0.1); }

        #send-btn {
            background: #5D4037;
            color: white;
            border: none;
            width: 50px;
            height: 50px;
            border-radius: 18px;
            cursor: pointer;
            display: flex;
            justify-content: center;
            align-items: center;
            transition: 0.3s;
        }
        #send-btn:hover { background: var(--saffron); transform: scale(1.05); }

        .typing-indicator {
            font-size: 0.8rem;
            color: var(--saffron);
            padding: 0 25px 10px;
            display: none;
            font-style: italic;
        }
    </style>
</head>
<body>

<div class="circle" style="width: 400px; height: 400px; top: -100px; left: -100px;"></div>
<div class="circle" style="width: 300px; height: 300px; bottom: -50px; right: -50px; animation-duration: 25s;"></div>

<div id="app-window">
    <div id="header">
        <h1>🕉️ GitaBot</h1>
        <p>CONVERSATIONS WITH THE DIVINE</p>
    </div>
    
    <div id="chat-flow">
        <div class="msg bot">Pranam. I am GitaBot. May the light of wisdom guide our conversation. What is on your soul today?</div>
    </div>

    <div id="chips-container">
        <div class="chip" onclick="quick('Teach me about the Soul')">The Eternal Soul</div>
        <div class="chip" onclick="quick('How to deal with stress?')">Finding Peace</div>
        <div class="chip" onclick="quick('What is the meaning of life?')">Life's Purpose</div>
    </div>

    <div class="typing-indicator" id="loading">GitaBot is reflecting on the scriptures...</div>

    <div id="input-area">
        <input type="text" id="user-input" placeholder="Type your inquiry..." autocomplete="off">
        <button id="send-btn" onclick="ask()">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
        </button>
    </div>
</div>

<script>
    const chatFlow = document.getElementById('chat-flow');
    const userInput = document.getElementById('user-input');
    const loading = document.getElementById('loading');

    userInput.addEventListener("keypress", (e) => { if(e.key === "Enter") ask(); });

    function quick(text) {
        userInput.value = text;
        ask();
    }

    async function ask() {
        const query = userInput.value.trim();
        if (!query) return;

        addMsg(query, 'user');
        userInput.value = '';
        loading.style.display = 'block';
        chatFlow.scrollTop = chatFlow.scrollHeight;

        try {
            const response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: query })
            });

            const data = await response.json();
            loading.style.display = 'none';
            addMsg(data.response, 'bot');
        } catch (err) {
            loading.style.display = 'none';
            addMsg("The connection to the divine knowledge is temporarily interrupted.", 'bot');
        }
    }

    function addMsg(text, type) {
        const div = document.createElement('div');
        div.className = `msg ${type}`;
        div.innerText = text;
        chatFlow.appendChild(div);
        chatFlow.scrollTop = chatFlow.scrollHeight;
    }
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_UI)

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(force=True)
        user_query = data.get("query", "").strip()

        print("📩 User query:", user_query)

        reply = gita_bot_response(user_query)

        print("🤖 Bot reply:", reply)

        return jsonify({"response": reply})

    except Exception as e:
        import traceback
        print("❌ CHAT ERROR:")
        traceback.print_exc()

        return jsonify({
            "response": "Backend error. Check terminal."
        }), 500


from pyngrok import ngrok
import os
# ---- ngrok authentication ----
ngrok.set_auth_token("39W68aWT2X2exNxILwza1bpJPaE_84SY6zeYxaoM8TaNgHNac")


if __name__ == "__main__":
    public_url = ngrok.connect(5000)
    print("🌐 Public UI URL:", public_url)
    app.run(host="0.0.0.0", port=5000, debug=False)
