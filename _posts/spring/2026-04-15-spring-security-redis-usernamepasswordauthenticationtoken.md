---
layout: post
title: "[Spring Security & Redis] UsernamePasswordAuthenticationToken"
date: 2026-04-15
categories: [spring]
tags: ['spring_security', 'spring', 'redis', 'UserNamePasswordAuthenticationToken']
last_modified_at: 2026-04-23
---



## Spring Security : UsernamePasswordAuthenticationToken 구조와 동작 원리

`UsernamePasswordAuthenticationToken`은 Spring Security에서 인증(Authentication) 처리를 위해 사용되는 대표적인 구현체이다. 이 객체의 핵심은 **인증 요청 객체**와 **인증 완료 객체**라는 두 가지 역할을 하나의 클래스가 모두 수행한다는 점이며, 생성자에 전달되는 인자(Argument)의 개수에 따라 객체의 상태와 역할이 명확히 구분된다.


---

### 인증 객체의 핵심 구성 요소

Spring Security의 인증 객체는 인증과 인가를 처리하기 위해 세 가지 주요 데이터를 관리한다. 다양한 인증 방식(일반 폼 로그인, OTP, OAuth 등)을 유연하게 수용하기 위해 `principal`과 `credentials`는 `Object` 타입으로 설계되어 있다.


- **Principal (주체)**
  - **설명:** 인증을 시도하거나 인증이 완료된 사용자의 식별 정보이다.
  - **예시:** 로그인 시도 시에는 `user@test.com`과 같은 문자열 아이디가 할당되며, 인증이 완료된 이후에는 `UserDetails` 구현체 객체가 할당된다.
- **Credentials (증명 정보)**
  - **설명:** 주체가 본인임을 증명하기 위한 보안 데이터이다.
  - **예시:** 일반 로그인에서는 사용자가 입력한 `password` 문자열이 할당된다. 인증 완료 후에는 보안을 위해 `null`로 비워두는 것이 일반적이다.
- **Authorities (권한 목록)**
  - **설명:** 인증된 주체에게 부여된 접근 권한들의 집합이다.
  - **예시:** `ROLE_USER`, `ROLE_ADMIN`과 같은 형태로 인가(Authorization) 로직에서 참조된다.

### 생성자 시그니처에 따른 역할 구분

동일한 클래스지만 생성 시 주입하는 인자의 개수에 따라 토큰의 내부 상태(`authenticated`)와 사용 목적이 달라진다.

- **인증 요청 객체 (2-Argument Constructor)**
  - **설명:** 사용자가 전달한 입력값을 기반으로 생성하는 미인증 상태의 임시 토큰이다. 내부 상태값인 `authenticated`가 `false`로 설정된다.
  - **예시:** 로그인 필터에서 클라이언트의 이메일과 비밀번호를 추출하여 아래와 같이 생성한다. 이 객체에 담긴 비밀번호(`credentials`)는 이후 `AuthenticationManager`가 DB의 암호화된 비밀번호와 대조(`matches`)하는 데 사용된다.Java
```java
Authentication requestToken = new UsernamePasswordAuthenticationToken(email, password);
```


- **인증 완료 객체 (3-Argument Constructor)**
  - **설명:** 내부 검증 로직이 성공적으로 수행된 후, 최종 사용자 정보와 권한을 담아 생성하는 토큰이다. `authenticated` 상태가 `true`로 설정된다.
  - **예시:** 검증이 끝난 후, 메모리에 비밀번호가 남아있는 보안 위험을 방지하기 위해 `credentials` 파라미터에 `null`을 전달하여 객체를 생성한다.Java
```java
Authentication authenticatedToken = new UsernamePasswordAuthenticationToken(userDetails, null, authorities);
```

### 전체 인증 처리 흐름

실제 애플리케이션에서 `UsernamePasswordAuthenticationToken`이 상태 변화를 겪으며 처리되는 과정은 다음과 같다.

- **로그인 데이터 인입:** 클라이언트가 식별자(email)와 증명 정보(password)를 서버로 전송한다.
- **요청 토큰 생성:** 전송된 데이터를 기반으로 미인증 상태의 2-Argument Token을 생성한다.
- **토큰 검증:** `AuthenticationManager`가 요청 토큰을 전달받아 내부 `UserDetailsService`를 호출해 DB 정보를 조회하고, 입력된 평문 비밀번호와 저장된 암호화 비밀번호를 대조한다.
- **완료 토큰 생성:** 검증에 성공하면 `UserDetails` 객체와 추출된 권한 정보를 바탕으로 인증 완료 상태의 3-Argument Token을 생성한다.
- **보안 컨텍스트 저장:** 최종 생성된 인증 객체를 `SecurityContextHolder`에 저장하여 애플리케이션 전반에서 로그인 상태를 유지하도록 처리한다.
- **JWT 인증 방식에서의 응용 예시:**
  - JWT 토큰 필터에서는 이미 서명 검증을 통해 신원 확인이 끝난 상태이므로 비밀번호 대조 과정이 필요하지 않다. 따라서 DB 검증 과정 없이 파싱된 토큰 정보를 바탕으로 즉시 3-Argument 생성자를 호출하여 인증 완료 객체를 만들고 Security Context에 등록한다.
### 상태 비교 요약

| **구분** | **2-Argument 생성자** | **3-Argument 생성자** |
| --- | --- | --- |
| **사용 목적** | 인증 요청 (로그인 시도 검증용) | 인증 완료 (로그인 성공 유지용) |
| **Authenticated** | `false` | `true` |
| **Principal** | 사용자 식별자 (예: Email String) | 검증된 사용자 객체 (예: UserDetails) |
| **Credentials** | 본인 증명 정보 (예: Password) | `null` (보안을 위해 메모리에서 제거) |
| **Authorities** | 없음 | 부여된 권한 목록 |
| **사용 위치** | `AuthenticationManager.authenticate()` 파라미터 | `SecurityContextHolder` 컨텍스트 저장 |

