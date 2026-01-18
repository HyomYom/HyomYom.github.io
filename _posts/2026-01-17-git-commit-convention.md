---
layout: post
title: "🧾 Git Commit Convention"
date: 2026-01-17
categories: [git]
tags: ['Convention']
last_modified_at: 2026-01-18
---



# ✍️ Commit Message 정리

> Commit message는 “이 커밋이 무엇을 하는지”를 명령문으로 설명하는 문장이다.

화이팅!!!!!!!!


---

## 1️⃣ 기본 형식 (⭐ 가장 중요)

```text
<type>(optional scope):<subject>

✅ 예시
feat(auth):add JWT authentication
fix(user): resolvenull pointerexception


```

> 이 형식만 잘 지켜도 커밋 메시지는 절반은 성공이다.


---

## 2️⃣ Type 종류 (필수)

Type은 이 커밋이 어떤 성격인지를 나타낸다.

> 👉 실무에서는 feat / fix가 가장 많이 쓰인다.


---

## 3️⃣ Scope (선택)

Scope는 어디를 수정했는지를 보여준다.

- 도메인 / 모듈 / 패키지 단위
- 보통 소문자 + 한 단어로 작성
### 예시

```text
feat(auth)
fix(security)
refactor(user)


```

> 필수는 아니지만, 있으면 커밋 히스토리 보기가 훨씬 좋다.


---

## 4️⃣ Subject (필수)

### ✨ 작성 규칙

- 명령문으로 작성
- 첫 글자 소문자
- 마침표 ❌
- 50자 이내
### ✅ 좋은 예

```text
feat: add login API
fix: handle expired token


```

### ❌ 나쁜 예

```text
Added login feature ❌
Fixing bug ❌
로그인 기능 추가 ❌

```

> ❗ 한국어 ❌ / 과거형 ❌


---

## 5️⃣ Body (선택)

Subject에서 다 설명이 안 될 때 사용한다.

- 왜(Why) 이 작업을 했는지
- 어떻게(How) 구현했는지
Subject 아래 한 줄 띄우고 작성한다.

### 예시

```text
feat(auth):add JWT authentication

- issue tokenonlogin
-validate tokenon request
- handle expiration

```

> 팀원이 커밋만 봐도 흐름을 이해할 수 있게 쓰는 게 목표


---

## 6️⃣ Footer (선택)

이슈나 PR과 연결할 때 사용한다.

```text
Closes#23

```


---

## 7️⃣ 실무에서 자주 쓰는 예시

### 🔐 Security / Auth 관련

```text
feat(security):addrole-basedauthorization

- apply ROLE_USERand ROLE_ADMIN
-restrictadmin endpoints

```

```text
fix(jwt): handle expired token exception

```

```text
refactor(auth): simplify authentication filter

```


---

## 8️⃣ 커밋 메시지 한 줄 요약 규칙

> 💡 Commit message = 명령문

- ❌ 무엇을 했다
- ✅ 무엇을 하라
```text
add login API
fix token validation
remove unused config

```

> 커밋 메시지를 보면


---

## 9️⃣ Spring + Security + JWT 프로젝트에서 자주 쓰는 Scope

```text
feat(auth)
feat(security)
fix(jwt)
refactor(user)
chore(config)

```


---

