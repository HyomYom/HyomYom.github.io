---
layout: post
title: "[Spring Security & Redis] UsernamePasswordAuthenticationToken"
date: 2026-04-15
categories: [spring]
tags: ['spring_security', 'spring', 'redis', 'UserNamePasswordAuthenticationToken']
last_modified_at: 2026-04-22
---



## Spring Security : UsernamePasswordAuthenticationToken 구조와 동작 원리

UsernamePasswordAuthenticationToken은 Spring Security에서 인증(Authentication) 처리를 위해 사용되는 대표적인 구현체이다. 이 객체의 핵심은 인증 요청 객체와 인증 완료 객체라는 두 가지 역할을 하나의 클래스가 모두 수행한다는 점이며, 생성자에 전달되는 인자(Argument)의 개수에 따라 객체의 상태와 역할이 명확히 구분된다.


---

### 인증 객체의 핵심 구성 요소

Spring Security의 인증 객체는 인증과 인가를 처리하기 위해 세 가지 주요 데이터를 관리한다. 다양한 인증 방식(일반 폼 로그인, OTP, OAuth 등)을 유연하게 수용하기 위해 principal과 credentials는 Object 타입으로 설계되어 있다.

- Principal (주체)
- Credentials (증명 정보)
- Authorities (권한 목록)
### 생성자 시그니처에 따른 역할 구분

동일한 클래스지만 생성 시 주입하는 인자의 개수에 따라 토큰의 내부 상태(authenticated)와 사용 목적이 달라진다.

- 인증 요청 객체 (2-Argument Constructor)


- 인증 완료 객체 (3-Argument Constructor)
### 전체 인증 처리 흐름

실제 애플리케이션에서 UsernamePasswordAuthenticationToken이 상태 변화를 겪으며 처리되는 과정은 다음과 같다.

- 로그인 데이터 인입: 클라이언트가 식별자(email)와 증명 정보(password)를 서버로 전송한다.
- 요청 토큰 생성: 전송된 데이터를 기반으로 미인증 상태의 2-Argument Token을 생성한다.
- 토큰 검증: AuthenticationManager가 요청 토큰을 전달받아 내부 UserDetailsService를 호출해 DB 정보를 조회하고, 입력된 평문 비밀번호와 저장된 암호화 비밀번호를 대조한다.
- 완료 토큰 생성: 검증에 성공하면 UserDetails 객체와 추출된 권한 정보를 바탕으로 인증 완료 상태의 3-Argument Token을 생성한다.
- 보안 컨텍스트 저장: 최종 생성된 인증 객체를 SecurityContextHolder에 저장하여 애플리케이션 전반에서 로그인 상태를 유지하도록 처리한다.
- JWT 인증 방식에서의 응용 예시:
### 상태 비교 요약

