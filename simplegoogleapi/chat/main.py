from httplib2 import Http
from json import dumps

def send_webhook_message(webhook, message):
    body = {
        'text': message
    }
    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    http_obj = Http()
    response = http_obj.request(
        uri=webhook,
        method='POST',
        headers=headers,
        body=dumps(body),
    )

if __name__ == '__main__':
    message = 'Hello'
    webhook = 'https://chat.googleapis.com/v1/spaces/...'
    # send_webhook_message(webhook=webhook, message=message)