import requests
import json

def get_vpc_details(token: str, vpc_id: str, region_code: str = "kr1"):
    """
    특정 VPC의 상세 정보를 조회하는 함수
    API: GET /v2.0/vpcs/{vpcId}
    """
    NETWORK_API_URL = f"https://{region_code}-api-network-infrastructure.nhncloudservice.com"
    url = f"{NETWORK_API_URL}/v2.0/vpcs/{vpc_id}"
    
    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 4xx or 5xx 에러 발생 시 예외 처리
        
        if response.status_code == 200:
            vpc_details = response.json().get('vpc', {})
            print(f"✅ VPC 상세 정보 조회 성공 (ID: {vpc_id})")
            return vpc_details
        else:
            print(f"❌ VPC 상세 정보 조회 실패 (Status: {response.status_code})")
            print(f"응답 내용: {response.text}")
            return None
            
    except requests.exceptions.HTTPError as http_err:
        print(f"❗ HTTP 오류 발생: {http_err}")
        print(f"응답 내용: {response.text}")
        return None
    except Exception as e:
        print(f"❗ 오류 발생: {e}")
        return None

if __name__ == '__main__':
    from get_token import get_token
    from config import tenant_id # Import tenant_id for example usage

    # 이 스크립트를 직접 실행할 때 필요한 설정
    # 1. 토큰 가져오기
    auth_token = get_token()["token_id"]
    
    # 2. 조회할 VPC ID (실제 존재하는 VPC ID로 변경해야 합니다)
    # config.py의 VPC 이름으로 생성된 VPC를 가정하고 조회
    print("⚠️ 실제 테스트를 위해서는 유효한 VPC ID가 필요합니다.")
    # 예시: main.py를 통해 VPC를 먼저 생성하고, 그 ID를 여기에 입력하세요.
    example_vpc_id = "YOUR_CREATED_VPC_ID_HERE" 

    if auth_token and example_vpc_id != "YOUR_CREATED_VPC_ID_HERE":
        details = get_vpc_details(auth_token, example_vpc_id)
        if details:
            print("--- VPC 상세 정보 ---")
            print(json.dumps(details, indent=4))
            
            # 서브넷 라우팅 테이블 ID 추출 예시
            subnets = details.get('subnets', [])
            if subnets:
                first_subnet_routing_table_id = subnets[0].get('routingtable', {}).get('id')
                if first_subnet_routing_table_id:
                    print(f"✨ 첫 번째 서브넷의 라우팅 테이블 ID: {first_subnet_routing_table_id}")
                else:
                    print("⚠️ 첫 번째 서브넷의 라우팅 테이블 ID를 찾을 수 없습니다.")
            else:
                print("⚠️ VPC에 서브넷이 없습니다.")
    else:
        print("인증 토큰을 가져오거나 조회할 VPC ID를 설정해야 합니다.")
