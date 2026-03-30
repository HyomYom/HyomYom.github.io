---
layout: post
title: "[MapStruct] 보일러플레이트의 늪 : Builder와 Mapstruct"
date: 2026-03-30
categories: [spring]
tags: ['mapstruct']
---



## 보일러플레이트(Boilerplate)?

앞선 게시글에서도 한 번 다룬것 처럼 보일러플레이트는 핵심 비즈니스 로직은 아니지만, 프로그램 구동을 위해 관용적이고 반복적으로 길게 작성해야 하는 코드를 뜻한다.

자바에서는 getter/setter, 생성자, 그리고 객체 간 데이터를 옮겨 담는 변환 매핑 코드가 대표적이라 할 수 있다.

ex)

```java
// 전형적인 매핑 보일러플레이트
UserDto dto = new UserDto();
dto.setId(user.getId());
dto.setName(user.getName());
dto.setEmail(user.getEmail());
// 필드가 30개라면 의미 없는 코드가 30줄이나 필요하다.
```


---

## Builder를 사용하면 보일러플레이트가 사라질까?

Lombok을 사용하면 ‘Builder Pattern 구조’를 만드는 보일러플레이트는 사라진다. 하지만 A 객체의 데이터를 꺼내 B 객체의 builder에 넣는 맵핑에서 발생하는 보일러플레이트는 해결되지 않는다.

즉, Builder는 객체를 안전하게 생성하는 도구일 뿐, 데이터를 옮겨 담는 반복적인 코드는 여전히 남아있다.




---

## MapStruct?

MapStruct는 위에서 본 mapping 보일러플레이트를 컴파일 시점에 완전히 지워주는 자동 코드 생성 라이브러리이다.

개발자 어떤 object를 어떤 object로 바꿀지 인터페이스를 지정하면, MapStruct가 builder 나 getter/setter 를 활용한 변환 코드를 대신 작성해주며 다음과 같은 이점을 가진다.

- 생산성 극대화 : 패핑 코드 없이 핵심 비즈니스 로직에 집중
- 휴먼 에러 완벽 차단 : 타켓 객체에 매핑되지 않는 필드가 있으면 컴파일 경고나 에러를 띄워 실수를 차단
- 유지보수성 향상 : 새로운 필드가 추가되었을 때 이름이 같으면 자동으로 매핑되므로 수정할 코드가 없고, 혹여 예외가 발생하더라도 MapStruct interface만 수정하면 되므로 편리하다. 
ex)

```java
@Mapper(componentModel = "spring")
public interface UserMapper {
    // 변환 규칙만 선언하면, MapStruct가 빌더를 호출하여 매핑하는 긴 코드를 자동 생성한다.
    User toEntity(UserRequest request;
}
```


---

## MapStruct 고급 매핑 및 어노테이션 활용 기법



### 1. Ignore

반환 과정에서 타겟 객체에 값을 채우고 싶지 않은 필드가 있을 때 사용한다. 주로 사용자 비밀번호 같은 민감한 정보를 DTO로 넘기지 않거나, DB 저장 시 자동 생성되는 ID나 등록일자 등을 빈 값으로 두기 위해 활용한다

ex)

```java
@Mapper(componentModel = "spring")
public interface UserMapper {
    // password 필드는 DTO로 변환할 때 매핑하지 않고 null로 남겨둔다.
    @Mapping(target = "password", ignore = true)
    UserResponse toResponse(User user);
}
```



### 2. Format

소스 데이터와 타켓 데이터의 타입이 달라도, 지정한 형식(Format)에 맞춰 MapStruct가 자동으로 파싱과 포맷팅 코드를 생성해 준다. 

ex)

```java
@Mapper(componentModel = "spring")
public interface EventMapper {
    // LocalDateTime 타입인 createdAt을 yyyy-MM-dd HH:mm 형식의 String으로 변환한다.
    @Mapping(source = "createdAt", target = "createdDate", dateFormat = "yyyy-MM-dd HH:mm")
    // Number 타입을 특정 포맷의 String으로 변환한다.
    @Mapping(source = "price", target = "priceString", numberFormat = "$#.00")
    EventDto toDto(Event event);
}
```



### 3. 고정값(Default) 및 고정값(Constant)

소스 데이터가 null일 때 대신 들어갈 기본값을 지정하건, 소스 데이터의 상태와 무관하게 항상 타겟 객체에 넣을 고정값을 설정할 수 있다.

ex)

```java
@Mapper(componentModel = "spring")
public interface ProductMapper {
    // name 필드가 null이면 "Unknown Product"라는 기본값을 넣는다.
    @Mapping(source = "name", target = "productName", defaultValue = "Unknown Product")
    // DTO의 status 필드에는 소스 객체 상관없이 무조건 "AVAILABLE"이라는 고정값을 넣는다.
    @Mapping(target = "status", constant = "AVAILABLE")
    ProductDto toDto(Product product);
}
```



### 4. 커스텀 로직 적용(QualifiedByName)

단순 매핑 외에, 직접 작성한 복잡한 변환 로직(암호화 등) 특정 필드에만 적용하고 싶을 때 사용한다

ex)

```java
@Mapper(componentModel = "spring")
public interface UserMapper {
    // phoneNumber 필드를 변환할 때 'formatPhone'이라는 커스텀 메서드를 거치도록 지정한다.
    @Mapping(source = "phoneNumber", target = "formattedPhone", qualifiedByName = "formatPhone")
    UserDto toDto(User user);

    // 개발자가 직접 작성한 커스텀 변환 로직
    @Named("formatPhone")
    default String formatPhone(String phone) {
        if (phone == null || phone.length() < 10) return phone;
        return phone.substring(0, 3) + "-" + phone.substring(3, 7) + "-" + phone.substring(7);
    }
}
```



### 5. 매퍼간 의존성 주입

A 객체 안에 B객체가 포함된 복잡한 구조를 매핑할 때, B 객체를 변환하는 로직을 A 매퍼에 또 작성하는 것은 비효율적이다. 이때 @Mapper(uses = {...}) 속성을 사용하면, 이미 만들어둔 다른 Mapper의 변환 메서드를 자동으로 가져와 사용할 수 있다.

ex)

```java
// 주소가 담긴 AddressMapper가 이미 구현되어 있다고 가정한다.
@Mapper(componentModel = "spring")
public interface AddressMapper {
    AddressDto toDto(Address address);
}

// UserMapper에서 AddressMapper를 가져다 쓴다.
@Mapper(componentModel = "spring", uses = {AddressMapper.class})
public interface UserMapper {
    // User 엔티티 안의 Address 객체를 매핑할 때, 위에서 명시한 AddressMapper를 자동으로 호출한다.
    UserDto toDto(User user);
}
```

