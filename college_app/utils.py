# gemini_integration/utils.py
import requests
from django.conf import settings

def get_gemini_data(endpoint, params=None):
    url = f"{settings.GEMINI_API_URL}/{endpoint}"
    headers = {
        'Authorization': f'Bearer {settings.GEMINI_API_KEY}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()
