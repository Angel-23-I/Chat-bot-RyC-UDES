from flask import Flask, request
import sett
import services
import json
import os

app = Flask(__name__)

@app.route('/bienvenido', methods=['GET'])
def bienvenido():
    return 'Hola mundo, desde flask'

@app.route('/webhook', methods=['GET'])
def verificar_token():
    try:
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if token == sett.token and challenge != None:
            return challenge
        else:
            return 'token incorrecto', 403
    except Exception as e:
        return str(e), 403

@app.route('/webhook', methods=['POST'])
def recibir_mensajes():
    try:
        body = request.get_json()
        
        # Log para debugging
        app.logger.info(f"Webhook recibido: {json.dumps(body)}")
        
        # Validar estructura básica
        entry = body.get('entry', [])
        if not entry:
            app.logger.info("Webhook sin entry")
            return 'ok', 200
            
        changes = entry[0].get('changes', [])
        if not changes:
            app.logger.info("Webhook sin changes")
            return 'ok', 200
            
        value = changes[0].get('value', {})
        
        # IMPORTANTE: Verificar si es notificación de estado vs mensaje
        if 'statuses' in value:
            # Es una notificación de estado (delivered, read, sent)
            app.logger.info("Notificación de estado recibida - ignorando")
            return 'ok', 200
        
        # Verificar que contiene mensajes
        if 'messages' not in value:
            app.logger.info("Webhook sin mensajes")
            return 'ok', 200
        
        # Procesar el mensaje
        message = value['messages'][0]
        number = message['from']
        messageId = message['id']
        contacts = value['contacts'][0]
        name = contacts['profile']['name']
        
        text = services.obtener_Mensaje_whatsapp(message)
        
        # Solo procesar si se obtuvo texto válido
        if text and text not in ['mensaje no reconocido', 'mensaje no procesado']:
            services.administrar_chatbot(text, number, messageId, name)
        else:
            app.logger.warning(f"Tipo de mensaje no soportado: {message.get('type', 'unknown')}")
            # Enviar mensaje al usuario indicando tipo no soportado
            data = services.text_Message(number, "Lo siento, ese tipo de mensaje no está soportado. Por favor envía texto.")
            services.enviar_Mensaje_whatsapp(data)

        return 'enviado', 200
    
    except KeyError as e:
        app.logger.error(f"KeyError en webhook: {str(e)}")
        app.logger.error(f"Body: {json.dumps(body) if 'body' in locals() else 'N/A'}")
        return 'ok', 200  # Devolver 200 para evitar reintentos
    
    except Exception as e:
        app.logger.error(f"Error en webhook: {str(e)}")
        return 'ok', 200  # Devolver 200 para evitar reintentos

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
