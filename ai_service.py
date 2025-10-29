from groq import Groq
from sett import api_key_groq
import os


def load_context():
    """Carga el contexto desde archivo txt"""
    try:
        with open('informacion.txt', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "No se encontró la base de conocimientos."
    
NO_INFO_MARKER = "NO_INFO"

def get_ai_response(query, number):
    try:
        client = Groq(api_key=api_key_groq)
        context = load_context()  # Cargar desde archivo
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"""Eres un asistente de la Universidad de Santander.
                    Si no hay información suficiente para responder, responde EXACTAMENTE: {NO_INFO_MARKER} 
                    Responde SOLO con esta información oficial:
                    
                    {context}"""
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            temperature=0.5,
            max_tokens=500
        )
        
        return chat_completion.choices[0].message.content
        
    except Exception as e:
        print(f"Error al obtener respuesta de IA: {e}")
        return "Lo siento, hubo un error al procesar tu pregunta. Por favor, intenta de nuevo, tambien puedes consultar la información en nuestra página oficial: https://udes.edu.co/registro-y-control-academico/preguntas-frecuentes "

# Diccionario para mantener el estado de conversación por usuario
user_states = {}

def set_user_state(number, state):
    """Establece el estado de conversación del usuario"""
    user_states[number] = state

def get_user_state(number):
    """Obtiene el estado de conversación del usuario"""
    return user_states.get(number, None)

def clear_user_state(number):
    """Limpia el estado de conversación del usuario"""
    if number in user_states:
        del user_states[number]
