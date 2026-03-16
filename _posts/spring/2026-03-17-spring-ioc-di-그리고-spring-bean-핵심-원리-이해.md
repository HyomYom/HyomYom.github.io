---
layout: post
title: "Spring IoC, DI, 그리고 Spring Bean : 핵심 원리 이해"
date: 2026-03-17
categories: [spring]
tags: ['spring', 'springboot']
---



## IoC, DI, 그리고 Spring Bean : 핵심 원리 이해

> ❗ 과거의 Java 애플리케이션, 특히 대규모 시스템에서는 ‘강한 결합(Tight Coupling)’이 가장 큰 문제였다

- 강한 결합이란?
- 문제점 : 위 코드에서 UserServiceImpl를 NewUserServiceImpl로 변경해야 한다면, 해당 객체가 선언된 클래스의 모든 코드를 직접 수정해야한다. 즉 해당 구조는 유지보수가 어렵고, 테스트가 힘들며, 유연성이 떨어지는 오류를 가지고있다
## 해결책의 등장 : Spring IoC, Bean, DI 

### 1. IoC (Inversion of Control) - 제어의 역전

IoC는 객체 생성과 관리의 제어권이 개발자에서 Spring 컨테이너로 넘어간 것을 의미한다. 일반적으로 애플리케이션의 생성과 관리는 사용자가 직접 하는것이 일반적이다. 하지만 이러한 상황에서 위에서 언급 한 바와 같이 코드가 다른 클래스에 강하게 결합되는 상황이 발생하게 된다.

Spring에서는 이러한 문제를 해결하기 위해 IoC 컨테이너가 객체 생성과 관리의 책임을 대신 수행한다.

- 개발자는 객체를 직접 생성하지 않고
- 필요한 객체를 사용한다고 선언만 하면
- Spring 컨테이너가 객체를 생성하고 연결
이렇게 객체 생성의 제어권이 개발자 → Spring으로 넘어가는 것을 제어의 역전(Inversion of Control)이라고 한다


---

### 2. Spring IoC 컨테이너

Spring IoC 컨테이너는 애플리케이션에서 사용하는 객체들을 생성하고 관리하는 핵심 엔진이다. 쉽게 말하면 객체를 생성하고 관리하는 "객체 공장(Object Factory)" 역할이다.

IoC 컨테이너의 주요 역할은 다음과 같다

### 1️⃣ 객체 생성 및 관리

Spring은 애플리케이션 실행 시 특정 어노테이션이 붙은 클래스를 찾아 객체를 생성한다. 예를 들어 다음과 같은 어노테이션이 붙어 있으면 Spring이 자동으로 객체를 생성한다

```text
@Component
@Service
@Repository
@Controller
```

이 과정을 컴포넌트 스캔(Component Scan)이라고 한다

### 2️⃣ 객체의 생명주기 관리

Spring은 객체의

- 생성
- 초기화
- 사용
- 소멸
까지 전체 생명주기(Lifecycle)를 관리한다

### 3️⃣ 객체 간 의존관계 설정

객체가 다른 객체를 필요로 할 때 Spring이 자동으로 연결해줍니다.

이 과정이 바로 DI (Dependency Injection) 입니다.


---

### 3. Spring Bean

Spring IoC 컨테이너가 생성하고 관리하는 객체를 Spring Bean이라고 한다. 즉, Spring이 관리하는 객체는 모두 Bean이라고 생각하면 된다.

예를 들어 다음과 같은 클래스가 있다고 가정해보자

```java
@Service
public class UserService {
}
```

Spring 애플리케이션이 실행되면

1. Spring이 UserService 클래스를 발견하고
1. 객체를 생성한 뒤
1. IoC 컨테이너에 등록
이렇게 등록된 객체가 바로 Spring Bean이다.

정리하면

```text
Spring Bean = Spring 컨테이너가 관리하는 객체
```


---

### 4. DI (Dependency Injection)

DI는 IoC 개념을 실제로 구현하는 기술이다. DI는 객체가 필요로 하는 다른 객체(의존성)를 Spring이 자동으로 주입하는 것을 의미한다

예를 들어 UserController가 UserService를 필요로 한다고 가정해보자

```java
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }
}
```

여기서 중요한 점은

- UserController는 UserService가 필요하다고 선언만 했을 뿐
- 직접 객체를 생성하지는 않았다는 것이다
Spring 컨테이너는

1. UserService Bean을 생성하고
1. UserController를 생성할 때
1. UserService 객체를 생성자에 전달하여 주입한다
즉 내부적으로는 다음과 같은 과정이 일어나다

```text
UserService 생성
↓
UserController 생성
↓
UserService 주입
```

이 과정을 의존성 주입(Dependency Injection)이라고 한다


---

### 5. IoC와 DI의 장점

IoC와 DI를 사용하면 느슨한 결합(Loose Coupling) 구조를 만들 수 있다

예를 들어 다음과 같은 코드가 있다고 가정해보자

```text
UserController → UserServiceImpl
```

이 경우 구현 클래스에 직접 의존하기 때문에 구현을 변경하기 어렵습니다.

하지만 인터페이스를 사용하면 다음과 같은 구조가 됩니다.

```text
UserController → UserService (Interface)
```

이제 구현체를 다음과 같이 변경해도

```text
UserServiceImpl
NewUserServiceImpl
```

UserController 코드는 수정할 필요가 없다

이처럼 IoC와 DI는

- 코드의 유연성
- 유지보수성
- 테스트 용이성
을 크게 향상시켜 준다


---

## 의존성 주입(DI)의 3가지 방식

Spring에서 객체의 의존성을 주입하는 방식은 크게 3가지가 있다.

### 1️⃣ 생성자 주입 (Constructor Injection)

생성자를 통해 의존성을 주입하는 방식이다.

현재 Spring에서 가장 권장되는 방식이다.

```java
@Service
@RequiredArgsConstructor
public class ProductService {
    private final ProductRepository productRepository;
    
    // public ProductService(ProductRepository productRepository) {
	  //     this.productRepository = productRepository;
    // }
    // -> @RequiredArgsConstructor이 다음과 같은 역할을 수행 
}
```

특징

- final 사용 가능 → 불변성 보장
- 필요한 의존성이 생성자에 명확하게 드러남
- 테스트 작성이 쉬움
- 순환 참조를 애플리케이션 시작 시점에 발견 가능

---

### 2️⃣ Setter 주입 (Setter Injection)

Setter 메서드를 통해 의존성을 주입하는 방식이다.

```java
@Autowired
public void setProductRepository(ProductRepository productRepository) {
    this.productRepository = productRepository;
}
```

특징

- 의존성을 선택적으로 주입할 때 사용
- 객체 생성 이후에도 의존성이 변경될 수 있음

---

### 3️⃣ 필드 주입 (Field Injection)

필드에 직접 @Autowired를 붙여 의존성을 주입하는 방식이다.

```java
@Autowired
private ProductRepository productRepository;
```

특징

- 코드가 가장 간결함
- 테스트 작성이 어려움
- 의존 관계가 명확하게 드러나지 않음
