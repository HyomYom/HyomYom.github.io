---
layout: post
title: "3주차 Spring MSA 학습 - Spring AI & LLM 실전 아키텍처 및 구현"
date: 2026-04-07
categories: [reboot]
tags: ['spring', 'ai', 'llm']
---



## AI와 LLM 코어 개념 및 비즈니스 전략

- 핵심 작동 원리: AI(추론 및 규칙) ➔ 머신러닝(데이터 기반 통계적 학습) ➔ 딥러닝(인공 신경망, 비정형 데이터 특화)의 계층으로 구성됨.
- 토큰화 (Tokenization): 문장을 AI의 처리 및 과금 단위인 '토큰'으로 분할함. 한글은 형태소 위주로 분할되어 영어보다 1.5~2배가량 토큰 소모가 큼.
- 임베딩 (Embedding): 토큰을 고차원 숫자 벡터로 변환하여 단어 간의 '의미적 거리'를 매핑함.
- 트랜스포머 (Transformer) 처리:
- 다음 토큰 예측: 한 번에 문장을 완성하는 것이 아니라, 통계적으로 다음에 올 가장 확률 높은 단어를 하나씩 이어 붙여 문장을 생성함.
> 비유: 셀프 어텐션은 전문가들이 모여 "이 문장에서 제일 중요한 단어가 무엇인지" 토론하는 과정이고, 피드 포워드는 토론 후 각자의 지식을 총동원해 정답을 도출하는 과정이다.

- 백엔드 통합의 당위성: 프론트엔드 직접 호출은 API Key 노출로 인한 과금 폭탄을 초래하므로 절대 금지함. 백엔드에서 키를 은닉하고, DB 데이터를 활용한 개인화 및 캐싱, 요금 제한(Rate Limiting) 등을 제어해야 함.

---

## Spring AI 프레임워크 핵심

- 모델 추상화 (Model Abstraction): OpenAI, Gemini, Ollama 등 제조사마다 다른 API를 ChatClient라는 통일된 인터페이스로 규격화함. 설정값 변경만으로 비즈니스 로직 수정 없이 모델 교체가 가능함.
- Prompt Template: 변수({variable})를 사용하여 프롬프트의 뼈대와 동적 데이터를 분리하여 재사용성을 극대화함.
- 메시지 타입 (Role):
- Structured Output (구조화된 응답): AI의 자연어 응답을 JSON 스키마로 강제하고, Java DTO 객체로 자동 파싱해주는 기능이다. 복잡한 문자열 파싱 로직을 제거함.
> 코드 예시:

```java
// 분석 결과를 담을 DTO 정의
public class ProductAnalysisResponse {
    @JsonProperty("sentiment") String sentiment;
    @JsonProperty("score") int score;
}

// Controller 호출부 (객체로 즉시 매핑)
ProductAnalysisResponse result = chatClient.prompt()
    .user("이 리뷰 분석해줘: " + review)
    .call()
    .entity(ProductAnalysisResponse.class);
```


---

## Context (문맥) 관리와 영속성 아키텍처

- Stateless 한계: LLM은 자체 기억력이 없어 이전 대화를 모두 묶어서 보내야 하므로, 대화가 길어질수록 입력 토큰 비용이 폭증함.
- 토큰 최적화 전략 (비용 절감):
- 하이브리드 메모리 레이어 아키텍처:

---

## 멀티모달 (Multimodal) 데이터 처리

- 개념: 텍스트뿐만 아니라 이미지, 오디오, 비디오를 동시에 입력받아 관계를 이해하고 추론하는 기능이다.
- Spring AI 구현: MultipartFile로 들어온 이미지를 Media 객체로 변환하여 텍스트 프롬프트와 함께 전송함.
- 실무 활용 사례:

---

## 로컬 LLM 환경 (Ollama) 및 파라미터 튜닝

- 클라우드 API vs 로컬 모델:
- Ollama 및 Qwen2.5: Ollama는 복잡한 설정 없이 모델을 띄워주는 실행 플랫폼이다. Qwen2.5 모델은 한국어 특화 및 코딩 능력이 우수하며 일반 노트북에서도 쾌적하게 구동됨.
- LLM 제어 파라미터 (창의성 및 정확성 제어):
