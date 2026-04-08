---
layout: post
title: "4주차 Spring MSA 학습 - Vector DB"
date: 2026-04-07
categories: [reboot]
tags: ['spring', 'embedding', 'vector']
last_modified_at: 2026-04-08
---



## 1. Vector DB (pgvector) 구축 및 문서 임베딩

- 개념: 기존 PostgreSQL RDBMS의 트랜잭션(ACID) 안정성을 유지하면서 고차원 벡터 데이터 저장 및 유사도 검색을 지원하는 확장 도구이다.
- 테이블 및 인덱스 설계: 원본 문서와 쪼개진 벡터(Chunk) 데이터를 분리하여 저장하고, 고속 검색을 위해 HNSW 인덱스를 사용한다.
```sql
-- 확장 기능 활성화
CREATE EXTENSION IF NOT EXISTS vector;

-- 벡터 데이터 저장 테이블 (3072차원)
CREATE TABLE vector_store
(
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content    TEXT      NOT NULL,
    metadata   JSONB,
    embedding  vector(3072),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 고속 검색을 위한 인덱스 (메타데이터 필터링 가속화)
CREATE INDEX idx_vector_store_metadata ON vector_store USING gin (metadata);
```

- 문서 분할 (Chunking) 및 저장: LLM의 컨텍스트 한계를 넘지 않기 위해 긴 문서를 TokenTextSplitter로 분할(오버랩 적용)하여 벡터화한다.
```sql
// TokenTextSplitter: (청크당 토큰, 오버랩, 최소 토큰, 최대 조각 수, 구분자 유지)
TextSplitter splitter = new TokenTextSplitter(500, 100, 5, 10000, true);

// 메타데이터 부착 (나중에 특정 문서 안에서만 검색하기 위함)
Map<String, Object> metadata = Map.of(
    "document_id", entity.getId().toString(),
    "filename", entity.getFileName()
);

Document rawDoc = new Document(content, metadata);
List<Document> splitChunks = splitter.split(rawDoc);

// Vector Store에 일괄 저장 (DB 인덱싱 수행)
vectorStore.add(splitChunks);
```


---

## 2. RAG (검색 증강 생성) 구현

- 개념: 사용자의 질문을 벡터로 변환하여 Vector DB에서 가장 유사한 문서 조각(Top-K)을 찾아낸 뒤, 이를 LLM의 프롬프트에 주입하여 환각(Hallucination) 없는 정확한 답변을 생성하는 패턴이다.
```sql
private static final String RAG_PROMPT_TEMPLATE = """
    다음 문서들을 참고하여 질문에 답변해주세요.
    문서에 없는 내용은 답변하지 마세요.

    [참고 문서]
    %s

    [질문]
    %s
    """;

public AnswerResponse ask(String question) {
    // 1. Vector DB 유사도 검색 (상위 5개, 임계값 0.7 이상)
    List<Document> relevantDocs = vectorStore.similaritySearch(
        SearchRequest.builder()
            .query(question)
            .topK(5)
            .similarityThreshold(0.7)
            .build()
    );

    // 2. 검색된 문서들을 하나의 문자열로 결합
    String context = combineDocuments(relevantDocs);

    // 3. LLM 프롬프트에 주입하여 답변 생성
    String answer = chatClient.prompt()
        .user(String.format(RAG_PROMPT_TEMPLATE, context, question))
        .call()
        .content();

    return AnswerResponse.builder().answer(answer).build();
}

  private String combineDocuments(List<Document> documents) {
    return documents.stream()
        .map(doc -> String.format("[%s]: %s",
            doc.getMetadata().getOrDefault("filename", "Unknown"),
            doc.getText()))
        .collect(Collectors.joining("\n\n---\n\n"));
  }
```


---

## 3. Spring AI Advisor 패턴

- 개념: ChatClient의 요청(Before)과 응답(After)을 가로채어 공통 로직(대화 저장, 보안 필터링 등)을 분리하는 미들웨어 패턴이다.
- ChatMemoryAdvisor (대화 기억 유지): 사용자의 이전 질문과 AI의 답변을 ConcurrentHashMap이나 DB에 저장했다가, 다음 질문 시 프롬프트에 함께 묶어 전달한다.
```sql
@Bean
public ChatClient chatClient(ChatClient.Builder builder) {
    // 세션 ID "user-123"의 최근 10개 대화 기억 유지
    ChatMemoryAdvisor memoryAdvisor = new ChatMemoryAdvisor("user-123", 10);

    return builder
        .defaultSystem("당신은 친절한 AI 어시스턴트입니다.")
        .defaultAdvisors(memoryAdvisor) // Advisor 장착
        .build();
}
```


---

## 4. Function Calling (함수 호출)

- 개념: LLM이 스스로 판단하여 날씨 API, 사내 DB, 계산기 등 외부 도구(Tool)를 호출할 수 있게 만드는 기술이다. 자연어에서 파라미터를 정확히 추출해 낸다.
```sql
// 1. 도구 정의 (AI가 읽고 판단할 수 있도록 설명 상세 작성)
@Service
public class FunctionTools {
  @Tool(description = "특정 도시의 현재 날씨 정보를 조회합니다")
  public WeatherResponse getWeather(WeatherRequest request) {
      // 실제 날씨 API 호출 로직...
      return new WeatherResponse(request.getCity(), 15, "맑음");
  }

  @Tool(description = "두 숫자의 사칙연산을 수행합니다")
  public CalculatorResponse calculator(CalculatorRequest request) {
      // 연산 로직...
  }
}

// 2. Service 호출 (도구 주입)
public String chat(String userMessage) {
    return chatClient.prompt()
        .user(userMessage)
        .tools(functionTools) // 등록된 도구를 LLM에게 제공
        .call()
        .content();
}
```


---

## 5. Agentic Workflow (자율형 에이전트 패턴)

- 개념: 단순 질의응답을 넘어 AI가 목표를 달성하기 위해 생각(Thought) -> 행동(Act) -> 관찰(Observation) 과정을 스스로 반복하는 고도화된 아키텍처이다.
- Plan-and-Execute (계획 후 실행) 패턴: 즉시 행동하지 않고 전체 로드맵을 먼저 설계하여 정확도를 높인다.
```sql
public String planAndExecute(String goal) {
    // 1. 계획 수립 (Planner)
    String plan = chatClient.prompt()
        .system("당신은 복잡한 목표를 위한 논리적인 단계를 수립하는 전략가입니다.")
        .user("목표: " + goal + "\n이 목표를 달성하기 위한 상세 계획을 번호를 매겨 세워주세요.")
        .call()
        .content();

    // 2. 계획 실행 (Executor) - 도구를 활용하여 수립된 계획을 순차적으로 수행
    return chatClient.prompt()
        .system("당신은 주어진 계획을 정확히 이행하는 실행 전문가입니다.")
        .tools("getWeather", "calculator") // 도구 활용 허용
        .user("수립된 계획: " + plan + "\n위 계획을 실행하고 최종 결과를 보고하세요.")
        .call()
        .content();
}
```

- Multi-Agent (멀티 에이전트) 협업: 특정 페르소나를 가진 여러 AI가 역할을 분담하여 파이프라인 형태로 작업을 처리한다. (예: Researcher 데이터 수집 -> Analyst 통계 분석 -> Writer 최종 리포트 작성)
