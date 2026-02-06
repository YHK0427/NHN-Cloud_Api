import requests
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

def main():
    # --- Configuration ---
    region_code = "kr1"
    tenant_id = "0cc0040eaa0044bc99f8a7f4bedc233b" # Replace with your actual Tenant ID

    # VPC and Subnet
    vpc_name = "my-python-vpc"
    vpc_cidr = "10.0.0.0/16"
    subnet_name = "my-python-subnet"
    subnet_cidr = "10.0.1.0/24" # Must be within VPC CIDR

    # Security Group and Rules
    sg_name = "my-python-sg"
    sg_description = "Security group for web server and SSH access"
    my_ip_for_ssh = "1.231.165.73/32" # e.g., "203.0.113.1/32" or "0.0.0.0/0" for testing

    # Instance Configuration
    instance_name = "my-web-instance"
    image_ref = "7342b6e2-74d6-4d2c-a65c-90242d1ee218" # Ubuntu Server 24.04.3 LTS - Container (2025.11.18)
    key_name = "yh_vm" # User to choose from listed key pairs
    
    # Floating IP Configuration (floating_network_id will be retrieved automatically)

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


    print("--- Starting Network Resource Orchestration ---")
    
    # --- 1. Get Token ---
    auth_token = get_token()["token_id"]
    if not auth_token:
        print("🚨 인증 토큰을 가져오지 못했습니다. 스크립트를 종료합니다.")
        return

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

    # --- 4. Create Security Group ---
    print(f"\nAttempting to create Security Group '{sg_name}'...")
    security_group_id = create_security_group(auth_token, sg_name, sg_description, region_code)
    if not security_group_id:
        print(f"🚨 Security Group '{sg_name}' 생성 실패. 스크립트를 종료합니다.")
        return
    print(f"✅ Security Group '{sg_name}' 생성 성공. ID: {security_group_id}")

    # --- 5. Add Security Group Rules ---
    # HTTP (80) Rule
    print("\n--- Adding HTTP (Port 80) Ingress Rule ---")
    rule_http_id = create_security_group_rule(
        auth_token,
        security_group_id,
        direction="ingress",
        protocol="tcp",
        port_range_min=80,
        port_range_max=80,
        remote_ip_prefix="1.231.165.73", # Allow from anywhere
        description="Allow HTTP access",
        region_code=region_code
    )
    if rule_http_id:
        print(f"✅ HTTP Ingress Rule 생성 성공. ID: {rule_http_id}")
    else:
        print("🚨 HTTP Ingress Rule 생성 실패.")

    # SSH (22) Rule
    if my_ip_for_ssh == "YOUR_PUBLIC_IP_CIDR_HERE":
        print("\n⚠️ 경고: 'my_ip_for_ssh'를 실제 공인 IP/CIDR로 변경해야 SSH 규칙을 생성할 수 있습니다.")
        print("    SSH 규칙 생성 단계를 건너뜁니다.")
    else:
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
    '''
    # --- 6. List Key Pairs ---
    print("\n--- Listing Available Key Pairs ---")
    if tenant_id == ".": # Check for placeholder tenant_id
        print("\n⚠️ 경고: 'tenant_id'를 실제 테넌트 ID로 변경해야 키페어 목록을 정확히 조회할 수 있습니다.")
        print("    키페어 목록 조회 단계를 건너뜁니다.")
        key_pairs = []
    else:
        key_pairs = list_key_pairs(auth_token, tenant_id, region_code)
        if key_pairs:
            print("✨ 사용 가능한 키페어:")
            for kp in key_pairs:
                print(f"  - 이름: {kp['name']}, 지문: {kp['fingerprint']}")
        else:
            print("🚨 키페어 목록 조회 실패 또는 사용 가능한 키페어가 없습니다.")
            
'''

    # --- 7. List Flavors & Select Lowest Spec ---
    print("\n--- Listing Available Flavors (Instance Types) ---")
    selected_flavor_id = None
    if tenant_id == ".": # Check for placeholder tenant_id
        print("\n⚠️ 경고: 'tenant_id'를 실제 테넌트 ID로 변경해야 플레이버 목록을 정확히 조회할 수 있습니다.")
        print("    플레이버 목록 조회 단계를 건너뜁니다.")
    else:
        flavors = list_flavors(auth_token, tenant_id, region_code)
        if flavors:
            # Sort by name to get 'm2.c1m2' or a similar lowest spec alphabetically first if multiple exist
            flavors_sorted = sorted(flavors, key=lambda f: f['name']) 
            
            # Try to find m2.c1m2 specifically
            for f in flavors_sorted:
                if f['name'] == "m2.c1m2":
                    selected_flavor_id = f['id']
                    print(f"✅ 'm2.c1m2' 플레이버 ID를 찾았습니다: {selected_flavor_id}")
                    break
            
            # If m2.c1m2 not found, pick the first (smallest spec by common naming conventions)
            if not selected_flavor_id and flavors_sorted:
                selected_flavor_id = flavors_sorted[0]['id']
                print(f"✅ 'm2.c1m2' 플레이버를 찾지 못하여, 가장 낮은 스펙으로 추정되는 플레이버 '{flavors_sorted[0]['name']}'을 선택합니다. ID: {selected_flavor_id}")
            elif not selected_flavor_id:
                print("\n🚨 플레이버 목록 조회는 성공했으나, 적절한 플레이버를 찾지 못했습니다.")
        else:
            print("🚨 플레이버 목록 조회 실패 또는 사용 가능한 플레이버가 없습니다.")


    print("\n--- Network Resource Orchestration Complete ---")
    
    # --- 8. Create Instance (Conditional) ---
    instance_id = None
    instance_port_id = None
    if selected_flavor_id and vpc_id and subnet_id and security_group_id and key_name != "YOUR_KEYPAIR_NAME_HERE" and tenant_id != ".":
        print("\n--- Attempting to Create Instance ---")
        instance_id, instance_port_id = create_instance(
            auth_token,
            tenant_id,
            instance_name,
            key_name,
            image_ref,
            selected_flavor_id,
            subnet_id, # Use subnet_id for network connection
            [sg_name], # Pass security group name for the instance
            nginx_user_data_script,
            region_code=region_code,
            volume_size=30
        )
        if instance_id and instance_port_id:
            print(f"✅ 인스턴스 '{instance_name}' 생성 및 활성화 성공. ID: {instance_id}, 포트 ID: {instance_port_id}")
        else:
            print(f"🚨 인스턴스 '{instance_name}' 생성 실패.")
    else:
        print("\n⚠️ 인스턴스 생성 전 필수 설정 (tenant_id, key_name)을 완료해야 합니다. 인스턴스 생성을 건너뜁니다.")

    # --- 9. Get Floating Network ID ---
    floating_network_id = None
    if tenant_id != ".": # Check for placeholder tenant_id
        print("\n--- Attempting to Get External Network ID for Floating IP ---")
        floating_network_id = get_external_network_id(auth_token, region_code)
        if floating_network_id:
            print(f"✅ 외부 네트워크 ID를 성공적으로 조회했습니다: {floating_network_id}")
        else:
            print("🚨 외부 네트워크 ID 조회 실패. 플로팅 IP를 생성할 수 없습니다.")
    else:
        print("\n⚠️ 'tenant_id'를 실제 테넌트 ID로 변경해야 외부 네트워크 ID를 조회할 수 있습니다. 플로팅 IP 생성을 건너뜁니다.")

    # --- 10. Create Floating IP (Conditional) ---
    floating_ip_id = None
    floating_ip_address = None
    if instance_id and instance_port_id and floating_network_id and tenant_id != ".":
        print("\n--- Attempting to Create Floating IP ---")
        fip_data = create_floating_ip(
            auth_token,
            floating_network_id,
            region_code=region_code
        )
        if fip_data:
            floating_ip_id = fip_data['id']
            floating_ip_address = fip_data['ip_address']
            print(f"✅ 플로팅 IP '{floating_ip_address}' 생성 성공. ID: {floating_ip_id}")
        else:
            print("🚨 플로팅 IP 생성 실패.")
    else:
        print("\n⚠️ 플로팅 IP 생성 전 필수 설정 (instance_id, instance_port_id, floating_network_id, tenant_id)을 완료해야 합니다. 플로팅 IP 생성을 건너뜁니다.")

    # --- 11. Associate Floating IP (Conditional) ---
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
        print("\n⚠️ 플로팅 IP 연결 전 필수 설정 (floating_ip_id, instance_port_id)을 완료해야 합니다. 플로팅 IP 연결을 건너뜁니다.")
    
    print("\n--- Orchestration Final Summary ---")
    if floating_ip_address:
        print(f"✨ 웹 서버에 접속할 수 있는 플로팅 IP 주소: http://{floating_ip_address}")
        print("✨ 잠시 후 Nginx 설치가 완료되면 해당 주소로 접속 가능합니다.")
    else:
        print("🚨 플로팅 IP가 할당되지 않아 웹 서버에 외부에서 접속할 수 없습니다.")
    print("\n--- 모든 작업 완료 ---")


if __name__ == "__main__":
    main()
