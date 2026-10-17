-- 로보그램 LMS DB 설계 SQL 초안 v1.0
-- PostgreSQL 15+ 기준

BEGIN;

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

CREATE TABLE classes (
  class_id BIGSERIAL PRIMARY KEY,
  school_id BIGINT NOT NULL REFERENCES schools(school_id),
  term_id BIGINT NOT NULL REFERENCES academic_terms(term_id),
  class_name VARCHAR(100) NOT NULL,
  grade_no SMALLINT NOT NULL,
  homeroom_teacher_id BIGINT REFERENCES teachers(teacher_id),
  student_count_planned INTEGER,
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

COMMIT;