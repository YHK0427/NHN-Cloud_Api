# nhn_api_module/compute.py

"""
NHN Cloud 컴퓨트 관련 API를 호출하는 함수들을 모아놓은 모듈입니다.
- 인스턴스 (서버)
- 플레이버 (인스턴스 타입)
- 키페어
"""

import requests
import json
import base64
import time

# --- Instance ---

def create_instance(
    token: str,
    tenant_id: str,
    instance_name: str,
    key_name: str,
    image_ref: str,
    flavor_ref: str,
    subnet_id: str,
    security_group_names: list,
    user_data: str,
    volume_size: int = 30,
    region_code: str = "kr1"
):
    """
    인스턴스를 생성합니다.

    :param token: 인증 토큰
    :param tenant_id: 테넌트 ID
    :param instance_name: 생성할 인스턴스의 이름
    :param key_name: 사용할 키페어의 이름
    :param image_ref: 사용할 이미지의 ID
    :param flavor_ref: 사용할 플레이버의 ID
    :param subnet_id: 연결할 서브넷의 ID
    :param security_group_names: 적용할 보안 그룹 이름의 리스트
    :param user_data: 인스턴스 시작 시 실행할 스크립트
    :param volume_size: 부트 볼륨의 크기 (GB)
    :param region_code: 리전 코드
    :return: 성공 시 (인스턴스 ID, 포트 ID) 튜플, 실패 시 (None, None)
    """
    COMPUTE_API_URL = f"https://{region_code}-api-instance-infrastructure.nhncloudservice.com"
    url = f"{COMPUTE_API_URL}/v2/{tenant_id}/servers"

    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }
    
    encoded_user_data = base64.b64encode(user_data.encode('utf-8')).decode('utf-8')

    payload = {
        "server": {
            "name": instance_name,
            "key_name": key_name,
            "flavorRef": flavor_ref,
            "networks": [{"subnet": subnet_id}],
            "security_groups": [{"name": sg_name} for sg_name in security_group_names],
            "user_data": encoded_user_data,
            "block_device_mapping_v2": [
                {
                    "boot_index": 0,
                    "source_type": "image",
                    "uuid": image_ref,
                    "volume_size": volume_size,
                    "destination_type": "volume",
                    "delete_on_termination": True,
                }
            ]
        }
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()

        server_info = response.json().get('server', {})
        instance_id = server_info.get('id')
        print(f"✅ 인스턴스 생성 요청 성공 (ID: {instance_id})")
        print(" - 상태: BUILDING (ACTIVE 상태가 될 때까지 대기합니다...)")
        
        active_server_info = _wait_for_instance_active(token, tenant_id, instance_id, region_code)
        
        if active_server_info:
            port_id = _get_port_id_by_instance(token, instance_id, region_code)
            if port_id:
                return instance_id, port_id
            else:
                print("🚨 인스턴스 생성 후 포트 ID를 조회하는 데 실패했습니다.")
                return instance_id, None
        else:
            print("🚨 인스턴스가 ACTIVE 상태가 되는 것을 기다리다 타임아웃되었습니다.")
            return None, None

    except requests.exceptions.HTTPError as http_err:
        print(f"❗ 인스턴스 생성 중 HTTP 오류 발생: {http_err}")
        print(f"    응답 내용: {http_err.response.text}")
        return None, None
    except Exception as e:
        print(f"❗ 인스턴스 생성 중 예상치 못한 오류 발생: {e}")
        return None, None

def _wait_for_instance_active(token: str, tenant_id: str, instance_id: str, region_code: str, timeout_seconds: int = 600, poll_interval: int = 10):
    """
    (내부 함수) 인스턴스가 ACTIVE 상태가 될 때까지 폴링합니다.
    성공 시 전체 서버 정보 객체를 반환합니다.
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
                return server_info
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

def _get_port_id_by_instance(token, instance_id, region_code="kr1"):
    """
    (내부 함수) 인스턴스 ID를 사용하여 네트워크 포트 ID를 조회합니다.
    """
    NETWORK_API_URL = f"https://{region_code}-api-network-infrastructure.nhncloudservice.com"
    url = f"{NETWORK_API_URL}/v2.0/ports?device_id={instance_id}"
    headers = {"X-Auth-Token": token}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        ports = response.json().get('ports', [])
        
        if ports:
            port_id = ports[0].get('id')
            print(f"✅ 인스턴스 포트 ID 조회 성공: {port_id}")
            return port_id
        else:
            print(f"🚨 인스턴스 '{instance_id}'에 연결된 포트를 찾을 수 없습니다.")
            return None
    except Exception as e:
        print(f"🚨 포트 ID 조회 중 오류 발생: {e}")
        return None

# --- Flavor ---

def list_flavors(token: str, tenant_id: str, region_code: str = "kr1"):
    """
    인스턴스 타입(플레이버) 목록을 조회합니다.

    :param token: 인증 토큰
    :param tenant_id: 테넌트 ID
    :param region_code: 리전 코드
    :return: 성공 시 플레이버 정보(id, name)가 담긴 dict의 리스트, 실패 시 None
    """
    COMPUTE_API_URL = f"https://{region_code}-api-instance-infrastructure.nhncloudservice.com"
    url = f"{COMPUTE_API_URL}/v2/{tenant_id}/flavors"
    headers = {"X-Auth-Token": token}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        flavors_data = response.json().get('flavors', [])
        print(f"✅ 플레이버 목록 조회 성공 (Region: {region_code})")
        
        return [{"id": f.get('id'), "name": f.get('name')} for f in flavors_data]

    except requests.exceptions.HTTPError as http_err:
        print(f"❗ 플레이버 목록 조회 중 HTTP 오류 발생: {http_err}")
        print(f"    응답 내용: {http_err.response.text}")
        return None
    except Exception as e:
        print(f"❗ 플레이버 목록 조회 중 예상치 못한 오류 발생: {e}")
        return None

# --- Key Pair ---

def list_key_pairs(token: str, tenant_id: str, region_code: str = "kr1"):
    """
    키페어 목록을 조회합니다.

    :param token: 인증 토큰
    :param tenant_id: 테넌트 ID
    :param region_code: 리전 코드
    :return: 성공 시 키페어 정보(name, fingerprint)가 담긴 dict의 리스트, 실패 시 None
    """
    COMPUTE_API_URL = f"https://{region_code}-api-compute-infrastructure.nhncloudservice.com"
    url = f"{COMPUTE_API_URL}/v2/{tenant_id}/os-keypairs"
    headers = {"X-Auth-Token": token}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        keypairs_data = response.json().get('keypairs', [])
        print(f"✅ 키페어 목록 조회 성공 (Region: {region_code})")

        key_pair_list = []
        for kp in keypairs_data:
            keypair_info = kp.get('keypair', {})
            key_pair_list.append({
                "name": keypair_info.get('name'),
                "fingerprint": keypair_info.get('fingerprint')
            })
        return key_pair_list

    except requests.exceptions.HTTPError as http_err:
        print(f"❗ 키페어 목록 조회 중 HTTP 오류 발생: {http_err}")
        print(f"    응답 내용: {http_err.response.text}")
        return None
    except Exception as e:
        print(f"❗ 키페어 목록 조회 중 예상치 못한 오류 발생: {e}")
        return None
