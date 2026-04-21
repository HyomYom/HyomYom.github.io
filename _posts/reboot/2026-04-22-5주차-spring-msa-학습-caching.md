---
layout: post
title: "5주차 Spring MSA 학습 - Caching"
date: 2026-04-22
categories: [reboot]
tags: ['spring', 'embedding', 'vector']
---



### 1. 캐싱(Caching) 핵심 개념

설명: 자주 접근하는 데이터를 인메모리(RAM) 등 임시 저장소에 보관하여 응답 속도를 높이고 데이터베이스 부하를 줄이는 기술이다. 성능 향상과 비용 절감의 장점이 있으나, 원본 데이터와의 일관성(Consistency) 유지 및 한정된 메모리 관리가 필수적이다.

예시: 환율 데이터 API를 호출할 때 매번 호출하는 대신, 한 번 호출한 결과를 캐시에 24시간 동안 저장(TTL)하고 이를 재사용하여 외부 API 호출 비용과 응답 시간을 줄인다.

### 2. 주요 캐싱 전략 (Caching Strategies)

Cache-aside (캐시-어사이드)

설명: 애플리케이션이 캐시를 먼저 확인하고, 데이터가 없으면(Cache Miss) 데이터베이스(DB)에서 조회한 후 캐시에 저장하는 가장 보편적인 패턴이다. 읽기 성능 최적화에 탁월하지만, 데이터 일관성 유지를 위해 적절한 만료 시간 설정이 필요하다.

예시: 게시글을 조회할 때 우선 Redis에서 찾고, 없으면 DB에서 찾은 뒤 Redis에 저장한다.

```java
String cachedData = redisTemplate.opsForValue().get("blog:post:1");

if (cachedData == null) {
    cachedData = blogPostRepository.findById("1");
    redisTemplate.opsForValue().set("blog:post:1", cachedData, Duration.ofMinutes(30));
}
return cachedData;
```



Write-through (라이트-스루)

설명: 데이터 쓰기 요청 시 캐시와 DB에 동시에 데이터를 업데이트하는 패턴이다. 강한 데이터 일관성을 보장하지만, 두 곳에 모두 쓰기 작업을 수행하므로 쓰기 지연이 발생할 수 있다.

예시: 카테고리를 신규 저장할 때, DB에 인서트함과 동시에 Redis의 전체 카테고리 캐시 데이터도 즉시 최신화한다.

```java
// 캐시와 DB 동시 저장 (트랜잭션 내에서 처리)
categoryRepository.save(newCategory);
redisTemplate.opsForValue().set("cachedCategories", JsonUtil.toJson(updatedCategories));
```



Write-back (라이트-백)

설명: 쓰기 요청 시 먼저 캐시에만 데이터를 저장하여 클라이언트에게 즉시 응답하고, DB 업데이트는 백그라운드에서 비동기로 일괄 처리하는 패턴이다. 쓰기 성능은 최고 수준이나 캐시 서버 장애 시 데이터 손실 위험이 있다.

예시: 조회수 카운트나 로그를 수집할 때, 우선 Redis에만 값을 올리고 실제 DB 반영은 별도의 비동기 스레드를 통해 처리한다.

```java
// Redis에 우선 저장하여 빠른 응답
redisTemplate.opsForValue().set("cachedCategories", JsonUtil.toJson(categories));

// DB 저장은 비동기로 처리 (데이터 손실 리스크 존재)
CompletableFuture.runAsync(() -> categoryRepository.save(newCategory));
```



Write-around (라이트-어라운드)

설명: 쓰기 작업 시 캐시를 우회하여 DB에만 직접 데이터를 저장하는 패턴이다. 캐시는 오직 읽기 요청(Cache Miss) 시에만 업데이트되며, 쓰기 성능에 캐시가 영향을 주지 않는다.

예시: DB에 데이터를 저장한 직후, 기존에 캐싱된 구버전 데이터를 명시적으로 삭제(Invalidate)하여 다음 읽기 요청 시 최신 데이터가 캐싱되도록 유도한다.

```java
// DB에만 직접 저장
userRepository.put(userId, updateData);

// 캐시를 무효화하여 다음 조회 시 DB에서 새로 불러오게 함
cacheTemplate.remove(userId);`
```

### 3. Redis 성능 최적화 핵심 기술

TTL (Time-To-Live)

설명: 데이터의 유효 기간을 설정하여 지정된 시간이 지나면 메모리에서 자동 삭제되도록 하는 설정이다. 한정된 메모리를 효율적으로 사용하고, 원본 데이터와의 불일치 문제를 완화한다.

예시: 데이터를 캐싱할 때, 1시간 뒤에 휘발되도록 TTL 파라미터를 추가한다.

```java
// 1시간 뒤 만료되는 TTL 설정하여 저장
redisTemplate.opsForValue().set("cachedCategories", cacheCategories, 1, TimeUnit.HOURS);
```

```bash
// Redis 명령어 예시
SET cachedCategories "data" EX 3600
```

- EX 3600 : 3600초(1시간) 뒤 자동 만료
- Java 코드의 TimeUnit.HOURS 와 동일한 의미입니다.


캐시 제거 정책 (Eviction Policy / maxmemory-policy)

설명: Redis의 최대 허용 메모리(maxmemory)를 초과했을 때 어떤 데이터를 우선적으로 삭제할지 결정하는 정책이다.

예시: maxmemory-policy 설정을 통해 가장 오랫동안 참조되지 않은 데이터를 지우는 LRU(Least Recently Used) 방식이나, 접근 빈도가 가장 적은 데이터를 지우는 LFU(Least Frequently Used) 방식을 적용한다.

```bash
# Redis CLI를 통해 런타임에 모든 키에 대해 LRU 정책 적용
CONFIG SET maxmemory-policy allkeys-lru
```



