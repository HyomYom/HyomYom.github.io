---
layout: post
title: "🐳 Docker DB (MySQL, PostgreSQL, Redis) 기본 명령어 가이드"
date: 2026-04-07
categories: [docker]
tags: ['docker', 'mysql', 'postgres', 'redis']
last_modified_at: 2026-04-08
---



# 🐬 MySQL

## 🧱 컨테이너 실행

### 📌 설명

docker run은 MySQL 이미지를 기반으로 컨테이너를 생성하고 실행한다.

MySQL은 실행 시 반드시 루트 비밀번호 설정이 필요하다.

EX)

```bash
docker run --name mysql-container \
-e MYSQL_ROOT_PASSWORD=mysecretpw \
-d \
-p 3306:3306 \
-v mysql-data:/var/lib/mysql \
mysql:latest
```

- 3306:3306 → 로컬에서 MySQL 접속 가능
- /var/lib/mysql → 실제 DB 데이터 저장 위치
- v 옵션 없으면 컨테이너 삭제 시 데이터도 삭제됨

---

## 💻 터미널 접속 및 로그인

### 📌 설명

docker exec로 실행 중인 컨테이너 내부에서 MySQL 클라이언트를 실행한다.


EX)

```bash
docker exec -it mysql-container mysql -u root -p
```

- it → 터미널 인터랙티브 모드
- p → 비밀번호 입력 요구

---

### 📌 Bash로 컨테이너 내부 진입 (디버깅)

```bash
docker exec -it mysql-container bash
```


---

## 🧾 기본 SQL 명령어

```sql
SHOW DATABASES;
CREATE DATABASE testdb;
USE testdb;
SHOW TABLES;
```


---

## 📊 로그 확인 (중요)

```bash
docker logs mysql-container
docker logs -f mysql-container
```


---

# 🐘 PostgreSQL

## 🧱 컨테이너 실행

### 📌 설명

PostgreSQL은 기본 계정이 postgres이며, 비밀번호 설정이 필수이다.


EX)

```bash
docker run --name postgres-container \
-e POSTGRES_PASSWORD=mysecretpw \
-d \
-p 5432:5432 \
-v postgres-data:/var/lib/postgresql/data \
postgres:latest
```

- 5432 → PostgreSQL 기본 포트
- /var/lib/postgresql/data → 데이터 저장 위치

---

## 💻 터미널 접속

```bash
docker exec -it postgres-container psql -U postgres
```


---

## 🧾 psql 메타 명령어

```sql
\l      -- 데이터베이스 목록
\c testdb  -- DB 접속
\dt     -- 테이블 목록
\q      -- 종료
```


---

## 📊 로그 확인

```bash
docker logs postgres-container
docker logs -f postgres-container
```


---

# 🟥 Redis

## 🧱 컨테이너 실행

### 📌 설명

Redis는 기본적으로 비밀번호 없이 빠르게 실행 가능한 인메모리 DB이다.

---

EX)

```bash
docker run --name redis-container \
-d \
-p 6379:6379 \
redis:latest
```

- 6379 → Redis 기본 포트
- 별도 설정 없이 바로 사용 가능

---

## 💻 터미널 접속

```bash
docker exec -it redis-container redis-cli
```


---

## 🧾 기본 명령어

```bash
SET mykey "Hello, Redis!"
GET mykey
KEYS *
DEL mykey
```


---

## 📊 로그 확인

```bash
docker logs redis-container
docker logs -f redis-container
```


---

# 🐳 공통 Docker 관리 명령어

## 📌 컨테이너 상태 확인

```bash
docker ps      # 실행 중
docker ps -a   # 전체 (종료 포함)
```


---

## 📌 컨테이너 제어

```bash
docker stop mysql-container
docker start mysql-container
docker restart mysql-container
```


---

## 📌 컨테이너 삭제

```bash
docker rm mysql-container
docker rm -f mysql-container   # 강제 삭제
```


---

## 📌 컨테이너 내부 접속

```bash
docker exec -it mysql-container bash
```


---

## 📌 로그 확인

```bash
docker logs mysql-container
docker logs -f mysql-container
```


---

# 💡 핵심 개념 정리

## 🔑 Docker 흐름

```text
이미지 → 컨테이너 생성(run) → 실행 → 접속(exec)
```


---

## 🔑 포트 포워딩

```bash
-p 3307:3306
```

👉 로컬 3307 → 컨테이너 3306 연결


---

