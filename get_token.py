import requests
import json
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

load_dotenv() # Load variables from .env file

TOKEN_FILE = "token.json"

def save_token(token_data):
    """
    Saves the token data to a JSON file.
    """
    with open(TOKEN_FILE, 'w') as f:
        json.dump(token_data, f, indent=4)

def load_token():
    """
    Loads the token data from a JSON file.
    Returns the token data if found and valid, otherwise returns None.
    """
    try:
        with open(TOKEN_FILE, 'r') as f:
            token_data = json.load(f)
            return token_data
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def parse_datetime(dt_str):
    """
    Parses an ISO formatted datetime string, handling timezone information.
    """
    # Assuming the format is like "2026-02-04T07:23:07.000Z"
    if dt_str.endswith('Z'):
        dt_str = dt_str[:-1] + '+00:00'
    return datetime.fromisoformat(dt_str)

def get_token():
    """
    Retrieves an authentication token.
    Checks for a cached, unexpired token first. If not found or expired,
    it fetches a new token from the API and caches it.
    """
    
    # Try to load existing token
    cached_token = load_token()
    if cached_token:
        try:
            expires_at = parse_datetime(cached_token['token_expires'])
            if expires_at > datetime.now(timezone.utc):
                print("Using cached token.")
                return cached_token
            else:
                print("Cached token expired. Fetching a new one.")
        except (KeyError, ValueError) as e:
            print(f"Error processing cached token: {e}. Fetching a new one.")

    print("No valid cached token found. Fetching a new token from API.")
    url = "https://api-identity-infrastructure.nhncloudservice.com"
    uri = "/v2.0/tokens"
    
    # Load sensitive data from environment variables
    tenant_id = os.getenv("TENANT_ID")
    username = os.getenv("API_USERNAME")
    password = os.getenv("API_PASSWORD")

    if not all([tenant_id, username, password]):
        print("🚨 Error: TENANT_ID, API_USERNAME, or API_PASSWORD environment variables not set.")
        print("    Please create a .env file from .env.example and fill in your credentials.")
        return None

    body = {
        "auth": {
            "tenantId": tenant_id,
            "passwordCredentials": {
                "username": username,
                "password": password
            }
        }
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url + uri, json=body, headers=headers)
    response.raise_for_status()  # Raise an exception for bad status codes

    token_data = response.json()["access"]["token"]
    
    token_dict = {
        "token_id": token_data["id"],
        'token_expires': token_data["expires"],
        'token_issued_at': token_data["issued_at"]
    }

    save_token(token_dict)
    return token_dict


if __name__ == "__main__":
    token = get_token()
    if token:
        print(token)
