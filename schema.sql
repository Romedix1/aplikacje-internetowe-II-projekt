-- Typy
CREATE TYPE user_role AS ENUM ('student', 'uopz', 'zopz', 'sekretariat');
CREATE TYPE doc_status AS ENUM ('draft', 'submitted', 'needs_revision', 'approved');
CREATE TYPE internship_status AS ENUM ('pending', 'active', 'completed', 'cancelled');

-- ------------------------------------------------------------
-- USERS — wszyscy użytkownicy systemu (studenci, opiekunowie)
-- ------------------------------------------------------------
CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    first_name      VARCHAR(100) NOT NULL,
    last_name       VARCHAR(100) NOT NULL,
    role            user_role   NOT NULL,
    created_at      TIMESTAMP   NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- INTERNSHIP — praktyka zawodowa (1 rekord = 1 praktyka studenta)
-- ------------------------------------------------------------
CREATE TABLE internship (
    id              SERIAL PRIMARY KEY,
    student_id      INT         NOT NULL REFERENCES users(id),
    uopz_id         INT         NOT NULL REFERENCES users(id),
    zopz_id         INT         NOT NULL REFERENCES users(id),
    company_name    VARCHAR(255) NOT NULL,
    company_address VARCHAR(255),
    start_date      DATE        NOT NULL,
    end_date        DATE        NOT NULL,
    status          internship_status NOT NULL DEFAULT 'pending',
    created_at      TIMESTAMP   NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP   NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- PROGRAM_SCHEDULE — Program i harmonogram praktyki (Zał. 2a)
-- ------------------------------------------------------------
CREATE TABLE program_schedule (
    id              SERIAL PRIMARY KEY,
    internship_id   INT         NOT NULL UNIQUE REFERENCES internship(id),
    goals           TEXT,
    tasks           TEXT,
    status          doc_status  NOT NULL DEFAULT 'draft',
    created_at      TIMESTAMP   NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP   NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- INTERNSHIP_CARD — Karta praktyki zawodowej (Zał. 3)
-- ------------------------------------------------------------
CREATE TABLE internship_card (
    id              SERIAL PRIMARY KEY,
    internship_id   INT         NOT NULL UNIQUE REFERENCES internship(id),
    zopz_opinion    TEXT,
    grade           VARCHAR(5),
    status          doc_status  NOT NULL DEFAULT 'draft',
    created_at      TIMESTAMP   NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP   NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- DIARY — Dziennik praktyki zawodowej (Zał. 6)
-- ------------------------------------------------------------
CREATE TABLE diary (
    id              SERIAL PRIMARY KEY,
    internship_id   INT         NOT NULL UNIQUE REFERENCES internship(id),
    status          doc_status  NOT NULL DEFAULT 'draft',
    submitted_at    TIMESTAMP,
    approved_at     TIMESTAMP,
    created_at      TIMESTAMP   NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP   NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- DIARY_ENTRY — pojedynczy wpis w dzienniku (tabela dynamiczna)
-- ------------------------------------------------------------
CREATE TABLE diary_entry (
    id                  SERIAL PRIMARY KEY,
    diary_id            INT         NOT NULL REFERENCES diary(id),
    work_date           DATE        NOT NULL,
    description         TEXT        NOT NULL,
    hours               INT         NOT NULL CHECK (hours BETWEEN 1 AND 8),
    confirmed_by_zopz   BOOLEAN     NOT NULL DEFAULT FALSE,
    confirmed_at        TIMESTAMP
);

-- ------------------------------------------------------------
-- LEARNING_OUTCOMES — Potwierdzenie efektów uczenia się (Zał. 4)
-- ------------------------------------------------------------
CREATE TABLE learning_outcomes (
    id                  SERIAL PRIMARY KEY,
    internship_id       INT         NOT NULL REFERENCES internship(id),
    outcome_description TEXT        NOT NULL,
    achieved            BOOLEAN     NOT NULL DEFAULT FALSE,
    uopz_comment        TEXT,
    created_at          TIMESTAMP   NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP   NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- REPORT — Sprawozdanie z praktyki (Zał. 7)
-- ------------------------------------------------------------
CREATE TABLE report (
    id              SERIAL PRIMARY KEY,
    internship_id   INT         NOT NULL UNIQUE REFERENCES internship(id),
    self_assessment TEXT,
    content         TEXT,
    status          doc_status  NOT NULL DEFAULT 'draft',
    submitted_at    TIMESTAMP,
    approved_at     TIMESTAMP,
    created_at      TIMESTAMP   NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP   NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- SURVEY — Kwestionariusz ankiety (Zał. 5)
-- ------------------------------------------------------------
CREATE TABLE survey (
    id                  SERIAL PRIMARY KEY,
    internship_id       INT         NOT NULL UNIQUE REFERENCES internship(id),
    overall_rating      INT         CHECK (overall_rating BETWEEN 1 AND 5),
    company_feedback    TEXT,
    tasks_feedback      TEXT,
    suggestions         TEXT,
    submitted_at        TIMESTAMP
);

-- ------------------------------------------------------------
-- EXAM_PROTOCOL — Protokół egzaminu ustnego (Zał. 8)
-- ------------------------------------------------------------
CREATE TABLE exam_protocol (
    id                  SERIAL PRIMARY KEY,
    internship_id       INT         NOT NULL UNIQUE REFERENCES internship(id),
    grade               VARCHAR(5)  NOT NULL,
    commission_notes    TEXT,
    exam_date           DATE        NOT NULL,
    created_at          TIMESTAMP   NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- DOCUMENT_COMMENT — uwagi opiekunów do dokumentów
-- ------------------------------------------------------------
CREATE TABLE document_comment (
    id              SERIAL PRIMARY KEY,
    author_id       INT         NOT NULL REFERENCES users(id),
    document_type   VARCHAR(50) NOT NULL,   -- 'diary', 'report', 'card' itp.
    document_id     INT         NOT NULL,
    content         TEXT        NOT NULL,
    created_at      TIMESTAMP   NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- Indeksy pomocnicze
-- ------------------------------------------------------------
CREATE INDEX idx_internship_student ON internship(student_id);
CREATE INDEX idx_internship_uopz    ON internship(uopz_id);
CREATE INDEX idx_diary_entry_diary  ON diary_entry(diary_id);
CREATE INDEX idx_comment_doc        ON document_comment(document_type, document_id);
