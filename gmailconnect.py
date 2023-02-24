import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configura las credenciales de autenticación
creds = Credentials.from_authorized_user_file('credentials.json', ['https://www.googleapis.com/auth/gmail.readonly'])

# Crea una instancia del cliente de la API de Gmail
service = build('gmail', 'v1', credentials=creds)

# Define los parámetros de búsqueda de los correos electrónicos
query = 'from:alertasynotificaciones@notificacionesbancolombia.com'
results = service.users().messages().list(userId='me', q=query).execute()

# Itera sobre los resultados y obtiene los datos de los correos electrónicos
for msg in results.get('messages', []):
    # Obtiene el ID del mensaje y los datos adicionales
    msg_id = msg['id']
    msg_data = service.users().messages().get(userId='me', id=msg_id).execute()
    
    # Obtiene los datos específicos del mensaje que deseas leer (por ejemplo, el asunto o el cuerpo)
    headers = msg_data['payload']['headers']
    subject = next(h['value'] for h in headers if h['name'] == 'Subject')
    body = msg_data['snippet']
    
    # Haz lo que desees con los datos del mensaje obtenidos (por ejemplo, guardarlos en una base de datos)
    print(f'Subject: {subject}\nBody: {body}\n')
    
