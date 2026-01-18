---
layout: post
title: "🧾 Git Commit Convention"
date: 2026-01-17
categories: [git]
---
## 1️⃣ 기본 형식 (⭐ 가장 중요)

```plain text
<type>(optional scope): <subject>

```

### ✅ 예시

```plain text
feat(auth): add JWT authentication
fix(user): resolve null pointer exception

```

---

## 2️⃣ Type 종류 (필수)

> 👉 실무에서 가장 중요한 건 feat / fix

---

## 3️⃣ Scope (선택)

- 변경된 도메인 / 모듈 / 패키지
- 소문자, 한 단어 권장
### 예시

```plain text
feat(auth)
fix(security)
refactor(user)

```

---

## 4️⃣ Subject (필수)

### ✨ 작성 규칙

- 명령문으로 작성
- 첫 글자 소문자
- 마침표 ❌
- 50자 이내
### ✅ 좋은 예

```plain text
feat: add login API
fix: handle expired token

```

### ❌ 나쁜 예

```plain text
Added login feature ❌
Fixing bug ❌
로그인 기능 추가 ❌

```

---

## 5️⃣ Body (선택)

- 왜(Why) 와 어떻게(How) 를 설명
- Subject 아래 한 줄 띄우고 작성
### 예시

```plain text
feat(auth): add JWT authentication

- issue token on login
- validate token on request
- handle expiration

```

---

## 6️⃣ Footer (선택)

- 이슈 트래킹, PR 연동용
```plain text
Closes #23

```

---

## 7️⃣ 실무에서 자주 쓰는 예시

### 🔐 Security / Auth

```plain text
feat(security): add role-based authorization

- apply ROLE_USER and ROLE_ADMIN
- restrict admin endpoints

```

```plain text
fix(jwt): handle expired token exception

```

```plain text
refactor(auth): simplify authentication filter

```

---

## 8️⃣ 커밋 한 줄 요약 규칙

> 💡 Commit message = 명령문

- ❌ 무엇을 했다
- ✅ 무엇을 하라
```plain text
add login API
fix token validation
remove unused config

```

---

## 9️⃣ Spring + Security + JWT 프로젝트 추천 Scope

```plain text
feat(auth)
feat(security)
fix(jwt)
refactor(user)
chore(config)

```

---

## ✅ 보너스: 커밋 전 체크리스트

---





