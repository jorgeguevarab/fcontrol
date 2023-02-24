from __future__ import print_function

import os.path
import base64
import email
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_body(message):
    """
    Recupera el cuerpo del mensaje.
    """
    payload = message['payload']
    if 'parts' in payload:
        parts = payload['parts']
        for part in parts:
            if part['filename'] == '':
                body = part['body']
                return body['data']
    else:
        return payload['body']['data']
    

def get_last_email(service, query):
    """Get the last email message from Gmail that matches the query."""
    try:
        response = service.users().messages().list(userId='me', q=query).execute()
        messages = [ ]
        if 'messages' in response:
            messages.extend(response['messages'])
        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId='me',q=query, pageToken=page_token).execute()
            if 'messages' in response:
                messages.extend(response['messages'])
        message_id = messages[0]['id']
        message = service.users().messages().get(userId='me', id=message_id).execute()
        return message
    except HttpError as error:
        print(f'An error occurred: {error}')


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        query = 'from:serviciopse@achcolombia.com.co'
        message = get_last_email(service, query)
        
        if message:
            # Extract data from email message
            message_body = get_body(message)
            decoded_message = base64.urlsafe_b64decode(message_body).decode('utf-8')
            value_regex = r'Valor de la Transacci.*?n: \$ ([\d,]+)'
            value_match = re.search(value_regex, decoded_message)
            #print(decoded_message)
            #print(type(value_match))

            if value_match:
                transaction_value = value_match.group(1)
                print(f'Transaction value: {transaction_value}')
            else:
                print('Transaction value not found in email.')
        else:
            print('No emails found that match the query.')
            
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')




if __name__ == '__main__':
    main()
