import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import google.generativeai as genai

app = Flask(__name__)

# Configuração do Gemini
genai.configure(api_key="GEMINI_API_KEY")
model = genai.GenerativeModel('gemini-1.5-flash')


@app.route("/bot", methods=['POST'])
def bot():
    # 1. Recebe a mensagem do WhatsApp
    user_msg = request.values.get('Body', '')

    # 2. Envia para o Gemini
    response = model.generate_content(user_msg)
    bot_response = response.text

    # 3. Prepara a resposta do Twilio
    twilio_resp = MessagingResponse()
    twilio_resp.message(bot_response)

    return str(twilio_resp)


if __name__ == "__main__":

    app.run(port=5000)
