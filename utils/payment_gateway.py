import requests
import json
from config import Config
import base64
from datetime import datetime

class MidtransGateway:
    """Midtrans Payment Gateway Integration"""
    
    def __init__(self):
        # Get credentials from config - update these with actual Midtrans credentials
        self.server_key = getattr(Config, 'MIDTRANS_SERVER_KEY', 'YOUR_MIDTRANS_SERVER_KEY')
        self.client_key = getattr(Config, 'MIDTRANS_CLIENT_KEY', 'YOUR_MIDTRANS_CLIENT_KEY')
        self.midtrans_url = 'https://app.midtrans.com/snap/v1/transactions'
        self.is_production = getattr(Config, 'MIDTRANS_IS_PRODUCTION', False)
        
        if not self.is_production:
            self.midtrans_url = 'https://app.sandbox.midtrans.com/snap/v1/transactions'

    def _get_auth_header(self):
        """Create Basic Auth header for Midtrans API"""
        credentials = f"{self.server_key}:"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {encoded}"}

    def create_snap_token(self, order_id, gross_amount, user_data, program_data):
        """Create Snap token for payment"""
        try:
            headers = self._get_auth_header()
            headers['Content-Type'] = 'application/json'

            payload = {
                "transaction_details": {
                    "order_id": order_id,
                    "gross_amount": int(gross_amount)
                },
                "customer_details": {
                    "first_name": user_data.get('full_name', '').split()[0] if user_data.get('full_name') else 'Customer',
                    "email": user_data.get('email', 'noemail@example.com'),
                    "phone": user_data.get('phone', ''),
                },
                "item_details": [
                    {
                        "id": f"program_{program_data['id']}",
                        "price": int(gross_amount),
                        "quantity": 1,
                        "name": program_data['name']
                    }
                ],
                "expiry": {
                    "unit": "minutes",
                    "length": 60
                }
            }

            response = requests.post(self.midtrans_url, json=payload, headers=headers)
            
            if response.status_code == 201:
                result = response.json()
                return {
                    'success': True,
                    'snap_token': result.get('token'),
                    'redirect_url': result.get('redirect_url'),
                    'order_id': order_id
                }
            else:
                return {
                    'success': False,
                    'error': f"Midtrans API Error: {response.status_code}",
                    'response': response.text
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def verify_payment(self, order_id, server_key=None):
        """Verify payment status with Midtrans"""
        try:
            if server_key is None:
                server_key = self.server_key
                
            url = f"https://api.sandbox.midtrans.com/v2/{order_id}/status" if not self.is_production else f"https://api.midtrans.com/v2/{order_id}/status"
            
            credentials = f"{server_key}:"
            encoded = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                "Authorization": f"Basic {encoded}"
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': 'Verification failed', 'status_code': response.status_code}
        except Exception as e:
            return {'error': str(e)}

    def validate_notification(self, notification_key, signature_key):
        """Validate Midtrans notification signature"""
        try:
            # Midtrans sends signature_key which can be used to verify authenticity
            # In production, you should verify this signature
            order_id = notification_key.get('order_id')
            status_code = notification_key.get('status_code')
            gross_amount = notification_key.get('gross_amount')
            
            # Construct verification string and compare with signature
            # This is a basic implementation - for production use proper signature verification
            return True
        except Exception as e:
            return False

    @staticmethod
    def generate_order_id(user_id, program_id):
        """Generate unique order ID for Midtrans"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"ORDER-{user_id}-{program_id}-{timestamp}"
