---
layout: post
title: "[Spring Security & Redis] 인증 구현 가이드"
date: 2026-04-22
categories: [spring]
tags: ['redis', 'spring_security']
last_modified_at: 2026-04-23
---



# Spring Security 및 Redis 기반 세션 인증 구현 가이드

## 개요

- JWT 없이 Spring Security, Spring Session, Redis 조합으로 세션 기반 인증을 구현한다.
- 로그인 시 생성된 SecurityContext를 HTTP 세션에 저장하고, Spring Session이 이를 Redis에 자동으로 외부화한다.
- 서버가 여러 대로 늘어나도 Redis에서 동일한 세션을 공유하여 시스템의 수평 확장성을 확보할 수 있다.
## 주요 개념 이해: SecurityContext

- **정의**: SecurityContext는 현재 애플리케이션을 사용 중인 인증된 사용자의 신분증(Authentication)을 담아두는 보관소 역할을 한다.
- **특징**: 로그인이 성공하면 사용자 정보가 이 컨텍스트에 저장되며, SecurityContextHolder를 통해 스레드 로컬(ThreadLocal) 방식으로 관리된다.
- **이점**: 컨트롤러나 서비스 로직 등 애플리케이션의 어느 계층에서든 DB를 매번 다시 조회할 필요 없이, 현재 로그인한 사용자의 정보를 즉시 꺼내어 사용할 수 있다.
## 프로젝트 의존성

```text
implementation 'org.springframework.boot:spring-boot-starter-security'
implementation 'org.springframework.session:spring-session-data-redis'
implementation 'org.springframework.boot:spring-boot-starter-data-redis'
```


---

가독성을 높이기 위해 문서의 전체적인 구조를 다듬고, 요청하신 `SecurityContext`의 개념과 인증 클래스(`CustomUserDetails`, `CustomUserDetailsService`)의 호출 흐름을 자연스럽게 통합했습니다.

기존에 작성하셨던 설정 코드와 엔드포인트 내용도 빠짐없이 유지하여, 노션에 바로 복사해 사용하시기 좋게 마크다운 문법으로 깔끔하게 정리해 드립니다.


---

## 핵심 구성 요소 및 호출 흐름

### 사용자 인증 처리 인터페이스 (UserDetails & UserDetailsService)

사용자가 로그인을 시도할 때, Spring Security의 AuthenticationManager가 아래 두 클래스를 순차적으로 호출하여 인증을 수행한다.

- **CustomUserDetailsService (DB 조회 역할) - **Java
  - 로그인 요청 시, 사용자가 입력한 이메일을 기반으로 `loadUserByUsername` 메서드가 자동으로 호출된다.
  - DB에서 사용자를 찾아와 Spring Security가 내부적으로 처리할 수 있는 규격(`CustomUserDetails`)으로 변환하여 반환한다.
```java
@Service
@RequiredArgsConstructor
public class CustomUserDetailsService implements UserDetailsService {
    private final UserRepository userRepository;

    @Override
    public UserDetails loadUserByUsername(String email) throws UsernameNotFoundException {
        User user = userRepository.findByEmail(email)
            .orElseThrow(() -> new UsernameNotFoundException("User not found with email: " + email));
        return CustomUserDetails.from(user);
    }
}
```


- **CustomUserDetails (인증 정보 보관 객체)**Java
  - `UserDetails`와 `Serializable`을 함께 구현한다.
  - 직렬화(`Serializable`)를 구현하는 이유는 인증이 성공한 후 이 객체가 SecurityContext에 담긴 채로 Redis에 저장되어야 하기 때문이다.
```java
@Getter
public class CustomUserDetails implements UserDetails, Serializable {
    private static final long serialVersionUID = 1L;

    private final Long userId;
    private final String email;
    private final String password;

    public CustomUserDetails(Long userId, String email, String password) {
        this.userId = userId;
        this.email = email;
        this.password = password;
    }

    public static CustomUserDetails from(User user) {
        return new CustomUserDetails(user.getId(), user.getEmail(), user.getPassword());
    }

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return Collections.singletonList(new SimpleGrantedAuthority(UserRole.USER.getRole()));
    }

    @Override
    public String getPassword() { return password; }

    @Override
    public String getUsername() { return email; }

    @Override
    public boolean isAccountNonExpired() { return true; }

    @Override
    public boolean isAccountNonLocked() { return true; }

    @Override
    public boolean isCredentialsNonExpired() { return true; }

    @Override
    public boolean isEnabled() { return true; }
}
```


### 환경 및 보안 설정 (Configuration)

- **SessionConfig (Redis 세션 저장소 활성화)**Java
  - `@EnableRedisHttpSession`을 선언하여 기존 WAS의 메모리 기반 세션을 Redis 기반 세션으로 전환한다.
```java
@Configuration
@EnableRedisHttpSession
public class SessionConfig {
    @Bean
    public RedisSerializer<Object> springSessionDefaultRedisSerializer() {
        return RedisSerializer.java();
    }
}
```


- **SecurityConfig (필터 체인 설정)**Java
```java
@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
public class SecurityConfig {
    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(AbstractHttpConfigurer::disable)
            .securityContext(ctx -> ctx.securityContextRepository(securityContextRepository()))
            .sessionManagement(session -> session
                .sessionCreationPolicy(SessionCreationPolicy.IF_REQUIRED)
                .maximumSessions(1)
                .maxSessionsPreventsLogin(false)
            )
            .authorizeHttpRequests(auth -> auth
                .requestMatchers(SECURITY_EXCLUDE_PATHS).permitAll()
                .anyRequest().permitAll()
            )
            .formLogin(AbstractHttpConfigurer::disable)
            .httpBasic(AbstractHttpConfigurer::disable)
            .exceptionHandling(ex -> ex
                .authenticationEntryPoint(/* 401 JSON 응답 처리 로직 */)
            );
        return http.build();
    }

    @Bean
    public SecurityContextRepository securityContextRepository() {
        return new HttpSessionSecurityContextRepository();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```


| **설정 속성** | **역할 설명** |
| --- | --- |
| **HttpSessionSecurityContextRepository** | 인증 정보를 HTTP 세션에 저장 및 로드하며, Spring Session이 이를 탐지하여 Redis로 외부화함 |
| **maximumSessions(1)** | 동일 계정의 동시 접속 세션을 1개로 제한함 |
| **maxSessionsPreventsLogin(false)** | 새로운 로그인 요청 시 기존의 이전 세션을 자동으로 만료시킴 |
| **formLogin / httpBasic 비활성화** | REST API 환경에 맞추어 불필요한 기본 인증 UI를 제거함 |

### 인증 서비스 로직 (AuthService)

- **로그인 처리 흐름 구현**Java
```java
@Service
@RequiredArgsConstructor
public class AuthService {
    // ... 의존성 주입 생략 ...

    public LoginResponse login(LoginRequest loginRequest, HttpServletRequest request, HttpServletResponse response) {

        // 인증 토큰 생성 및 검증 요청
        Authentication authentication = authenticationManager.authenticate(
            new UsernamePasswordAuthenticationToken(
                loginRequest.getEmail(),
                loginRequest.getPassword()
            )
        );

        // 비어있는 SecurityContext 생성 후 검증된 인증 객체 등록
        SecurityContext context = SecurityContextHolder.createEmptyContext();
        context.setAuthentication(authentication);
        SecurityContextHolder.setContext(context);

        // HTTP 세션에 저장 (Spring Session에 의해 Redis로 자동 동기화됨)
        securityContextRepository.saveContext(context, request, response);

        // 로그인 완료 사용자 정보 응답 반환
        CustomUserDetails userDetails = (CustomUserDetails) authentication.getPrincipal();
        return LoginResponse.builder()
            .userId(userDetails.getUserId())
            .email(userDetails.getEmail())
            .build();
    }
}
```


## 전체 시스템 인증 파이프라인

- **최초 로그인 절차**
  - 클라이언트가 이메일과 비밀번호 데이터로 `POST /api/auth/login`을 호출한다.
  - `AuthenticationManager`가 `CustomUserDetailsService`를 호출해 DB에서 사용자 정보를 가져온다.
  - `BCryptPasswordEncoder`가 사용자가 입력한 비밀번호와 DB의 암호화된 비밀번호를 대조하여 검증한다.
  - 검증 성공 시 `SecurityContext`가 생성되고, `HttpSession`에 저장된다.
  - Spring Session 필터가 이를 가로채어 Redis에 세션 데이터를 해시 구조로 저장한다.
  - 클라이언트에게 인증 증명서인 `JSESSIONID` 쿠키가 반환된다.

- **이후 API 요청 (인증 유지 절차)**
  - 클라이언트가 헤더에 쿠키(`JSESSIONID`)를 포함하여 보호된 API를 요청한다.
  - Spring Session이 해당 쿠키값을 키로 삼아 Redis에서 세션 데이터를 찾아온다.
  - `HttpSessionSecurityContextRepository`가 Redis 데이터로부터 `SecurityContext`를 스레드 로컬에 복원한다.
  - 애플리케이션은 사용자가 로그인된 상태임을 인지하고 후속 비즈니스 로직을 수행한다.

- **로그아웃 절차 (세션 만료)**
  - 클라이언트가 `GET /api/auth/logout`을 호출한다.
  - `SecurityContextHolder.clearContext()`가 실행되어 현재 스레드 내 인증 정보가 제거된다.
  - `session.invalidate()`가 호출되어 Redis 서버에 저장된 세션 키와 데이터가 영구적으로 삭제된다.
