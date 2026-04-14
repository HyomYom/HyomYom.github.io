---
layout: post
title: "[Spring Security & Redis] UsernamePasswordAuthenticationToken"
date: 2026-04-15
categories: [spring]
tags: ['spring_security', 'spring', 'redis', 'UserNamePasswordAuthenticationToken']
---



## UsernamePasswordAuthenticationToken

Spring Security에서 인증 처리에 사용하는 대표적인 Authentication 구현체이다.

핵심은 같은 클래스를 로그인 요청 객체로도 사용하고, 인증 완료 객체로도 사용한다는 점이다.

또한 생성자 인자 개수(2개 / 3개)에 따라 역할이 달라진다.


---

# 1. Authentication 객체의 핵심 구성요소

Spring Security의 인증 객체는 크게 3가지 정보를 가진다.


---

## principal 이란?

로그인하려는 사용자를 식별하는 값이다.

예:

- username
- email
- loginId
- 인증 완료 후 UserDetails 객체
```java
principal = "user@test.com"
```


---

## credentials 란?

사용자가 진짜 본인인지 증명하는 값이다.

대표적으로:

- password
- OTP 번호
- JWT 토큰
- 인증서
로그인에서는 보통 비밀번호가 들어간다.

```java
credentials = "1234"
```

즉:

> principal 은 누구인지


---

## authorities 란?

인증된 사용자의 권한 정보이다.

예:

```java
ROLE_USER
ROLE_ADMIN
```


---

# 2. 왜 principal / credentials 가 Object 타입일까?

Spring Security는 다양한 인증 방식을 지원해야 한다.

예:

- 일반 로그인 → email + password
- OTP 로그인 → phone + code
- JWT 로그인 → user + token
- OAuth 로그인 → social user info
그래서 타입을 고정하지 않고:

```java
Object principal
Object credentials
```

로 설계되었다.


---

# 3. 생성자 2개짜리 vs 3개짜리 차이


---

## 2-argument 생성자 → 인증 요청용

```java
new UsernamePasswordAuthenticationToken(
    principal,
    credentials
)
```

예:

```java
new UsernamePasswordAuthenticationToken(
    email,
    password
)
```

내부 상태:

```java
authenticated = false
```

의미:

> 아직 인증되지 않은 상태


---

## 3-argument 생성자 → 인증 완료용

```java
new UsernamePasswordAuthenticationToken(
    principal,
    credentials,
    authorities
)
```

예:

```java
new UsernamePasswordAuthenticationToken(
    userDetails,
    null,
    authorities
)
```

내부 상태:

```java
authenticated = true
```

의미:

> 인증 완료 상태


---

# 4. email / password 넣는 게 맞는가?

많이 헷갈리는 부분이다.

```java
new UsernamePasswordAuthenticationToken(
    email,
    password
)
```

이렇게 작성하는 것은 정상적인 표준 방식이다.

여기서:

즉:

> 나는 user@test.com 이고

라는 요청 객체이다.


---

# 5. credentials 에 password 넣는 게 왜 중요한가?

절대 무의미하지 않다.

로그인 인증의 핵심 데이터이다.

Spring Security 내부에서 비밀번호 비교에 사용된다.

```java
String inputPassword =
    authentication.getCredentials().toString();

String dbPassword =
    userDetails.getPassword();

passwordEncoder.matches(
    inputPassword,
    dbPassword
);
```

즉:

- 사용자가 입력한 비밀번호
- DB에 저장된 암호화 비밀번호
를 비교해서 로그인 성공 여부를 판단한다.


---

# 6. 로그인 성공 후 credentials 가 null 인 이유

인증 완료 후에는 비밀번호를 계속 들고 있을 필요가 없다.

그래서 보통:

```java
new UsernamePasswordAuthenticationToken(
    userDetails,
    null,
    authorities
)
```

이렇게 만든다.

이유:

- 인증 이미 끝남
- 비밀번호 메모리 보관 위험
- 보안상 제거하는 것이 안전함

---

# 7. 전체 로그인 흐름

## [1단계] 로그인 요청

사용자가 이메일 / 비밀번호 입력

```java
email = "user@test.com"
password = "1234"
```

