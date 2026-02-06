import requests
import json
from get_token import get_token

def create_security_group(token: str, sg_name: str, description: str = "", region_code: str = "kr1"):
    """
    보안 그룹을 생성하는 함수
    API: POST /v2.0/security-groups
    """
    NETWORK_API_URL = f"https://{region_code}-api-network-infrastructure.nhncloudservice.com"
    url = f"{NETWORK_API_URL}/v2.0/security-groups"

    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }

    payload = {
        "security_group": {
            "name": sg_name,
            "description": description
        }
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        if response.status_code == 201: # Assuming 200 OK for successful creation
            sg_info = response.json().get('security_group', {})
            print(f"✅ 보안 그룹 생성 성공! (Region: {region_code})")
            print(f" - 이름: {sg_info.get('name')}")
            print(f" - ID: {sg_info.get('id')}")
            print(f" - 설명: {sg_info.get('description')}")
            return sg_info.get('id')
        else:
            print(f"❌ 보안 그룹 생성 실패 (Status: {response.status_code})")
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

    # 2. 보안 그룹 생성 시도
    sg_name = "my-test-security-group"
    sg_description = "Security group for test instance"
    
    created_sg_id = create_security_group(auth_token, sg_name, sg_description, "kr1")

    if created_sg_id:
        print(f"✨ 최종적으로 생성된 보안 그룹 ID: {created_sg_id}")
    else:
        print("🚨 보안 그룹 생성에 실패했습니다.")
