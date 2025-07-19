---
layout: post
title: "OAuth2 로그인 구현 [Kakao]"
categories: [SpringBoot, API, OAuth2, Kakao]
tags: [Blog, Oauth2, Social-login]
author: "Hyomyeong"
---
 해당글은 공부 목적으로 정리한 개인적인 기록입니다.
 정확하지 않은 정보가 포함될 수 있으며, 최신 기술 동향이나 공식 문서와는 차이가 있을 수 있습니다!
 처음 구현하시는 분들께 작은 도움이 되었으면 하며, 혹시 틀리 내용이 있다면 댓그로 알려주시면 감사하겠습니다.

 ---
 
 ### ✅1. Oauth2
 Oauth2는 **권환 위임(Authorization Delegation)**을 위한 표준 프로토콜이다.
 쉽게 말해, A 서비스가 B 서비스의 리소스(정보) 등에 접근 할 수 있도록, 사용자가 허락해주는 방식을 제공한다.
 예시 :
 - 특정 웹사이트 가입 시, 카카오 계정으로 로그인할 수 있다.

 ---

 ### ✅2. 주요 용어
| 용어                       | 설명                                   |
| ------------------------ | ------------------------------------ |
| **Resource Owner**       | 사용자 (나)                              |
| **Client**               | 내 서비스를 사용하는 웹사이트 또는 앱                |
| **Authorization Server** | 카카오 로그인 서버                           |
| **Resource Server**      | 사용자의 리소스를 저장한 서버 (예: 카카오 프로필, 이메일 등) |

---
### ✅3. OAuth2 기본 흐름(Authorization Code Grant 기준)
1. 사용자가 로그인 요청
    - 사용자가 "카카오 로그인" 버튼 클릭
2. 인증 요청 리다이렉트
    - 사용자를 카카오 인증 서버 (https://kauth.kakao.com/oauth/authorize)로 리다이렉트
3. Authorization Code 발급
    - 사용자가 동의하면 카카오는 authorization code를 클라이언트에게 보냄 (콜백 URL)
4. Access Tokken 요청
    - 클라리언트는 받은 code를 이용해, 카카오에 access token을 요청
5. Acess Token 발급
    - 카카오는 access token을 발급함
6. API 요청 (프로필 등)
    - 클라이언트는 사용자의 정보(프로필, 닉네임, 이메일 등)를 카카오 API로부터 받아옴

---
### ✅4. 구현(Spring Boot)
(기본적인 구성은 생략)
```java

```
