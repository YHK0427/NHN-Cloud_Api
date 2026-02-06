# NHN Cloud API 파이썬 모듈

## 1. 프로젝트 개요

이 프로젝트는 NHN Cloud API를 보다 쉽고 효율적으로 사용할 수 있도록 도와주는 파이썬 모듈(`nhn_api_module`)과 그 활용 예제 코드를 제공합니다. 복잡한 API 호출 로직을 재사용 가능한 함수들로 추상화하여, 개발자가 NHN Cloud의 다양한 리소스를 파이썬 스크립트로 손쉽게 관리하고 자동화할 수 있도록 설계되었습니다.

주요 목표는 다음과 같습니다:
- **모듈성:** 인증, 네트워킹, 컴퓨트, 보안 등 각 기능 영역별로 코드를 모듈화하여 관리 용이성과 재사용성을 극대화합니다.
- **직관적인 API:** NHN Cloud API 명세를 깊이 이해하지 않아도, 명확하고 간결한 함수 호출을 통해 리소스를 생성하고 관리할 수 있도록 돕습니다.
- **손쉬운 확장:** 새로운 NHN Cloud API 기능이 추가되거나 기존 기능을 확장해야 할 경우, 명확하게 분리된 모듈 구조 덕분에 쉽게 코드를 추가하거나 수정할 수 있습니다.

## 2. 프로젝트 구조

```
nhn_api/
├── nhn_api_module/           # 핵심 API 호출 로직이 담긴 파이썬 패키지 (라이브러리 역할)
│   ├── __init__.py           # 패키지 초기화 파일
│   ├── auth.py               # 인증 토큰 발급 및 관리 기능
│   ├── networking.py         # VPC, 서브넷, Floating IP, 인터넷 게이트웨이 등 네트워크 관련 기능
│   ├── compute.py            # 인스턴스 생성/조회, 플레이버/키페어 목록 조회 등 컴퓨트 관련 기능
│   └── security.py           # 보안 그룹 및 보안 그룹 규칙 관리 기능
├── examples/                 # nhn_api_module 사용 예제 코드 디렉터리
│   ├── __init__.py           # 패키지 초기화 파일
│   └── provision_web_server.py # NHN Cloud에 웹 서버 전체를 프로비저닝하는 종합 예제
├── .gitignore                # Git 추적에서 제외할 파일 목록
├── .env.example              # 환경 변수 설정을 위한 템플릿 파일
├── README.md                 # 프로젝트 설명서 (현재 파일)
└── requirements.txt          # 프로젝트 의존성 라이브러리 목록
```

## 3. 전제 조건

- **Python 3.x**: 파이썬 3.6 이상 버전이 설치되어 있어야 합니다.
- **프로젝트 의존성 라이브러리**: 아래 명령어를 통해 필요한 모든 라이브러리를 한 번에 설치할 수 있습니다:
  ```bash
  pip install -r requirements.txt
  ```

## 4. 환경 설정 (중요!)

이 프로젝트는 NHN Cloud API에 접근하기 위한 민감 정보(예: API 사용자 이름, 비밀번호, 테넌트 ID)를 `.env` 파일을 통해 안전하게 관리합니다. 소스 코드에 직접 정보를 노출하지 않도록, 아래 단계를 따라 개발 환경을 구성해주세요.

1.  **`.env` 파일 생성:**
    프로젝트의 루트 디렉터리에 있는 `.env.example` 파일을 `.env` 라는 이름으로 복사합니다.

2.  **`.env` 파일 수정:**
    방금 생성한 `.env` 파일을 텍스트 편집기로 열고, 각 변수(`API_USERNAME`, `API_PASSWORD`, `TENANT_ID`, `MY_IP_FOR_SSH`, `KEY_NAME`)에 자신의 NHN Cloud 환경에 맞는 실제 값을 입력합니다.

    ```dotenv
    # .env 파일 예시 (반드시 자신의 정보로 교체해야 합니다!)

    # NHN Cloud API Credentials
    API_USERNAME="[자신의 NHN Cloud API 사용자 이름]"
    API_PASSWORD="[자신의 NHN Cloud API 비밀번호]"
    TENANT_ID="[자신의 NHN Cloud 테넌트/프로젝트 ID]"

    # Environment-specific settings
    MY_IP_FOR_SSH="[SSH 접속 허용할 자신의 공인 IP 주소]/32" # 예: "203.0.113.10/32"
    KEY_NAME="[NHN Cloud에 등록된 키페어 이름]" # 예: "my-ssh-key"
    ```

## 5. 모듈 상세 설명 및 사용법

`nhn_api_module` 패키지는 NHN Cloud API와 상호작용하는 핵심 함수들을 포함하고 있습니다. 각 모듈은 특정 리소스 영역을 담당하며, 사용자는 이 함수들을 자신의 스크립트에서 직접 임포트하여 활용할 수 있습니다.

### 5.1. `nhn_api_module.auth` (인증 모듈)

NHN Cloud API 인증 토큰을 발급받고 관리하는 기능을 제공합니다.

#### `get_token()` 함수

*   **설명:** NHN Cloud API 인증 토큰을 발급받거나, `token.json`에 캐시된 유효한 토큰을 반환합니다. 이 함수는 `API_USERNAME`, `API_PASSWORD`, `TENANT_ID` 환경 변수를 사용합니다.
*   **매개변수:** 없음
*   **반환:**
    *   성공 시 토큰 정보(`token_id`, `token_expires`, `token_issued_at`)가 담긴 딕셔너리
    *   실패 시 `None`
*   **사용 예시:**
    ```python
    from nhn_api_module.auth import get_token
    # .env 파일은 진입 스크립트에서 한번 로드하는 것을 권장합니다.
    # from dotenv import load_dotenv; load_dotenv()

    auth_token_data = get_token()
    if auth_token_data:
        token_id = auth_token_data['token_id']
        print(f"인증 토큰 ID: {token_id}")
    else:
        print("NHN Cloud 인증 토큰 발급에 실패했습니다.")
    ```

### 5.2. `nhn_api_module.networking` (네트워킹 모듈)

VPC, 서브넷, 인터넷 게이트웨이, Floating IP 등 NHN Cloud의 네트워크 리소스 관리를 위한 함수들을 제공합니다.

#### `create_vpc(token, vpc_name, cidr, region_code="kr1")` 함수

*   **설명:** 새로운 VPC(가상 프라이빗 클라우드)를 생성합니다.
*   **매개변수:** `token` (인증 토큰), `vpc_name` (VPC 이름), `cidr` (CIDR 블록, 예: "10.0.0.0/16"), `region_code` (리전 코드)
*   **반환:** 성공 시 생성된 VPC의 ID (문자열), 실패 시 `None`.

#### `get_vpc_details(token, vpc_id, region_code="kr1")` 함수

*   **설명:** 특정 VPC의 상세 정보를 조회합니다. VPC에 속한 서브넷 정보 및 라우팅 테이블 ID를 얻는 데 주로 사용됩니다.
*   **매개변수:** `token`, `vpc_id` (조회할 VPC의 ID), `region_code`
*   **반환:** 성공 시 VPC 상세 정보가 담긴 딕셔너리, 실패 시 `None`.

#### `create_vpc_subnet(token, vpc_id, subnet_name, cidr, region_code="kr1")` 함수

*   **설명:** 지정된 VPC 내에 새로운 서브넷을 생성합니다.
*   **매개변수:** `token`, `vpc_id` (서브넷이 속할 VPC의 ID), `subnet_name` (서브넷 이름), `cidr` (서브넷 CIDR 블록, 예: "10.0.1.0/24"), `region_code`
*   **반환:** 성공 시 생성된 서브넷의 ID (문자열), 실패 시 `None`.

#### `get_external_network_id(token, region_code="kr1")` 함수

*   **설명:** 외부 연결이 가능한 네트워크(Public Network)의 ID를 조회합니다. 이 ID는 인터넷 게이트웨이 생성 및 Floating IP 할당에 필수적으로 사용됩니다.
*   **매개변수:** `token`, `region_code`
*   **반환:** 성공 시 외부 네트워크 ID (문자열), 실패 시 `None`.

#### `create_internet_gateway(token, ig_name, external_network_id, region_code="kr1")` 함수

*   **설명:** 새로운 인터넷 게이트웨이를 생성합니다.
*   **매개변수:** `token`, `ig_name` (인터넷 게이트웨이 이름), `external_network_id` (연결할 외부 네트워크 ID), `region_code`
*   **반환:** 성공 시 생성된 인터넷 게이트웨이의 ID (문자열), 실패 시 `None`.

#### `attach_gateway_to_routing_table(token, routing_table_id, internet_gateway_id, region_code="kr1")` 함수

*   **설명:** 특정 라우팅 테이블에 인터넷 게이트웨이를 연결하여 외부 통신 경로를 설정합니다.
*   **매개변수:** `token`, `routing_table_id` (연결할 라우팅 테이블의 ID), `internet_gateway_id` (연결할 인터넷 게이트웨이의 ID), `region_code`
*   **반환:** 성공 시 `True`, 실패 시 `False`.

#### `create_floating_ip(token, floating_network_id, region_code="kr1")` 함수

*   **설명:** 새로운 Floating IP(공인 IP)를 할당합니다.
*   **매개변수:** `token`, `floating_network_id` (Floating IP를 할당할 외부 네트워크의 ID), `region_code`
*   **반환:** 성공 시 Floating IP의 ID 및 IP 주소가 담긴 딕셔너리(`{'id': '...', 'ip_address': '...'}`), 실패 시 `None`.

#### `associate_floating_ip(token, floating_ip_id, port_id, region_code="kr1")` 함수

*   **설명:** 할당된 Floating IP를 인스턴스의 특정 네트워크 포트에 연결합니다.
*   **매개변수:** `token`, `floating_ip_id` (연결할 Floating IP의 ID), `port_id` (Floating IP를 연결할 인스턴스 포트의 ID), `region_code`
*   **반환:** 성공 시 `True`, 실패 시 `False`.

*   **네트워킹 모듈 사용 예시:**
    ```python
    from nhn_api_module.auth import get_token
    from nhn_api_module.networking import create_vpc, create_vpc_subnet
    from dotenv import load_dotenv; load_dotenv()
    import os

    auth_token_data = get_token()
    token_id = auth_token_data['token_id'] if auth_token_data else None

    if token_id:
        vpc_id = create_vpc(token_id, "my-custom-vpc", "10.10.0.0/16", "kr1")
        if vpc_id:
            subnet_id = create_vpc_subnet(token_id, vpc_id, "my-custom-subnet", "10.10.1.0/24", "kr1")
            if subnet_id:
                print(f"VPC ID: {vpc_id}, 서브넷 ID: {subnet_id} 생성 완료.")
    ```

### 5.3. `nhn_api_module.compute` (컴퓨트 모듈)

NHN Cloud 컴퓨트 리소스(인스턴스, 플레이버, 키페어) 관리를 위한 함수들을 제공합니다.

#### `create_instance(token, tenant_id, instance_name, key_name, image_ref, flavor_ref, subnet_id, security_group_names, user_data, volume_size=30, region_code="kr1")` 함수

*   **설명:** 새로운 컴퓨트 인스턴스(가상 머신)를 생성하고, 인스턴스가 `ACTIVE` 상태가 될 때까지 폴링하며 대기합니다. 인스턴스 생성 후 해당 인스턴스의 네트워크 포트 ID도 함께 조회하여 반환합니다. `user_data`에는 Base64로 인코딩된 셸 스크립트를 전달해야 합니다.
*   **매개변수:** `token`, `tenant_id`, `instance_name`, `key_name` (등록된 키페어 이름), `image_ref` (이미지 ID), `flavor_ref` (플레이버 ID), `subnet_id`, `security_group_names` (적용할 보안 그룹 이름 리스트), `user_data` (인스턴스 시작 시 실행할 Base64 인코딩된 셸 스크립트), `volume_size` (부트 볼륨 크기), `region_code`
*   **반환:** 성공 시 `(인스턴스 ID, 포트 ID)` 튜플, 실패 시 `(None, None)`.

#### `list_flavors(token, tenant_id, region_code="kr1")` 함수

*   **설명:** 사용 가능한 인스턴스 사양(플레이버) 목록을 조회합니다.
*   **매개변수:** `token`, `tenant_id`, `region_code`
*   **반환:** 성공 시 플레이버 정보(`{'id': '...', 'name': '...'}`) 딕셔너리 리스트, 실패 시 `None`.

#### `list_key_pairs(token, tenant_id, region_code="kr1")` 함수

*   **설명:** 현재 프로젝트에 등록된 키페어 목록을 조회합니다.
*   **매개변수:** `token`, `tenant_id`, `region_code`
*   **반환:** 성공 시 키페어 정보(`{'name': '...', 'fingerprint': '...'}`) 딕셔너리 리스트, 실패 시 `None`.

*   **컴퓨트 모듈 사용 예시:**
    ```python
    from nhn_api_module.auth import get_token
    from nhn_api_module.compute import list_flavors, list_key_pairs
    from dotenv import load_dotenv; load_dotenv()
    import os

    auth_token_data = get_token()
    token_id = auth_token_data['token_id'] if auth_token_data else None
    tenant_id = os.getenv("TENANT_ID")

    if token_id and tenant_id:
        flavors = list_flavors(token_id, tenant_id, "kr1")
        if flavors:
            print(f"사용 가능한 플레이버: {flavors[0]['name']}")

        key_pairs = list_key_pairs(token_id, tenant_id, "kr1")
        if key_pairs:
            print(f"등록된 키페어: {key_pairs[0]['name']}")
    ```

### 5.4. `nhn_api_module.security` (보안 모듈)

NHN Cloud 보안 그룹 및 보안 그룹 규칙 관리를 위한 함수들을 제공합니다.

#### `create_security_group(token, sg_name, description="", region_code="kr1")` 함수

*   **설명:** 새로운 보안 그룹을 생성합니다.
*   **매개변수:** `token`, `sg_name` (보안 그룹 이름), `description` (설명), `region_code`
*   **반환:** 성공 시 생성된 보안 그룹의 ID (문자열), 실패 시 `None`.

#### `create_security_group_rule(token, security_group_id, direction, protocol=None, port_range_min=None, port_range_max=None, remote_ip_prefix=None, description=None, region_code="kr1")` 함수

*   **설명:** 지정된 보안 그룹에 인그레스(Ingress) 또는 이그레스(Egress) 규칙을 추가합니다.
*   **매개변수:** `token`, `security_group_id` (규칙을 추가할 보안 그룹 ID), `direction` ("ingress" 또는 "egress"), `protocol` (예: "tcp", "udp", "icmp"), `port_range_min` (시작 포트), `port_range_max` (종료 포트), `remote_ip_prefix` (원격 IP 주소 또는 CIDR, 예: "0.0.0.0/0"), `description` (규칙 설명), `region_code`
*   **반환:** 성공 시 생성된 규칙의 ID (문자열), 실패 시 `None`.

*   **보안 모듈 사용 예시:**
    ```python
    from nhn_api_module.auth import get_token
    from nhn_api_module.security import create_security_group, create_security_group_rule
    from dotenv import load_dotenv; load_dotenv()
    import os

    auth_token_data = get_token()
    token_id = auth_token_data['token_id'] if auth_token_data else None

    if token_id:
        sg_id = create_security_group(token_id, "my-app-sg", "웹 애플리케이션 보안 그룹", "kr1")
        if sg_id:
            create_security_group_rule(token_id, sg_id, "ingress", "tcp", 80, 80, "0.0.0.0/0", "HTTP 허용", "kr1")
            print(f"보안 그룹 {sg_id} 생성 및 규칙 추가 완료.")
    ```

## 6. 사용 방법

### 6.1. 웹 서버 프로비저닝 예제 실행하기

`examples/provision_web_server.py` 스크립트는 `nhn_api_module`의 함수들을 사용하여 NHN Cloud에 웹 서버 환경을 완벽하게 프로비저닝하는 방법을 보여주는 종합 예제입니다.

**실행 전 확인 사항:**
- 위의 **4. 환경 설정** 단계를 완료하여 `.env` 파일에 유효한 정보가 입력되어 있는지 확인합니다.
- 예제 스크립트(`examples/provision_web_server.py`) 내에 정의된 리소스 이름(VPC, 인스턴스 등)이나 이미지 ID(`image_ref`)가 현재 환경에 적합한지 확인하고 필요시 수정합니다.

구성 완료 후, 프로젝트 루트 디렉터리에서 다음 명령어를 실행합니다:

```bash
python examples/provision_web_server.py
```

이 스크립트는 NHN Cloud API를 통해 인증부터 시작하여 VPC, 서브넷, 인터넷 게이트웨이, 보안 그룹 및 규칙, 인스턴스 생성 및 Floating IP 연결까지 모든 과정을 자동으로 수행하고 최종 웹 서버 접속 주소를 출력합니다.

### 6.2. 자신의 파이썬 스크립트에서 모듈 활용하기

`nhn_api_module`은 라이브러리 형태로 제공되므로, 개발자는 자신의 파이썬 프로젝트에서 필요한 기능을 직접 임포트하여 활용할 수 있습니다.

예를 들어, 단순히 사용 가능한 인스턴스 플레이버 목록을 조회하는 스크립트를 작성하고 싶다면 다음과 같이 할 수 있습니다:

```python
# my_custom_script.py (프로젝트 루트 디렉터리 내)

import sys
import os
from dotenv import load_dotenv

# 프로젝트 루트를 Python Path에 추가 (모듈 임포트를 위해 필요)
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.append(project_root)

# .env 파일 로드 (진입 스크립트에서 한 번만 로드 권장)
load_dotenv()

from nhn_api_module.auth import get_token
from nhn_api_module.compute import list_flavors

def main():
    token_data = get_token()
    if not token_data:
        print("토큰 발급 실패, 스크립트 종료.")
        return
    auth_token = token_data['token_id']
    tenant_id = os.getenv("TENANT_ID")

    if not tenant_id:
        print("TENANT_ID 환경 변수가 설정되지 않았습니다.")
        return
    
    print("\n--- 사용 가능한 인스턴스 플레이버 목록 ---")
    flavors = list_flavors(auth_token, tenant_id, "kr1")
    if flavors:
        for f in flavors:
            print(f"  - 이름: {f['name']}, ID: {f['id']}")
    else:
        print("플레이버 목록 조회 실패 또는 플레이버가 없습니다.")

if __name__ == "__main__":
    main()
```

## 7. 리소스 정리 (권장)

예제 스크립트(`examples/provision_web_server.py`)는 리소스를 생성만 할 뿐, 자동으로 삭제하지 않습니다. 불필요한 요금 발생을 방지하려면, 테스트 또는 사용 완료 후 **NHN Cloud 콘솔**을 통해 생성된 모든 리소스를 직접 삭제해야 합니다.

생성된 리소스는 의존성 관계를 고려하여 생성의 역순으로 삭제하는 것이 안전합니다:
1.  Floating IP (연결 해제 후 반납)
2.  인스턴스 (종료)
3.  인터넷 게이트웨이 (삭제)
4.  보안 그룹 (삭제)
5.  서브넷 (삭제)
6.  VPC (삭제)
```