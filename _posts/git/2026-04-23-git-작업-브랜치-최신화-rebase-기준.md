---
layout: post
title: "Git 작업 브랜치 최신화 (Rebase 기준)"
date: 2026-04-23
categories: [git]
tags: ['git', 'commit', 'rebase']
last_modified_at: 2026-04-23
---



# 개념

작업 브랜치 최신화란, **내가 작업 중인 feature 브랜치를 최신 main 브랜치 기준으로 다시 맞추는 작업**이다.

프로젝트를 진행하는 동안 다른 팀원들이 `main` 브랜치에 새로운 코드를 계속 반영하면,

내 브랜치는 예전 `main` 기준으로 만들어졌기 때문에 점점 뒤처지게 된다.

이 상태로 작업을 계속하면:

- Pull Request(PR) 시 충돌 발생 가능성 증가
- 최신 공통 코드와 충돌 가능
- 테스트 환경 차이 발생
- 리뷰 시 복잡해짐
그래서 **최신 main 브랜치 내용을 반영하여 내 작업 브랜치를 업데이트**해야 한다.


---

# Rebase란?

`rebase`는 **내가 작업한 커밋들을 최신 main 브랜치 위로 다시 올려놓는 방식**이다.

즉:

- 기존 작업 내용은 유지됨
- 최신 main 코드 반영됨
- 커밋 히스토리가 깔끔해짐

---

# 예시

## 최신화 전 상태

```bash
main         A - B - C - D
feature/abc  A - B - 작업1 - 작업2
```

- `feature/abc` 브랜치는 `A-B` 시점에서 생성됨
- 이후 main 브랜치에 `C`, `D`가 추가됨

---

## 최신화 후 (rebase)

```bash
main         A - B - C - D
feature/abc  A - B - C - D - 작업1 - 작업2
```

즉, 내 작업이 최신 main 기준 위로 다시 정렬된다.


---

# 작업 순서

## 1. 작업 브랜치 이동

```bash
git checkout feature/abc
```

## 2. 원격 저장소 최신 정보 가져오기

```bash
git fetch origin
```

## 3. 최신 main 기준으로 rebase

```bash
git rebase origin/main
```


---

# 충돌 발생 시

rebase 중 충돌이 날 수 있다.

## 1. 충돌 파일 수정

직접 코드 수정

## 2. 수정 내용 추가

```bash
git add .
```

## 3. rebase 계속 진행

```bash
git rebase --continue
```


---

# rebase 취소

문제가 생기면:

```bash
git rebase --abort
```


---

# 원격 브랜치에 이미 push한 경우

rebase는 커밋 이력이 바뀌므로 push 시 다음 명령어 사용:

```bash
git push --force-with-lease
```


---

# 실무에서 자주 사용하는 전체 흐름

```bash
git checkout feature/abc
git fetch origin
git rebase origin/main
git push --force-with-lease
```


---

# 언제 하면 좋은가?

- PR 올리기 전
- main 브랜치 변경사항이 많을 때
- 충돌을 미리 해결하고 싶을 때
- 최신 코드 기준으로 테스트하고 싶을 때

---

# 주의사항

- 개인 작업 브랜치(feature)는 rebase 자주 사용 가능
- 여러 명이 함께 쓰는 공용 브랜치는 rebase 주의

---

# 한 줄 정리

**작업 브랜치 최신화 = 내 feature 브랜치를 최신 main 기준으로 다시 맞추는 작업이며, 주로 rebase를 사용한다.**

