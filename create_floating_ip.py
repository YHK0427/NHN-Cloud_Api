import requests
import json
from get_token import get_token

def create_floating_ip(
    token: str,
    floating_network_id: str,
    region_code: str = "kr1",
    port_id: str = None, # Optional: to associate immediately
    delete_protection: bool = False,
    label: str = None
):
    """
    플로팅 IP를 생성(할당)하는 함수
    API: POST /v2.0/floatingips
    """
    NETWORK_API_URL = f"https://{region_code}-api-network-infrastructure.nhncloudservice.com"
    url = f"{NETWORK_API_URL}/v2.0/floatingips"

    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }

    payload = {
        "floatingip": {
            "floating_network_id": floating_network_id,
            "delete_protection": delete_protection
        }
    }
    if port_id:
        payload["floatingip"]["port_id"] = port_id
    if label:
        payload["floatingip"]["label"] = label

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        if response.status_code == 200: # Assuming 200 OK for successful creation
            fip_info = response.json().get('floatingip', {})
            print(f"✅ 플로팅 IP 생성 성공! (Region: {region_code})")
            print(f" - ID: {fip_info.get('id')}")
            print(f" - IP 주소: {fip_info.get('floating_ip_address')}")
            print(f" - 외부 네트워크 ID: {fip_info.get('floating_network_id')}")
            return {
                "id": fip_info.get('id'),
                "ip_address": fip_info.get('floating_ip_address')
            }
        else:
            print(f"❌ 플로팅 IP 생성 실패 (Status: {response.status_code})")
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

    # 2. 플로팅 IP 생성 시도
    # 실제 외부 네트워크 ID를 사용해야 합니다.
    # NHN Cloud 콘솔에서 '외부 네트워크' 또는 '공용 네트워크'의 ID를 확인하세요.
    example_floating_network_id = "YOUR_FLOATING_NETWORK_ID_HERE" 
    
    if example_floating_network_id == "YOUR_FLOATING_NETWORK_ID_HERE":
        print("⚠️ 경고: 'example_floating_network_id'를 실제 외부 네트워크 ID로 변경해주세요!")
        print("    NHN Cloud 콘솔에서 플로팅 IP를 할당할 외부 네트워크 ID를 확인하세요.")
    else:
        fip_data = create_floating_ip(auth_token, example_floating_network_id, "kr1")

        if fip_data:
            print(f"✨ 최종적으로 생성된 플로팅 IP 정보: ID={fip_data['id']}, IP={fip_data['ip_address']}")
        else:
            print("🚨 플로팅 IP 생성에 실패했습니다.")
