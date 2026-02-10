import os
import google.generativeai as genai
from flask import Flask, request
import requests
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Configuração simplificada e estável
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key, transport='rest')

# Modelo Gemini 3 detectado nos seus logs anteriores
model = genai.GenerativeModel('models/gemini-3-flash-preview')

@app.route("/bot", methods=['POST'])
def bot():
    user_msg = request.values.get('Body', '')
    num_media = int(request.values.get('NumMedia', 0))
    
    content = [user_msg] if user_msg else ["Analise esta imagem:"]

    try:
        # Se você enviar uma foto, ele usa a visão computacional
        if num_media > 0:
            media_url = request.values.get('MediaUrl0')
            mime_type = request.values.get('MediaContentType0')
            if 'image' in mime_type:
                image_data = requests.get(media_url).content
                content.append({'mime_type': mime_type, 'data': image_data})

        response = model.generate_content(content)
        bot_response = response.text
    except Exception as e:
        print(f"Erro: {e}")
        bot_response = "Ops, tive um problema. Vamos tentar novamente com uma mensagem mais curta?"

    twilio_resp = MessagingResponse()
    twilio_resp.message(bot_response)
    return str(twilio_resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
