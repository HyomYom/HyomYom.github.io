---
layout: post
title: "MacOS Java 환경변수 설정"
date: 2026-03-09
categories: [setting]
tags: ['mac', 'java', 'homebrew']
---



## 1️⃣ Homebrew 설치

macOS에서 Homebrew로 Java(OpenJDK)를 설치하면 JDK는 다음 경로에 설치됩니다.

```text
/opt/homebrew/opt/openjdk@21
```

하지만 기본적으로 JAVA_HOME 환경 변수는 자동으로 설정되지 않기 때문에

직접 설정해야 Java 기반 개발 도구들이 정상적으로 동작합니다.


---

## 2️⃣ OpenJDK 설치

Homebrew로 Java 설치

```bash
brew install openjdk@21
```

설치 확인

```bash
java -version
```

예시

```text
openjdk version "21"
```


---

## 3️⃣ macOS Java 시스템 경로 등록

Homebrew Java는 macOS 기본 Java 경로에 등록되지 않기 때문에

다음 명령어로 심볼릭 링크를 생성해야 합니다.

```bash
sudo ln -sfn /opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk \
/Library/Java/JavaVirtualMachines/openjdk-21.jdk
```

이 작업을 하면 macOS Java 시스템에서 JDK를 인식합니다.


---

## 4️⃣ JAVA_HOME 환경 변수 설정

macOS 기본 쉘(zsh)의 설정 파일을 수정합니다.

파일 위치

```text
~/.zshrc
```

다음 내용을 추가합니다.

```bash
export JAVA_HOME=$(/usr/libexec/java_home -v 21)
export PATH=$JAVA_HOME/bin:$PATH
```

설정 적용

```bash
source ~/.zshrc
```


---

## 5️⃣ JAVA_HOME 확인

환경 변수가 정상적으로 설정되었는지 확인합니다.

```bash
echo $JAVA_HOME
```

예시 출력

```text
/Library/Java/JavaVirtualMachines/openjdk-21.jdk/Contents/Home
```

Java 실행 확인

```bash
java -version
```


---

## 6️⃣ 현재 macOS에 설치된 Java 확인

설치된 Java 목록 조회

```bash
/usr/libexec/java_home -V
```

예시

```text
Matching Java Virtual Machines (1):
21 (arm64) "Homebrew" - "OpenJDK 21"
/Library/Java/JavaVirtualMachines/openjdk-21.jdk/Contents/Home
```


---

## 7️⃣ 특정 Java 버전으로 JAVA_HOME 변경

여러 버전이 설치된 경우 특정 버전으로 변경 가능

예시 (Java 21)

```bash
export JAVA_HOME=$(/usr/libexec/java_home -v 21)
```

예시 (Java 17)

```bash
export JAVA_HOME=$(/usr/libexec/java_home -v 17)
```


---

# 8️⃣ 실무 팁 (개발자용)

Spring Boot 프로젝트에서는 보통 다음 조합을 사용합니다.

특히 다음 상황에서 JAVA_HOME 설정이 중요합니다.

- Gradle build 오류
- Maven compile 오류
- IntelliJ SDK 인식 실패
- Spring Boot 실행 오류

---

## 9️⃣ 문제 해결

### JAVA_HOME이 설정되지 않은 경우

오류 예시

```text
JAVA_HOME is not set
```

해결

```text
export JAVA_HOME=$(/usr/libexec/java_home -v 21)
```


---

### Java 버전이 다르게 나오는 경우

확인

```bash
which java
```

정상 경로

```text
/opt/homebrew/opt/openjdk@21/bin/java
```


---

# 🔧 정리

macOS + Homebrew Java 환경 설정 순서

1️⃣ Java 설치

```text
brew install openjdk@21
```

2️⃣ macOS Java 경로 등록

```text
sudo ln -sfn /opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk \
/Library/Java/JavaVirtualMachines/openjdk-21.jdk
```

3️⃣ JAVA_HOME 설정

```text
export JAVA_HOME=$(/usr/libexec/java_home -v 21)
```

4️⃣ 적용

```text
source ~/.zshrc
```


---

