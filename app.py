import os
import requests
import pandas as pd
import google.generativeai as genai
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Configuração com o modelo Gemini 3 (o que sua chave exige)
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
            
            # Processamento de Planilhas (Excel)
            if 'spreadsheetml' in content_type or 'excel' in content_type:
                # Baixa e lê o Excel diretamente da Twilio
                df = pd.read_excel(media_url)
                # Convertemos os primeiros dados para texto para a IA analisar
                excel_text = f"\n[DADOS DA PLANILHA EXCEL]\n{df.head(50).to_string(index=False)}"
                content_to_send.append(excel_text)
            
            # Processamento de Imagens (Exercícios, Gráficos de Stress-Strain)
            elif 'image' in content_type:
                image_data = requests.get(media_url).content
                content_to_send.append({'mime_type': content_type, 'data': image_data})

        # O Gemini 3 gera a resposta técnica completa
        response = model.generate_content(content_to_send)
        bot_response = response.text

    except Exception as e:
        print(f"Erro detalhado no processamento: {e}")
        bot_response = "Tive um erro ao ler o arquivo. Verifique se o formato está correto e se o servidor está ativo."

    twilio_resp = MessagingResponse()
    twilio_resp.message(bot_response)
    return str(twilio_resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
