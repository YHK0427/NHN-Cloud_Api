# examples/provision_web_server.py

import sys
import os
import base64
from dotenv import load_dotenv

# 프로젝트 루트 디렉토리를 Python Path에 추가합니다.
# 이렇게 하면 어느 디렉토리에서 스크립트를 실행하든 nhn_api_module을 올바르게 임포트할 수 있습니다.
# 예를 들어, `nhn_api/examples/provision_web_server.py`가 실행되면
# `nhn_api` 디렉토리가 sys.path에 추가됩니다.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

# .env 파일의 위치를 명시적으로 지정하여 로드합니다.
# 프로젝트 루트에 있는 .env 파일을 사용합니다.
dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path=dotenv_path)


# nhn_api_module에서 필요한 함수들을 임포트합니다.
from nhn_api_module.auth import get_token
from nhn_api_module.networking import (
    create_vpc,
    create_vpc_subnet,
    get_vpc_details,
    get_external_network_id,
    create_internet_gateway,
    attach_gateway_to_routing_table,
    create_floating_ip,
    associate_floating_ip
)
from nhn_api_module.compute import (
    create_instance,
    list_flavors,
    list_key_pairs
)
from nhn_api_module.security import (
    create_security_group,
    create_security_group_rule
)

def main():
    """
    NHN Cloud에 웹 서버 환경을 프로비저닝하는 전체 과정을 실행합니다.
    """
    # .env 파일에서 환경 변수 로드
    load_dotenv()

    # --- 1. 환경 변수 및 설정 불러오기 ---
    print("--- 1. 환경 변수 및 설정 불러오기 ---")
    
    # 민감 정보 로드
    tenant_id = os.getenv("TENANT_ID")
    my_ip_for_ssh = os.getenv("MY_IP_FOR_SSH")
    key_name = os.getenv("KEY_NAME")

    if not all([tenant_id, my_ip_for_ssh, key_name]):
        print("🚨 오류: .env 파일에 필요한 환경 변수(TENANT_ID, MY_IP_FOR_SSH, KEY_NAME)가 설정되지 않았습니다.")
        print("   .env.example 파일을 .env로 복사하여 값을 입력해주세요.")
        return
    
    # 예제용 설정 (필요시 수정 가능)
    region_code = "kr1"
    vpc_name = "my-python-vpc"
    vpc_cidr = "10.0.0.0/16"
    subnet_name = "my-python-subnet"
    subnet_cidr = "10.0.1.0/24"
    sg_name = "my-python-sg"
    sg_description = "웹 서버 및 SSH 접속을 위한 보안 그룹"
    instance_name = "my-web-instance"
    image_ref = "7342b6e2-74d6-4d2c-a65c-90242d1ee218" # Ubuntu Server 24.04
    volume_size = 30
    
    # Nginx 설치 User Data 스크립트
    try:
        # 프로젝트 루트에 있는 index.html 파일을 읽어옵니다.
        with open(os.path.join(project_root, 'index.html'), 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print("🚨 오류: 프로젝트 루트에 index.html 파일이 없습니다. 스크립트를 중단합니다.")
        return
        
    encoded_html = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
    nginx_user_data_script = f"""#!/bin/bash
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1
apt-get update
apt-get install -y nginx
echo "{encoded_html}" | base64 -d > /var/www/html/index.html
systemctl enable nginx
systemctl restart nginx
"""
    print("✅ 설정 로드 완료")


    # --- 2. 인증 토큰 발급 ---
    print("--- 2. 인증 토큰 발급 ---")
    token_data = get_token()
    if not token_data:
        return
    auth_token = token_data["token_id"]


    # --- 3. VPC 생성 ---
    print(f"--- 3. VPC '{vpc_name}' 생성 ---")
    vpc_id = create_vpc(auth_token, vpc_name, vpc_cidr, region_code)
    if not vpc_id:
        print(f"🚨 VPC 생성에 실패하여 스크립트를 중단합니다.")
        return


    # --- 4. 서브넷 생성 ---
    print(f"--- 4. 서브넷 '{subnet_name}' 생성 ---")
    subnet_id = create_vpc_subnet(auth_token, vpc_id, subnet_name, subnet_cidr, region_code)
    if not subnet_id:
        print(f"🚨 서브넷 생성에 실패하여 스크립트를 중단합니다.")
        return

    
    # --- 5. 인터넷 게이트웨이 설정 ---
    print("--- 5. 인터넷 게이트웨이 설정 ---")
    
    # 5-1. 라우팅 테이블 ID 조회
    vpc_details = get_vpc_details(auth_token, vpc_id, region_code)
    routing_table_id = None
    if vpc_details and vpc_details.get('subnets'):
        routing_table_id = vpc_details['subnets'][0].get('routingtable', {}).get('id')
    
    if not routing_table_id:
        print(f"🚨 라우팅 테이블 ID를 찾지 못해 스크립트를 중단합니다.")
        return

    # 5-2. 외부 네트워크 ID 조회
    external_network_id = get_external_network_id(auth_token, region_code)
    if not external_network_id:
        print("🚨 외부 네트워크 ID를 찾지 못해 스크립트를 중단합니다.")
        return

    # 5-3. 인터넷 게이트웨이 생성
    ig_name = f"{vpc_name}-igw"
    internet_gateway_id = create_internet_gateway(auth_token, ig_name, external_network_id, region_code)
    if not internet_gateway_id:
        print(f"🚨 인터넷 게이트웨이 생성에 실패하여 스크립트를 중단합니다.")
        return

    # 5-4. 라우팅 테이블에 게이트웨이 연결
    attached = attach_gateway_to_routing_table(auth_token, routing_table_id, internet_gateway_id, region_code)
    if not attached:
        print(f"🚨 인터넷 게이트웨이를 라우팅 테이블에 연결하는 데 실패하여 스크립트를 중단합니다.")
        return
    print("✅ 인터넷 게이트웨이 설정 완료")


    # --- 6. 보안 그룹 및 규칙 생성 ---
    print(f"--- 6. 보안 그룹 '{sg_name}' 생성 및 규칙 추가 ---")
    security_group_id = create_security_group(auth_token, sg_name, sg_description, region_code)
    if not security_group_id:
        print(f"🚨 보안 그룹 생성에 실패하여 스크립트를 중단합니다.")
        return

    # HTTP 규칙
    create_security_group_rule(
        auth_token, security_group_id, "ingress", "tcp", 80, 80, my_ip_for_ssh, "HTTP 허용"
    )
    # SSH 규칙
    create_security_group_rule(
        auth_token, security_group_id, "ingress", "tcp", 22, 22, my_ip_for_ssh, "SSH 허용"
    )
    print("✅ 보안 그룹 규칙 추가 완료")


    # --- 7. 인스턴스 사양(Flavor) 선택 ---
    print("--- 7. 인스턴스 사양(Flavor) 선택 ---")
    flavors = list_flavors(auth_token, tenant_id, region_code)
    selected_flavor_id = None
    if flavors:
        # 가장 작은 사양 중 하나인 'u2.c1m2'를 우선 선택
        for f in flavors:
            if f['name'] == "m2.c1m2":
                selected_flavor_id = f['id']
                print(f"✅ 'm2.c1m2' 플레이버를 선택했습니다. (ID: {selected_flavor_id})")
                break
        # 없을 경우 목록의 첫 번째 플레이버 선택
        if not selected_flavor_id and flavors:
            selected_flavor_id = flavors[0]['id']
            print(f"✅ 'm2.c1m2'를 찾지 못해, 목록의 첫 플레이버 '{flavors[0]['name']}'을 선택합니다. (ID: {selected_flavor_id})")
    
    if not selected_flavor_id:
        print("🚨 적절한 플레이버를 찾지 못해 스크립트를 중단합니다.")
        return
    
    
    # --- 8. 인스턴스 생성 ---
    print("--- 8. 인스턴스 생성 ---")
    instance_id, port_id = create_instance(
        auth_token, tenant_id, instance_name, key_name, image_ref,
        selected_flavor_id, subnet_id, [sg_name], nginx_user_data_script,
        volume_size, region_code
    )
    if not instance_id:
        print(f"🚨 인스턴스 생성에 실패하여 스크립트를 중단합니다.")
        return

        
    # --- 9. Floating IP 생성 및 연결 ---
    print("--- 9. Floating IP 생성 및 연결 ---")
    fip_data = create_floating_ip(auth_token, external_network_id, region_code)
    if not fip_data:
        print("🚨 Floating IP 생성에 실패하여 스크립트를 중단합니다.")
        return

    floating_ip_id = fip_data['id']
    floating_ip_address = fip_data['ip_address']

    associated = associate_floating_ip(auth_token, floating_ip_id, port_id, region_code)
    if not associated:
        print("🚨 Floating IP 연결에 실패하여 스크립트를 중단합니다.")
        return
    

    # --- 10. 최종 결과 출력 ---
    print("🎉 모든 리소스 프로비저닝 성공! 🎉")
    print("-----------------------------------------")
    print(f"✅ 웹 서버 접속 주소: http://{floating_ip_address}")
    print(f"✅ SSH 접속: ssh ubuntu@{floating_ip_address}")
    print("-----------------------------------------")
    print("(참고: 인스턴스 부팅 및 Nginx 설치에 약 1~2분 소요될 수 있습니다.)")


if __name__ == "__main__":
    main()
