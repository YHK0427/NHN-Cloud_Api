import requests
import json
from get_token import get_token

# ================= Configuration =================
# 주의: 네트워크 작업은 'api-network-infrastructure' 도메인을 사용합니다.

def create_vpc(token, vpc_name, cidr, region_code="kr1"):
    """
    VPC를 생성하는 함수
    API: POST /v2.0/vpcs
    """
    NETWORK_API_URL = f"https://{region_code}-api-network-infrastructure.nhncloudservice.com"
    url = f"{NETWORK_API_URL}/v2.0/vpcs"
    
    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }
    
    # 요청 본문 (Payload) 구성
    payload = {
        "vpc": {
            "name": vpc_name,
            "cidrv4": cidr
            # "external_network_id": "..." # 외부 네트워크 연결 시 필요 (옵션)
        }
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 201: # Created
            vpc_info = response.json().get('vpc', {})
            print(f"✅ VPC 생성 성공! (Region: {region_code})")
            print(f" - 이름: {vpc_info.get('name')}")
            print(f" - ID: {vpc_info.get('id')}")
            print(f" - CIDR: {vpc_info.get('cidrv4')}")
            return vpc_info.get('id')
        else:
            print(f"❌ VPC 생성 실패 (Status: {response.status_code})")
            print(f"응답 내용: {response.text}")
            return None
            
    except Exception as e:
        print(f"❗ 오류 발생: {e}")
        return None

# ================= 실행 =================
if __name__ == "__main__":
    token = get_token()["token_id"]
    
    # 예: 10.0.0.0/16 대역의 'my-python-vpc' 생성 (kr1 리전)
    my_vpc_id = create_vpc(token, "my-python-vpc", "10.0.0.0/16", "kr1")
    
    # 다른 리전에 VPC 생성 예시 (kr2 리전)
    # my_vpc_id_kr2 = create_vpc(token, "my-python-vpc-kr2", "10.1.0.0/16", "kr2")