---
layout: post
title: "[MySQL] 다중 컬럼 인덱스(Multi-column Index) 설계 및 사용"
date: 2026-04-24
categories: [java]
tags: ['DB', 'schema', 'mysql']
---



# MySQL 다중 컬럼 인덱스(Multi-column Index) 사용 시 핵심 주의사항 4가지


---

## 1. 테스트 환경 구축 (순수 SQL)

인덱스 테스트를 위해 `employees`(직원) 테이블을 생성하고,  순수 SQL 쿼리를 활용해 약 100만 건의 더미 데이터를 삽입

**[테이블 생성 DDL]**

```sql
CREATE TABLE `employees` (
  `id` int NOT NULL AUTO_INCREMENT,
  `department` varchar(50) NOT NULL,
  `emp_name` varchar(50) NOT NULL,
  `hire_date` date NOT NULL,
  `salary` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**[더미 데이터 100만 건 삽입 (MySQL 8.0 CTE 활용)]**

별도의 애플리케이션 코드 없이, MySQL의 재귀 CTE(Recursive CTE)를 사용하면 쿼리 한 번으로 대량의 더미 데이터를 빠르게 생성할 수 있다.

```sql
-- 재귀 깊이 제한을 100만으로 늘려줍니다.
SET SESSION cte_max_recursion_depth = 1000000;

-- 100만 건 데이터 삽입
INSERT INTO employees (department, emp_name, hire_date, salary)
WITH RECURSIVE cte (n) AS (
  SELECT 1
  UNION ALL
  SELECT n + 1 FROM cte WHERE n < 1000000
)
SELECT
  -- 4개 부서 중 하나를 랜덤으로 배정
  ELT(FLOOR(1 + (RAND() * 4)), 'Sales', 'Engineering', 'HR', 'Marketing'),
  -- User_1, User_2 형식으로 고유한 이름 생성
  CONCAT('User_', n),
  -- 최근 약 8년 내의 날짜를 랜덤으로 배정
  DATE_ADD('2015-01-01', INTERVAL FLOOR(RAND() * 3000) DAY),
  -- 3000 ~ 10000 사이의 급여 랜덤 배정
  FLOOR(3000 + (RAND() * 7000))
FROM cte;

-- (emp_name, department) 순서로 새로운 인덱스 생성
CREATE INDEX idx_name_dept ON employees(emp_name, department);
```



---

## 1. 다중 컬럼 인덱스의 정렬 방식과 스캔

다중 컬럼 인덱스는 **첫 번째 컬럼부터 차례대로 정렬**되며, N번째 인덱스 컬럼은 N-1번째 인덱스의 정렬에 의존한다. 이 구조적 특징 때문에 조회 시 몇 가지 주의사항이 발생한다

### [1-1] 인덱스 컬럼의 순서에 따른 성능 차이

다중 컬럼 인덱스 내의 **컬럼 순서**가 필터링 성능에 어떤 영향을 미치는지 확인해 보고자한다. 특정 직원(`User_500000`)을 찾는 상황을 가정해 보자

**A. 동등 비교 (****`=`****) 쿼리 (가장 빠름)**

```sql
SELECT * FROM employees 
WHERE department = 'Engineering' AND emp_name = 'User_6000';
```

- **결과**: 약 0.001초 소요
![](https://prod-files-secure.s3.us-west-2.amazonaws.com/013ba03b-dfcd-4cc1-aebc-737c7a6ca6a7/98595a2e-17fb-4bb4-9a29-0dfbe843fec6/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466ZXAIUX2I%2F20260424%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20260424T002552Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEKX%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJHMEUCIQCi4ZFRbf3WSM4vDotQDWA5mGO2dUu%2B1DmPpdHT%2FiS5CQIgAXrjBBQBaXWhRsOkyy%2Fs4MWJN0jk6iMcTE1cKGtxUhcq%2FwMIbhAAGgw2Mzc0MjMxODM4MDUiDDjEYRSGVvn%2Bar4bBCrcAxd%2F%2FX%2Fb%2BvieggatGrtIZfODTMiBNs1on%2Fw3UjWmKs3mX3PjbsDdeNuYR%2BRrdGs7YnoBzOViVWRIQG10O5aTFrBE0Zos2J1Lc4zN2ZS1ns3S8muphT%2B5tSSzuK%2BM4TAYVCSXVeeHmqVrSwVcDZed%2FsWBwRRcxpkouUdWoDHHzNJc9vbuW5iib5aBhe%2BG3Z3YKOMT4KcpeQJNfhR01Vj8tu4SI%2Fy%2BUlv70YcBOED%2BnOJOMbgZYG31CYJnhS9q50ERG3Y%2Bp1LY1Y3jki6IwlPruEzcgJHyIFoIgQQWOLNF4oO03m%2FUeayJ7YF%2F8J5YqTjP9aQb6W1xXJtvDg4CF4n92A9IN%2Fg1V1tXXOGUjTwAgy87ACiXmeg8IYqILAg0%2FI%2F15ZQkaWhh%2BrzvCcVr0PEATsmXAL1OTxTZhbcpNUSLkcsqyLuqWoTuV11gqpvsjzjWCc8Fib1KxFjCWnK5NSxN4D2YHwaQTBP%2BEUOJlGVeEc%2BgSKN2SzCsBGEHtGzd8xQ3F5NIBqWu69pH0tdRIqhDT6Me9dzjNMxOP0mes1DHMrI9dmLSotGNP4lqbP57lHFdA09Z1ItFWiAad4M58mhHwtaXhQSEED2cRyshWoDsR7Ez6KAPZ5aZgoDFFrwoMNGWqs8GOqUB3JSEClttnEu0dcD0XymRW%2FDau59VZfEjLtg2eRSoyQILI2IAZLWDQXE69Lciqf36LM3RiRDzImWOExGeGfEcztZ9xeaCejFOgOeB0z75qPzegqQjUYYr0fKQZ3Eo%2BInltCsRnXOFyeFd7r52gpZ3cFC%2BEMN4nuvifuTECmfqM3%2B4oh34uqHtwc%2BTBANO2y5v%2Be98%2BGuUxNdMdKkLA676xyJrtxOX&X-Amz-Signature=27ea2e62a860901d2f4a8cedda52b087bb8e929f66999714c31723c570a2bc89&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject)

- **이유**: `department` -> `emp_name` 순으로 정렬된 인덱스를 정확히 타기 때문에, 유효한 데이터 하나를 즉시 찾아낸다.

**B. 부정 비교 (****`!=`****)가 포함된 쿼리 (성능 저하 발생)**

```sql
SELECT * FROM employees 
WHERE department != 'Engineering' AND emp_name = 'User_6000';
```

- **결과**: 성능 현저히 저하 (Full Index Scan 발생에 가까움).
![](https://prod-files-secure.s3.us-west-2.amazonaws.com/013ba03b-dfcd-4cc1-aebc-737c7a6ca6a7/94d94c60-e076-4d64-b8db-2f91aac9f83d/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466ZXAIUX2I%2F20260424%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20260424T002552Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEKX%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJHMEUCIQCi4ZFRbf3WSM4vDotQDWA5mGO2dUu%2B1DmPpdHT%2FiS5CQIgAXrjBBQBaXWhRsOkyy%2Fs4MWJN0jk6iMcTE1cKGtxUhcq%2FwMIbhAAGgw2Mzc0MjMxODM4MDUiDDjEYRSGVvn%2Bar4bBCrcAxd%2F%2FX%2Fb%2BvieggatGrtIZfODTMiBNs1on%2Fw3UjWmKs3mX3PjbsDdeNuYR%2BRrdGs7YnoBzOViVWRIQG10O5aTFrBE0Zos2J1Lc4zN2ZS1ns3S8muphT%2B5tSSzuK%2BM4TAYVCSXVeeHmqVrSwVcDZed%2FsWBwRRcxpkouUdWoDHHzNJc9vbuW5iib5aBhe%2BG3Z3YKOMT4KcpeQJNfhR01Vj8tu4SI%2Fy%2BUlv70YcBOED%2BnOJOMbgZYG31CYJnhS9q50ERG3Y%2Bp1LY1Y3jki6IwlPruEzcgJHyIFoIgQQWOLNF4oO03m%2FUeayJ7YF%2F8J5YqTjP9aQb6W1xXJtvDg4CF4n92A9IN%2Fg1V1tXXOGUjTwAgy87ACiXmeg8IYqILAg0%2FI%2F15ZQkaWhh%2BrzvCcVr0PEATsmXAL1OTxTZhbcpNUSLkcsqyLuqWoTuV11gqpvsjzjWCc8Fib1KxFjCWnK5NSxN4D2YHwaQTBP%2BEUOJlGVeEc%2BgSKN2SzCsBGEHtGzd8xQ3F5NIBqWu69pH0tdRIqhDT6Me9dzjNMxOP0mes1DHMrI9dmLSotGNP4lqbP57lHFdA09Z1ItFWiAad4M58mhHwtaXhQSEED2cRyshWoDsR7Ez6KAPZ5aZgoDFFrwoMNGWqs8GOqUB3JSEClttnEu0dcD0XymRW%2FDau59VZfEjLtg2eRSoyQILI2IAZLWDQXE69Lciqf36LM3RiRDzImWOExGeGfEcztZ9xeaCejFOgOeB0z75qPzegqQjUYYr0fKQZ3Eo%2BInltCsRnXOFyeFd7r52gpZ3cFC%2BEMN4nuvifuTECmfqM3%2B4oh34uqHtwc%2BTBANO2y5v%2Be98%2BGuUxNdMdKkLA676xyJrtxOX&X-Amz-Signature=1375a365521f5a232aceb74cffe95aff0aea07bfce119af8d489cb7159152ba9&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject)

- **이유**: `(department, emp_name)` 인덱스 트리에서는 `Engineering`이 아닌 모든 부서(Sales, HR 등 수십만 건)에 대해 `emp_name = 'User_500000'`인지 일일이 뒤져야 하기 때문이다.
**C. 인덱스 순서 변경 후 재조회 (성능 향상)**

```sql
- (emp_name, department) 순서로 새로운 인덱스 생성
CREATE INDEX idx_name_dept ON employees(emp_name, department);

- 쿼리 재실행SELECT  FROM employees
WHERE department != 'Engineering' AND emp_name = 'User_6000';
```

- **결과**: 다시 0.001초 대로 짧은 시간 내에 조회 완료!
![](https://prod-files-secure.s3.us-west-2.amazonaws.com/013ba03b-dfcd-4cc1-aebc-737c7a6ca6a7/35768f4f-407a-4cd9-b610-2f308f006700/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466ZXAIUX2I%2F20260424%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20260424T002552Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEKX%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJHMEUCIQCi4ZFRbf3WSM4vDotQDWA5mGO2dUu%2B1DmPpdHT%2FiS5CQIgAXrjBBQBaXWhRsOkyy%2Fs4MWJN0jk6iMcTE1cKGtxUhcq%2FwMIbhAAGgw2Mzc0MjMxODM4MDUiDDjEYRSGVvn%2Bar4bBCrcAxd%2F%2FX%2Fb%2BvieggatGrtIZfODTMiBNs1on%2Fw3UjWmKs3mX3PjbsDdeNuYR%2BRrdGs7YnoBzOViVWRIQG10O5aTFrBE0Zos2J1Lc4zN2ZS1ns3S8muphT%2B5tSSzuK%2BM4TAYVCSXVeeHmqVrSwVcDZed%2FsWBwRRcxpkouUdWoDHHzNJc9vbuW5iib5aBhe%2BG3Z3YKOMT4KcpeQJNfhR01Vj8tu4SI%2Fy%2BUlv70YcBOED%2BnOJOMbgZYG31CYJnhS9q50ERG3Y%2Bp1LY1Y3jki6IwlPruEzcgJHyIFoIgQQWOLNF4oO03m%2FUeayJ7YF%2F8J5YqTjP9aQb6W1xXJtvDg4CF4n92A9IN%2Fg1V1tXXOGUjTwAgy87ACiXmeg8IYqILAg0%2FI%2F15ZQkaWhh%2BrzvCcVr0PEATsmXAL1OTxTZhbcpNUSLkcsqyLuqWoTuV11gqpvsjzjWCc8Fib1KxFjCWnK5NSxN4D2YHwaQTBP%2BEUOJlGVeEc%2BgSKN2SzCsBGEHtGzd8xQ3F5NIBqWu69pH0tdRIqhDT6Me9dzjNMxOP0mes1DHMrI9dmLSotGNP4lqbP57lHFdA09Z1ItFWiAad4M58mhHwtaXhQSEED2cRyshWoDsR7Ez6KAPZ5aZgoDFFrwoMNGWqs8GOqUB3JSEClttnEu0dcD0XymRW%2FDau59VZfEjLtg2eRSoyQILI2IAZLWDQXE69Lciqf36LM3RiRDzImWOExGeGfEcztZ9xeaCejFOgOeB0z75qPzegqQjUYYr0fKQZ3Eo%2BInltCsRnXOFyeFd7r52gpZ3cFC%2BEMN4nuvifuTECmfqM3%2B4oh34uqHtwc%2BTBANO2y5v%2Be98%2BGuUxNdMdKkLA676xyJrtxOX&X-Amz-Signature=ad6ecc8e0b1e4fa0a6deae39cc3ba131b2b3cc9791a8aa4a233e51ef9b0c130f&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject)

- **이유**: 인덱스가 `emp_name`으로 먼저 정렬되어 있으므로 해당 이름만 빠르게 찾고 부서만 대조한 뒤 탐색을 즉시 종료할 수 있다. 가장 확실하게 데이터를 걸러낼 수 있는 동등 비교 조건의 컬럼을 선행으로 두어야 한다.
### [1-2] 선행 컬럼 누락 시 인덱스 사용 불가

현재 `(department, emp_name)` 인덱스가 생성된 상태에서, 선행 컬럼인 `department`를 빼고 후행 컬럼인 `emp_name`만 조건으로 쿼리를 날려본다

```sql
SELECT * FROM employees WHERE emp_name = 'User_6000';
```

![](https://prod-files-secure.s3.us-west-2.amazonaws.com/013ba03b-dfcd-4cc1-aebc-737c7a6ca6a7/5bc17e0f-3313-4507-8f14-8f4a6dcb15fd/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466ZXAIUX2I%2F20260424%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20260424T002552Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEKX%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJHMEUCIQCi4ZFRbf3WSM4vDotQDWA5mGO2dUu%2B1DmPpdHT%2FiS5CQIgAXrjBBQBaXWhRsOkyy%2Fs4MWJN0jk6iMcTE1cKGtxUhcq%2FwMIbhAAGgw2Mzc0MjMxODM4MDUiDDjEYRSGVvn%2Bar4bBCrcAxd%2F%2FX%2Fb%2BvieggatGrtIZfODTMiBNs1on%2Fw3UjWmKs3mX3PjbsDdeNuYR%2BRrdGs7YnoBzOViVWRIQG10O5aTFrBE0Zos2J1Lc4zN2ZS1ns3S8muphT%2B5tSSzuK%2BM4TAYVCSXVeeHmqVrSwVcDZed%2FsWBwRRcxpkouUdWoDHHzNJc9vbuW5iib5aBhe%2BG3Z3YKOMT4KcpeQJNfhR01Vj8tu4SI%2Fy%2BUlv70YcBOED%2BnOJOMbgZYG31CYJnhS9q50ERG3Y%2Bp1LY1Y3jki6IwlPruEzcgJHyIFoIgQQWOLNF4oO03m%2FUeayJ7YF%2F8J5YqTjP9aQb6W1xXJtvDg4CF4n92A9IN%2Fg1V1tXXOGUjTwAgy87ACiXmeg8IYqILAg0%2FI%2F15ZQkaWhh%2BrzvCcVr0PEATsmXAL1OTxTZhbcpNUSLkcsqyLuqWoTuV11gqpvsjzjWCc8Fib1KxFjCWnK5NSxN4D2YHwaQTBP%2BEUOJlGVeEc%2BgSKN2SzCsBGEHtGzd8xQ3F5NIBqWu69pH0tdRIqhDT6Me9dzjNMxOP0mes1DHMrI9dmLSotGNP4lqbP57lHFdA09Z1ItFWiAad4M58mhHwtaXhQSEED2cRyshWoDsR7Ez6KAPZ5aZgoDFFrwoMNGWqs8GOqUB3JSEClttnEu0dcD0XymRW%2FDau59VZfEjLtg2eRSoyQILI2IAZLWDQXE69Lciqf36LM3RiRDzImWOExGeGfEcztZ9xeaCejFOgOeB0z75qPzegqQjUYYr0fKQZ3Eo%2BInltCsRnXOFyeFd7r52gpZ3cFC%2BEMN4nuvifuTECmfqM3%2B4oh34uqHtwc%2BTBANO2y5v%2Be98%2BGuUxNdMdKkLA676xyJrtxOX&X-Amz-Signature=d436a5938c4285f5cc41f9323244cac3dd2fd1321131e5a21bc7c2586566fada&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject)

이 쿼리의 실행 계획(`EXPLAIN`)을 확인해보면, **우리가 만든 인덱스를 타지 않고 거의 모든 Row를 스캔(Full Table Scan)**하는 것을 볼 수 있다. 다중 컬럼 인덱스는 첫 번째 컬럼을 기준으로 큰 틀이 정렬되어 있기 때문에, 선행 조건이 없으면 시작점을 찾지 못해 인덱스 활용을 포기해버린다.


---

## 2. 정렬(ORDER BY) 작업에서의 인덱스 활용 여부

데이터를 필터링(WHERE)하는 것뿐만 아니라 **정렬(ORDER BY)**을 수행할 때도 다중 컬럼 인덱스의 구조가 중요하다. DB 서버에서 별도의 정렬 연산을 수행하는 것(`Using filesort`)은 CPU와 메모리를 크게 소모하므로 가급적 피해야 한다

현재 `(department, emp_name)` 인덱스가 걸려있다고 가정해 보자

**A. 인덱스를 통해 정렬이 최적화되는 경우 (Good)**

```sql
SELECT * FROM employees 
WHERE department = 'Engineering' 
ORDER BY emp_name;
```

- 선행 컬럼인 `department`가 동등(`=`) 조건으로 고정되어있다. `Engineering` 부서 안에서는 이미 데이터가 `emp_name` 순서로 정렬되어 있기 때문에, MySQL은 인덱스 트리를 순서대로 읽기만 하면 된다.
**B. 인덱스 정렬을 활용하지 못하는 경우 (Bad - Using filesort 발생)**

```sql
SELECT * FROM employees 
WHERE department IN ('Engineering', 'Sales') 
ORDER BY emp_name;
```

- `Engineering` 내부, `Sales` 내부는 각각 이름이 정렬되어 있지만, 두 부서를 합쳐놓으면 전체 이름 기준으로는 뒤죽박죽이 된다. 따라서 메모리나 디스크에 데이터를 올려두고 새롭게 정렬(`Using filesort`)을 수행해야 한다.

---

## 3. 인덱스의 ASC/DESC 설정과 스캔 방향에 따른 성능 차이

다중 컬럼 인덱스를 생성할 때 지정하는 정렬 방향(`ASC`, `DESC`)과 실제 쿼리의 `ORDER BY` 방향이 일치하느냐에 따라 DB 내부의 물리적인 스캔 방식이 달라지며, 이는 쿼리 속도 차이로 직결된다.

### [3-1] 정순 스캔(Forward Scan) vs 역순 스캔(Backward Scan)

- **정순 스캔:** `ORDER BY salary ASC`로 조회. 인덱스 트리를 앞에서부터 읽는다
- **역순 스캔:** `ORDER BY salary DESC`로 조회. 인덱스 트리를 뒤에서부터 거꾸로 읽는다
> **💡 성능 차이:** 역순 스캔이 정순 스캔보다 **약 20~30% 더 느리다.**

### [3-2] 복합 정렬(Mixed-order)에서의 대참사와 MySQL 8.0의 해결책

단일 정렬 방향이 아닌, 두 개 이상의 컬럼이 **혼합된 정렬(하나는 ASC, 하나는 DESC)**을 요구할 때는 문제가 심각해진다.

```sql
- 기존 인덱스: 모두 ASC로 생성되어 있음CREATE INDEX idx_dept_salary ON employees(department ASC, salary ASC);
- 쿼리: 부서는 오름차순, 급여는 내림차순으로 정렬 요구SELECT  FROM employees
WHERE department = 'Engineering'ORDER BY department ASC, salary DESC;
```

이 경우 기존 인덱스(`ASC, ASC`)로는 정렬을 해결할 수 없어 무조건 **`Using filesort`**가 발생한다


하지만 **MySQL 8.0부터는 내림차순 인덱스(Descending Index)를 공식 지원**하여 이를 완벽히 해결할 수 있다

```sql
- MySQL 8.0+: 혼합 정렬에 완벽히 대응하는 인덱스 생성CREATE INDEX idx_dept_asc_salary_desc ON employees(department ASC, salary DESC);
- 다시 쿼리 실행SELECT  FROM employees
WHERE department = 'Engineering'ORDER BY department ASC, salary DESC;
```

새로 만든 혼합 인덱스를 타게 되면 `Using filesort`가 완전히 사라지며, DB 엔진은 이 인덱스를 가장 빠른 **정순 스캔(Forward Scan)**으로 처리하게 된다


---

## 4. 최종 마무리 요약

1. **컬럼 순서의 중요성**: 다중 컬럼 인덱스는 필터링 성능에 절대적인 영향을 미친다. 가장 확실하게 데이터를 걸러낼 수 있는 동등 비교(`=`) 조건의 컬럼을 앞에 배치.
1. **선행 컬럼 필수 포함**: 다중 컬럼 인덱스를 필터링에 활용하려면, 선행하는 인덱스 컬럼 조건이 쿼리의 WHERE 절에 반드시 포함되어야 한다
1. **Filesort 방지**: 정렬 최적화를 위해서는 `ORDER BY` 컬럼 앞단의 모든 인덱스 컬럼들이 동등(`=`) 조건으로 고정되어야 한다.
1. **내림차순 인덱스 활용**: 자주 사용되는 `ORDER BY` 방향이 혼합되어 있다면(ASC & DESC), MySQL 8.0의 **내림차순 인덱스**를 명시적으로 생성하여 `Using filesort`를 방지하고 정순 스캔을 유도
