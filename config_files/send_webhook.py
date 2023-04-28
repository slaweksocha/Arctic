import requests
from config_files.config import webhook_url

def webhook(pdf_name, date, kontrahent):
    # treść wiadomości
    message = {
        "text": f"{pdf_name} document from {kontrahent} dated {date} has been successfully processed"
    }

    # wysyłanie wiadomości
    response = requests.post(webhook_url, json=message)

    # sprawdzenie połaczenia
    if response.status_code == 200:
        print("Message sent to Teams successfully.")
    else:
        print("Error sending message to Teams:", response.status_code, response.text)
