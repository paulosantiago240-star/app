import os
import requests
import pandas as pd
import google.generativeai as genai
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Configuração com o modelo Gemini 3 detectado nos seus logs
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key, transport='rest')
model = genai.GenerativeModel('models/gemini-3-flash-preview')

@app.route("/bot", methods=['POST'])
def bot():
    user_msg = request.values.get('Body', '')
    num_media = int(request.values.get('NumMedia', 0))
    
    # Preparamos o conteúdo para a IA (Texto + Arquivos)
    content_to_send = [user_msg if user_msg else "Analise este arquivo:"]

    try:
        if num_media > 0:
            media_url = request.values.get('MediaUrl0')
            content_type = request.values.get('MediaContentType0')
            
            # Lógica para Planilhas Excel
            if 'spreadsheetml' in content_type or 'excel' in content_type:
                # O pandas lê o arquivo diretamente da URL segura da Twilio
                df = pd.read_excel(media_url)
                resumo_excel = f"\n[DADOS DA PLANILHA EXCEL DETECTADOS]\n{df.to_string(index=False)}"
                content_to_send.append(resumo_excel)
            
            # Lógica para Imagens (Gráficos, Circuitos, Exercícios)
            elif 'image' in content_type:
                image_data = requests.get(media_url).content
                content_to_send.append({'mime_type': content_type, 'data': image_data})

        # O Gemini 3 processa tudo e gera a resposta técnica
        response = model.generate_content(content_to_send)
        bot_response = response.text

    except Exception as e:
        print(f"Erro no processamento: {e}")
        bot_response = "Consegui receber seu arquivo, mas tive um erro ao lê-lo. Verifique se ele não tem senha."

    twilio_resp = MessagingResponse()
    twilio_resp.message(bot_response)
    return str(twilio_resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
