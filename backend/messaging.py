from abc import ABC, abstractmethod
import httpx

class MessageResult:
    def __init__(self, success: bool, error_message: str = None):
        self.success = success
        self.error_message = error_message

class NotificationChannel(ABC):
    @abstractmethod
    def send_prescription(self, patient_contact: str, pdf_url: str, patient_name: str) -> MessageResult:
        pass

class TelegramChannel(NotificationChannel):
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        # In a real scenario we'd map patient phone numbers to Telegram Chat IDs.
        # For this demo, we will use a dummy/hardcoded chat ID or just print to console.
        # Let's assume `patient_contact` for this demo is just a Telegram Chat ID for simplicity,
        # or we simulate a successful send if it's a normal phone number.
    def send_prescription(self, patient_contact: str, pdf_url: str, patient_name: str) -> MessageResult:
        print(f"[Telegram] Sending PDF to {patient_name} at chat ID {patient_contact}. PDF: {pdf_url}")
        
        url = f"https://api.telegram.org/bot{self.bot_token}/sendDocument"
        
        try:
            with open(pdf_url, "rb") as pdf_file:
                files = {'document': (pdf_url.split('/')[-1].split('\\')[-1], pdf_file, 'application/pdf')}
                data = {
                    'chat_id': patient_contact,
                    'caption': f"Hello {patient_name}, here is your digital prescription."
                }
                
                # We use timeout=10 in case network is slow for uploading the PDF
                response = httpx.post(url, data=data, files=files, timeout=10.0)
                
                if response.status_code == 200:
                    print(f"[Telegram] Success! Sent to {patient_contact}")
                    return MessageResult(success=True)
                else:
                    err_msg = f"HTTP {response.status_code}: {response.text}"
                    print(f"[Telegram] Failed: {err_msg}")
                    return MessageResult(success=False, error_message=err_msg)
        except Exception as e:
            print(f"[Telegram] Exception: {e}")
            return MessageResult(success=False, error_message=str(e))

from twilio.rest import Client

class WhatsAppTwilioChannel(NotificationChannel):
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number

    def send_prescription(self, patient_contact: str, pdf_url: str, patient_name: str) -> MessageResult:
        print(f"[WhatsApp] Sending PDF to {patient_name} at {patient_contact}")
        
        # 1. Convert PDF to Image and upload to freeimage.host
        public_image_url = None
        try:
            import fitz
            import base64
            
            # Convert first page of PDF to image
            doc = fitz.open(pdf_url)
            page = doc.load_page(0)
            pix = page.get_pixmap(dpi=150)
            png_data = pix.tobytes()
            b64_image = base64.b64encode(png_data).decode('utf-8')
            
            # Upload to freeimage.host
            response = httpx.post(
                'https://freeimage.host/api/1/upload',
                data={
                    'key': '6d207e02198a847aa98d0a2a901485a5',
                    'action': 'upload',
                    'source': b64_image,
                    'format': 'json'
                },
                timeout=20.0
            )
            
            if response.status_code == 200:
                public_image_url = response.json().get('image', {}).get('url')
                print(f"[WhatsApp] Successfully uploaded image for Twilio: {public_image_url}")
        except Exception as e:
            print(f"[WhatsApp] Image conversion/upload exception: {e}")

        # 2. Send via Twilio
        try:
            client = Client(self.account_sid, self.auth_token)
            
            if not patient_contact.startswith("+"):
                patient_contact = "+91" + patient_contact
                
            to_number = f"whatsapp:{patient_contact}" if not patient_contact.startswith("whatsapp:") else patient_contact
            from_number_fmt = f"whatsapp:{self.from_number}" if not self.from_number.startswith("whatsapp:") else self.from_number
                
            body_text = f"Hello {patient_name}, here is your digital prescription."
            
            message_kwargs = {
                "from_": from_number_fmt,
                "body": body_text,
                "to": to_number
            }
            
            if public_image_url:
                message_kwargs["media_url"] = [public_image_url]
                
            message = client.messages.create(**message_kwargs)
            
            print(f"[WhatsApp] Success! Message SID: {message.sid}")
            return MessageResult(success=True)
            
        except Exception as e:
            print(f"[WhatsApp] Exception: {e}")
            return MessageResult(success=False, error_message=str(e))

class SMSChannel(NotificationChannel):
    def send_prescription(self, patient_contact: str, pdf_url: str, patient_name: str) -> MessageResult:
        # [PROD] stub
        raise NotImplementedError("SMS channel not yet implemented")
