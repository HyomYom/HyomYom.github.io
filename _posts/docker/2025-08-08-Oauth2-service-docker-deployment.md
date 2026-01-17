---
layout: post
title: "OAuth2 로그인 서비스 도커 배포"
categories: [docker]
tags: [Blog, Oauth2, Social-login, docker, deployment]
author: "Hyomyeong"
---
 해당글은 공부 목적으로 정리한 개인적인 기록입니다.
 정확하지 않은 정보가 포함될 수 있으며, 최신 기술 동향이나 공식 문서와는 차이가 있을 수 있습니다!
 처음 구현하시는 분들께 작은 도움이 되었으면 하며, 혹시 틀리 내용이 있다면 댓그로 알려주시면 감사하겠습니다.

---
## 🐳 Spring Boot OAuth2 인증 서비스 Docker로 배포하기
(Docker내 커스텀 네트워크 설정 & Mysql 연동)

---
이번 글에서는 앞서 작성했던 Oauth2 로그인 서비스를 Docker로 배포하는 과정을 기록하고자한다.

서비스 배포 경험을 위해 간략하게 진행하기 때문에 자세한 설정 관련 된 내용은 추가로 찾아보는 걸 권장한다

## 디렉토리 구성 요약
```
auth-lgoin-serivce
├─ Dockerfile
├─ docker-compose.yml
├─ .env
└─ build/libs/auth-login-service-jar (빌드 후 생성)
```
(Root Dir 기준) 다음과 같이 프로젝트가 구성되있음을 기준으로 작성하였다

---
## Docker와 Docker Compse의 관계
- Docker → 애플리케이션과 그 실행 환경(OS, 라이브러리, 설정 등)을 컨테이너로 패키징하고 실행하는 도구

- Docker Compose → 여러 개의 컨테이너(예: DB, 서버, 캐시 서버 등)를 하나의 서비스 세트로 정의하고, 명령 한 번에 실행/중지/관리할 수 있게 해주는 도구

즉, 여러 서비스를 container로 실행시키고 싶을 때 `docker run ...` 명령을 여러 번 쓰는 대신
`docker-compose.yml` 파일에 컨테이너 설정을 모아두고 `docker-compose up` 한 줄로 전체 시스템을 실행할 수 있다

### 1. docker-compose 특징
- 멀티 컨테이너 환경 관리
    Ex) Mysql(DB) + Spring Boot(Server) + Redis등을 한번에 실행
- 환경변수(.env) 사용 가능
- 네트워크(bridge) 자동 생성
    각 컨테이너끼리 서비스 이름으로 통신 가능
- 볼륨 관리
    DB 데이터나 로그등을 컨테이너 삭제 후에도 유지 가능
- 의존성 관리
   `depends_on` 옵션으로 서비스 실행 순서와 조건 제어

---
## Dockerfile(기본 설정)
```dockerfile
FROM eclipse-temurin:17-jdk
ARG JAR_FILE=build/libs/*.jar
COPY ${JAR_FLILE} app.jar
ENTRYPOINT ["java","-jar", "/app.jar"]
```

### 명령어

| 명령어 | 의미 |
|--------|------|
| `FROM eclipse-temurin:17-jdk` | Java 17 JDK가 설치된 공식 이미지 사용 |
| `ARG JAR_FILE` | jar 파일 경로를 외부에서 변수로 받기 위함 |
| `COPY ${JAR_FILE} app.jar` | jar 파일을 컨테이너로 복사 |
| `ENTRYPOINT` | 컨테이너 실행 시 명령어 지정 (`java -jar`) |

---
## docker-compose.yml

```yaml
services:
  mysql:
    image: mysql:latest
    container_name: social-login
    ports:
      - "3306:3306"
    environment:
      MYSQL_DATABASE: ${MYSQL_DATABASE}
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
    volumes:
      - auth-mysql-data:/var/lib/mysql
    networks:
      - social-login-networks
    healthcheck:
      test: ["CMD","mysqladmin", "ping", "-h", "localhost", "-p$MYSQL_ROOT_PASSWORD"]
      interval: 5s
      retries: 10

  app:
    build: .
    ports:
      - "8080:8080"
    depends_on:
      mysql:
        condition: service_healthy
    environment:
      SPRING_PROFILES_ACTIVE: ${SPRING_PROFILES_ACTIVE}
    networks:
      - social-login-networks
      - proxy

volumes:
  auth-mysql-data:
    name: auth-mysql-data

networks:
  proxy:
    external: true
  social-login-networks:
    internal: true 
    driver: bridge
```

### 전체 구성
- 두 개의 서비스
    - mysql: 공식 MySQL 컨테이너

    - app: 스프링 부트 앱(로컬 Dockerfile로 빌드)

- 공유 리소스
    - 볼륨 auth-mysql-data: MySQL 데이터 영속화

    - 네트워크 social-login-networks: 두 서비스가 통신하는 전용 브리지 네트워크

    - (정의만 있음) proxy: 외부에서 이미 존재하는 네트워크에 붙일 수 있도록 예약

- 기동 순서
    - app → mysql의 healthcheck가 통과하면 시작 (depends_on 조건)

### 1. services.mysql: 데이터베이스 컨테이너
- image: mysql:latest

    - 공식 이미지 사용

- container_name: social-login

    - 컨테이너에 사람이 읽기 좋은 이름 부여(로그/명령어에서 편함).

- ports: "3306:3306"

    - 호스트 3306 → 컨테이너 3306. 로컬 클라이언트(IDE, DBeaver 등)가 직접 접속 가능.

- environment:

   - MySQL이 실제로 사용하는 변수

        - MYSQL_ROOT_PASSWORD: 루트 계정 비밀번호(필수)

        - MYSQL_DATABASE: 초기 생성 DB 이름

        - MYSQL_USER/MYSQL_PASSWORD: 애플리케이션용 일반 계정

- volumes: auth-mysql-data:/var/lib/mysql

    - MySQL 데이터 파일을 호스트 볼륨에 영구 저장 → 컨테이너 재시작/재생성에도 데이터 유지.

- networks: social-login-networks

    앱과 같은 네트워크에 붙여 컨테이너 간 이름 기반 통신 가능(예: mysql:3306).

- healthcheck

    - mysqladmin ping으로 DB 준비 여부 체크. 준비되기 전에는 unhealthy.

    - interval: 5s, retries: 10 → 최대 약 50초(5 * 10) 동안 재시도.

### 2. services.app : 스프링 부트 app
- build: .

    - 현재 디렉터리의 Dockerfile로 이미지를 빌드.

    - 대조: image:는 레지스트리에서 가져오고, build:는 로컬에서 만든다.

- ports: "8080:8080"

    - 호스트 8080 → 컨테이너 8080. 브라우저에서 http://localhost:8080 접근.

- depends_on + condition: service_healthy

    - 헬스체크 기반 의존성: DB가 “healthy”가 된 뒤 앱을 시작 → 커넥션 오류 감소.

    - (Compose v2 스펙에서 지원)

- environment: SPRING_PROFILES_ACTIVE: docker

    - 스프링 프로필을 docker로 강제. application-docker.yml(또는 -docker.properties)를 로드하도록 유도.

- networks: social-login-networks

    - DB와 같은 네트워크 → 호스트네임 mysql로 접속 가능

    - 예: JDBC URL jdbc:mysql://mysql:3306/${MYSQL_DATABASE}

### 3. volumes: 데이터 영속화
- MySQL 컨테이너가 사라져도 데이터는 이 볼륨에 남음
- CI에서 동일 이름으로 일관성 있게 재사용 가능

### 4. networks: 서비스 간 통신 범위
- driver: bridge

    - Docker 기본 브리지 네트워크. 같은 네트워크의 컨테이너끼리 이름 기반 통신.

- social-login-networks: internal: true

    - 해당 네트워크를 외부로 라우팅하지 않음(egress 차단)

    - 컨테이너끼리는 통신 가능하지만, 인터넷으로 나가는 트래픽이 막힐 수 있음

    - 소셜 로그인/외부 API 호출/패키지 다운로드가 필요하면 internal: true를 제거하거나, 외부 통신 가능한 네트워크를 추가로 붙이는 것을 고려

    - 참고: 호스트 포트 공개(ports)는 여전히 동작합니다(호스트↔컨테이너 인바운드는 가능)

- proxy: external: true

    - 이미 사전에 존재하는 외부 네트워크(예: 리버스 프록시 traefik/nginx-proxy가 만든 네트워크)에 컨테이너를 연결할 때 사용

---
## .env

```
SPRING_PROFILES_ACTIVE=
MYSQL_DATABASE=
MYSQL_USER=
MYSQL_PASSWORD=
MYSQL_ROOT_PASSWORD=
```
.env 파일은 compose 스크립트의 환경변수를 선언할 수 있는 파일이다

물론 시스템에 접근할 수 있는 코드 등 민감 정보를 다루기 때문에 배포 전 `.dockerignore`을 통해 제외 선언을 해줘야 docker 빌드 시 해당 파일이 제외된 채 빌드된다

---
## 🚀 실행 절차
1. 프로젝트 비륻
```bash
./gradlew clean build
```
→ build/libs/*.jar 생성

2. 네트워크 생성
```bash
docker network create --driver bridge proxy
```
→ external 네트워크이므로 미리 만들어야 함

3. 컨테이너 실행
```bash
docker-compose up --build
---
docker-compose up -d
```
- build → Dockerfile 변경 사항 반영
- MySQL → 앱 순서로 실행됨 (depends_on 설정)
docker-compose up -d → 터미널 점유 없이 백그라운드 실행

4. 종료
```bash
docker-compose down
docker network rm proxy  # 필요 시 네트워크 삭제
```



