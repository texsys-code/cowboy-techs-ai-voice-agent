import requests
import os
from dotenv import load_dotenv
import time

load_dotenv()

class HaloAPIClient:
    def __init__(self):
        self.client_id = os.environ["HALO_CLIENT_ID"]
        self.client_secret = os.environ["HALO_CLIENT_SECRET"]
        self.api_url = os.environ["HALO_API_URL"]
        self.token_url = f"{self.api_url}/auth/token"
        self.access_token = None
        self.token_expiry = 0

    def get_access_token(self):
        if self.access_token and time.time() < self.token_expiry - 60:
            return self.access_token
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'all'
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post(self.token_url, data=data, headers=headers)
        response.raise_for_status()
        token_data = response.json()
        self.access_token = token_data['access_token']
        self.token_expiry = time.time() + token_data.get('expires_in', 3600)
        return self.access_token

    def create_ticket(self, queue, name, company, details):
        token = self.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = [
                    {
                        "summary": f"{name} - {company}",
                        "details": details,
                        "status_id": 1,
                        "tickettype_id": 1,
                        "sla_id": 3,
                        "sla_name": "Incident SLA",
                        "priority_id": 4,
                        "client_id": 174,
                        "client_name": "IBT HQ",
                        "site_id": 216,
                        "site_name": "Main Office",
                        "user_id": 267,
                        "user_name": "Company Contact ",
                        "team_id": queue,
                        "agent_id": 1,
                        "category_1": "Business Applications",
                        "impact": 3,
                        "urgency": 2,	
                    }
                ]
        response = requests.post(
            f"{self.api_url}/api/tickets",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json() 

    def lookup_user_by_phone(self, phone_number):
        """
        Look up a user by phone number in Halo PSA.
        
        Args:
            phone_number (str): The phone number to search for
            
        Returns:
            dict: User information if found, None if not found
        """
        token = self.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Clean the phone number (remove any non-digit characters)
        clean_phone = ''.join(filter(str.isdigit, phone_number))
        
        # Remove country code if present (common patterns)
        # Remove +1 (US/Canada), +44 (UK), +61 (Australia), etc.
        if clean_phone.startswith('1') and len(clean_phone) == 11:
            # US/Canada number with country code
            clean_phone = clean_phone[1:]
        elif clean_phone.startswith('44') and len(clean_phone) >= 12:
            # UK number with country code
            clean_phone = clean_phone[2:]
        elif clean_phone.startswith('61') and len(clean_phone) >= 11:
            # Australia number with country code
            clean_phone = clean_phone[2:]
        elif clean_phone.startswith('86') and len(clean_phone) >= 13:
            # China number with country code
            clean_phone = clean_phone[2:]
        elif clean_phone.startswith('81') and len(clean_phone) >= 12:
            # Japan number with country code
            clean_phone = clean_phone[2:]
        elif clean_phone.startswith('49') and len(clean_phone) >= 12:
            # Germany number with country code
            clean_phone = clean_phone[2:]
        elif clean_phone.startswith('33') and len(clean_phone) >= 11:
            # France number with country code
            clean_phone = clean_phone[2:]
        elif clean_phone.startswith('39') and len(clean_phone) >= 11:
            # Italy number with country code
            clean_phone = clean_phone[2:]
        elif clean_phone.startswith('34') and len(clean_phone) >= 11:
            # Spain number with country code
            clean_phone = clean_phone[2:]
        elif clean_phone.startswith('31') and len(clean_phone) >= 10:
            # Netherlands number with country code
            clean_phone = clean_phone[2:]
        elif clean_phone.startswith('46') and len(clean_phone) >= 10:
            # Sweden number with country code
            clean_phone = clean_phone[2:]
        elif clean_phone.startswith('47') and len(clean_phone) >= 9:
            # Norway number with country code
            clean_phone = clean_phone[2:]
        elif clean_phone.startswith('45') and len(clean_phone) >= 9:
            # Denmark number with country code
            clean_phone = clean_phone[2:]
        elif clean_phone.startswith('358') and len(clean_phone) >= 11:
            # Finland number with country code
            clean_phone = clean_phone[3:]
        elif clean_phone.startswith('48') and len(clean_phone) >= 10:
            # Poland number with country code
            clean_phone = clean_phone[2:]
        elif clean_phone.startswith('420') and len(clean_phone) >= 11:
            # Czech Republic number with country code
            clean_phone = clean_phone[3:]
        elif clean_phone.startswith('36') and len(clean_phone) >= 10:
            # Hungary number with country code
            clean_phone = clean_phone[2:]
        elif clean_phone.startswith('40') and len(clean_phone) >= 10:
            # Romania number with country code
            clean_phone = clean_phone[2:]
        elif clean_phone.startswith('7') and len(clean_phone) == 11:
            # Russia number with country code
            clean_phone = clean_phone[1:]
        elif clean_phone.startswith('91') and len(clean_phone) >= 11:
            # India number with country code
            clean_phone = clean_phone[2:]
        elif clean_phone.startswith('82') and len(clean_phone) >= 11:
            # South Korea number with country code
            clean_phone = clean_phone[2:]
        elif clean_phone.startswith('65') and len(clean_phone) >= 9:
            # Singapore number with country code
            clean_phone = clean_phone[2:]
        elif clean_phone.startswith('60') and len(clean_phone) >= 10:
            # Malaysia number with country code
            clean_phone = clean_phone[2:]
        elif clean_phone.startswith('66') and len(clean_phone) >= 10:
            # Thailand number with country code
            clean_phone = clean_phone[2:]
        elif clean_phone.startswith('84') and len(clean_phone) >= 10:
            # Vietnam number with country code
            clean_phone = clean_phone[2:]
        elif clean_phone.startswith('971') and len(clean_phone) >= 11:
            # UAE number with country code
            clean_phone = clean_phone[3:]
        elif clean_phone.startswith('966') and len(clean_phone) >= 11:
            # Saudi Arabia number with country code
            clean_phone = clean_phone[3:]
        elif clean_phone.startswith('972') and len(clean_phone) >= 10:
            # Israel number with country code
            clean_phone = clean_phone[3:]
        elif clean_phone.startswith('27') and len(clean_phone) >= 10:
            # South Africa number with country code
            clean_phone = clean_phone[2:]
        elif clean_phone.startswith('55') and len(clean_phone) >= 12:
            # Brazil number with country code
            clean_phone = clean_phone[2:]
        elif clean_phone.startswith('52') and len(clean_phone) >= 11:
            # Mexico number with country code
            clean_phone = clean_phone[2:]
        elif clean_phone.startswith('54') and len(clean_phone) >= 11:
            # Argentina number with country code
            clean_phone = clean_phone[2:]
        elif clean_phone.startswith('56') and len(clean_phone) >= 10:
            # Chile number with country code
            clean_phone = clean_phone[2:]
        elif clean_phone.startswith('57') and len(clean_phone) >= 11:
            # Colombia number with country code
            clean_phone = clean_phone[2:]
        elif clean_phone.startswith('58') and len(clean_phone) >= 11:
            # Venezuela number with country code
            clean_phone = clean_phone[2:]
        elif clean_phone.startswith('51') and len(clean_phone) >= 10:
            # Peru number with country code
            clean_phone = clean_phone[2:]
        elif clean_phone.startswith('593') and len(clean_phone) >= 10:
            # Ecuador number with country code
            clean_phone = clean_phone[3:]
        elif clean_phone.startswith('595') and len(clean_phone) >= 10:
            # Paraguay number with country code
            clean_phone = clean_phone[3:]
        elif clean_phone.startswith('598') and len(clean_phone) >= 9:
            # Uruguay number with country code
            clean_phone = clean_phone[3:]
        elif clean_phone.startswith('591') and len(clean_phone) >= 9:
            # Bolivia number with country code
            clean_phone = clean_phone[3:]
        elif clean_phone.startswith('593') and len(clean_phone) >= 10:
            # Ecuador number with country code
            clean_phone = clean_phone[3:]
        elif clean_phone.startswith('507') and len(clean_phone) >= 9:
            # Panama number with country code
            clean_phone = clean_phone[3:]
        elif clean_phone.startswith('506') and len(clean_phone) >= 9:
            # Costa Rica number with country code
            clean_phone = clean_phone[3:]
        elif clean_phone.startswith('502') and len(clean_phone) >= 9:
            # Guatemala number with country code
            clean_phone = clean_phone[3:]
        elif clean_phone.startswith('503') and len(clean_phone) >= 9:
            # El Salvador number with country code
            clean_phone = clean_phone[3:]
        elif clean_phone.startswith('504') and len(clean_phone) >= 9:
            # Honduras number with country code
            clean_phone = clean_phone[3:]
        elif clean_phone.startswith('505') and len(clean_phone) >= 9:
            # Nicaragua number with country code
            clean_phone = clean_phone[3:]
        elif clean_phone.startswith('501') and len(clean_phone) >= 8:
            # Belize number with country code
            clean_phone = clean_phone[3:]
        elif clean_phone.startswith('509') and len(clean_phone) >= 9:
            # Haiti number with country code
            clean_phone = clean_phone[3:]
        elif clean_phone.startswith('1') and len(clean_phone) == 10:
            # US/Canada number without country code (already clean)
            pass
        elif clean_phone.startswith('0') and len(clean_phone) >= 10:
            # Remove leading zero (common in some countries)
            clean_phone = clean_phone[1:]
        
        # Build the search URL
        search_url = f"{self.api_url}/api/users"
        params = {
            "search": clean_phone,
            "search_phonenumbers": "true"
        }
        
        try:
            response = requests.get(search_url, headers=headers, params=params)
            response.raise_for_status()
            
            users_data = response.json()
            
            # Check if we found any users
            if users_data and len(users_data) > 0:
                # Return the first matching user
                user = users_data[0]
                return {
                    "id": user.get("id"),
                    "name": user.get("name"),
                    "firstname": user.get("firstname"),
                    "surname": user.get("surname"),
                    "email": user.get("email"),
                    "phone": user.get("phone"),
                    "company": user.get("company_name"),
                    "client_id": user.get("client_id"),
                    "site_id": user.get("site_id")
                }
            else:
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error looking up user by phone number: {e}")
            return None