import requests
import json
import base64
import time
from get_token import get_token

def create_instance(
    token: str,
    tenant_id: str,
    instance_name: str,
    key_name: str,
    image_ref: str,
    flavor_ref: str,
    network_id: str,
    security_group_names: list,
    user_data: str,
    volume_size: int = 20, # Linux default is 10GB
    region_code: str = "kr1"
):
    """
    인스턴스를 생성하는 함수
    API: POST /v2/{tenantId}/servers
    """
    COMPUTE_API_URL = f"https://{region_code}-api-instance-infrastructure.nhncloudservice.com"
    url = f"{COMPUTE_API_URL}/v2/{tenant_id}/servers"

    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }
    
    # User data must be base64 encoded
    encoded_user_data = base64.b64encode(user_data.encode('utf-8')).decode('utf-8')

    payload = {
        "server": {
            "name": instance_name,
            "key_name": key_name,
            "flavorRef": flavor_ref,
            "networks": [{"subnet": network_id}],
            "security_groups": [{"name": sg_name} for sg_name in security_group_names],
            "user_data": encoded_user_data,
            "block_device_mapping_v2": [
                {
                    "boot_index": 0,
                    "source_type": "image",
                    "uuid": image_ref,            # ✅ 여기에 Ubuntu 24.04 ID가 들어갑니다!
                    "volume_size": volume_size,
                    "destination_type": "volume",
                    "delete_on_termination": True,
                }
            ],
            "min_count": 1,
            "max_count": 1
        }
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()

        if response.status_code == 202: # 202 Accepted is the typical response for async creation
            server_info = response.json().get('server', {})
            instance_id = server_info.get('id')
            print(f"✅ 인스턴스 생성 요청 성공! (Region: {region_code})")
            print(f" - 이름: {instance_name}")
            print(f" - ID: {instance_id}")
            print(" - 상태: BUILDING (상태가 ACTIVE가 될 때까지 대기합니다...)")
            active_server_info = wait_for_instance_active(token, tenant_id, instance_id, region_code)
            
            if active_server_info:
                # 2. [수정 포인트] 별도 API를 통해 port_id를 확실하게 가져옴
                print("🔍 인스턴스 포트 정보를 조회합니다...")
                port_id = get_port_id_by_instance(token, instance_id, region_code)
                
                return instance_id, port_id

            else:
                print("🚨 인스턴스가 ACTIVE 상태가 되는 것을 기다리다 타임아웃되었습니다.")
                return None, None
        else:
            print(f"❌ 인스턴스 생성 요청 실패 (Status: {response.status_code})")
            print(f"응답 내용: {response.text}")
            return None, None

    except requests.exceptions.HTTPError as http_err:
        print(f"❗ HTTP 오류 발생: {http_err}")
        print(f"응답 내용: {response.text}")
        return None, None
    except Exception as e:
        print(f"❗ 오류 발생: {e}")
        return None, None

def wait_for_instance_active(token: str, tenant_id: str, instance_id: str, region_code: str, timeout_seconds: int = 600, poll_interval: int = 10):
    """
    인스턴스가 ACTIVE 상태가 될 때까지 폴링하는 함수
    성공 시 전체 서버 정보 객체를 반환하며, 실패 시 None을 반환합니다.
    """
    COMPUTE_API_URL = f"https://{region_code}-api-instance-infrastructure.nhncloudservice.com"
    url = f"{COMPUTE_API_URL}/v2/{tenant_id}/servers/{instance_id}"
    
    headers = {"X-Auth-Token": token}
    
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            server_info = response.json().get('server', {})
            server_status = server_info.get('status')
            
            if server_status == 'ACTIVE':
                print("✅ 인스턴스가 ACTIVE 상태가 되었습니다.")
                return server_info # Return full server info
            elif server_status == 'ERROR':
                print(f"❌ 인스턴스 생성 중 오류 발생. 상태: {server_status}")
                return None
            else:
                print(f" - 현재 상태: {server_status}... ({int(time.time() - start_time)}초 경과)")
            
            time.sleep(poll_interval)
            
        except requests.exceptions.HTTPError as http_err:
            print(f"❗ 인스턴스 상태 조회 중 HTTP 오류 발생: {http_err}")
            time.sleep(poll_interval)
        except Exception as e:
            print(f"❗ 인스턴스 상태 조회 중 오류 발생: {e}")
            return None
            
    print(f"❌ 인스턴스가 {timeout_seconds}초 안에 ACTIVE 상태가 되지 않아 타임아웃되었습니다.")
    return None

def get_port_id_by_instance(token, instance_id, region_code="kr1"):
    """
    인스턴스 ID를 사용하여 해당 인스턴스에 할당된 네트워크 포트 ID를 조회합니다.
    """
    NETWORK_API_URL = f"https://{region_code}-api-network-infrastructure.nhncloudservice.com"
    # device_id 쿼리 파라미터를 사용하여 인스턴스에 연결된 포트만 필터링
    url = f"{NETWORK_API_URL}/v2.0/ports?device_id={instance_id}"
    
    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        ports = response.json().get('ports', [])
        
        if ports:
            # 일반적으로 인스턴스 생성 시 포트가 하나 생성되므로 첫 번째 요소를 반환
            port_id = ports[0].get('id')
            print(f"🔍 포트 조회 성공 (Instance ID: {instance_id} -> Port ID: {port_id})")
            return port_id
        else:
            print(f"🚨 인스턴스 {instance_id}에 연결된 포트를 찾을 수 없습니다.")
            return None
    except Exception as e:
        print(f"🚨 포트 조회 중 오류 발생: {e}")
        return None


if __name__ == "__main__":
    # Nginx 설치 User Data 스크립트
    nginx_user_data_script = """#!/bin/bash
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1
echo "🚀 [Start] Ubuntu 24.04 Nginx Setup"
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y nginx
cat <<EOF > /var/www/html/index.html
<!DOCTYPE html>
<html>
<head><title>Ubuntu 24.04 Server</title></head>
<body><h1>🦊 Hello, Ubuntu 24.04!</h1><p>NHN Cloud API로 자동 생성된 웹 서버입니다.</p></body>
</html>
EOF
systemctl enable nginx
systemctl restart nginx
echo "✅ [Finish] Nginx Setup Complete"
"""

    # --- 설정 값 (실제 값으로 변경 필요) ---
    # 1. 토큰 가져오기
    auth_token = get_token()["token_id"]
    
    # 2. 테넌트 ID
    example_tenant_id = "0cc0040eaa0044bc99f8a7f4bedc233b"
    
    # 3. 인스턴스 설정
    example_instance_name = "my-web-instance"
    example_key_name = "YOUR_KEYPAIR_NAME_HERE" # list_key_pairs.py로 확인한 키페어 이름
    example_image_ref = "YOUR_UBUNTU_24_04_IMAGE_ID_HERE" # NHN Cloud 콘솔에서 Ubuntu 24.04 이미지 ID 확인
    example_flavor_ref = "u2.c1m1" # 예시 인스턴스 타입 ID
    example_network_id = "YOUR_VPC_NETWORK_ID_HERE" # create_vpc.py로 생성된 VPC ID
    example_security_group_names = ["YOUR_SECURITY_GROUP_NAME_HERE"] # create_security_group.py로 생성된 보안 그룹 이름

    if "YOUR_" in example_key_name or "YOUR_" in example_image_ref or "YOUR_" in example_network_id or "YOUR_" in example_security_group_names[0]:
        print("⚠️ 경고: 예제 코드의 'YOUR_...' 값들을 실제 환경에 맞게 변경해주세요.")
        print("    - key_name: 'list_key_pairs.py'로 확인한 키페어 이름")
        print("    - image_ref: NHN Cloud 콘솔에서 'Ubuntu 24.04' 이미지 ID")
        print("    - network_id: 'create_vpc.py'로 생성된 VPC ID")
        print("    - security_group_names: 'create_security_group.py'로 생성된 보안 그룹 이름")
    else:
        created_instance_id, created_port_id = create_instance(
            auth_token,
            example_tenant_id,
            example_instance_name,
            example_key_name,
            example_image_ref,
            example_flavor_ref,
            example_network_id,
            example_security_group_names,
            nginx_user_data_script
        )
        if created_instance_id:
            print(f"✨ 최종적으로 생성된 인스턴스 ID: {created_instance_id}, 포트 ID: {created_port_id}")
        else:
            print("🚨 인스턴스 생성에 실패했습니다.")

