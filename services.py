from ai_service import get_ai_response, set_user_state, get_user_state, clear_user_state, NO_INFO_MARKER
import requests
import sett
import json
import time

def obtener_Mensaje_whatsapp(message):
    if 'type' not in message:
        return None  # En lugar de 'mensaje no reconocido'
    
    typeMessage = message['type']
    
    if typeMessage == 'text':
        return message['text']['body']
    
    elif typeMessage == 'button':
        return message['button']['text']
    
    elif typeMessage == 'interactive' and message['interactive']['type'] == 'list_reply':
        return message['interactive']['list_reply']['title']
    
    elif typeMessage == 'interactive' and message['interactive']['type'] == 'button_reply':
        return message['interactive']['button_reply']['title']
    
    # Tipos no soportados
    elif typeMessage in ['image', 'video', 'audio', 'document', 'sticker', 'location', 'contacts']:
        return None
    
    else:
        return None



def enviar_Mensaje_whatsapp(data):
    try:
        whatsapp_token = sett.whatsapp_token
        whatsapp_url  = sett.whatsapp_url
        headers = {'Content-Type': 'application/json','Authorization' : 'Bearer ' + whatsapp_token}
        print("se envia", data)
        response = requests.post(whatsapp_url, headers=headers, data=data)

        if response.status_code == 200:
            return 'mensaje enviado', 200
        else:
            return 'error al enviar mensaje', response.status_code
    except Exception as e:
        return e,403

def text_Message(number, text):
    data = json.dumps(
            {
                "messaging_product": "whatsapp",   
                "recipient_type": "individual",
                "to": number,
                "type": "text",
                "text": {
                    "body": text
                }
            }
    )
    return data

def buttonReply_Message(number, options, body, footer, sedd, messageId):
    buttons = []
    for i, option in enumerate(options):
        buttons.append({
            "type": "reply",
            "reply": {
                "id": sedd + "_btn_" + str(i+1),
                "title": option
            }
        })

    data = json.dumps(
                {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": body
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "buttons": buttons
                }
            }
        }
    )
    return data

def listReply_Message (number, options, body, footer, sedd, messageId):
    rows = []
    for i, option in enumerate(options):
        rows.append(
            {
                "id": sedd + "_row_" + str(i+1),
                "title": option,
                "description": ""
            }
        )

    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {
                    "text": body
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "button": "Ver Opciones",
                    "sections": [
                        {
                            "title": "Secciones",
                            "rows": rows
                        }
                    ]
                }
            }
        }
    )
    return data

def document_Message(number, url, caption, filename):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                "link": url,
                "caption": caption,
                "filename": filename
            }
        }
    )
    return data

def get_media_id(media_name , media_type):
    media_id = ""
    if media_type == "sticker":
        media_id = sett.stickers.get(media_name, None)
    #elif media_type == "image":
    #    media_id = sett.images.get(media_name, None)
    #elif media_type == "video":
    #    media_id = sett.videos.get(media_name, None)
    #elif media_type == "audio":
    #    media_id = sett.audio.get(media_name, None)
    return media_id

def replyReaction_Message(number, messageId, emoji):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "reaction",
            "reaction": {
                "message_id": messageId,
                "emoji": emoji
            }
        }
    )
    return data

def replyText_Message(number, messageId, text):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "context": {
                "message_id": messageId
            },
            "type": "text",
            "text": {
                "body": text
            }
        }
    )
    return data

def markRead_Message(messageId):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": messageId
        }
    )
    return data

def media_Message_URL(number, image_url, caption=""):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "image",
            "image": {
                "link": image_url,
                "caption": caption
            }
        }
    )
    return data



def administrar_chatbot(text,number, messageId, name):
    text = text.lower() #mensaje que enviio el usuario
    list = []
    print("mensaje del usuario: ",text)

    markRead = markRead_Message(messageId)
    list.append(markRead)
    time.sleep(2)

    # Verificar si el usuario está en modo pregunta personalizada
    user_state = get_user_state(number)

    if "hola" in text or "buenos dias" in text or "buenas tardes" in text or "buenas noches" in text or "hi" in text or "." in text:
        #data = text_Message(number,"¡Bienvenido al Chat bot de registro y control de la Universidad de Santander! 👋")
        #enviar_Mensaje_whatsapp(data)
        body ="¡Hola! ¡Bienvenido al Chat bot de registro y control de la Universidad de Santander! 👋 ¿En qué puedo ayudarte hoy?"
        footer = "Universidad de Santander - UDES"
        options = ["Fechas importantes","Procedimientos","Preguntas Frecuentes","Horarios de atención", "Pregunta personalizada"]

        listReply = listReply_Message(number, options, body, footer, "sed1", messageId)
        list.append(listReply)

    elif "fechas importantes" in text:
        data = text_Message(number, "Aquí tienes las fechas importantes:\n\n- Inicio de clases: 1 de agosto\n- Fin de semestre: 15 de diciembre\n- Vacaciones: 20 de diciembre - 10 de enero")
        enviar_Mensaje_whatsapp(data)

        document = document_Message(number, sett.document_url, "Tambien te comparto el calendario academico:", "Calendario_2025.pdf")
        enviar_Mensaje_whatsapp(document)
        time.sleep(3)
        body = "¿Necesitas ayuda con algo más?"
        footer = "Universidad de Santander - UDES"
        options = ["✅ Si, por favor", "❌ No, gracias"]
        replyButtonData = buttonReply_Message(number, options, body, footer, "sed2", messageId)
        list.append(replyButtonData)

    elif "pregunta personalizada" in text:
        set_user_state(number, "awaiting_custom_q1")
        data = text_Message(number, "🤖 *Modo pregunta personalizada activado*\n\n¿Qué deseas saber sobre algun procedimiento del area de registro y control?\n\nEscribe tu pregunta y te responderé basándome en la información oficial.\n\n_Para volver al menú principal, escribe 'menu'_")
        enviar_Mensaje_whatsapp(data)

    elif user_state == "awaiting_custom_q1":
        ai_response = get_ai_response(text, number)
        if ai_response == NO_INFO_MARKER:
            # Pide precisión para segundo intento
            set_user_state(number, "awaiting_custom_q2")
            data = (
                "No encuentro información específica. Indica un detalle para ayudarme, por ejemplo:\n"
                "- Sede (Bucaramanga/Valledupar/Cúcuta)\n"
                "- Trámite exacto (p. ej., prórroga de pago, tarjeta de crédito, grados)\n"
                "Escribe el detalle y lo intento de nuevo."
            )
            list.append(text_Message(number, data))
        else:
            # Respuesta única
            data = text_Message(number, f"🤖 {ai_response}")
            enviar_Mensaje_whatsapp(data)
            body = "¿Necesitas ayuda con algo más?"
            footer = "Universidad de Santander - UDES"
            options = ["✅ Si, por favor", "❌ No, gracias"]
            replyButtonData = buttonReply_Message(number, options, body, footer, "sed2", messageId)
            list.append(replyButtonData)
            clear_user_state(number)

    elif user_state == "awaiting_custom_q2":
        ai_response = get_ai_response(text, number)
        if ai_response == NO_INFO_MARKER:
            list.append(text_Message(number, "Sigue sin haber información en la base oficial sobre esa consulta. Puedes consultar nuestra página oficial para más detalles: https://udes.edu.co/registro-y-control-academico/preguntas-frecuentes "))
        else:
            list.append(text_Message(number, ai_response))
        body = "¿Necesitas ayuda con algo más?"
        footer = "Universidad de Santander - UDES"
        options = ["✅ Si, por favor", "❌ No, gracias"]
        replyButtonData = buttonReply_Message(number, options, body, footer, "sed2", messageId)
        list.append(replyButtonData)
        clear_user_state(number)
    
    elif "procedimientos" in text :
        body ="Aquí tienes algunos procedimientos comunes:"
        footer = "Universidad de Santander - UDES"
        options = ["Matrícula","Cancelaciones","Inscripciones"]

        replyButtonData = buttonReply_Message(number, options, body, footer, "procedimientos", messageId)
        list.append(replyButtonData)

    elif "matrícula" in text:
        data = text_Message(number, "Para realizar la matrícula, sigue estos pasos:\n\n1. Ingresa a tu cuenta en el portal estudiantil.\n2. Navega a la sección de 'Matrícula'.\n3. Selecciona los cursos que deseas inscribir.\n4. Confirma tu selección y realiza el pago correspondiente.")
        enviar_Mensaje_whatsapp(data)
        document = document_Message(number, sett.matricula_doc, "Aquí tienes la guía de matrícula para más detalles:", "Guia_Matricula_2025.pdf")
        enviar_Mensaje_whatsapp(document)
        time.sleep(3)
        body = "¿Necesitas ayuda con algo más?"
        footer = "Universidad de Santander - UDES"
        options = ["✅ Si, por favor", "❌ No, gracias"]
        replyButtonData = buttonReply_Message(number, options, body, footer, "sed2", messageId)
        list.append(replyButtonData)

    elif "cancelaciones" in text:
        image_url = "https://udes.edu.co/media/k2/items/cache/8c375e48fc385cd83256deb3ac6cc88c_M.jpg?t=20251007_200733"
    
        imageData = media_Message_URL(
            number, 
            image_url, 
            caption="📅 Fechas cancelaciones 2025B"
        )
        enviar_Mensaje_whatsapp(imageData)
        time.sleep(1)
    
        data = text_Message(number, "Para cancelar un curso, sigue estos pasos:\n\n1. Ingresa a tu cuenta en el portal estudiantil.\n2. Navega a la sección de 'Cancelaciones'.\n3. Selecciona el curso que deseas cancelar.\n4. Confirma la cancelación y guarda el comprobante.")
        enviar_Mensaje_whatsapp(data)
        body = "¿Necesitas ayuda con algo más?"
        footer = "Universidad de Santander - UDES"
        options = ["✅ Si, por favor", "❌ No, gracias"]
        replyButtonData = buttonReply_Message(number, options, body, footer, "sed2", messageId)
        list.append(replyButtonData)

    elif "inscripciones" in text:
        data = text_Message(number, "Para inscribirte como nuevo aspirante, sigue estos pasos:\n\n1. Visita la página de inscripciones de la UDES.\n2. Completa el formulario de inscripción con tus datos personales.\n3. Adjunta los documentos requeridos.\n4. Envía tu solicitud y espera la confirmación.")
        enviar_Mensaje_whatsapp(data)
        document = document_Message(number, sett.inscripcion_doc, "Aquí tienes la guía de inscripciones para más detalles:", "Guia_Inscripcion_2025.pdf")
        enviar_Mensaje_whatsapp(document)
        time.sleep(3)
        body = "¿Necesitas ayuda con algo más?"
        footer = "Universidad de Santander - UDES"
        options = ["✅ Si, por favor", "❌ No, gracias"]
        replyButtonData = buttonReply_Message(number, options, body, footer, "sed2", messageId)
        list.append(replyButtonData)

    elif "horarios de atención" in text:
        data = text_Message(number, "Nuestros horarios de atención son:\n\n- lunes a viernes de 8:00 am a 12:00 pm y de 2:00 pm a 7:00 pm\n- Domingos: Cerrado")
        enviar_Mensaje_whatsapp(data)
        body = "¿Necesitas ayuda con algo más?"
        footer = "Universidad de Santander - UDES"
        options = ["✅ Si, por favor", "❌ No, gracias"]
        replyButtonData = buttonReply_Message(number, options, body, footer, "sed2", messageId)
        list.append(replyButtonData)
    
    elif "adiós" in text or "gracias" in text or "hasta luego" in text or "bye" in text or "adios" in text:
        data = text_Message(number, "¡Gracias por contactarnos! Si tienes más preguntas, no dudes en volver. ¡Que tengas un excelente día! 👋")
        enviar_Mensaje_whatsapp(data)

    elif "si, por favor" in text:
        body ="¡Claro! ¿En qué más puedo ayudarte?"
        footer = "Universidad de Santander - UDES"
        options = ["Fechas importantes","Procedimientos","Preguntas Frecuentes","Horarios de atención", "Pregunta personalizada"]

        listReply = listReply_Message(number, options, body, footer, "sed1", messageId)
        list.append(listReply)

    elif "no, gracias." in text:
        data = text_Message(number, "¡Gracias por contactarnos! Si tienes más preguntas, no dudes en volver. ¡Que tengas un excelente día! 👋")
        enviar_Mensaje_whatsapp(data)

    else:
        body ="Lo siento, no entendí tu mensaje. Por favor, selecciona una de las opciones a continuación o escribe 'Hola' para comenzar."
        footer = "Universidad de Santander - UDES"
        options = ["Fechas importantes","Procedimientos","Preguntas Frecuentes","Horarios de atención", "Pregunta personalizada"]

        listReply = listReply_Message(number, options, body, footer, "sed1", messageId)
        list.append(listReply)

    for item in list:
        enviar_Mensaje_whatsapp(item)

    #data = text_Message(number,"¡Bienvenido al Chat bot de registro y control de la Universidad de Santander! 👋")
    #enviar_Mensaje_whatsapp(data)