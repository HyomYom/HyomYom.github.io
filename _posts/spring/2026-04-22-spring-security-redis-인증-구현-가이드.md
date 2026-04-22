---
layout: post
title: "[Spring Security & Redis] 인증 구현 가이드"
date: 2026-04-22
categories: [spring]
tags: ['redis', 'spring_security']
---



# Spring Security 및 Redis 기반 세션 인증 구현 가이드

## 개요

- JWT 없이 Spring Security, Spring Session, Redis 조합으로 세션 기반 인증을 구현한다.
- 로그인 시 생성된 SecurityContext를 HTTP 세션에 저장하고, Spring Session이 이를 Redis에 자동으로 외부화한다.
- 서버가 여러 대로 늘어나도 Redis에서 동일한 세션을 공유하여 시스템의 수평 확장성을 확보할 수 있다.
## 주요 개념 이해: SecurityContext

- 정의: SecurityContext는 현재 애플리케이션을 사용 중인 인증된 사용자의 신분증(Authentication)을 담아두는 보관소 역할을 한다.
- 특징: 로그인이 성공하면 사용자 정보가 이 컨텍스트에 저장되며, SecurityContextHolder를 통해 스레드 로컬(ThreadLocal) 방식으로 관리된다.
- 이점: 컨트롤러나 서비스 로직 등 애플리케이션의 어느 계층에서든 DB를 매번 다시 조회할 필요 없이, 현재 로그인한 사용자의 정보를 즉시 꺼내어 사용할 수 있다.
## 프로젝트 의존성

```text
implementation 'org.springframework.boot:spring-boot-starter-security'
implementation 'org.springframework.session:spring-session-data-redis'
implementation 'org.springframework.boot:spring-boot-starter-data-redis'
```


---

가독성을 높이기 위해 문서의 전체적인 구조를 다듬고, 요청하신 SecurityContext의 개념과 인증 클래스(CustomUserDetails, CustomUserDetailsService)의 호출 흐름을 자연스럽게 통합했습니다.

기존에 작성하셨던 설정 코드와 엔드포인트 내용도 빠짐없이 유지하여, 노션에 바로 복사해 사용하시기 좋게 마크다운 문법으로 깔끔하게 정리해 드립니다.


---

## 핵심 구성 요소 및 호출 흐름

### 사용자 인증 처리 인터페이스 (UserDetails & UserDetailsService)

사용자가 로그인을 시도할 때, Spring Security의 AuthenticationManager가 아래 두 클래스를 순차적으로 호출하여 인증을 수행한다.

- CustomUserDetailsService (DB 조회 역할) - Java
- CustomUserDetails (인증 정보 보관 객체)Java
### 환경 및 보안 설정 (Configuration)

- SessionConfig (Redis 세션 저장소 활성화)Java
- SecurityConfig (필터 체인 설정)Java
### 인증 서비스 로직 (AuthService)

- 로그인 처리 흐름 구현Java


## 전체 시스템 인증 파이프라인

- 최초 로그인 절차
- 이후 API 요청 (인증 유지 절차)
- 로그아웃 절차 (세션 만료)
