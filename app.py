import os
import google.generativeai as genai
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Configuração da API Key vinda do Render
# Certifique-se de que o nome na aba Environment do Render seja GEMINI_API_KEY
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("ERRO: A variável GEMINI_API_KEY não foi encontrada no ambiente!")
else:
    genai.configure(api_key=api_key)

# Inicializa o modelo
model = genai.GenerativeModel('gemini-1.5-flash-latest')

@app.route("/bot", methods=['POST'])
def bot():
    user_msg = request.values.get('Body', '').lower()
    
    try:
        # Gera a resposta usando o Gemini
        response = model.generate_content(user_msg)
        bot_response = response.text
    except Exception as e:
        # Se der erro na API, ele imprime o erro nos logs do Render
        print(f"Erro na API Gemini: {e}")
        bot_response = "Ops, tive um problema técnico para processar isso agora."

    # Prepara a resposta para o WhatsApp via Twilio
    twilio_resp = MessagingResponse()
    twilio_resp.message(bot_response)
    
    return str(twilio_resp)

if __name__ == "__main__":
    # O Render define a porta automaticamente, o Flask a lerá
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


