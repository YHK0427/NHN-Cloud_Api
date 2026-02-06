import requests
import json
from get_token import get_token

def get_external_network_id(token: str, region_code: str = "kr1"):
    """
    외부 네트워크 ID를 조회하는 함수
    API: GET /v2.0/vpcs?router:external=true
    """
    NETWORK_API_URL = f"https://{region_code}-api-network-infrastructure.nhncloudservice.com"
    url = f"{NETWORK_API_URL}/v2.0/vpcs?router:external=true"

    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        if response.status_code == 200:
            vpcs_data = response.json().get('vpcs', [])
            
            external_networks = [vpc for vpc in vpcs_data if vpc.get('router:external') is True]

            if external_networks:
                # Assuming we take the first external network found
                external_network_id = external_networks[0].get('id')
                external_network_name = external_networks[0].get('name')
                print(f"✅ 외부 네트워크 ID 조회 성공! (Region: {region_code})")
                print(f" - 이름: {external_network_name}, ID: {external_network_id}")
                return external_network_id
            else:
                print(" - router:external=true인 외부 네트워크를 찾을 수 없습니다.")
                return None
        else:
            print(f"❌ 외부 네트워크 ID 조회 실패 (Status: {response.status_code})")
            print(f"응답 내용: {response.text}")
            return None

    except requests.exceptions.HTTPError as http_err:
        print(f"❗ HTTP 오류 발생: {http_err}")
        print(f"응답 내용: {response.text}")
        return None
    except Exception as e:
        print(f"❗ 오류 발생: {e}")
        return None

if __name__ == "__main__":
    # 1. 토큰 가져오기
    auth_token = get_token()["token_id"]

    # 2. 외부 네트워크 ID 조회 시도
    external_net_id = get_external_network_id(auth_token, "kr1")

    if external_net_id:
        print(f"✨ 최종적으로 조회된 외부 네트워크 ID: {external_net_id}")
    else:
        print("🚨 외부 네트워크 ID 조회에 실패했습니다.")
