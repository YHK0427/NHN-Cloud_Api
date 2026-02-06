import requests
import json
from get_token import get_token

def associate_floating_ip(
    token: str,
    floating_ip_id: str,
    port_id: str,
    region_code: str = "kr1",
    fixed_ip_address: str = None
):
    """
    플로팅 IP를 인스턴스의 특정 포트에 연결하는 함수
    API: PUT /v2.0/floatingips/{floatingIpId}
    """
    NETWORK_API_URL = f"https://{region_code}-api-network-infrastructure.nhncloudservice.com"
    url = f"{NETWORK_API_URL}/v2.0/floatingips/{floating_ip_id}"

    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }

    payload = {
        "floatingip": {
            "port_id": port_id
        }
    }
    if fixed_ip_address:
        payload["floatingip"]["fixed_ip_address"] = fixed_ip_address

    try:
        response = requests.put(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        if response.status_code == 200: # Assuming 200 OK for successful update
            print(f"✅ 플로팅 IP '{floating_ip_id}'가 포트 '{port_id}'에 성공적으로 연결되었습니다. (Region: {region_code})")
            return True
        else:
            print(f"❌ 플로팅 IP 연결 실패 (Status: {response.status_code})")
            print(f"응답 내용: {response.text}")
            return False

    except requests.exceptions.HTTPError as http_err:
        print(f"❗ HTTP 오류 발생: {http_err}")
        print(f"응답 내용: {response.text}")
        return False
    except Exception as e:
        print(f"❗ 오류 발생: {e}")
        return False

if __name__ == "__main__":
    # 1. 토큰 가져오기
    auth_token = get_token()["token_id"]

    # 2. 플로팅 IP 연결 시도
    # 실제 플로팅 IP ID와 포트 ID를 사용해야 합니다.
    example_floating_ip_id = "YOUR_FLOATING_IP_ID_HERE" 
    example_port_id = "YOUR_INSTANCE_PORT_ID_HERE" 
    
    if example_floating_ip_id == "YOUR_FLOATING_IP_ID_HERE" or example_port_id == "YOUR_INSTANCE_PORT_ID_HERE":
        print("⚠️ 경고: 'example_floating_ip_id'와 'example_port_id'를 실제 값으로 변경해주세요!")
        print("    먼저 플로팅 IP를 생성하고 인스턴스를 생성하여 ID를 확인하세요.")
    else:
        associated = associate_floating_ip(auth_token, example_floating_ip_id, example_port_id, "kr1")

        if associated:
            print("✨ 플로팅 IP 연결 작업이 성공적으로 완료되었습니다.")
        else:
            print("🚨 플로팅 IP 연결 작업에 실패했습니다.")
