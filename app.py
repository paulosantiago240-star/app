import os
import google.generativeai as genai
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Configuração da API Key com tratamento de erro e transporte REST para estabilidade
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("ERRO CRÍTICO: Variável GEMINI_API_KEY não encontrada no Render!")
else:
    # O transport='rest' evita problemas de conexão em servidores como o Render
    genai.configure(api_key=api_key, transport='rest')

# Inicializa o modelo com o caminho completo do recurso
model = genai.GenerativeModel('models/gemini-1.5-flash')

@app.route("/bot", methods=['POST'])
def bot():
    user_msg = request.values.get('Body', '')
    print(f"Mensagem recebida: {user_msg}") # Log para acompanhamento
    
    try:
        # Tenta gerar a resposta
        response = model.generate_content(user_msg)
        bot_response = response.text
    except Exception as e:
        # Se falhar, imprime o erro exato no log do Render
        print(f"Erro detalhado na API: {e}")
        bot_response = "Ops, tive um problema técnico para processar isso agora. Verifique os logs."

    # Prepara a resposta para o WhatsApp
    twilio_resp = MessagingResponse()
    twilio_resp.message(bot_response)
    
    return str(twilio_resp)

if __name__ == "__main__":
    # Porta dinâmica para o Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
