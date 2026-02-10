import os
import google.generativeai as genai
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Configuração da API Key com transporte REST para estabilidade no Render
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("ERRO: GEMINI_API_KEY não configurada no Environment do Render!")
else:
    # O transport='rest' é essencial para evitar quedas de conexão
    genai.configure(api_key=api_key, transport='rest')

# Inicializa o modelo Gemini 3 (o que sua chave exige)
model = genai.GenerativeModel('models/gemini-3-flash-preview')

# Configurações para garantir que a resposta não demore muito e cause timeout
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "max_output_tokens": 600, # Suficiente para explicações de engenharia
}

@app.route("/bot", methods=['POST'])
def bot():
    user_msg = request.values.get('Body', '')
    print(f"Mensagem recebida: {user_msg}") # Monitoramento nos Logs
    
    try:
        # Gera a resposta técnica
        response = model.generate_content(
            user_msg, 
            generation_config=generation_config
        )
        bot_response = response.text
    except Exception as e:
        # Imprime o erro exato no log do Render se algo falhar
        print(f"Erro detalhado na API: {e}")
        bot_response = "Ops, tive um problema técnico para processar isso agora. Verifique os logs."

    # Prepara a resposta XML para o WhatsApp (Twilio)
    twilio_resp = MessagingResponse()
    twilio_resp.message(bot_response)
    
    return str(twilio_resp)

if __name__ == "__main__":
    # Garante que o Flask use a porta correta do Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
