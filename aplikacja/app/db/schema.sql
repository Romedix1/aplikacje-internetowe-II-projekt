CREATE TYPE user_role AS ENUM (
    'student',
    'uopz',
    'zopz',
    'sekretariat',
    'administrator',
    'pending'
);

CREATE TYPE doc_status AS ENUM (
    'draft',
    'submitted',
    'under_review',
    'needs_revision',
    'approved'
);

CREATE TYPE internship_status AS ENUM ('pending', 'active', 'completed', 'cancelled');

-- ------------------------------------------------------------
-- USERS — wszyscy użytkownicy systemu
-- ------------------------------------------------------------
CREATE TABLE
    users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) NOT NULL UNIQUE,
        first_name VARCHAR(100) NOT NULL,
        last_name VARCHAR(100) NOT NULL,
        auth_provider VARCHAR(50) NOT NULL DEFAULT 'microsoft',
        index_number VARCHAR(20) UNIQUE,
        external_id VARCHAR(255) UNIQUE,
        role user_role NOT NULL,
        study_field VARCHAR(100),
        study_year VARCHAR(20),
        study_form VARCHAR(50),
        semester INTEGER,
        is_active BOOLEAN NOT NULL DEFAULT TRUE,
        created_at TIMESTAMP NOT NULL DEFAULT NOW (),
        updated_at TIMESTAMP NOT NULL DEFAULT NOW ()
    );

-- ------------------------------------------------------------
-- INTERNSHIP — praktyka zawodowa (1 rekord = 1 praktyka studenta)
-- ------------------------------------------------------------
CREATE TABLE
    internship (
        id SERIAL PRIMARY KEY,
        student_id INT NOT NULL REFERENCES users (id),
        uopz_id INT REFERENCES users (id),
        zopz_id INT REFERENCES users (id),
        company_name VARCHAR(255) NOT NULL,
        company_address VARCHAR(255),
        agreement_no VARCHAR(50),
        agreement_date DATE,
        start_date DATE NOT NULL,
        end_date DATE NOT NULL,
        working_days INT NOT NULL DEFAULT 120 CHECK (working_days = 120),
        status internship_status NOT NULL DEFAULT 'pending',
        created_at TIMESTAMP NOT NULL DEFAULT NOW (),
        updated_at TIMESTAMP NOT NULL DEFAULT NOW (),
        CHECK (end_date > start_date)
    );

-- ------------------------------------------------------------
-- PROGRAM_SCHEDULE — Program i harmonogram praktyki (Zał. 2a)
-- ------------------------------------------------------------
CREATE TABLE
    program_schedule (
        id SERIAL PRIMARY KEY,
        internship_id INT NOT NULL UNIQUE REFERENCES internship (id),
        agreed_date DATE,
        uopz_comment VARCHAR(255),
        status doc_status NOT NULL DEFAULT 'draft',
        created_at TIMESTAMP NOT NULL DEFAULT NOW (),
        updated_at TIMESTAMP NOT NULL DEFAULT NOW ()
    );

-- Harmonogram dni roboczych
CREATE TABLE
    schedule_entry (
        id SERIAL PRIMARY KEY,
        program_id INT NOT NULL REFERENCES program_schedule (id) ON DELETE CASCADE,
        lp INT NOT NULL,
        department VARCHAR(255) NOT NULL,
        planned_days INT NOT NULL CHECK (planned_days > 0),
        UNIQUE (program_id, lp)
    );

-- Tabela zadań dla 13 efektów uczenia się
CREATE TABLE
    program_task (
        id SERIAL PRIMARY KEY,
        program_id INT NOT NULL REFERENCES program_schedule (id) ON DELETE CASCADE,
        outcome_number INT NOT NULL CHECK (outcome_number BETWEEN 1 AND 13),
        description TEXT NOT NULL DEFAULT '',
        UNIQUE (program_id, outcome_number)
    );

-- ------------------------------------------------------------
-- INTERNSHIP_CARD — Karta praktyki zawodowej (Zał. 3)
-- ------------------------------------------------------------
CREATE TABLE
    internship_card (
        id SERIAL PRIMARY KEY,
        internship_id INT NOT NULL UNIQUE REFERENCES internship (id),
        zopz_comment TEXT,
        zopz_grade VARCHAR(5),
        uopz_comment TEXT,
        uopz_grade VARCHAR(5),
        report_grade VARCHAR(5),
        status VARCHAR(50) NOT NULL DEFAULT 'draft',
        date DATE,
        created_at TIMESTAMP NOT NULL DEFAULT NOW (),
        updated_at TIMESTAMP NOT NULL DEFAULT NOW ()
    );

-- ------------------------------------------------------------
-- DIARY — Dziennik praktyki zawodowej (Zał. 6)
-- ------------------------------------------------------------
CREATE TABLE
    diary (
        id SERIAL PRIMARY KEY,
        internship_id INT NOT NULL UNIQUE REFERENCES internship (id),
        status VARCHAR(50) NOT NULL DEFAULT 'draft',
        submitted_at TIMESTAMP,
        approved_at TIMESTAMP,
        created_at TIMESTAMP NOT NULL DEFAULT NOW (),
        updated_at TIMESTAMP NOT NULL DEFAULT NOW ()
    );

-- Pojedynczy wpis w dzienniku
CREATE TABLE
    diary_entry (
        id SERIAL PRIMARY KEY,
        diary_id INT NOT NULL REFERENCES diary (id),
        day_number INT NOT NULL CHECK (day_number BETWEEN 1 AND 120),
        work_date DATE NOT NULL,
        description TEXT NOT NULL,
        outcome_numbers VARCHAR(50),
        is_rejected BOOLEAN DEFAULT FALSE NOT NULL,
        confirmed_by_zopz BOOLEAN NOT NULL DEFAULT FALSE,
        confirmed_at TIMESTAMP,
        UNIQUE (diary_id, day_number),
        UNIQUE (diary_id, work_date)
    );

-- ------------------------------------------------------------
-- LEARNING_OUTCOMES — Potwierdzenie efektów uczenia się (Zał. 4)
-- ------------------------------------------------------------
CREATE TABLE
    learning_outcomes_forms (
        id SERIAL PRIMARY KEY,
        internship_id INTEGER REFERENCES internship (id) ON DELETE CASCADE,
        status VARCHAR(20) DEFAULT 'draft',
        supervisor_comment_general TEXT,
        submitted_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

-- 3. Tworzenie tabeli dla poszczególnych 13 efektów
CREATE TABLE
    learning_outcomes_items (
        id SERIAL PRIMARY KEY,
        form_id INTEGER REFERENCES learning_outcomes_forms (id) ON DELETE CASCADE,
        outcome_number INTEGER NOT NULL,
        achieved BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

-- ------------------------------------------------------------
-- REPORT — Sprawozdanie z praktyki (Zał. 7)
-- ------------------------------------------------------------
CREATE TABLE
    report (
        id SERIAL PRIMARY KEY,
        internship_id INT NOT NULL UNIQUE REFERENCES internship (id),
        company_description TEXT,
        work_description TEXT,
        self_assessment TEXT,
        status doc_status NOT NULL DEFAULT 'draft',
        submitted_at TIMESTAMP,
        approved_at TIMESTAMP,
        created_at TIMESTAMP NOT NULL DEFAULT NOW (),
        updated_at TIMESTAMP NOT NULL DEFAULT NOW ()
    );

-- ------------------------------------------------------------
-- SURVEY — Kwestionariusz ankiety (Zał. 5)
-- ------------------------------------------------------------
CREATE TABLE
    survey (
        id SERIAL PRIMARY KEY,
        internship_id INT NOT NULL UNIQUE REFERENCES internship (id),
        status VARCHAR(50) NOT NULL DEFAULT 'draft',
        remarks TEXT,
        q1 INT,
        q2 INT,
        q3 INT,
        q4 INT,
        q5 INT,
        q6 INT,
        q7 INT,
        q8 INT,
        q9 INT,
        q10 INT,
        q11 INT,
        q12 INT,
        q13 INT,
        q14 INT,
        submitted_at TIMESTAMP,
        created_at TIMESTAMP NOT NULL DEFAULT NOW (),
        updated_at TIMESTAMP NOT NULL DEFAULT NOW ()
    );

CREATE TABLE
    document (
        id SERIAL PRIMARY KEY,
        internship_id INT NOT NULL REFERENCES internship (id),
        name VARCHAR(255) NOT NULL,
        doc_type VARCHAR(50) NOT NULL,
        status VARCHAR(50) NOT NULL DEFAULT 'draft',
        submitted_at TIMESTAMP,
        supervisor_comment TEXT,
        created_at TIMESTAMP NOT NULL DEFAULT NOW ()
    );

-- ------------------------------------------------------------
-- EXAM_PROTOCOL — Protokół egzaminu ustnego (Zał. 8)
-- ------------------------------------------------------------
CREATE TABLE
    exam_protocol (
        id SERIAL PRIMARY KEY,
        internship_id INT NOT NULL UNIQUE REFERENCES internship (id),
        grade VARCHAR(5) NOT NULL CHECK (grade IN ('2', '3', '3.5', '4', '4.5', '5')),
        commission_notes TEXT,
        exam_date DATE NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT NOW ()
    );

-- ------------------------------------------------------------
-- DOCUMENT_COMMENT — uwagi opiekunów do dokumentów (F-06)
-- ------------------------------------------------------------
CREATE TABLE
    document_comment (
        id SERIAL PRIMARY KEY,
        author_id INT NOT NULL REFERENCES users (id),
        document_type VARCHAR(50) NOT NULL CHECK (
            document_type IN (
                'diary',
                'report',
                'card',
                'program_schedule',
                'learning_outcomes'
            )
        ),
        document_id INT NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT NOW ()
    );

-- ------------------------------------------------------------
-- Indeksy pomocnicze
-- ------------------------------------------------------------
CREATE INDEX idx_internship_student ON internship (student_id);

CREATE INDEX idx_internship_uopz ON internship (uopz_id);

CREATE INDEX idx_internship_zopz ON internship (zopz_id);

CREATE INDEX idx_diary_entry_diary ON diary_entry (diary_id);

CREATE INDEX idx_diary_entry_date ON diary_entry (work_date);

CREATE INDEX idx_learning_outcomes_int ON learning_outcomes_forms (internship_id);

CREATE INDEX idx_comment_doc ON document_comment (document_type, document_id);

CREATE INDEX idx_schedule_entry_prog ON schedule_entry (program_id);