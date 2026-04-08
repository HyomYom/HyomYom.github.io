---
layout: post
title: "2주차 Spring MSA 학습 - RESTful API 설계와 스프링 프레임워크"
date: 2026-03-14
categories: [reboot]
tags: ['1주차', 'RESTful', 'spring', 'framework']
---
# 1. Spring Core & 웹 아키텍처

### ⚙️ 핵심 개념

- 강한 결합(Tight Coupling)의 문제점: 객체가 직접 new 키워드로 의존 객체를 생성하면, 하나를 수정할 때 연관된 코드를 모두 수정해야 하는 치명적인 유지보수 문제가 발생한다.
- IoC (Inversion of Control, 제어의 역전): 개발자가 직접 객체를 생성하고 제어하던 권한을 Spring 컨테이너(총괄 셰프)에게 넘기는 철학.
- DI (Dependency Injection, 의존성 주입): IoC를 구현하는 실제 기술. 클래스는 추상화된 인터페이스에만 의존하고, 실제 구현체는 Spring이 실행 시점에 주입하여 **느슨한 결합(Loose Coupling)**을 완성한다.
### 💉 DI (의존성 주입) 3가지 방식

- 생성자 주입 (Constructor Injection): 불변성 보장, 순환 참조 방지, 테스트 용이성 덕분에 강력 권장 (@RequiredArgsConstructor와 조합).
- 수정자 주입 (Setter Injection): 선택적/런타임 의존성 변경 시에만 제한적으로 사용.
- 필드 주입 (Field Injection): 코드는 간결하나 외부에서 의존성을 주입할 방법이 없어 순수 자바 테스트가 힘들어 비추천 (@Autowired 필드 부착).
### 🏛️ 계층형 아키텍처와 도메인 설계

- Controller: HTTP 요청 수신, 데이터 유효성 검증, 응답 반환 (문지기 역할).
- Service: 핵심 비즈니스 로직 처리, 트랜잭션 관리 (두뇌 역할).
- Repository: 데이터베이스 통신 (JPA, QueryDSL).

---

## 2. RESTful API 설계 & 예외 처리

### 🌐 RESTful 설계 원칙과 HTTP 속성

- 자원(Resource): URI는 명사 복수형을 사용한다. (/api/products)
- 행위(Verb): HTTP 메서드로 표현한다 (GET, POST, PUT, PATCH, DELETE). 단, 환불/승인 같은 특수 동작은 자원의 하위 리소스로 취급하여 POST로 처리한다. (POST /orders/{id}/refund)
- 안전성 (Safe): 호출해도 서버 상태가 변하지 않는 성질 ➔ GET
- 멱등성 (Idempotent): 여러 번 호출해도 결과가 똑같은 성질 ➔ GET, PUT(전체 덮어쓰기), DELETE (POST와 PATCH는 멱등성 보장 안 됨).
### 🛡️ 전역 예외 처리 및 공통 응답 구조

- Entity 노출 금지 (DTO 사용): Entity를 응답으로 내보내면 DB 스키마가 노출되고 결합도가 높아진다. 반드시 DTO를 거쳐야 한다.
- ApiResponse<T>: 어떤 상황이든 클라이언트가 결과를 예측할 수 있도록 result, data, error 구조를 가진 공통 응답 포맷을 사용한다.
- @RestControllerAdvice: * 비즈니스 로직(Service)에서는 try-catch 없이 커스텀 예외(DomainException)만 던진다.

---

## 3. 데이터 검증 & 유틸리티 라이브러리

### ✅ Spring Validation (입력값 검증)

- 동작 방식: DTO 필드에 검증 규칙 지정 ➔ Controller의 파라미터 앞에 @Valid 부착 ➔ 실패 시 MethodArgumentNotValidException 발생 (예외 핸들러가 가로채어 400 응답).
- 주요 검증: @NotBlank (문자열 빈칸 차단, 가장 안전), @NotNull, @Size, @Pattern (정규식 검사).
### 🪄 Lombok & Jackson (보일러플레이트 제거와 직렬화)

- Lombok 권장: @Getter, @RequiredArgsConstructor 위주로 사용. 불변성을 깨고 순환 참조 위험이 있는 @Data, @Setter는 지양한다.
- @Builder (빌더 패턴): 생성자 오버로딩과 Setter의 단점을 해결.
- Jackson 응답 제어: * @JsonInclude(Include.NON_NULL): 값이 null인 필드를 JSON 응답에서 아예 제외시켜 깔끔하게 만든다.
### 🗺️ MapStruct (객체 매핑 자동화)

- 특징: Entity ↔ DTO 간의 반복적인 변환 코드를 컴파일 시점에 자동 생성해 주는 도구. 리플렉션이 없어 성능 저하가 없다.
- @Mapping 활용: 이름이 다른 필드를 수동 연결하거나, 객체 내부의 중첩된 데이터를 평탄화(Flattening)하여 DTO로 손쉽게 빼낼 수 있다.

---

## 4. JPA 트랜잭션과 영속성 컨텍스트

### 🤝 @Transactional의 원리와 함정

- 동작 원리: AOP 프록시(Proxy) 기반. 실제 로직 실행 전 프록시 객체가 트랜잭션을 시작(BEGIN)하고, 종료 시 커밋(COMMIT)한다. (반드시 public 메서드여야 동작함)
- 롤백(Rollback) 룰: * 기본적으로 RuntimeException(언체크 예외)과 Error에 대해서만 롤백이 발생한다.
### 🗳️ 영속성 컨텍스트 (Persistence Context)

- 애플리케이션과 DB 사이에서 엔티티를 관리하는 논리적 캐시(장바구니) 공간.
- 4가지 혜택:
### 🔄 Flush (플러시) 메커니즘

- 영속성 컨텍스트의 쓰기 지연 저장소에 쌓인 SQL 쿼리를 DB에 **'전송(동기화)'**하는 작업 (커밋과는 다르며, 플러시 후 롤백도 가능).
- 자동 호출 시점: 트랜잭션 커밋 직전, 그리고 JPQL 쿼리 실행 직전 (메모리에만 있고 DB엔 없는 데이터를 조회하려는 정합성 오류를 막기 위함).

---

## 5. QueryDSL (타입 안전 동적 쿼리)

### 🧑‍💻 QueryDSL 핵심

- 도입 이유: JPQL은 문자열(String)이므로 오타를 내도 런타임에 에러가 터진다. QueryDSL은 컴파일 시점에 타입 안전(Type-safe)하게 코드로 쿼리를 작성할 수 있다.
- Q클래스: 컴파일 시점에 엔티티 메타데이터를 기반으로 생성되는 객체 (예: QProduct). JPAQueryFactory와 결합하여 사용한다.
### 🛠️ 동적 쿼리 및 성능 최적화

- BooleanExpression (동적 쿼리): where 절에 null이 들어가면 무시되는 속성을 활용한다. 조건들을 개별 메서드로 분리하면 쿼리 가독성이 높아지고 여러 곳에서 조건을 재사용할 수 있다.
- Join: .join(), .leftJoin() 등을 사용해 직관적으로 연관 데이터를 묶어 조회한다.
- 페이징 처리: 과거에 쓰던 fetchResults()는 버그로 인해 Deprecated(사용 중단) 되었다. 콘텐츠 리스트를 조회하는 쿼리와 전체 개수(count())를 구하는 쿼리를 분리하여 두 번 작성하는 것이 표준이다.
### ✨ DTO 프로젝션 (@QueryProjection)

- 목적: 엔티티 전체(모든 컬럼)를 불러오는 대신, 쿼리 단에서 꼭 필요한 컬럼만 DTO로 직접 꽂아 넣어 성능을 최적화하는 기법.
- 동작: DTO 생성자에 @QueryProjection을 붙이면 Q-DTO가 생성되며, 쿼리의 select 절에 이 생성자를 직접 호출하여 타입 안전성을 완벽히 보장받는다.
- 아키텍처 트레이드오프: 안전하고 편리하지만, 순수해야 할 DTO 클래스가 QueryDSL이라는 특정 기술 라이브러리에 의존하게 된다는 단점이 있다.
