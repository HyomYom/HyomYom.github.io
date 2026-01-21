---
layout: post
title: "Git Commit Convention"
date: 2026-01-17
categories: [git]
tags: ['Convention']
last_modified_at: 2026-01-21
---



해당글은 공부 목적으로 정리한 개인적인 기록입니다. 정확하지 않은 정보가 포함될 수 있으며, 최신 기술 동향이나 공식 문서와는 차이가 있을 수 있습니다! 처음 구현하시는 분들께 작은 도움이 되었으면 하며, 혹시 틀리 내용이 있다면 댓글로 알려주시면 감사하겠습니다.


---

# ✍️ Commit Message 정

> Commit message는 “이 커밋이 무엇을 하는지”를 명령문으로 설명하는 문장이다.


---

## 1) 기본 형식

```text
<type>[optional scope]: <subject>

[optional body]

[optional footer]


```

### 예시

```text
feat(auth): add JWT authentication
fix(jwt): handle expired token
chore(ci): update build workflow


```


---

## 2) Type 목록 (가장 자주 쓰는 것)

- feat: 새로운 기능 추가
- fix: 버그 수정
- docs: 문서 변경(README, 주석 등)
- style: 포맷/스타일 변경(동작 변화 없음)
- refactor: 리팩토링(동작 변화 없음)
- test: 테스트 추가/수정
- chore: 빌드/설정/패키지/잡일(코드 동작 변화 없음)

---

## 3) Scope (선택)

어떤 영역을 수정했는지 표시한다.

형식:

```text
type(scope): subject


```

예시:

```text
feat(auth):addrefresh token rotation
fix(user): prevent duplicate email signup
refactor(security): simplify authfilter


```


---

## 4) Subject 규칙

- 명령문(동사 원형)으로 작성: add / fix / remove / update / refactor
- 소문자 시작
- 마침표 금지
- 짧게(권장 50자 이내)
좋은 예:

```text
feat:addlogin API
fix: preventnull pointerin tokenparser


```

나쁜 예:

```text
Added login feature
Fixing bug
로그인 기능 추가


```


---

## 5) Body (선택)

Subject에서 설명이 부족할 때만 작성한다.

권장 구성:

- 무엇을 변경했는지
- 왜 변경했는지(필요 시)
예시:

```text
feat(auth):add JWT authentication

- issueaccess tokenonlogin
-validate tokenoneach request
-return401on expiration


```


---

## 6) Footer (선택)

이슈/PR 연결, 브레이킹 체인지 명시 등에 사용한다.

### 이슈 닫기

```text
Closes#123


```

### Breaking Change

```text
feat(api): change token response schema

BREAKING CHANGE: token response now wraps data in `result`.


```


---

## 7) 실무에서 바로 쓰는 템플릿

### 기본

```text
type(scope): subject


```

### 변경 이유까지

```text
type(scope): subject

- change 1
- change 2

Closes#issue


```

