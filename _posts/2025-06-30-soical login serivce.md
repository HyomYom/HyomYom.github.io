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
 
 ###✅1. Oauth2
 Oauth2는 **권환 위임(Authorization Delegation)**을 위한 표준 프로토콜이다.
 쉽게 말해, A 서비스가 B 서비스의 리소스(정보) 등에 접근 할 수 있도록, 사용자가 허락해주는 방식을 제공한다.
 예시 :
 - 특정 웹사이트 가입 시, 카카오 계정으로 로그인할 수 있다.

 ###✅2. 주요 용어
| 용어                       | 설명                                   |
| ------------------------ | ------------------------------------ |
| **Resource Owner**       | 사용자 (나)                              |
| **Client**               | 내 서비스를 사용하는 웹사이트 또는 앱                |
| **Authorization Server** | 카카오 로그인 서버                           |
| **Resource Server**      | 사용자의 리소스를 저장한 서버 (예: 카카오 프로필, 이메일 등) |
