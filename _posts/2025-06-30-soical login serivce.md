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
## ✅ 1. Oauth2

 Oauth2는 **권환 위임(Authorization Delegation)**을 위한 표준 프로토콜이다.
 쉽게 말해, A 서비스가 B 서비스의 리소스(정보) 등에 접근 할 수 있도록, 사용자가 허락해주는 방식을 제공한다.
 예시 :
 - 특정 웹사이트 가입 시, 카카오 계정으로 로그인할 수 있다.

 ---
## ✅ 2. 주요 용어

| 용어                       | 설명                                   |
| ------------------------ | ------------------------------------ |
| **Resource Owner**       | 사용자 (나)                              |
| **Client**               | 내 서비스를 사용하는 웹사이트 또는 앱                |
| **Authorization Server** | 카카오 로그인 서버                           |
| **Resource Server**      | 사용자의 리소스를 저장한 서버 (예: 카카오 프로필, 이메일 등) |

---
## ✅ 3. OAuth2 기본 흐름(Authorization Code Grant 기준)
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
## ✅4-1. 구현(카카오 개발자 콘솔 설정)
![kakao dev 앱생성](/assets/img/oauth2-2-2025.jpeg)

카카오 developers(https://developers.kakao.com)에 접속해 로그인을하면 탭에서 앱이라는 항목에 접근을 할 수 있는데, 이곳에서 앱 생성을 통해 카카오톡 로그인을 구현하려는 서비스의 정보를 등록 및 설정해야 한다

![설정 목록](/assets/img/oauth2-3-2025.jpeg)

앱 생성 후 해당 앱을 클릭하면 대시보드로 이동하게 되는데, 로그인 서비스를 사용하기 위해 필수로 설정해야 하는 설정 목록을 보여준다.

### 1. 카카오로그인 설정
![로그인 설정](/assets/img/oauth2-4-2025.jpeg)
가장 기본이 되는 설정으로, 활성화 해야지만 카카오 계정을 통해 OAuth2 인증을 진행할 수 있다.

### 2. Redirect Url 설정
![Redirect 설정](/assets/img/oauth2-5-2025.jpeg)
다음은 카카로 로그인에 사용할 리다이렉트 URI설정이다.
카카오 로그인 후 인가코드를 얻을 수 있는데, 등록된 해당 주소로 다음 코드를 전달하기 때문에 필수로 지정해야하는 설정이다.

### 3. 동의항목 설정
![동의항목 설정](/assets/img/oauth2-6-2025.jpeg)
카카오 로그인 시 사용자에게 어떤 정보(예: 이메일, 닉네임, 프로필 사진 등)를 요청할지 설정하는 부분이다.
설정한 항목에 따라 로그인 시 카카오가 사용자에게 동의를 요청하게 되며, 추후 yml 설정파일과 연관되기 때문에 주의하여 설정하여야한다.


---
## ✅4-2. 구현(Spring Boot)
(기본적인 Spring Boot 구성은 생략)

- OAuth@ 소셜 로그인에 필요한 필수 라이브러리 추가
    - build.gradle - Spring Security, OAuth2
```java
    implementation 'org.springframework.boot:spring-boot-starter-security'
    implementation 'org.springframework.boot:spring-boot-starter-oauth2-client'
```

starter-oauth2-client는 로그인, 인증 흐름, 사용자 정보 요청, 리다이랙션 처리 등 클리언트 측 로직을 포함하고 있기 때문에 다음 기능을 수행하기 위해서는 꼭 추가해야 할 라이브러리이다.

- 

