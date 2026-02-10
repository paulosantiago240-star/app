import os
import requests
import pandas as pd
import google.generativeai as genai
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Configuração da API (Gemini 3 Flash)
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key, transport='rest')
model = genai.GenerativeModel('models/gemini-3-flash-preview')

@app.route("/bot", methods=['POST'])
def bot():
    user_msg = request.values.get('Body', '')
    num_media = int(request.values.get('NumMedia', 0))
    
    # Lista para armazenar o que enviaremos para a IA
    content_to_send = [user_msg]

    try:
        # Se houver arquivo (Excel ou Imagem)
        if num_media > 0:
            media_url = request.values.get('MediaUrl0')
            content_type = request.values.get('MediaContentType0')
            
            # Se for Excel, usamos Pandas para ler e transformar em texto
            if 'spreadsheetml' in content_type or 'excel' in content_type:
                df = pd.read_excel(media_url)
                # Convertemos os primeiros dados para texto para a IA analisar
                excel_text = f"\nConteúdo do arquivo Excel:\n{df.head(20).to_string()}"
                content_to_send.append(excel_text)
            
            # Se for Imagem, o Gemini 3 já consegue ler pela URL (via Twilio)
            elif 'image' in content_type:
                image_data = requests.get(media_url).content
                content_to_send.append({'mime_type': content_type, 'data': image_data})

        # Geração da resposta
        response = model.generate_content(content_to_send)
        bot_response = response.text

    except Exception as e:
        print(f"Erro detalhado: {e}")
        bot_response = "Tive um problema ao processar seu arquivo. Verifique se ele não está protegido por senha."

    twilio_resp = MessagingResponse()
    twilio_resp.message(bot_response)
    return str(twilio_resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
