from src.services.whatsapp_notifier import WhatsAppNotifier
import os

w = WhatsAppNotifier(api_url='https://example.test', api_key='ABC123', auth_header_name=os.getenv('EVOLUTION_AUTH_HEADER_NAME','apikey'), instance_name='inst')
print('Headers:')
print(w.headers)
print('Auth header name:', w.auth_header_name)
print('Instance:', w.instance_name)
