import requests
import os
from dotenv import load_dotenv
from get_token import get_token
# from get_my_instance import get_my_instance # Not directly used in this orchestration
from create_vpc import create_vpc
from create_vpc_subnet import create_vpc_subnet
from create_security_group import create_security_group
from create_security_group_rule import create_security_group_rule
from list_key_pairs import list_key_pairs
from list_flavors import list_flavors
from create_instance import create_instance # Removed wait_for_instance_active as it's now internal to create_instance
from create_floating_ip import create_floating_ip
from associate_floating_ip import associate_floating_ip
from get_external_network_id import get_external_network_id # New import
from get_vpc_details import get_vpc_details
from create_internet_gateway import create_internet_gateway
from attach_gateway_to_routing_table import attach_gateway_to_routing_table

def main():
    load_dotenv() # Load variables from .env file

    # Import non-sensitive configurations from config.py
    from config import (
        region_code,
        vpc_name, vpc_cidr, subnet_name, subnet_cidr,
        sg_name, sg_description,
        instance_name, image_ref, volume_size,
        nginx_user_data_script
    )

    # Load sensitive data from environment variables
    tenant_id = os.getenv("TENANT_ID")
    my_ip_for_ssh = os.getenv("MY_IP_FOR_SSH")
    key_name = os.getenv("KEY_NAME")

    # --- 0. Validate Environment Variables ---
    if not all([tenant_id, my_ip_for_ssh, key_name]):
        print("🚨 Error: TENANT_ID, MY_IP_FOR_SSH, or KEY_NAME environment variables not set.")
        print("    Please create a .env file from .env.example and fill in your values.")
        return

    print("--- Starting Network Resource Orchestration ---")
    
    # --- 1. Get Token ---
    token_data = get_token()
    if not token_data:
        # get_token() already prints an error, so we can just exit.
        return
    auth_token = token_data["token_id"]

    # --- 2. Create VPC ---
    print(f"\nAttempting to create VPC '{vpc_name}'...")
    vpc_id = create_vpc(auth_token, vpc_name, vpc_cidr, region_code)
    if not vpc_id:
        print(f"🚨 VPC '{vpc_name}' 생성 실패. 스크립트를 종료합니다.")
        return
    print(f"✅ VPC '{vpc_name}' 생성 성공. ID: {vpc_id}")

    # --- 3. Create Subnet ---
    print(f"\nAttempting to create Subnet '{subnet_name}' in VPC '{vpc_name}'...")
    subnet_id = create_vpc_subnet(auth_token, vpc_id, subnet_name, subnet_cidr, region_code)
    if not subnet_id:
        print(f"🚨 Subnet '{subnet_name}' 생성 실패. 스크립트를 종료합니다.")
        return
    print(f"✅ Subnet '{subnet_name}' 생성 성공. ID: {subnet_id}")

    # --- 4. Get VPC Details and Routing Table ID ---
    print(f"\nAttempting to get details for VPC '{vpc_name}' to find Routing Table ID...")
    vpc_details = get_vpc_details(auth_token, vpc_id, region_code)
    routing_table_id = None
    if vpc_details and vpc_details.get('subnets'):
        routing_table_id = vpc_details['subnets'][0].get('routingtable', {}).get('id')
    
    if not routing_table_id:
        print(f"🚨 VPC '{vpc_name}'의 라우팅 테이블 ID를 찾지 못했습니다. 스크립트를 종료합니다.")
        return
    print(f"✅ 라우팅 테이블 ID를 찾았습니다: {routing_table_id}")

    # --- 5. Get External Network ID (for Internet Gateway and Floating IP) ---
    print("\n--- Attempting to Get External Network ID for Internet Gateway and Floating IP ---")
    external_network_id = get_external_network_id(auth_token, region_code)
    if not external_network_id:
        print("🚨 외부 네트워크 ID 조회 실패. 인터넷 게이트웨이 및 플로팅 IP를 생성할 수 없습니다. 스크립트를 종료합니다.")
        return
    print(f"✅ 외부 네트워크 ID를 성공적으로 조회했습니다: {external_network_id}")

    # --- 6. Create Internet Gateway ---
    ig_name = f"{vpc_name}-ig"
    print(f"\nAttempting to create Internet Gateway '{ig_name}'...")
    internet_gateway_id = create_internet_gateway(auth_token, ig_name, external_network_id, region_code)
    if not internet_gateway_id:
        print(f"🚨 인터넷 게이트웨이 '{ig_name}' 생성 실패. 스크립트를 종료합니다.")
        return
    print(f"✅ 인터넷 게이트웨이 '{ig_name}' 생성 성공. ID: {internet_gateway_id}")

    # --- 7. Attach Internet Gateway to Routing Table ---
    print(f"\nAttempting to attach Internet Gateway '{ig_name}' to Routing Table '{routing_table_id}'...")
    attached_ig = attach_gateway_to_routing_table(auth_token, routing_table_id, internet_gateway_id, region_code)
    if not attached_ig:
        print(f"🚨 라우팅 테이블에 인터넷 게이트웨이 연결 실패. 스크립트를 종료합니다.")
        return
    print(f"✅ 인터넷 게이트웨이 '{ig_name}'가 라우팅 테이블 '{routing_table_id}'에 성공적으로 연결되었습니다.")

    # --- 8. Create Security Group ---
    print(f"\nAttempting to create Security Group '{sg_name}'...")
    security_group_id = create_security_group(auth_token, sg_name, sg_description, region_code)
    if not security_group_id:
        print(f"🚨 Security Group '{sg_name}' 생성 실패. 스크립트를 종료합니다.")
        return
    print(f"✅ Security Group '{sg_name}' 생성 성공. ID: {security_group_id}")

    # --- 9. Add Security Group Rules ---
    print("\n--- Adding HTTP (Port 80) Ingress Rule ---")
    rule_http_id = create_security_group_rule(
        auth_token,
        security_group_id,
        direction="ingress",
        protocol="tcp",
        port_range_min=80,
        port_range_max=80,
        remote_ip_prefix=my_ip_for_ssh.split('/')[0],
        description="Allow HTTP access",
        region_code=region_code
    )
    if rule_http_id:
        print(f"✅ HTTP Ingress Rule 생성 성공. ID: {rule_http_id}")
    else:
        print("🚨 HTTP Ingress Rule 생성 실패.")

    print("\n--- Adding SSH (Port 22) Ingress Rule ---")
    rule_ssh_id = create_security_group_rule(
        auth_token,
        security_group_id,
        direction="ingress",
        protocol="tcp",
        port_range_min=22,
        port_range_max=22,
        remote_ip_prefix=my_ip_for_ssh,
        description="Allow SSH access from specified IP",
        region_code=region_code
    )
    if rule_ssh_id:
        print(f"✅ SSH Ingress Rule 생성 성공. ID: {rule_ssh_id}")
    else:
        print("🚨 SSH Ingress Rule 생성 실패.")

    # --- 10. List Flavors & Select Lowest Spec ---
    print("\n--- Listing Available Flavors (Instance Types) ---")
    flavors = list_flavors(auth_token, tenant_id, region_code)
    selected_flavor_id = None
    if flavors:
        flavors_sorted = sorted(flavors, key=lambda f: f['name']) 
        for f in flavors_sorted:
            if f['name'] == "m2.c1m2":
                selected_flavor_id = f['id']
                print(f"✅ 'm2.c1m2' 플레이버 ID를 찾았습니다: {selected_flavor_id}")
                break
        
        if not selected_flavor_id and flavors_sorted:
            selected_flavor_id = flavors_sorted[0]['id']
            print(f"✅ 'm2.c1m2' 플레이버를 찾지 못하여, 가장 낮은 스펙으로 추정되는 플레이버 '{flavors_sorted[0]['name']}'을 선택합니다. ID: {selected_flavor_id}")
        elif not selected_flavor_id:
            print("\n🚨 플레이버 목록 조회는 성공했으나, 적절한 플레이버를 찾지 못했습니다.")
    else:
        print("🚨 플레이버 목록 조회 실패 또는 사용 가능한 플레이버가 없습니다.")

    print("\n--- Network Resource Orchestration Complete ---")
    
    # --- 11. Create Instance (Conditional) ---
    instance_id = None
    instance_port_id = None
    if selected_flavor_id and vpc_id and subnet_id and security_group_id:
        print("\n--- Attempting to Create Instance ---")
        instance_id, instance_port_id = create_instance(
            auth_token,
            tenant_id,
            instance_name,
            key_name,
            image_ref,
            selected_flavor_id,
            subnet_id,
            [sg_name],
            nginx_user_data_script,
            region_code=region_code,
            volume_size=volume_size
        )
        if instance_id and instance_port_id:
            print(f"✅ 인스턴스 '{instance_name}' 생성 및 활성화 성공. ID: {instance_id}, 포트 ID: {instance_port_id}")
        else:
            print(f"🚨 인스턴스 '{instance_name}' 생성 실패.")
    else:
        print("\n⚠️ 인스턴스 생성에 필요한 리소스(Flavor, VPC, Subnet, Security Group)가 준비되지 않았습니다. 인스턴스 생성을 건너뜁니다.")

    # --- 12. Create Floating IP (Conditional) ---
    floating_ip_id = None
    floating_ip_address = None
    if instance_id and instance_port_id and external_network_id:
        print("\n--- Attempting to Create Floating IP ---")
        fip_data = create_floating_ip(
            auth_token,
            external_network_id,
            region_code=region_code
        )
        if fip_data:
            floating_ip_id = fip_data['id']
            floating_ip_address = fip_data['ip_address']
            print(f"✅ 플로팅 IP '{floating_ip_address}' 생성 성공. ID: {floating_ip_id}")
        else:
            print("🚨 플로팅 IP 생성 실패.")
    else:
        print("\n⚠️ 플로팅 IP 생성에 필요한 리소스(Instance, Port, External Network)가 준비되지 않았습니다. 플로팅 IP 생성을 건너뜁니다.")

    # --- 13. Associate Floating IP (Conditional) ---
    if floating_ip_id and instance_port_id:
        print(f"\n--- Attempting to Associate Floating IP '{floating_ip_address}' with Instance Port '{instance_port_id}' ---")
        associated = associate_floating_ip(
            auth_token,
            floating_ip_id,
            instance_port_id,
            region_code=region_code
        )
        if associated:
            print(f"✅ 플로팅 IP '{floating_ip_address}'가 인스턴스에 성공적으로 연결되었습니다.")
        else:
            print("🚨 플로팅 IP 연결 실패.")
    else:
        print("\n⚠️ 플로팅 IP 연결에 필요한 리소스(Floating IP, Instance Port)가 준비되지 않았습니다. 플로팅 IP 연결을 건너뜁니다.")
    
    print("\n--- Orchestration Final Summary ---")
    if floating_ip_address:
        print(f"✨ 웹 서버에 접속할 수 있는 플로팅 IP 주소: http://{floating_ip_address}")
        print("✨ 잠시 후 Nginx 설치가 완료되면 해당 주소로 접속 가능합니다.")
    else:
        print("🚨 플로팅 IP가 할당되지 않아 웹 서버에 외부에서 접속할 수 없습니다.")
    print("\n--- 모든 작업 완료 ---")


if __name__ == "__main__":
    main()
