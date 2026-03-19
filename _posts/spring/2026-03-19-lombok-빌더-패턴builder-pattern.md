---
layout: post
title: "[Lombok] 빌더 패턴(Builder Pattern)"
date: 2026-03-19
categories: [spring]
tags: ['lombok', 'builder']
last_modified_at: 2026-03-19
---



## 1. 빌더(Builder)란 무엇인가?

빌더 패턴은 복잡한 객체를 단계별로 조립해서 만드는 객체 생성 디자인 패턴이다.

- 비유하자면 서브웨이 샌드위치 주문과 같다. 빵을 고르고, 야채를 넣고, 소스를 뿌리는 준비 과정(Builder)을 모두 마친 뒤에야 비로소 완성된 샌드위치(Product)를 건네받는 것과 같은 원리다.
- 즉, 객체를 곧바로 new 키워드로 찍어내는 것이 아니라, 임시 바구니(Builder)에 값을 다 모은 뒤 최종적으로 조립을 완료하여 진짜 객체를 반환하는 방식이다.

---

## 2. 빌더의 중요성 (왜 써야만 하는가?)

실무에서 복잡한 생성자 대신 빌더를 적극적으로 도입하는 이유는 안전성과 가독성을 극대화하기 위해서다.

- 가독성 (명시적 데이터 주입): new Product("노트북", 1500000, 20, "Apple")처럼 생성자는 인자가 많아지면 어떤 값이 어디로 들어가는지 알기 어렵다. 실수로 순서를 바꿔 넣어도 타입만 같으면 컴파일 에러가 나지 않아 치명적이다. 빌더를 쓰면 .name("노트북").price(1500000)처럼 필드명이 명시되어 실수를 원천 차단한다.
- 불변성 (Immutability) 보장: 객체를 만들고 나서 값을 바꾸는 Setter를 열어두면 데이터가 언제 어디서 오염될지 모른다. 빌더를 사용하면 필드를 final로 선언하고 Setter를 아예 없앨 수 있어, 한 번 생성된 객체는 절대 변하지 않음을 보장한다. 
- 유연성 (선택적 매개변수): 필수 값과 선택 값이 섞여 있을 때, 경우의 수마다 생성자를 여러 개 만들 필요(생성자 오버로딩 지옥) 없이 필요한 세팅 메서드만 호출하면 된다.

---

## 3. 수동 빌더 구현

```java

public class Product {
    private final String name;
    private final double price;

    // 생성자는 private으로 하여 외부에서 직접 생성을 막음
    private Product(Builder builder) {
        this.name = builder.name;
        this.price = builder.price;
    }

    // 정적 내부 빌더 클래스
    public static class Builder {
        private String name;
        private double price;

        public Builder name(String name) { this.name = name; return this; }
        public Builder price(double price) { this.price = price; return this; }

        public Product build() {
            return new Product(this);
        }
    }
}
```

### 1) Builder 생성

```java
Product.Builder builder = new Product.Builder();
```


---

### 2) Builder 세팅

```java
builder.name("콜라");
builder.price(2000);
```

여기서는 Product에 바로 넣는 게 아니라

Builder 안에 임시로 값 저장하는 거야.


---

### 3) build() 호출

```java
Product product = builder.build();
```

이 순간에 비로소 진짜 Product가 생성돼.


---

## 4) build() 호출

```java
return new Product(this);
```


---

### 5) Product 생성자에서 값 복사

```java
private Product(Builder builder) {
this.name = builder.name;
this.price = builder.price;
}
```

