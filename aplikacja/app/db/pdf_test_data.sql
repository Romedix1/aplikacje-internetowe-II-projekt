INSERT INTO
    users (
        id,
        email,
        first_name,
        last_name,
        auth_provider,
        index_number,
        external_id,
        role,
        study_field,
        study_year,
        study_form,
        semester,
        is_active
    )
VALUES
    (
        5000,
        'student@development.pl',
        'Piotr',
        'Wiśniewski',
        'microsoft',
        '12345',
        'ext-student-001',
        'student',
        'Inżynieria Oprogramowania',
        '2024/2025',
        'stacjonarne',
        7,
        TRUE
    );

INSERT INTO
    users (
        id,
        email,
        first_name,
        last_name,
        auth_provider,
        index_number,
        external_id,
        role,
        is_active
    )
VALUES
    (
        5001,
        'uopz@development.pl',
        'Jan',
        'Kowalski',
        'microsoft',
        NULL,
        'ext-uopz-001',
        'uopz',
        TRUE
    );

INSERT INTO
    users (
        id,
        email,
        first_name,
        last_name,
        auth_provider,
        index_number,
        external_id,
        role,
        is_active
    )
VALUES
    (
        5002,
        'zopz@development.pl',
        'Anna',
        'Nowak',
        'microsoft',
        NULL,
        'ext-zopz-001',
        'zopz',
        TRUE
    );

INSERT INTO
    users (
        id,
        email,
        first_name,
        last_name,
        auth_provider,
        index_number,
        external_id,
        role,
        is_active
    )
VALUES
    (
        5003,
        'sekretariat@development.pl',
        'Maria',
        'Kamińska',
        'microsoft',
        NULL,
        'ext-sek-001',
        'sekretariat',
        TRUE
    );

INSERT INTO
    users (
        id,
        email,
        first_name,
        last_name,
        auth_provider,
        index_number,
        external_id,
        role,
        is_active
    )
VALUES
    (
        5004,
        'admin@development.pl',
        'Admin',
        'Testowy',
        'microsoft',
        NULL,
        'ext-admin-001',
        'administrator',
        TRUE
    );

-- 1. INTERNSHIP — praktyka
INSERT INTO
    internship (
        id,
        student_id,
        uopz_id,
        zopz_id,
        company_name,
        company_address,
        agreement_no,
        agreement_date,
        start_date,
        end_date,
        working_days,
        status
    )
VALUES
    (
        100,
        5000,
        5001,
        5002,
        'Firma Testowa Sp. z o.o.',
        'ul. Testowa 1, 80-001 Gdańsk',
        'PZ/2024/001',
        '2024-01-15',
        '2024-02-01',
        '2024-07-31',
        120,
        'completed'
    );

-- 2. INTERNSHIP_CARD — Karta praktyki (Zał. 3)
INSERT INTO
    internship_card (
        internship_id,
        zopz_comment,
        zopz_grade,
        uopz_comment,
        uopz_grade,
        report_grade,
        status,
        date
    )
VALUES
    (
        100,
        'Student wykazał się wysokim zaangażowaniem i profesjonalizmem. Zadania były wykonywane terminowo i zgodnie z wymaganiami. Szczególnie wyróżniał się w obszarze programowania i analizy systemów.',
        '5',
        'Praktyka przebiegła zgodnie z planem. Student aktywnie uczestniczył w życiu firmy i zrealizował wszystkie założone efekty uczenia się.',
        '5',
        '4',
        'approved',
        '2024-07-31'
    );

-- 3. PROGRAM_SCHEDULE — Program i harmonogram (Zał. 2a)
INSERT INTO
    program_schedule (internship_id, agreed_date, uopz_comment, status)
VALUES
    (
        100,
        '2024-01-20',
        'Program zaakceptowany. Harmonogram jest realistyczny i zgodny z wymaganiami kierunku.',
        'approved'
    );

-- schedule_entry — działy/stanowiska (suma = 120 dni)
INSERT INTO
    schedule_entry (program_id, lp, department, planned_days)
VALUES
    (
        (
            SELECT
                id
            FROM
                program_schedule
            WHERE
                internship_id = 100
        ),
        1,
        'Dział IT / Programowanie',
        40
    ),
    (
        (
            SELECT
                id
            FROM
                program_schedule
            WHERE
                internship_id = 100
        ),
        2,
        'Dział Analiz i Systemów',
        30
    ),
    (
        (
            SELECT
                id
            FROM
                program_schedule
            WHERE
                internship_id = 100
        ),
        3,
        'Dział Obsługi Klienta IT',
        20
    ),
    (
        (
            SELECT
                id
            FROM
                program_schedule
            WHERE
                internship_id = 100
        ),
        4,
        'Dział Infrastruktury Sieciowej',
        20
    ),
    (
        (
            SELECT
                id
            FROM
                program_schedule
            WHERE
                internship_id = 100
        ),
        5,
        'Dział Bezpieczeństwa Informacji',
        10
    );

-- program_task — 13 efektów uczenia się
INSERT INTO
    program_task (program_id, outcome_number, description)
VALUES
    (
        (
            SELECT
                id
            FROM
                program_schedule
            WHERE
                internship_id = 100
        ),
        1,
        'Analiza wymagań i projektowanie systemów informatycznych przy użyciu notacji UML.'
    ),
    (
        (
            SELECT
                id
            FROM
                program_schedule
            WHERE
                internship_id = 100
        ),
        2,
        'Programowanie aplikacji webowych w technologiach Python/Flask oraz JavaScript.'
    ),
    (
        (
            SELECT
                id
            FROM
                program_schedule
            WHERE
                internship_id = 100
        ),
        3,
        'Projektowanie i zarządzanie relacyjnymi bazami danych PostgreSQL.'
    ),
    (
        (
            SELECT
                id
            FROM
                program_schedule
            WHERE
                internship_id = 100
        ),
        4,
        'Testowanie oprogramowania — testy jednostkowe, integracyjne i akceptacyjne.'
    ),
    (
        (
            SELECT
                id
            FROM
                program_schedule
            WHERE
                internship_id = 100
        ),
        5,
        'Konfiguracja i administracja środowiskami serwerowymi Linux.'
    ),
    (
        (
            SELECT
                id
            FROM
                program_schedule
            WHERE
                internship_id = 100
        ),
        6,
        'Wdrażanie aplikacji z użyciem narzędzi CI/CD (GitLab, Docker).'
    ),
    (
        (
            SELECT
                id
            FROM
                program_schedule
            WHERE
                internship_id = 100
        ),
        7,
        'Dokumentowanie procesów i systemów informatycznych.'
    ),
    (
        (
            SELECT
                id
            FROM
                program_schedule
            WHERE
                internship_id = 100
        ),
        8,
        'Praca w zespole projektowym metodą Agile/Scrum.'
    ),
    (
        (
            SELECT
                id
            FROM
                program_schedule
            WHERE
                internship_id = 100
        ),
        9,
        'Stosowanie zasad bezpieczeństwa informacji i ochrony danych osobowych (RODO).'
    ),
    (
        (
            SELECT
                id
            FROM
                program_schedule
            WHERE
                internship_id = 100
        ),
        10,
        'Konfiguracja urządzeń sieciowych i diagnozowanie problemów sieciowych.'
    ),
    (
        (
            SELECT
                id
            FROM
                program_schedule
            WHERE
                internship_id = 100
        ),
        11,
        'Obsługa systemów helpdesk i wsparcie użytkowników końcowych.'
    ),
    (
        (
            SELECT
                id
            FROM
                program_schedule
            WHERE
                internship_id = 100
        ),
        12,
        'Analiza i optymalizacja wydajności systemów informatycznych.'
    ),
    (
        (
            SELECT
                id
            FROM
                program_schedule
            WHERE
                internship_id = 100
        ),
        13,
        'Prezentowanie wyników pracy i komunikacja z interesariuszami projektu.'
    );

-- 4. DIARY — Dziennik praktyki (Zał. 6)
INSERT INTO
    diary (internship_id, status, submitted_at, approved_at)
VALUES
    (
        100,
        'approved',
        '2024-07-31 12:00:00',
        '2024-08-05 10:00:00'
    );

-- diary_entry — 120 wpisów (dni robocze 2024-02-01 do 2024-07-31)
INSERT INTO
    diary_entry (
        diary_id,
        day_number,
        work_date,
        description,
        outcome_numbers,
        is_rejected,
        confirmed_by_zopz,
        confirmed_at
    )
SELECT
    (
        SELECT
            id
        FROM
            diary
        WHERE
            internship_id = 100
    ),
    ROW_NUMBER() OVER (
        ORDER BY
            d
    ),
    CAST(d AS DATE),
    CASE MOD(
            CAST(
                ROW_NUMBER() OVER (
                    ORDER BY
                        d
                ) AS INTEGER
            ),
            13
        )
        WHEN 0 THEN 'Analiza wymagań nowego modułu systemu ERP. Udział w spotkaniu z klientem.'
        WHEN 1 THEN 'Programowanie endpointów REST API w Pythonie. Code review z mentorem.'
        WHEN 2 THEN 'Projektowanie schematu bazy danych dla nowego modułu raportowania.'
        WHEN 3 THEN 'Pisanie testów jednostkowych dla modułu autoryzacji użytkowników.'
        WHEN 4 THEN 'Konfiguracja środowiska testowego na serwerze Ubuntu. Instalacja zależności.'
        WHEN 5 THEN 'Przygotowanie pipeline CI/CD w GitLab. Konfiguracja Docker Compose.'
        WHEN 6 THEN 'Aktualizacja dokumentacji technicznej API. Opis endpointów w Swagger.'
        WHEN 7 THEN 'Daily standup, planning sprintu, podział zadań w Jirze.'
        WHEN 8 THEN 'Szkolenie wewnętrzne z zakresu RODO i polityki bezpieczeństwa danych.'
        WHEN 9 THEN 'Diagnostyka problemów sieciowych, konfiguracja VLAN na przełączniku.'
        WHEN 10 THEN 'Obsługa zgłoszeń helpdesk. Rozwiązanie 8 ticketów pierwszej linii wsparcia.'
        WHEN 11 THEN 'Profilowanie zapytań SQL, optymalizacja indeksów w bazie danych.'
        ELSE 'Prezentacja postępów prac na spotkaniu projektowym. Demonstracja nowych funkcji.'
    END,
    CAST(
        MOD(
            CAST(
                ROW_NUMBER() OVER (
                    ORDER BY
                        d
                ) AS INTEGER
            ),
            13
        ) + 1 AS VARCHAR
    ),
    FALSE,
    TRUE,
    '2024-08-01 08:00:00'
FROM
    generate_series (
        CAST('2024-02-01' AS DATE),
        CAST('2024-08-31' AS DATE),
        INTERVAL '1 day'
    ) AS d
WHERE
    EXTRACT(
        DOW
        FROM
            d
    ) NOT IN (0, 6)
LIMIT
    120;

-- 5. LEARNING_OUTCOMES — Efekty uczenia się (Zał. 4)
INSERT INTO
    learning_outcomes_forms (
        internship_id,
        status,
        supervisor_comment_general,
        submitted_at
    )
VALUES
    (
        100,
        'approved',
        'Student zrealizował wszystkie zaplanowane efekty uczenia się. Wykazał się inicjatywą i samodzielnością w powierzonych zadaniach.',
        '2024-07-31 12:00:00'
    );

INSERT INTO
    learning_outcomes_items (form_id, outcome_number, achieved)
VALUES
    (
        (
            SELECT
                id
            FROM
                learning_outcomes_forms
            WHERE
                internship_id = 100
        ),
        1,
        TRUE
    ),
    (
        (
            SELECT
                id
            FROM
                learning_outcomes_forms
            WHERE
                internship_id = 100
        ),
        2,
        TRUE
    ),
    (
        (
            SELECT
                id
            FROM
                learning_outcomes_forms
            WHERE
                internship_id = 100
        ),
        3,
        TRUE
    ),
    (
        (
            SELECT
                id
            FROM
                learning_outcomes_forms
            WHERE
                internship_id = 100
        ),
        4,
        TRUE
    ),
    (
        (
            SELECT
                id
            FROM
                learning_outcomes_forms
            WHERE
                internship_id = 100
        ),
        5,
        TRUE
    ),
    (
        (
            SELECT
                id
            FROM
                learning_outcomes_forms
            WHERE
                internship_id = 100
        ),
        6,
        TRUE
    ),
    (
        (
            SELECT
                id
            FROM
                learning_outcomes_forms
            WHERE
                internship_id = 100
        ),
        7,
        TRUE
    ),
    (
        (
            SELECT
                id
            FROM
                learning_outcomes_forms
            WHERE
                internship_id = 100
        ),
        8,
        TRUE
    ),
    (
        (
            SELECT
                id
            FROM
                learning_outcomes_forms
            WHERE
                internship_id = 100
        ),
        9,
        FALSE
    ),
    (
        (
            SELECT
                id
            FROM
                learning_outcomes_forms
            WHERE
                internship_id = 100
        ),
        10,
        TRUE
    ),
    (
        (
            SELECT
                id
            FROM
                learning_outcomes_forms
            WHERE
                internship_id = 100
        ),
        11,
        TRUE
    ),
    (
        (
            SELECT
                id
            FROM
                learning_outcomes_forms
            WHERE
                internship_id = 100
        ),
        12,
        TRUE
    ),
    (
        (
            SELECT
                id
            FROM
                learning_outcomes_forms
            WHERE
                internship_id = 100
        ),
        13,
        TRUE
    );

-- 6. REPORT — Sprawozdanie z praktyki (Zał. 7)
INSERT INTO
    report (
        internship_id,
        company_description,
        work_description,
        self_assessment,
        status,
        submitted_at,
        approved_at
    )
VALUES
    (
        100,
        'Firma Testowa Sp. z o.o. jest średniej wielkości przedsiębiorstwem działającym w branży IT od 2010 roku. Zatrudnia około 80 pracowników i specjalizuje się w tworzeniu dedykowanych systemów ERP dla sektora produkcyjnego. Posiada certyfikaty ISO 9001 i ISO 27001. Firma prowadzi projekty zarówno dla klientów krajowych, jak i zagranicznych.',
        'W trakcie praktyki brałem udział w rozwoju modułu raportowania systemu ERP klasy SaaS. Moje główne zadania obejmowały: projektowanie i implementację endpointów REST API w Pythonie (Flask), pisanie testów jednostkowych i integracyjnych (pytest), projektowanie schematów baz danych w PostgreSQL oraz konfigurację środowisk deweloperskich z użyciem Docker i GitLab CI. Uczestniczyłem w codziennych spotkaniach Scrum i planowaniach sprintów.',
        'Praktyka zawodowa pozwoliła mi skonfrontować wiedzę zdobytą na studiach z rzeczywistymi wymaganiami rynku pracy. Szczególnie cenne okazały się umiejętności pracy zespołowej oraz stosowania metodyk zwinnych. Utrwaliłem znajomość Pythona i SQL, a także zdobyłem nowe kompetencje w zakresie DevOps. Praktyka utwierdziła mnie w przekonaniu, że chcę rozwijać się w kierunku backend developmentu.',
        'approved',
        '2024-07-31 14:00:00',
        '2024-08-07 09:00:00'
    );

-- 7. SURVEY — Kwestionariusz ankiety (Zał. 5)
INSERT INTO
    survey (
        internship_id,
        status,
        remarks,
        q1,
        q2,
        q3,
        q4,
        q5,
        q6,
        q7,
        q8,
        q9,
        q10,
        q11,
        q12,
        q13,
        q14,
        submitted_at
    )
VALUES
    (
        100,
        'submitted',
        'Praktyka spełniła moje oczekiwania. Polecam tę firmę innym studentom. Szczególnie cenne było środowisko pracy i otwartość zespołu na pytania stażystów.',
        5,
        5,
        4,
        5,
        4,
        5,
        5,
        4,
        5,
        4,
        5,
        4,
        5,
        5,
        '2024-07-31 15:00:00'
    );

-- 8. EXAM_PROTOCOL — Protokół egzaminu ustnego (Zał. 8)
INSERT INTO
    exam_protocol (internship_id, grade, commission_notes, exam_date)
VALUES
    (
        100,
        '5',
        'Student wykazał bardzo dobrą znajomość zagadnień omawianych podczas praktyki. Odpowiedzi były wyczerpujące i świadczyły o głębokim zrozumieniu tematu. Komisja jednogłośnie przyznała ocenę bardzo dobrą.',
        '2024-08-15'
    );

-- 9. DOCUMENT_COMMENT
INSERT INTO
    document_comment (author_id, document_type, document_id, content)
VALUES
    (
        5001,
        'program_schedule',
        100,
        'Program praktyki jest zgodny z wymaganiami. Harmonogram zatwierdzam.'
    ),
    (
        5001,
        'diary',
        100,
        'Dziennik prowadzony starannie. Wpisy szczegółowe i merytoryczne.'
    ),
    (
        5001,
        'report',
        100,
        'Sprawozdanie napisane poprawnie. Proszę o nieznaczne rozszerzenie sekcji samooceny.'
    ),
    (
        5002,
        'diary',
        100,
        'Potwierdzam obecność studenta i zgodność wpisów z wykonywanymi zadaniami.'
    ),
    (
        5002,
        'card',
        100,
        'Student wywiązał się ze wszystkich obowiązków. Ocena bardzo dobra.'
    );

-- Weryfikacja
SELECT
    'internship' AS tabela,
    COUNT(*) AS rekordy
FROM
    internship
WHERE
    id = 100
UNION ALL
SELECT
    'internship_card',
    COUNT(*)
FROM
    internship_card
WHERE
    internship_id = 100
UNION ALL
SELECT
    'program_schedule',
    COUNT(*)
FROM
    program_schedule
WHERE
    internship_id = 100
UNION ALL
SELECT
    'schedule_entry',
    COUNT(*)
FROM
    schedule_entry
WHERE
    program_id = (
        SELECT
            id
        FROM
            program_schedule
        WHERE
            internship_id = 100
    )
UNION ALL
SELECT
    'program_task',
    COUNT(*)
FROM
    program_task
WHERE
    program_id = (
        SELECT
            id
        FROM
            program_schedule
        WHERE
            internship_id = 100
    )
UNION ALL
SELECT
    'diary',
    COUNT(*)
FROM
    diary
WHERE
    internship_id = 100
UNION ALL
SELECT
    'diary_entry',
    COUNT(*)
FROM
    diary_entry
WHERE
    diary_id = (
        SELECT
            id
        FROM
            diary
        WHERE
            internship_id = 100
    )
UNION ALL
SELECT
    'learning_outcomes_forms',
    COUNT(*)
FROM
    learning_outcomes_forms
WHERE
    internship_id = 100
UNION ALL
SELECT
    'learning_outcomes_items',
    COUNT(*)
FROM
    learning_outcomes_items
WHERE
    form_id = (
        SELECT
            id
        FROM
            learning_outcomes_forms
        WHERE
            internship_id = 100
    )
UNION ALL
SELECT
    'report',
    COUNT(*)
FROM
    report
WHERE
    internship_id = 100
UNION ALL
SELECT
    'survey',
    COUNT(*)
FROM
    survey
WHERE
    internship_id = 100
UNION ALL
SELECT
    'exam_protocol',
    COUNT(*)
FROM
    exam_protocol
WHERE
    internship_id = 100
UNION ALL
SELECT
    'document_comment',
    COUNT(*)
FROM
    document_comment
WHERE
    document_id = 100;