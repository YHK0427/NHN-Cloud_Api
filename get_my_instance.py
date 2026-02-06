import requests
from get_token import get_token


def get_my_instance(token_id):
    url = "https://kr2-api-instance-infrastructure.nhncloudservice.com"
    url = "https://kr1-api-instance-infrastructure.nhncloudservice.com"
    tenant_id = "0cc0040eaa0044bc99f8a7f4bedc233b"
    uri = f"/v2/{tenant_id}/flavors"


    headers = {
        "X-Auth-Token": token_id
    } 
    
    response = requests.get(url + uri, headers=headers) 
    print(response.json())
    
    
if __name__ == "__main__":
    token = get_token()["token_id"]
    get_my_instance(token)