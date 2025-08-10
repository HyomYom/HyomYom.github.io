# 🐳 Spring Boot OAuth2 인증 서비스 Docker로 배포하기  
**– MySQL 연동 & 커스텀 네트워크 설정 포함 –**

---

## 📌 개요

이번 글에서는 `Spring Boot + OAuth2 + JWT` 기반의 인증 서비스를 Docker로 배포한 과정을 기록합니다.  
특히 **애플리케이션 컨테이너와 MySQL 컨테이너 간의 통신을 위한 Docker 네트워크 구성**에 중점을 두었습니다.

---

## 📁 디렉토리 구성 요약

```
auth-login-service/
├── Dockerfile
├── docker-compose.yml
├── .env
└── build/libs/auth-login-service.jar (빌드 후 생성)
```

이 글을 읽기 전에 위와 같은 구조로 프로젝트가 구성되어 있다고 가정합니다.

---

## 🧱 1. Dockerfile 설명

```dockerfile
FROM eclipse-temurin:17-jdk
ARG JAR_FILE=build/libs/*.jar
COPY ${JAR_FILE} app.jar
ENTRYPOINT ["java", "-jar", "/app.jar"]
```

### 🔍 주요 명령어 설명

| 명령어 | 의미 |
|--------|------|
| `FROM eclipse-temurin:17-jdk` | Java 17 JDK가 설치된 공식 이미지 사용 |
| `ARG JAR_FILE` | jar 파일 경로를 외부에서 변수로 받기 위함 |
| `COPY ${JAR_FILE} app.jar` | jar 파일을 컨테이너로 복사 |
| `ENTRYPOINT` | 컨테이너 실행 시 명령어 지정 (`java -jar`) |

👉 이 Dockerfile은 Gradle로 빌드한 `.jar` 파일을 복사하고 바로 실행하는 구조입니다. 불필요한 단계 없이 배포할 수 있어 효율적입니다.

---

## ⚙️ 2. docker-compose.yml 설명

```yaml
services:
  mysql:
    image: mysql:latest
    container_name: social-login
    ports:
      - "3306:3306"
    environment:
      SPRING_PROFILES_ACTIVE: ${SPRING_PROFILES_ACTIVE}
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
      SPRING_PROFILES_ACTIVE: docker
    networks:
      - social-login-networks

volumes:
  auth-mysql-data:

networks:
  social-login-networks:
    external: true
    driver: bridge
```

📌 여기서 주목할 부분:

- **두 컨테이너가 같은 네트워크 (`social-login-networks`)에 속해 있어 통신 가능**
- `depends_on`으로 DB가 완전히 준비된 후에 Spring Boot 앱이 실행됨
- `.env` 파일로 환경 변수 관리

---

## 🌐 3. Docker 네트워크 구성

```bash
docker network create --driver bridge social-login-networks
```

> `external: true` 옵션을 사용했기 때문에, `docker-compose`는 네트워크를 자동 생성하지 않습니다. **직접 위 명령어로 만들어야 합니다.**

👉 이렇게 하면 `mysql` 컨테이너와 `app` 컨테이너가 내부에서 DNS로 서로를 찾을 수 있게 됩니다.

---

## 🔐 4. .env 파일 구성 예시

```env
SPRING_PROFILES_ACTIVE=docker
MYSQL_DATABASE=authdb
MYSQL_USER=appuser
MYSQL_PASSWORD=appuser123
MYSQL_ROOT_PASSWORD=rootpass
```

> 이렇게 `.env` 파일에 민감한 정보를 분리해 관리하면 코드가 깔끔해지고 보안에도 유리합니다.

---

## 🚀 5. 전체 실행 순서

### ① 프로젝트 빌드

```bash
./gradlew clean build
```

→ `build/libs/*.jar` 생성됨. 이 파일을 기반으로 컨테이너가 실행됩니다.

---

### ② 도커 네트워크 생성

```bash
docker network create --driver bridge social-login-networks
```

→ 반드시 먼저 실행되어야 `docker-compose`가 네트워크를 인식할 수 있습니다.

---

### ③ 컨테이너 실행

```bash
docker-compose up --build
```

- `--build` 옵션은 변경된 Dockerfile을 기반으로 이미지 재생성
- `mysql` 서비스 → `app` 서비스 순서로 실행됨

---

### 💡 백그라운드 실행

```bash
docker-compose up -d
```

> `-d` 옵션은 데몬 모드로 실행 (터미널 점유 X)

---

## 🔗 6. MySQL ↔ Spring Boot 연결 설명

컨테이너끼리 같은 도커 네트워크 내에 있기 때문에, `application.yml`에서 다음처럼 설정하면 됩니다:

```yaml
spring:
  datasource:
    url: jdbc:mysql://mysql:3306/authdb
    username: appuser
    password: appuser123
```

- `mysql`은 **컨테이너명**
- 외부에서 연결 시에는 `localhost`, 컨테이너 내부에서는 **서비스 이름으로 접근**

---

## 🧼 7. 종료 및 정리 명령어

```bash
# 모든 컨테이너 중지 및 정리
docker-compose down

# 네트워크 제거 (필요 시)
docker network rm social-login-networks
```

---

## ✅ 마무리

이번 배포에서 강조된 핵심 포인트는 다음과 같습니다:

- Spring Boot 서비스를 Dockerfile로 이미지화
- MySQL과 통신 가능한 커스텀 네트워크 구성
- `docker-compose`로 전체 시스템 손쉽게 관리

실제 배포 환경을 고려한 설정이기 때문에, 취업 포트폴리오나 블로그 공유용으로도 훌륭합니다 💪