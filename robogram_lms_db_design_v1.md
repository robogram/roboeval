
# 로보그램 LMS 실제 개발용 DB 테이블 설계서 v1.0

## 1. 설계 목표

본 설계서는 로보그램 LMS에서 다음 업무를 안정적으로 처리하기 위한 관계형 데이터베이스 구조를 정의한다.

- 학교/기관별 수업 운영
- 학년별 문항풀 랜덤 출제
- 학생 응답 저장 및 자동 채점
- 학급/학년/학교 단위 집계
- 교사용 시각화 대시보드
- PDF 보고서 및 학습 리포트 생성
- 문항 버전 관리, anchor 문항 관리, 로그 추적

권장 DBMS는 **PostgreSQL 15+** 기준으로 작성한다.  
이유는 JSONB, 윈도우 함수, materialized view, partitioning, 인덱스 기능이 안정적이기 때문이다.

---

## 2. 설계 범위

### 2-1. 포함 범위
- 기관/학교/학급/교사/학생 기본 구조
- 콘텐츠(과정, 차시, 문항풀, 문항, 보기)
- 응답/채점/노출 로그
- 집계 스냅샷
- 보고서 생성 이력
- 권한/사용자 관리 최소 구조

### 2-2. 제외 범위
- 결제/정산
- 라이선스 청구
- 강사 급여
- CMS/홈페이지 게시판
- 파일 스토리지 자체 구현

---

## 3. 핵심 엔터티 개요

1. 조직 영역
- organizations
- schools
- academic_terms
- classes
- teachers
- students

2. 수업 운영 영역
- programs
- program_instances
- lessons
- class_lesson_sessions

3. 평가 콘텐츠 영역
- assessment_pools
- items
- item_options
- item_tags
- item_pool_map

4. 출제/응답 영역
- item_exposure_logs
- student_responses
- response_events

5. 집계/리포트 영역
- domain_score_snapshots
- class_dashboard_snapshots
- report_jobs
- generated_reports

6. 권한/운영 영역
- users
- user_roles
- audit_logs

---

## 4. 논리 ER 구조

- 1개 organization은 여러 school을 가진다.
- 1개 school은 여러 class, teacher, student를 가진다.
- 1개 academic_term은 여러 program_instance를 가진다.
- 1개 program_instance는 여러 lesson을 가진다.
- 1개 class는 여러 class_lesson_session에 연결된다.
- 1개 assessment_pool은 여러 item을 포함한다.
- 1개 item은 여러 option을 가진다.
- 1개 student는 여러 response를 가진다.
- 1개 response는 1개 item에 연결된다.
- 응답은 class, lesson, pool, item 기준으로 집계된다.

---

## 5. 코드 체계

### 5-1. school_level_code
- E : 초등
- M : 중등
- H : 고등

### 5-2. pool_code
- P1 : 1차시용 문항풀
- P2 : 2차시용 문항풀

### 5-3. item_type_code
- MCQ4 : 4지선다 객관식
- LIKERT5 : 5점 척도
- TF : 진위형
- SHORT : 단답형(향후 확장)

### 5-4. domain_code
- PRIV : 개인정보 보호
- NET : 디지털 시민성/온라인 예절
- INFO : 정보 신뢰성 판단
- SAFE : 디지털 안전
- AIU : AI 이해
- AIC : AI 비판적 활용
- DPS : 디지털 문제해결
- COL : 협업
- CARE : 진로 연계 인식

### 5-5. difficulty_band
- A : 쉬움
- B : 보통
- C : 상대적 고난도

---

## 6. 물리 테이블 정의

## 6-1. organizations
기관/법인/재단/학교군 상위 단위

| 컬럼명 | 타입 | NULL | 설명 |
|---|---|---:|---|
| organization_id | bigserial PK | N | 기관 ID |
| organization_name | varchar(200) | N | 기관명 |
| organization_type | varchar(50) | N | school_foundation / youth_center / academy 등 |
| region_code | varchar(20) | Y | 지역 코드 |
| active_yn | char(1) | N | Y/N |
| created_at | timestamptz | N | 생성일시 |
| updated_at | timestamptz | N | 수정일시 |

인덱스:
- idx_organizations_type (organization_type)
- idx_organizations_region (region_code)

---

## 6-2. schools
실제 수업 운영 단위

| 컬럼명 | 타입 | NULL | 설명 |
|---|---|---:|---|
| school_id | bigserial PK | N | 학교 ID |
| organization_id | bigint FK | N | organizations.organization_id |
| school_name | varchar(200) | N | 학교명 |
| school_level_code | char(1) | N | E/M/H |
| school_type | varchar(50) | Y | elementary / middle / high / youth_center |
| region_code | varchar(20) | Y | 지역 |
| school_code_external | varchar(50) | Y | 외부연동 코드 |
| active_yn | char(1) | N | Y/N |
| created_at | timestamptz | N | 생성일시 |
| updated_at | timestamptz | N | 수정일시 |

인덱스:
- idx_schools_org (organization_id)
- idx_schools_level_region (school_level_code, region_code)

---

## 6-3. academic_terms
학기/캠프 운영기간

| 컬럼명 | 타입 | NULL | 설명 |
|---|---|---:|---|
| term_id | bigserial PK | N | 학기 ID |
| school_id | bigint FK | N | schools.school_id |
| term_name | varchar(100) | N | 2026-1학기, 2026 여름캠프 |
| start_date | date | N | 시작일 |
| end_date | date | N | 종료일 |
| created_at | timestamptz | N | 생성일시 |

인덱스:
- idx_terms_school (school_id)
- idx_terms_period (start_date, end_date)

---

## 6-4. classes
학급/반/프로그램 운영반

| 컬럼명 | 타입 | NULL | 설명 |
|---|---|---:|---|
| class_id | bigserial PK | N | 학급 ID |
| school_id | bigint FK | N | schools.school_id |
| term_id | bigint FK | N | academic_terms.term_id |
| class_name | varchar(100) | N | 4학년 2반 |
| grade_no | smallint | N | 학년 |
| homeroom_teacher_id | bigint FK | Y | teachers.teacher_id |
| student_count_planned | integer | Y | 계획 학생수 |
| active_yn | char(1) | N | Y/N |
| created_at | timestamptz | N | 생성일시 |

인덱스:
- idx_classes_school_term (school_id, term_id)
- idx_classes_grade (grade_no)

---

## 6-5. teachers
교사/담당자

| 컬럼명 | 타입 | NULL | 설명 |
|---|---|---:|---|
| teacher_id | bigserial PK | N | 교사 ID |
| school_id | bigint FK | N | schools.school_id |
| teacher_name | varchar(100) | N | 이름 |
| role_title | varchar(100) | Y | 정보부장, 담당교사 등 |
| phone_enc | text | Y | 암호화 전화번호 |
| email_enc | text | Y | 암호화 이메일 |
| active_yn | char(1) | N | Y/N |
| created_at | timestamptz | N | 생성일시 |

인덱스:
- idx_teachers_school (school_id)

---

## 6-6. students
학생 익명 기준 저장을 권장

| 컬럼명 | 타입 | NULL | 설명 |
|---|---|---:|---|
| student_id | bigserial PK | N | 내부 학생 ID |
| class_id | bigint FK | N | classes.class_id |
| student_hash_id | varchar(64) UNIQUE | N | 익명 해시 ID |
| grade_no | smallint | N | 학년 |
| student_no | varchar(30) | Y | 학번/번호 |
| gender_code | varchar(10) | Y | 선택 저장 |
| active_yn | char(1) | N | Y/N |
| created_at | timestamptz | N | 생성일시 |

인덱스:
- idx_students_class (class_id)
- idx_students_hash (student_hash_id)

권장:
- 학생 실명은 별도 민감정보 저장소 또는 저장하지 않음
- 대시보드는 student_hash_id 기준 처리

---

## 6-7. programs
상품/과정 마스터

| 컬럼명 | 타입 | NULL | 설명 |
|---|---|---:|---|
| program_id | bigserial PK | N | 과정 ID |
| program_name | varchar(200) | N | 잼S 학기형, 로보미 캠프 등 |
| content_type | varchar(50) | N | JEMS / ROBOMI_MOBILE / ROBOMI_PC |
| duration_lessons | smallint | N | 총 차시 |
| active_yn | char(1) | N | Y/N |
| created_at | timestamptz | N | 생성일시 |

인덱스:
- idx_programs_type (content_type)

---

## 6-8. program_instances
학교별 실제 운영 과정

| 컬럼명 | 타입 | NULL | 설명 |
|---|---|---:|---|
| program_instance_id | bigserial PK | N | 운영 ID |
| program_id | bigint FK | N | programs.program_id |
| school_id | bigint FK | N | schools.school_id |
| term_id | bigint FK | N | academic_terms.term_id |
| instructor_name | varchar(100) | Y | 파견강사명 |
| start_date | date | N | 시작일 |
| end_date | date | N | 종료일 |
| status_code | varchar(30) | N | planned / active / closed |
| created_at | timestamptz | N | 생성일시 |

인덱스:
- idx_program_instances_school (school_id)
- idx_program_instances_term (term_id)
- idx_program_instances_status (status_code)

---

## 6-9. lessons
차시 마스터

| 컬럼명 | 타입 | NULL | 설명 |
|---|---|---:|---|
| lesson_id | bigserial PK | N | 차시 ID |
| program_instance_id | bigint FK | N | program_instances.program_instance_id |
| lesson_no | smallint | N | 1~10 |
| lesson_title | varchar(200) | Y | 차시명 |
| pool_code | varchar(10) | Y | P1/P2/기타 |
| lesson_date | date | Y | 예정일 |
| created_at | timestamptz | N | 생성일시 |

유니크:
- uq_lessons_instance_no (program_instance_id, lesson_no)

---

## 6-10. class_lesson_sessions
학급별 실제 차시 실행 단위

| 컬럼명 | 타입 | NULL | 설명 |
|---|---|---:|---|
| session_id | bigserial PK | N | 세션 ID |
| class_id | bigint FK | N | classes.class_id |
| lesson_id | bigint FK | N | lessons.lesson_id |
| started_at | timestamptz | Y | 시작 |
| ended_at | timestamptz | Y | 종료 |
| attendance_count | integer | Y | 참석수 |
| status_code | varchar(30) | N | scheduled / open / closed |
| created_at | timestamptz | N | 생성일시 |

유니크:
- uq_session_class_lesson (class_id, lesson_id)

---

## 6-11. assessment_pools
문항풀 마스터

| 컬럼명 | 타입 | NULL | 설명 |
|---|---|---:|---|
| pool_id | bigserial PK | N | 문항풀 ID |
| school_level_code | char(1) | N | E/M/H |
| grade_no | smallint | N | 학년 |
| pool_code | varchar(10) | N | P1/P2 |
| pool_name | varchar(100) | N | 초4 1번 문항풀 |
| total_items | integer | N | 10 |
| anchor_item_count | integer | N | 2 |
| version_no | varchar(20) | N | 1.0 |
| active_yn | char(1) | N | Y/N |
| created_at | timestamptz | N | 생성일시 |

유니크:
- uq_pool_grade_code_version (school_level_code, grade_no, pool_code, version_no)

---

## 6-12. items
문항 마스터

| 컬럼명 | 타입 | NULL | 설명 |
|---|---|---:|---|
| item_id | varchar(30) PK | N | 예: E4-P1-01 |
| pool_id | bigint FK | N | assessment_pools.pool_id |
| school_level_code | char(1) | N | E/M/H |
| grade_no | smallint | N | 학년 |
| pool_code | varchar(10) | N | P1/P2 |
| anchor_flag | char(1) | N | Y/N |
| domain_code | varchar(10) | N | 영역 |
| subdomain_code | varchar(30) | Y | 세부영역 |
| item_type_code | varchar(20) | N | MCQ4 등 |
| difficulty_band | char(1) | N | A/B/C |
| item_goal | varchar(300) | Y | 측정 의도 |
| item_text | text | N | 문항 본문 |
| correct_option_no | smallint | Y | 1~4 |
| score_correct | numeric(6,2) | N | 정답점수 |
| score_incorrect | numeric(6,2) | N | 오답점수 |
| exposure_weight | numeric(5,2) | N | 랜덤 가중치 |
| active_yn | char(1) | N | Y/N |
| version_no | varchar(20) | N | 버전 |
| created_at | timestamptz | N | 생성일시 |
| updated_at | timestamptz | N | 수정일시 |

인덱스:
- idx_items_pool (pool_id)
- idx_items_domain (domain_code)
- idx_items_anchor (anchor_flag)
- idx_items_grade_pool (school_level_code, grade_no, pool_code)

---

## 6-13. item_options
보기 마스터

| 컬럼명 | 타입 | NULL | 설명 |
|---|---|---:|---|
| option_id | bigserial PK | N | 보기 ID |
| item_id | varchar(30) FK | N | items.item_id |
| option_no | smallint | N | 1~4 |
| option_text | text | N | 보기 |
| is_correct | char(1) | N | Y/N |
| created_at | timestamptz | N | 생성일시 |

유니크:
- uq_item_option_no (item_id, option_no)

---

## 6-14. item_tags
문항 태그(확장형)

| 컬럼명 | 타입 | NULL | 설명 |
|---|---|---:|---|
| item_tag_id | bigserial PK | N | 태그 ID |
| item_id | varchar(30) FK | N | items.item_id |
| tag_type | varchar(50) | N | difficulty, theme, report_group 등 |
| tag_value | varchar(100) | N | 태그 값 |
| created_at | timestamptz | N | 생성일시 |

인덱스:
- idx_item_tags_item (item_id)
- idx_item_tags_type_value (tag_type, tag_value)

---

## 6-15. item_exposure_logs
실제 학생에게 어떤 문항이 노출되었는지 추적

| 컬럼명 | 타입 | NULL | 설명 |
|---|---|---:|---|
| exposure_id | bigserial PK | N | 노출 ID |
| session_id | bigint FK | N | class_lesson_sessions.session_id |
| student_id | bigint FK | N | students.student_id |
| item_id | varchar(30) FK | N | items.item_id |
| exposed_at | timestamptz | N | 노출시각 |
| random_seed | varchar(100) | Y | 추첨용 seed |
| exposure_rank | integer | Y | 후보군 정렬순위 |
| created_at | timestamptz | N | 생성일시 |

유니크:
- uq_exposure_session_student (session_id, student_id)

인덱스:
- idx_exposure_item (item_id)
- idx_exposure_student (student_id)

---

## 6-16. student_responses
학생 응답 및 채점 결과

| 컬럼명 | 타입 | NULL | 설명 |
|---|---|---:|---|
| response_id | bigserial PK | N | 응답 ID |
| exposure_id | bigint FK | N | item_exposure_logs.exposure_id |
| session_id | bigint FK | N | class_lesson_sessions.session_id |
| student_id | bigint FK | N | students.student_id |
| item_id | varchar(30) FK | N | items.item_id |
| response_value | varchar(50) | Y | 선택값 |
| selected_option_no | smallint | Y | 1~4 |
| is_correct | char(1) | Y | Y/N |
| raw_score | numeric(6,2) | Y | 원점수 |
| response_time_sec | integer | Y | 응답시간 |
| started_at | timestamptz | Y | 응답 시작 |
| submitted_at | timestamptz | Y | 제출 완료 |
| no_response_flag | char(1) | N | Y/N |
| abnormal_flag | char(1) | N | Y/N |
| device_type | varchar(30) | Y | PC/Tablet/Mobile |
| browser_type | varchar(50) | Y | 브라우저 |
| created_at | timestamptz | N | 생성일시 |

유니크:
- uq_response_exposure (exposure_id)

인덱스:
- idx_responses_session (session_id)
- idx_responses_item (item_id)
- idx_responses_student (student_id)
- idx_responses_submitted (submitted_at)

대용량 운영 시:
- 월별 range partition 또는 term_id 기준 partition 권장

---

## 6-17. response_events
프론트 상호작용 이벤트 로그

| 컬럼명 | 타입 | NULL | 설명 |
|---|---|---:|---|
| response_event_id | bigserial PK | N | 이벤트 ID |
| response_id | bigint FK | Y | student_responses.response_id |
| exposure_id | bigint FK | Y | item_exposure_logs.exposure_id |
| event_type | varchar(50) | N | page_open / option_click / submit / timeout |
| event_payload | jsonb | Y | 부가 정보 |
| occurred_at | timestamptz | N | 발생시각 |

인덱스:
- idx_response_events_response (response_id)
- idx_response_events_type (event_type)

---

## 6-18. domain_score_snapshots
학생/학급/학년/학교 집계 스냅샷

| 컬럼명 | 타입 | NULL | 설명 |
|---|---|---:|---|
| snapshot_id | bigserial PK | N | 스냅샷 ID |
| snapshot_date | date | N | 기준일 |
| scope_type | varchar(20) | N | student/class/grade/school |
| school_id | bigint FK | N | schools.school_id |
| class_id | bigint FK | Y | classes.class_id |
| grade_no | smallint | Y | 학년 |
| student_id | bigint FK | Y | students.student_id |
| lesson_no | smallint | Y | 차시 |
| domain_code | varchar(10) | N | 영역 |
| response_count | integer | N | 응답수 |
| correct_rate | numeric(5,2) | Y | 정답률 |
| score_avg | numeric(6,2) | Y | 평균점수 |
| computed_at | timestamptz | N | 계산시각 |

인덱스:
- idx_domain_snapshot_scope (scope_type, school_id, class_id, grade_no)
- idx_domain_snapshot_domain (domain_code)

---

## 6-19. class_dashboard_snapshots
교사 대시보드용 요약 스냅샷

| 컬럼명 | 타입 | NULL | 설명 |
|---|---|---:|---|
| dashboard_snapshot_id | bigserial PK | N | 스냅샷 ID |
| snapshot_date | date | N | 기준일 |
| school_id | bigint FK | N | 학교 |
| class_id | bigint FK | Y | 학급 |
| grade_no | smallint | Y | 학년 |
| lesson_no | smallint | Y | 차시 |
| participation_rate | numeric(5,2) | Y | 참여율 |
| avg_response_time_sec | numeric(8,2) | Y | 평균응답시간 |
| digital_basic_index | numeric(6,2) | Y | 1차시 디지털 기초지수 |
| ai_basic_index | numeric(6,2) | Y | 2차시 AI 활용기초지수 |
| warning_flag | char(1) | N | Y/N |
| snapshot_json | jsonb | Y | 차트 데이터 |
| created_at | timestamptz | N | 생성일시 |

인덱스:
- idx_dashboard_snapshot_school_class (school_id, class_id, grade_no)

---

## 6-20. report_jobs
보고서 생성 요청

| 컬럼명 | 타입 | NULL | 설명 |
|---|---|---:|---|
| report_job_id | bigserial PK | N | 잡 ID |
| requested_by_user_id | bigint FK | N | users.user_id |
| school_id | bigint FK | N | 학교 |
| class_id | bigint FK | Y | 학급 |
| report_type | varchar(50) | N | class_summary / school_summary |
| report_period_start | date | N | 시작일 |
| report_period_end | date | N | 종료일 |
| status_code | varchar(30) | N | queued / running / done / failed |
| requested_at | timestamptz | N | 요청시각 |
| finished_at | timestamptz | Y | 완료시각 |

---

## 6-21. generated_reports
생성된 파일 메타

| 컬럼명 | 타입 | NULL | 설명 |
|---|---|---:|---|
| generated_report_id | bigserial PK | N | 파일 ID |
| report_job_id | bigint FK | N | report_jobs.report_job_id |
| file_name | varchar(255) | N | 파일명 |
| file_path | varchar(500) | N | 스토리지 경로 |
| file_format | varchar(20) | N | pdf/xlsx/png |
| generated_at | timestamptz | N | 생성일시 |

---

## 6-22. users
로그인 사용자

| 컬럼명 | 타입 | NULL | 설명 |
|---|---|---:|---|
| user_id | bigserial PK | N | 사용자 ID |
| school_id | bigint FK | Y | 소속 학교 |
| login_id | varchar(100) UNIQUE | N | 로그인ID |
| password_hash | text | N | 비밀번호 해시 |
| user_name | varchar(100) | N | 이름 |
| user_type | varchar(30) | N | admin / teacher / analyst |
| active_yn | char(1) | N | Y/N |
| last_login_at | timestamptz | Y | 마지막 로그인 |
| created_at | timestamptz | N | 생성일시 |

---

## 6-23. user_roles
권한 매핑

| 컬럼명 | 타입 | NULL | 설명 |
|---|---|---:|---|
| user_role_id | bigserial PK | N | 권한 ID |
| user_id | bigint FK | N | users.user_id |
| role_code | varchar(50) | N | SUPER_ADMIN / SCHOOL_ADMIN / TEACHER_VIEW |
| granted_at | timestamptz | N | 부여시각 |

유니크:
- uq_user_role (user_id, role_code)

---

## 6-24. audit_logs
관리자/운영 변경 이력

| 컬럼명 | 타입 | NULL | 설명 |
|---|---|---:|---|
| audit_log_id | bigserial PK | N | 로그 ID |
| user_id | bigint FK | Y | 작업 사용자 |
| target_table | varchar(100) | N | 대상 테이블 |
| target_pk | varchar(100) | N | 대상 PK |
| action_type | varchar(30) | N | INSERT / UPDATE / DELETE / LOGIN |
| before_json | jsonb | Y | 이전값 |
| after_json | jsonb | Y | 이후값 |
| created_at | timestamptz | N | 생성시각 |

---

## 7. 권장 FK 관계 요약

- schools.organization_id -> organizations.organization_id
- academic_terms.school_id -> schools.school_id
- classes.school_id -> schools.school_id
- classes.term_id -> academic_terms.term_id
- teachers.school_id -> schools.school_id
- students.class_id -> classes.class_id
- program_instances.program_id -> programs.program_id
- program_instances.school_id -> schools.school_id
- program_instances.term_id -> academic_terms.term_id
- lessons.program_instance_id -> program_instances.program_instance_id
- class_lesson_sessions.class_id -> classes.class_id
- class_lesson_sessions.lesson_id -> lessons.lesson_id
- assessment_pools -> grade, pool 기준 마스터
- items.pool_id -> assessment_pools.pool_id
- item_options.item_id -> items.item_id
- item_exposure_logs.session_id -> class_lesson_sessions.session_id
- item_exposure_logs.student_id -> students.student_id
- student_responses.exposure_id -> item_exposure_logs.exposure_id
- student_responses.item_id -> items.item_id
- report_jobs.requested_by_user_id -> users.user_id

---

## 8. 필수 인덱스 전략

### OLTP 인덱스
- students(student_hash_id)
- classes(school_id, term_id, grade_no)
- lessons(program_instance_id, lesson_no)
- items(school_level_code, grade_no, pool_code, active_yn)
- item_exposure_logs(session_id, student_id)
- student_responses(session_id, item_id)
- student_responses(student_id, submitted_at)

### 집계 인덱스
- student_responses(submitted_at)
- student_responses(item_id, is_correct)
- domain_score_snapshots(snapshot_date, school_id, class_id, grade_no)
- class_dashboard_snapshots(snapshot_date, school_id, class_id)

---

## 9. 파티셔닝 권장

운영 학생 수가 커지면 **student_responses**와 **response_events**는 빠르게 커진다.

권장:
- student_responses: submitted_at 기준 월별 range partition
- response_events: occurred_at 기준 월별 partition

예:
- student_responses_2026_03
- student_responses_2026_04

장점:
- 조회 성능 개선
- 보관 정책 관리 용이
- 기간별 삭제/아카이빙 쉬움

---

## 10. 개인정보/보안 권장사항

1. 학생 실명은 기본 DB에 저장하지 않는 방향 권장
2. student_hash_id를 기본 식별자로 사용
3. teacher phone/email은 암호화 저장
4. password_hash는 Argon2 또는 bcrypt 사용
5. audit_logs 필수 적용
6. 보고서 다운로드 권한은 학교별 row-level security 적용 검토
7. 분석용 뷰는 익명화된 집계만 노출

---

## 11. 랜덤 출제 로직을 위한 조회 규칙

우선순위:
1. 해당 학년 + pool_code 일치
2. active_yn = 'Y'
3. 학생에게 아직 미노출 문항
4. 학급 내 노출 횟수가 가장 적은 문항 우선
5. anchor 문항은 exposure_weight 1.2
6. 동률 시 random()

필요한 보조 뷰:
- v_item_exposure_count_by_class
- v_student_unseen_items

---

## 12. 집계용 뷰 설계

### 12-1. v_item_response_stats
문항별 정답률/응답수

### 12-2. v_class_domain_scores
학급별 영역 평균 점수

### 12-3. v_grade_dashboard
학년별 참여율/영역지수

### 12-4. v_school_overview
학교 전체 요약 지표

### 12-5. mv_school_daily_dashboard
대시보드 가속용 materialized view

---

## 13. 최소 SQL DDL 초안

아래 DDL은 핵심 테이블만 우선 제시한다.

```sql
CREATE TABLE organizations (
  organization_id BIGSERIAL PRIMARY KEY,
  organization_name VARCHAR(200) NOT NULL,
  organization_type VARCHAR(50) NOT NULL,
  region_code VARCHAR(20),
  active_yn CHAR(1) NOT NULL DEFAULT 'Y',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE schools (
  school_id BIGSERIAL PRIMARY KEY,
  organization_id BIGINT NOT NULL REFERENCES organizations(organization_id),
  school_name VARCHAR(200) NOT NULL,
  school_level_code CHAR(1) NOT NULL,
  school_type VARCHAR(50),
  region_code VARCHAR(20),
  school_code_external VARCHAR(50),
  active_yn CHAR(1) NOT NULL DEFAULT 'Y',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE academic_terms (
  term_id BIGSERIAL PRIMARY KEY,
  school_id BIGINT NOT NULL REFERENCES schools(school_id),
  term_name VARCHAR(100) NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE classes (
  class_id BIGSERIAL PRIMARY KEY,
  school_id BIGINT NOT NULL REFERENCES schools(school_id),
  term_id BIGINT NOT NULL REFERENCES academic_terms(term_id),
  class_name VARCHAR(100) NOT NULL,
  grade_no SMALLINT NOT NULL,
  homeroom_teacher_id BIGINT,
  student_count_planned INTEGER,
  active_yn CHAR(1) NOT NULL DEFAULT 'Y',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE teachers (
  teacher_id BIGSERIAL PRIMARY KEY,
  school_id BIGINT NOT NULL REFERENCES schools(school_id),
  teacher_name VARCHAR(100) NOT NULL,
  role_title VARCHAR(100),
  phone_enc TEXT,
  email_enc TEXT,
  active_yn CHAR(1) NOT NULL DEFAULT 'Y',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE students (
  student_id BIGSERIAL PRIMARY KEY,
  class_id BIGINT NOT NULL REFERENCES classes(class_id),
  student_hash_id VARCHAR(64) NOT NULL UNIQUE,
  grade_no SMALLINT NOT NULL,
  student_no VARCHAR(30),
  gender_code VARCHAR(10),
  active_yn CHAR(1) NOT NULL DEFAULT 'Y',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE programs (
  program_id BIGSERIAL PRIMARY KEY,
  program_name VARCHAR(200) NOT NULL,
  content_type VARCHAR(50) NOT NULL,
  duration_lessons SMALLINT NOT NULL,
  active_yn CHAR(1) NOT NULL DEFAULT 'Y',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE program_instances (
  program_instance_id BIGSERIAL PRIMARY KEY,
  program_id BIGINT NOT NULL REFERENCES programs(program_id),
  school_id BIGINT NOT NULL REFERENCES schools(school_id),
  term_id BIGINT NOT NULL REFERENCES academic_terms(term_id),
  instructor_name VARCHAR(100),
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  status_code VARCHAR(30) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE lessons (
  lesson_id BIGSERIAL PRIMARY KEY,
  program_instance_id BIGINT NOT NULL REFERENCES program_instances(program_instance_id),
  lesson_no SMALLINT NOT NULL,
  lesson_title VARCHAR(200),
  pool_code VARCHAR(10),
  lesson_date DATE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_lessons_instance_no UNIQUE (program_instance_id, lesson_no)
);

CREATE TABLE class_lesson_sessions (
  session_id BIGSERIAL PRIMARY KEY,
  class_id BIGINT NOT NULL REFERENCES classes(class_id),
  lesson_id BIGINT NOT NULL REFERENCES lessons(lesson_id),
  started_at TIMESTAMPTZ,
  ended_at TIMESTAMPTZ,
  attendance_count INTEGER,
  status_code VARCHAR(30) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_session_class_lesson UNIQUE (class_id, lesson_id)
);

CREATE TABLE assessment_pools (
  pool_id BIGSERIAL PRIMARY KEY,
  school_level_code CHAR(1) NOT NULL,
  grade_no SMALLINT NOT NULL,
  pool_code VARCHAR(10) NOT NULL,
  pool_name VARCHAR(100) NOT NULL,
  total_items INTEGER NOT NULL,
  anchor_item_count INTEGER NOT NULL,
  version_no VARCHAR(20) NOT NULL,
  active_yn CHAR(1) NOT NULL DEFAULT 'Y',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_pool_grade_code_version UNIQUE (school_level_code, grade_no, pool_code, version_no)
);

CREATE TABLE items (
  item_id VARCHAR(30) PRIMARY KEY,
  pool_id BIGINT NOT NULL REFERENCES assessment_pools(pool_id),
  school_level_code CHAR(1) NOT NULL,
  grade_no SMALLINT NOT NULL,
  pool_code VARCHAR(10) NOT NULL,
  anchor_flag CHAR(1) NOT NULL DEFAULT 'N',
  domain_code VARCHAR(10) NOT NULL,
  subdomain_code VARCHAR(30),
  item_type_code VARCHAR(20) NOT NULL,
  difficulty_band CHAR(1) NOT NULL,
  item_goal VARCHAR(300),
  item_text TEXT NOT NULL,
  correct_option_no SMALLINT,
  score_correct NUMERIC(6,2) NOT NULL DEFAULT 100,
  score_incorrect NUMERIC(6,2) NOT NULL DEFAULT 0,
  exposure_weight NUMERIC(5,2) NOT NULL DEFAULT 1.00,
  active_yn CHAR(1) NOT NULL DEFAULT 'Y',
  version_no VARCHAR(20) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE item_options (
  option_id BIGSERIAL PRIMARY KEY,
  item_id VARCHAR(30) NOT NULL REFERENCES items(item_id) ON DELETE CASCADE,
  option_no SMALLINT NOT NULL,
  option_text TEXT NOT NULL,
  is_correct CHAR(1) NOT NULL DEFAULT 'N',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_item_option_no UNIQUE (item_id, option_no)
);

CREATE TABLE item_exposure_logs (
  exposure_id BIGSERIAL PRIMARY KEY,
  session_id BIGINT NOT NULL REFERENCES class_lesson_sessions(session_id),
  student_id BIGINT NOT NULL REFERENCES students(student_id),
  item_id VARCHAR(30) NOT NULL REFERENCES items(item_id),
  exposed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  random_seed VARCHAR(100),
  exposure_rank INTEGER,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_exposure_session_student UNIQUE (session_id, student_id)
);

CREATE TABLE student_responses (
  response_id BIGSERIAL PRIMARY KEY,
  exposure_id BIGINT NOT NULL REFERENCES item_exposure_logs(exposure_id) ON DELETE CASCADE,
  session_id BIGINT NOT NULL REFERENCES class_lesson_sessions(session_id),
  student_id BIGINT NOT NULL REFERENCES students(student_id),
  item_id VARCHAR(30) NOT NULL REFERENCES items(item_id),
  response_value VARCHAR(50),
  selected_option_no SMALLINT,
  is_correct CHAR(1),
  raw_score NUMERIC(6,2),
  response_time_sec INTEGER,
  started_at TIMESTAMPTZ,
  submitted_at TIMESTAMPTZ,
  no_response_flag CHAR(1) NOT NULL DEFAULT 'N',
  abnormal_flag CHAR(1) NOT NULL DEFAULT 'N',
  device_type VARCHAR(30),
  browser_type VARCHAR(50),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_response_exposure UNIQUE (exposure_id)
);

CREATE TABLE response_events (
  response_event_id BIGSERIAL PRIMARY KEY,
  response_id BIGINT REFERENCES student_responses(response_id) ON DELETE CASCADE,
  exposure_id BIGINT REFERENCES item_exposure_logs(exposure_id) ON DELETE CASCADE,
  event_type VARCHAR(50) NOT NULL,
  event_payload JSONB,
  occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE domain_score_snapshots (
  snapshot_id BIGSERIAL PRIMARY KEY,
  snapshot_date DATE NOT NULL,
  scope_type VARCHAR(20) NOT NULL,
  school_id BIGINT NOT NULL REFERENCES schools(school_id),
  class_id BIGINT REFERENCES classes(class_id),
  grade_no SMALLINT,
  student_id BIGINT REFERENCES students(student_id),
  lesson_no SMALLINT,
  domain_code VARCHAR(10) NOT NULL,
  response_count INTEGER NOT NULL,
  correct_rate NUMERIC(5,2),
  score_avg NUMERIC(6,2),
  computed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE class_dashboard_snapshots (
  dashboard_snapshot_id BIGSERIAL PRIMARY KEY,
  snapshot_date DATE NOT NULL,
  school_id BIGINT NOT NULL REFERENCES schools(school_id),
  class_id BIGINT REFERENCES classes(class_id),
  grade_no SMALLINT,
  lesson_no SMALLINT,
  participation_rate NUMERIC(5,2),
  avg_response_time_sec NUMERIC(8,2),
  digital_basic_index NUMERIC(6,2),
  ai_basic_index NUMERIC(6,2),
  warning_flag CHAR(1) NOT NULL DEFAULT 'N',
  snapshot_json JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE users (
  user_id BIGSERIAL PRIMARY KEY,
  school_id BIGINT REFERENCES schools(school_id),
  login_id VARCHAR(100) NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  user_name VARCHAR(100) NOT NULL,
  user_type VARCHAR(30) NOT NULL,
  active_yn CHAR(1) NOT NULL DEFAULT 'Y',
  last_login_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE user_roles (
  user_role_id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  role_code VARCHAR(50) NOT NULL,
  granted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_user_role UNIQUE (user_id, role_code)
);

CREATE TABLE report_jobs (
  report_job_id BIGSERIAL PRIMARY KEY,
  requested_by_user_id BIGINT NOT NULL REFERENCES users(user_id),
  school_id BIGINT NOT NULL REFERENCES schools(school_id),
  class_id BIGINT REFERENCES classes(class_id),
  report_type VARCHAR(50) NOT NULL,
  report_period_start DATE NOT NULL,
  report_period_end DATE NOT NULL,
  status_code VARCHAR(30) NOT NULL,
  requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  finished_at TIMESTAMPTZ
);

CREATE TABLE generated_reports (
  generated_report_id BIGSERIAL PRIMARY KEY,
  report_job_id BIGINT NOT NULL REFERENCES report_jobs(report_job_id) ON DELETE CASCADE,
  file_name VARCHAR(255) NOT NULL,
  file_path VARCHAR(500) NOT NULL,
  file_format VARCHAR(20) NOT NULL,
  generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE audit_logs (
  audit_log_id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(user_id),
  target_table VARCHAR(100) NOT NULL,
  target_pk VARCHAR(100) NOT NULL,
  action_type VARCHAR(30) NOT NULL,
  before_json JSONB,
  after_json JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_schools_org ON schools(organization_id);
CREATE INDEX idx_classes_school_term ON classes(school_id, term_id);
CREATE INDEX idx_students_class ON students(class_id);
CREATE INDEX idx_lessons_instance_no ON lessons(program_instance_id, lesson_no);
CREATE INDEX idx_items_grade_pool ON items(school_level_code, grade_no, pool_code);
CREATE INDEX idx_items_domain ON items(domain_code);
CREATE INDEX idx_exposure_session_student ON item_exposure_logs(session_id, student_id);
CREATE INDEX idx_responses_session_item ON student_responses(session_id, item_id);
CREATE INDEX idx_responses_student_submitted ON student_responses(student_id, submitted_at);
CREATE INDEX idx_response_events_type ON response_events(event_type);
CREATE INDEX idx_domain_snapshot_scope ON domain_score_snapshots(scope_type, school_id, class_id, grade_no);
CREATE INDEX idx_dashboard_snapshot_school_class ON class_dashboard_snapshots(school_id, class_id, grade_no);
```

---

## 14. 대시보드용 예시 뷰

```sql
CREATE OR REPLACE VIEW v_item_response_stats AS
SELECT
    r.item_id,
    COUNT(*) AS response_count,
    SUM(CASE WHEN r.is_correct = 'Y' THEN 1 ELSE 0 END) AS correct_count,
    ROUND(100.0 * SUM(CASE WHEN r.is_correct = 'Y' THEN 1 ELSE 0 END) / NULLIF(COUNT(*),0), 2) AS correct_rate
FROM student_responses r
WHERE r.no_response_flag = 'N'
GROUP BY r.item_id;

CREATE OR REPLACE VIEW v_class_domain_scores AS
SELECT
    c.school_id,
    c.class_id,
    c.grade_no,
    i.domain_code,
    COUNT(*) AS response_count,
    ROUND(AVG(COALESCE(r.raw_score,0)), 2) AS score_avg
FROM student_responses r
JOIN items i ON r.item_id = i.item_id
JOIN classes c ON r.student_id IN (
    SELECT s.student_id FROM students s WHERE s.class_id = c.class_id
)
GROUP BY c.school_id, c.class_id, c.grade_no, i.domain_code;
```

실구현 시 `JOIN classes c ON r.student_id IN (...)` 형태는 비효율적이므로  
`student_responses -> students -> classes` 직접 조인으로 변경한다.

---

## 15. 운영 시퀀스

1. 학교/학급/학생 등록
2. 프로그램 인스턴스 생성
3. 차시 생성
4. 학년별 문항풀 연결
5. 차시 시작 시 session 생성
6. 학생 로그인
7. item_exposure_logs 생성
8. student_responses 저장
9. 배치/실시간 집계
10. 대시보드 스냅샷 생성
11. 교사용 보고서 생성

---

## 16. 개발 우선순위

### 1차 개발(MVP)
- organizations ~ students
- programs ~ lessons
- assessment_pools / items / item_options
- item_exposure_logs
- student_responses
- users / roles
- 기본 집계 뷰 3개

### 2차 개발
- response_events
- domain_score_snapshots
- class_dashboard_snapshots
- report_jobs / generated_reports

### 3차 개발
- RLS
- materialized view refresh 자동화
- 캐시 전략
- 고급 이상징후 탐지

---

## 17. 최종 권장

현 단계에서는 **정규화된 관계형 구조 + 집계 스냅샷 테이블 + 보고서 메타 관리** 구조가 가장 안정적이다.

특히 로보그램 운영자료에 이미 제시된 **학기형 10~20차시 운영**, **LMS 기반 과제·수료관리 기능 연계 가능**, **학생 학습 리포트 제공** 흐름과 맞추려면, DB도 단순 응답 저장을 넘어 **차시 운영 + 보고서 생성 + 집계 스냅샷**까지 포함해야 한다.  
