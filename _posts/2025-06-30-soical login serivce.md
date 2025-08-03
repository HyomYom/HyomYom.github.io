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
![kakao dev 앱생성](/assets/images/login/oauth2-2-2025.jpeg)

카카오 developers(https://developers.kakao.com)에 접속해 로그인을하면 탭에서 앱이라는 항목에 접근을 할 수 있는데, 이곳에서 앱 생성을 통해 카카오톡 로그인을 구현하려는 서비스의 정보를 등록 및 설정해야 한다

![설정 목록](/assets/images/login/oauth2-3-2025.jpeg)

앱 생성 후 해당 앱을 클릭하면 대시보드로 이동하게 되는데, 로그인 서비스를 사용하기 위해 필수로 설정해야 하는 설정 목록을 보여준다.

### 1. 카카오로그인 설정
![로그인 설정](/assets/images/login/oauth2-4-2025.jpeg)
가장 기본이 되는 설정으로, 활성화 해야지만 카카오 계정을 통해 OAuth2 인증을 진행할 수 있다.

### 2. Redirect Url 설정 
![Redirect 설정](/assets/images/login/oauth2-5-2025.jpeg)
다음은 카카로 로그인에 사용할 리다이렉트 URI설정이다.<br>
카카오 로그인 후 인가코드를 얻을 수 있는데, 등록된 해당 주소로 다음 코드를 전달하기 때문에 필수로 지정해야하는 설정이다.

### 3. 동의항목 설정
![동의항목 설정](/assets/images/login/oauth2-6-2025.jpeg)
카카오 로그인 시 사용자에게 어떤 정보(예: 이메일, 닉네임, 프로필 사진 등)를 요청할지 설정하는 부분이다.<br>
설정한 항목에 따라 로그인 시 카카오가 사용자에게 동의를 요청하게 되며, 추후 yml 설정파일과 연관되기 때문에 주의하여 설정하여야한다.

---
## ✅4-2. 구현(Spring Boot)
소셜 로그인을 구현 할 때 OAuth2-Client 또는 직접구현 방법이 있다.

로그인 및 권환 요청을 직접 구현할 경우

1. 사용자 → 카카오 로그인 페이지로 리디렉션

2. 인가 코드(code) 수신

3. 서버에서 access token 요청

4. access token으로 사용자 정보 요청

5. 세션 또는 JWT 발급 → 로그인 완료 (서비스 구성에 따른 개별 설정)

다음 과정을 거쳐야하는데, SpringSecurity, OAuth2-Client를 사용할 경우 모든 절차를 자동으로 처리해준다.

### 1. 필수 라이브러리 추가
- OAuth2 소셜 로그인에 필요한 필수 라이브러리 추가
    - build.gradle - Spring Security, OAuth2
```java
    implementation 'org.springframework.boot:spring-boot-starter-security'
    implementation 'org.springframework.boot:spring-boot-starter-oauth2-client'
```

starter-oauth2-client는 로그인, 인증 흐름, 사용자 정보 요청, 리다이랙션 처리 등 클리언트 측 로직을 포함하고 있기 때문에 다음 기능을 수행하기 위해서는 꼭 추가해야 할 라이브러리이다.

### 2. Application.yml 정
```java
spring:
  security:
    oauth2:
      client:
        registration:
          kakao:
            client-id: {REST_API_KEY}
            redirect-uri: "{baseUrl}/login/oauth2/code/{registrationId}"
            authorization-grant-type: authorization_code
            scope: profile_nickname, profile_image
            client-name: Kakao
        provider:
          kakao:
            authorization-uri: https://kauth.kakao.com/oauth/authorize
            token-uri: https://kauth.kakao.com/oauth/token
            user-info-uri: https://kapi.kakao.com/v2/user/me
            user-name-attribute: id

```
scope 값은 앞서 카카오 개발자 콘솔의 동의항목 설정에서 허용 했던 항목들을 입력해야한다
설정 외 값을 입력하게 되면 오류가 발생하기 때문에 주의해야한다.
provider 옵션은 앞서 설명한 것처럼, Spring Security는 등록 된 uri를 통해 AccessToken, UserInfo등을 자동으로 처리한다.

### 3. Security 설정(SecurityConfig.java)
SecurityFilterChain의 oauth2Login을 다음과 같이 구현한다
```java
                .oauth2Login(outh2 ->
                            outh2
                                    .loginPage("/login")
                                    .userInfoEndpoint(user ->
                                                user
                                                        .userService(customOAuth2UserService)
                                            )
                                    .defaultSuccessUrl("/profile", true)
                                    .failureHandler((request, response, exception) -> {
                                        exception.printStackTrace(); // 콘솔에서 확인 가능
                                        response.sendRedirect("/login?error");
                                    })
                        )
```
loginPage : oauth2 소셜 로그인을 진행할 경로 설정
userInfoEndpoin : 로그인 후 Access Token과 UserInfo를 커스텀으로 처리 할 수 있는 class 경로 설정
failureHandler : 소셜 로그인 실패 시 발생하는 예외 상황을 모니터링 및 확인 할 수 있는 설정


### 4. OAuth2UserService 구현
UserService를 통해 카카오에서 받아온 사용자 정보를 가공할 수 있다.
카카오 API에서 내려주는 JSON 데이터 구조에 맞춰 닉네임, 프로필 이미지, 이메일 등을 추출 할 수 있다.

```java
@Getter
@Builder
@AllArgsConstructor
public class OAuthAttributes {
    private final Map<String, Object> attributes;
    private final String provider;
    private final String providerId;
    private final String email;
    private final String nickname;


    public static OAuthAttributes of(String provider, Map<String, Object> attributes) {
        switch (provider){
            case "kakao" -> {return ofKaKao(attributes);}
            default      -> throw new IllegalArgumentException("지원하지 않는 provider");

        }
    }

    public static OAuthAttributes ofKaKao(Map<String, Object> attrs) {
        String providerId = String.valueOf(attrs.get("id"));
        Map<String, Object> kakaoAccount = (Map<String, Object>) attrs.get("kakao_account");
        Map<String, Object> profile = (Map<String, Object>) kakaoAccount.get("profile");

        return OAuthAttributes.builder()
                .provider("kakao")
                .providerId(providerId)
                .email((String) kakaoAccount.get("email"))
                .nickname((String) profile.get("nickname"))
                .attributes(attrs)
                .build();

    }
}
```
추후 추가 될 소셜 로그인을 일관되게 처리 할 수 있도록 Attributes 클래스를 만들어 다음과 같이 처리를 유도했다.
각 소셜 로그인이 제공하는 JSON 구조에 따라 메소드를 작성하면 된다.

```java
@Slf4j
@Service
@RequiredArgsConstructor
public class CustomOAuth2UserService implements OAuth2UserService<OAuth2UserRequest, OAuth2User> {

    private final MemberRepository memberRepository;

    @Override
    public OAuth2User loadUser(OAuth2UserRequest userRequest) throws OAuth2AuthenticationException {
        log.info("🔐 OAuth2 로그인 시도 중...");

        DefaultOAuth2UserService delegate = new DefaultOAuth2UserService();
        OAuth2User oAuth2User = delegate.loadUser(userRequest);
        String provider = userRequest.getClientRegistration().getRegistrationId();


        OAuthAttributes attr = OAuthAttributes.of(provider, oAuth2User.getAttributes());


        Member member  = memberRepository.findByProviderAndProviderId(provider, attr.getProviderId())
                .map(m -> {m.update(attr); return m;})
                .orElseGet(() -> memberRepository.save(Member.of(attr)));

        return new DefaultOAuth2User(Collections.singleton(new SimpleGrantedAuthority("ROLE_"+member.getRole())), attr.getAttributes(), "id");
    }
}
```
카카오 API에서 제공하는 유저 정보를 추출하여 Member Table에 유저정보를 저장하는 로직과, 저장 후 유저 정보 및 권한을 담아 SecurityContext에 설정하는 부분까지 작성해보았다.
이후 로그인 구성에 따라 JWT Token 발급 등의 로직을 원한다면 이를 기반으로 확장하여 개발할 수 있다.

---
## ✅5. Test & 주의사항
- scope 값은 반드시 카카오 개발자 콘솔에서 허용한 항목과 동일해야 함.

- redirect-uri는 로컬 테스트 시 http://{사용자등록url}/login/oauth2/code/kakao 형식이어야 함.

