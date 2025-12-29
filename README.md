# SQL Dialect Transformation + Safety Validator (HCX)

자연어 또는 표준 SQL을 입력하면

1️⃣ **표준 SQL로 정규화**  
2️⃣ **타겟 DBMS Dialect로 변환**  
3️⃣ **LLM Validator로 안전/의미 점검**  
4️⃣ **결과와 로그를 CSV로 기록**

까지 자동으로 수행하는 NL2SQL 기본 파이프라인

지원 DBMS:

- TIBERO
- ORACLE
- PostgreSQL
- MySQL

---

<br>

## 🎯 1차 목표

> 실행보다 **변환 + 안전성 검증**에 초점을 둠

- `SELECT`만 허용 (기본 정책)
- Validator 통과 SQL만 “선택적으로” 실행 가능
- 다음 항목 자동 차단

  - INSERT / UPDATE / DELETE
  - CREATE / ALTER / DROP
  - TRUNCATE / MERGE
  - 권한/관리 명령
  - 기타 파괴적/비가역 명령

- DBMS에 종속되지 않는 **Canonical SQL 중심 개발**
- 변환/검증/결과 로그 **모두 기록**

---

<br>

## 🧭 파이프라인

```
Canonical SQL
↓
Dialect 변환 (TIBERO / ORACLE / POSTGRESQL / MYSQL)
↓
LLM Validator (안전 + 의미 점검)
├─ PASS → SELECT만 실행(옵션)
└─ FAIL → 실행 금지 + 사유 기록
↓
CSV 로그 저장
```

> 기본 정책:  
> **쿼리 변환이 주목적 — 실행은 옵션이며 기본적으로 안전 모드**

---

## 🔒 제한 사항

- 실행은 원칙적으로 **SELECT 전용**
- Validator FAIL 시 무조건 차단
- 의미 왜곡이 감지되면 차단
- 문법 오류가 감지되면 차단

---

## 📂 프로젝트 구조
```
.
├── .env
├── main.py
├── sql_transform_runner.py
├── core/
│ ├── config.py
│ ├── transform.py
│ ├── validate.py
│ ├── canonical_validate.py
│ ├── execute.py
│ └── logger.py
├── sql/
│ └── canonical.sql
└── sql_transform_logs.csv
```


| 파일 | 역할 |
|------|------|
| main.py | 전체 파이프라인 엔트리 |
| sql_transform_runner.py | 배치/테스트 실행 러너 |
| core/config.py | 환경 변수 및 설정 |
| core/transform.py | DBMS별 SQL 변환 |
| core/validate.py | LLM 기반 안전/의미 Validator |
| core/canonical_validate.py | Canonical SQL 구조 점검 |
| core/execute.py | SELECT 실행(안전 모드) |
| core/logger.py | CSV 로그 생성/헤더 관리 |
| sql/canonical.sql | 기준이 되는 표준 SQL 목록 |

---

<br>

## 📌 향후 계획
- 실패 SQL 자동 수정 루프(Repair Loop)
- WHERE 없는 SELECT 경고
- Sandbox DB 완전 분리
- Streamlit 대시보드 모니터링
- 토큰/비용 리포트 자동화