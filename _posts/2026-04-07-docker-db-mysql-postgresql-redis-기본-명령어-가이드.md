---
layout: post
title: "🐳 Docker DB (MySQL, PostgreSQL, Redis) 기본 명령어 가이드"
date: 2026-04-07
---



노션(Notion)에 붙여넣었을 때 줄바꿈이나 코드 블록이 깨지지 않도록 마크다운 여백과 형식을 수정하여 다시 정리했다.


---

## 🐳 Docker DB 기본 명령어 가이드

### 🐬 MySQL

### 컨테이너 실행

- [설명] docker run 명령어를 사용하여 MySQL 컨테이너를 백그라운드(d)에서 실행한다. 호스트와 컨테이너의 3306 포트를 연결(p)하며, 환경 변수(e)를 통해 루트 계정의 비밀번호를 필수로 설정해야 한다.


- [예시]
```java
docker run --name mysql-container -e MYSQL_ROOT_PASSWORD=mysecretpw -d -p 3306:3306 mysql:latest
```

### 터미널 접속 및 로그인

- [설명] docker exec 명령어로 실행 중인 컨테이너에 접근하여 mysql 클라이언트 프로그램을 실행한다. p 옵션을 주었기 때문에 실행 후 비밀번호 입력을 요구한다.
- [예시]
Bash

```java
docker exec -it mysql-container mysql -u root -p
```



### 기본 SQL 명령어

- [설명] 접속 후 데이터베이스 목록을 확인하거나, 새로운 데이터베이스를 생성하고 사용하는 기본적인 제어 명령어이다.
- [예시]
SQL

```java
SHOW DATABASES;
CREATE DATABASE testdb;
USE testdb;
SHOW TABLES;
```


---

### 🐘 PostgreSQL

### 컨테이너 실행

- [설명] 공식 Postgres 이미지를 기반으로 컨테이너를 실행한다. 기본 사용자 이름은 postgres이며, 환경 변수(POSTGRES_PASSWORD)를 통해 계정의 비밀번호를 설정한다. 기본 포트는 5432이다.
- [예시]
Bash

# 

docker run --name postgres-container -e POSTGRES_PASSWORD=mysecretpw -d -p 5432:5432 postgres:latest

### 터미널 접속 및 로그인

- [설명] PostgreSQL의 기본 CLI 도구인 psql을 사용하여 데이터베이스 셸에 접속한다. U 옵션으로 사용자명(postgres)을 지정한다.
- [예시]
Bash

# 

docker exec -it postgres-container psql -U postgres

### 기본 psql 메타 명령어

- [설명] 일반적인 SQL 외에도 \로 시작하는 고유의 메타 명령어를 통해 데이터베이스 시스템 정보를 확인할 수 있다.
- [예시]
SQL

# 

\l
\c testdb
\dt
\q


---

### 🟥 Redis

### 컨테이너 실행

- [설명] 인메모리 데이터 구조 저장소인 Redis를 실행한다. 별도의 초기 비밀번호 설정 없이 빠르게 띄울 수 있으며, 기본 포트는 6379를 사용한다.
- [예시]
Bash

# 

docker run --name redis-container -d -p 6379:6379 redis:latest

### 터미널 접속 및 로그인

- [설명] 컨테이너 내부에서 제공하는 redis-cli 도구를 실행하여 Redis 서버와 명령어를 주고받을 수 있는 프롬프트로 진입한다.
- [예시]
Bash

# 

docker exec -it redis-container redis-cli

### 기본 제어 명령어

- [설명] Redis는 Key-Value(키-값) 형태로 데이터를 저장한다. 데이터를 입력, 조회, 삭제하는 기본 명령어이다.
- [예시]
Plaintext

# 

SET mykey "Hello, Redis!"
GET mykey
KEYS *
DEL mykey


---

### 💡 공통 Docker 관리 명령어

### 컨테이너 제어

- [설명] 컨테이너의 상태를 확인하거나 중지/삭제할 때 사용하는 기본 명령어이다. 삭제 시에는 컨테이너가 먼저 중지되어 있어야 한다.
- [예시]
Bash

# 

docker ps
docker stop mysql-container
docker rm mysql-container

