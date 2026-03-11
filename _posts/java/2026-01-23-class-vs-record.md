---
layout: post
title: " class vs record"
date: 2026-01-23
categories: [java]
tags: ['class', 'record']
---



# 1️⃣ class vs record

## class

```java
publicclassUser {
private String name;
privateint age;

publicUser(String name, int age) {
this.name = name;
this.age = age;
    }

public StringgetName() {return name; }
}


```

### 특징

- mutable (값 변경 가능)
- setter 존재 가능
- 상속 가능
- 로직 포함 가능
### 언제 사용?

- 상태가 변함
- 비즈니스 로직 있음
- JPA Entity
- Principal, Domain 객체

---

## record

```java
publicrecordUser(String name, int age) {}


```

### 특징

- immutable (불변)
- setter 없음
- 상속 불가
- 값 객체(value object)에 특화
### 언제 사용?

- DTO
- API Response
- JWT Claim 결과
- 단순 데이터 전달

---

## 핵심 비교


---

# 2️⃣ record vs Lombok @Value

## Lombok @Value

```java
@Value
publicclassUser {
    String name;
int age;
}


```

### 특징

- final 필드
- getter 생성
- 생성자 생성
- equals/hashCode 생성
- 컴파일 타임 코드 생성

---

## record

```java
publicrecordUser(String name, int age) {}


```

### 차이 핵심

👉 record가 가능하면 record 추천


---

# 3️⃣ JPA Entity에 record 못 쓰는 이유

### JPA Entity 요구사항

- 기본 생성자 필요
- 프록시 생성을 위한 상속 가능성
- 필드 변경 가능해야 함
### record와 충돌

- 모든 필드 final
- 기본 생성자 없음
- 상속 불가
- setter 없음
```java
@Entity
publicrecordUser(...) {}// ❌ 불가


```

👉 Entity = 상태 객체 → class만 가능


---

# 4️⃣ Lombok 없이 DTO 짜는 방법

## Java 16+ (추천)

```java
publicrecordUserResponse(String name, int age) {}


```

## Java 8~15

```java
publicclassUserResponse {
privatefinal String name;
privatefinalint age;

publicUserResponse(String name, int age) {
this.name = name;
this.age = age;
    }

public StringgetName() {return name; }
publicintgetAge() {return age; }
}


```

### 기준

- setter 없음
- 필드 final
- 생성자로만 주입

---

# 5️⃣ Spring Security Principal엔 뭐가 적절한가?

### Principal 요구사항

- 인증 이후에도 사용됨
- 권한, 사용자 정보 포함
- 확장 가능해야 함
### ❌ record (비추천)

- 불변
- 인터페이스 구현 불편
- 확장 어려움
### ⭕ class (추천)

```java
publicclassUserPrincipalimplementsUserDetails {
privatefinal Long id;
privatefinal String username;
privatefinal Collection<?extendsGrantedAuthority> authorities;

// constructor, getters
}


```

### 이유

- Spring Security와 궁합 좋음
- UserDetails 구현
- 인증 정보 확장 가능

---

# 한 줄 요약 모음

- class vs record → 행동/상태 vs 값
- record vs @Value → 표준 vs Lombok
- Entity → 무조건 class
- DTO → record가 최선
- Principal → class만 적합
