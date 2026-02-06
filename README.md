# NHN Cloud API 파이썬 모듈

## 1. 프로젝트 개요

이 프로젝트는 NHN Cloud API를 보다 쉽게 사용할 수 있도록 도와주는 파이썬 모듈(`nhn_api_module`)과 그 사용법을 보여주는 예제 코드를 제공합니다. 복잡한 API 호출을 직관적인 함수로 추상화하여, NHN Cloud의 다양한 리소스를 스크립트로 손쉽게 관리할 수 있습니다.

주요 목표는 다음과 같습니다:
- **모듈성:** VPC, 인스턴스, 보안 그룹 등 각 기능별로 모듈을 분리하여 재사용성을 높입니다.
- **직관성:** 사용자가 API 명세를 깊이 이해하지 않아도, 간단한 함수 호출만으로 리소스를 생성하고 관리할 수 있도록 합니다.
- **확장성:** 새로운 API 기능을 쉽게 추가할 수 있는 구조를 제공합니다.

## 2. 프로젝트 구조

```
nhn_api/
├── nhn_api_module/           # 핵심 로직이 담긴 파이썬 패키지
│   ├── __init__.py
│   ├── auth.py               # 인증 및 토큰 관리
│   ├── networking.py         # VPC, 서브넷, Floating IP 등 네트워크 관련 기능
│   ├── compute.py            # 인스턴스, 플레이버, 키페어 등 컴퓨트 관련 기능
│   └── security.py           # 보안 그룹 관련 기능
├── examples/                 # 모듈 사용 예제 디렉터리
│   ├── __init__.py
│   └── provision_web_server.py # 웹 서버 전체를 프로비저닝하는 예제
├── .gitignore
├── .env.example              # 환경 변수 설정을 위한 템플릿
├── README.md                 # 프로젝트 설명서
└── requirements.txt          # 프로젝트 의존성 목록
```

## 3. 전제 조건

- Python 3.x
- 프로젝트 의존성 라이브러리. 아래 명령어로 한 번에 설치할 수 있습니다:
  ```bash
  pip install -r requirements.txt
  ```

## 4. 환경 설정 (중요!)

이 프로젝트는 민감 정보(API 자격 증명 등)를 `.env` 파일을 통해 안전하게 관리합니다. 아래 단계에 따라 환경을 구성해주세요.

1.  **`.env` 파일 생성:**
    프로젝트의 루트 디렉터리에 있는 `.env.example` 파일을 `.env` 라는 이름으로 복사합니다.

2.  **`.env` 파일 수정:**
    방금 생성한 `.env` 파일을 열고, 각 변수에 자신의 NHN Cloud 환경에 맞는 실제 값을 입력합니다.

    ```dotenv
    # .env 파일

    # NHN Cloud API Credentials
    API_USERNAME="YOUR_API_USERNAME"
    API_PASSWORD="YOUR_API_PASSWORD"
    TENANT_ID="YOUR_TENANT_ID"

    # Environment-specific settings
    MY_IP_FOR_SSH="YOUR_PUBLIC_IP/32"
    KEY_NAME="YOUR_KEYPAIR_NAME"
    ```

## 5. 사용 방법

### 5.1. 웹 서버 프로비저닝 예제 실행하기

프로젝트에 포함된 웹 서버 생성 예제를 실행하여 전체 모듈의 작동 방식을 확인할 수 있습니다.

**실행 전 주의사항:**
- 위의 **4. 환경 설정** 단계를 완료해야 합니다.
- `examples/provision_web_server.py` 파일 내에 하드코딩된 리소스 이름(VPC, 인스턴스 등)이나 이미지 ID(`image_ref`)가 현재 환경에 적합한지 확인하세요.

구성 완료 후, 터미널에서 다음 명령어를 실행합니다:

```bash
python examples/provision_web_server.py
```

이 스크립트는 인증부터 시작하여 VPC, 인터넷 게이트웨이, 인스턴스, Floating IP 연결까지 모든 과정을 자동으로 수행하고 최종 접속 주소를 출력합니다.

### 5.2. 직접 모듈 활용하기

이 프로젝트의 핵심은 `nhn_api_module`입니다. 자신의 파이썬 스크립트에서 필요한 함수들을 직접 임포트하여 사용할 수 있습니다.

예를 들어, VPC만 생성하고 싶다면 다음과 같이 스크립트를 작성할 수 있습니다.

```python
# my_script.py
from dotenv import load_dotenv
from nhn_api_module.auth import get_token
from nhn_api_module.networking import create_vpc

load_dotenv() # .env 파일 로드

# 1. 토큰 발급
token_data = get_token()
if not token_data:
    exit()
auth_token = token_data['token_id']

# 2. VPC 생성
vpc_id = create_vpc(
    token=auth_token,
    vpc_name="my-custom-vpc",
    cidr="10.10.0.0/16",
    region_code="kr1"
)

if vpc_id:
    print(f"나만의 VPC가 성공적으로 생성되었습니다. ID: {vpc_id}")

```

## 6. 리소스 정리

예제 스크립트(`provision_web_server.py`)는 리소스를 생성만 할 뿐, 자동으로 삭제하지 않습니다. 불필요한 요금 발생을 방지하려면, 테스트 완료 후 **NHN Cloud 콘솔**을 통해 생성된 모든 리소스를 직접 삭제해야 합니다.

생성된 리소스는 생성의 역순으로 삭제하는 것이 안전합니다:
1.  Floating IP (연결 해제 및 반납)
2.  인스턴스
3.  인터넷 게이트웨이
4.  보안 그룹
5.  서브넷
6.  VPC
```