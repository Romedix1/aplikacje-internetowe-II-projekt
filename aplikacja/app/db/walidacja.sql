-- ============================================================
-- CZĘŚĆ C. DANE TESTOWE — poprawne
-- ============================================================

-- Użytkownicy
INSERT INTO users (id, email, password_hash, first_name, last_name, role) VALUES
(1, 'jan.kowalski@ans-elblag.pl', 'hash', 'Jan',   'Kowalski', 'student'),
(2, 'anna.nowak@ans.edu.pl',           'hash', 'Anna',  'Nowak',    'uopz'),
(3, 'piotr.zielinski@abcsoftware.pl',  'hash', 'Piotr', 'Zielinski','zopz');

-- Praktyka
INSERT INTO internship (id, student_id, uopz_id, zopz_id, company_name, company_address, start_date, end_date, working_days) VALUES
(1, 1, 2, 3, 'ABC Software Sp. z o.o.', 'Elbląg', '2026-07-01', '2026-12-15', 120);

-- Program i harmonogram (Zał. 2a)
INSERT INTO program_schedule (id, internship_id, goals, tasks, status) VALUES
(1, 1, 'Nabycie umiejętności programowania webowego', 'Tworzenie aplikacji Flask', 'draft');

INSERT INTO schedule_entry (program_id, lp, department, planned_days) VALUES
(1,  1, 'Dział Backend',       10),
(1,  2, 'Dział Frontend',      10),
(1,  3, 'Dział Baz Danych',    10),
(1,  4, 'Dział DevOps',        10),
(1,  5, 'Dział QA',            10),
(1,  6, 'Dział Bezpieczeństwa', 8),
(1,  7, 'Dział Sieci',          8),
(1,  8, 'Dział Wsparcia IT',    8),
(1,  9, 'Dział Dokumentacji',   8),
(1, 10, 'Dział Zarządzania',    8),
(1, 11, 'Dział Analityki',      8),
(1, 12, 'Dział UX',             8),
(1, 13, 'Dział Projektowy',    14);
-- suma: 120 dni

-- Efekty uczenia się (Zał. 4) — 13 efektów
INSERT INTO learning_outcomes (internship_id, outcome_number, outcome_description, achieved) VALUES
(1,  1, 'Ma wiedzę na temat realizacji zadań inżynierskich z zachowaniem norm technicznych', TRUE),
(1,  2, 'Zna technologie, narzędzia i sprzęt stosowane w informatyce', TRUE),
(1,  3, 'Zna ekonomiczne i prawne skutki własnych działań', TRUE),
(1,  4, 'Zna zasady bezpieczeństwa pracy i ergonomii w zawodzie informatyka', TRUE),
(1,  5, 'Pozyskuje informacje z źródeł polsko- i anglojęzycznych', TRUE),
(1,  6, 'Podnosi kompetencje w zakresie sprzętu i oprogramowania', TRUE),
(1,  7, 'Opracowuje dokumentację i referuje zagadnienia ustnie', TRUE),
(1,  8, 'Identyfikuje i rozwiązuje problemy informatyczne', TRUE),
(1,  9, 'Stosuje normy i standardy informatyczne z uwzględnieniem aspektów etycznych', TRUE),
(1, 10, 'Pracuje w zespole IT', TRUE),
(1, 11, 'Przestrzega zasad etyki zawodowej', TRUE),
(1, 12, 'Komunikuje się ze środowiskiem pozabranżowym', TRUE),
(1, 13, 'Dostrzega tempo deaktualizacji wiedzy informatycznej', TRUE);

-- Dziennik (Zał. 6) — przykładowe wpisy
INSERT INTO diary (id, internship_id, status) VALUES (1, 1, 'draft');

INSERT INTO diary_entry (diary_id, day_number, work_date, description, outcome_numbers, confirmed_by_zopz) VALUES
(1,  1, '2026-07-01', 'Zapoznanie z infrastrukturą firmy i szkolenie BHP', '04', TRUE),
(1,  2, '2026-07-02', 'Konfiguracja środowiska deweloperskiego', '02', TRUE),
(1,  3, '2026-07-03', 'Przegląd dokumentacji projektu backendowego', '01,07', TRUE);

-- Karta praktyki (Zał. 3)
INSERT INTO internship_card (internship_id, zopz_opinion, zopz_grade, status) VALUES
(1, 'Student wykonywał zadania rzetelnie i terminowo.', '5', 'draft');

-- Sprawozdanie (Zał. 7)
INSERT INTO report (internship_id, company_description, work_description, self_assessment, status) VALUES
(1,
 'ABC Software Sp. z o.o. to firma tworząca aplikacje webowe.',
 'Uczestniczyłem w tworzeniu backendu aplikacji w technologii Flask.',
 'Osiągnąłem wszystkie zakładane efekty uczenia się.',
 'draft');

-- Ankieta (Zał. 5)
INSERT INTO survey (internship_id, overall_rating, company_feedback, tasks_feedback) VALUES
(1, 5, 'Bardzo dobra organizacja praktyki.', 'Zadania były zgodne z programem studiów.');


-- ============================================================
-- CZĘŚĆ D. ZAPYTANIA KONTROLNE — walidacja pojedynczych formularzy
-- ============================================================

-- ------------------------------------------------------------
-- 1. Program i harmonogram (Zał. 2a)
-- ------------------------------------------------------------

-- D1. Kompletność danych podstawowych praktyki
SELECT i.id, i.student_id, i.company_name, i.start_date, i.end_date
FROM internship i
WHERE i.student_id IS NULL
   OR i.company_name IS NULL
   OR i.start_date IS NULL
   OR i.end_date IS NULL
   OR i.working_days IS NULL;
-- Brak wyników = dane kompletne

-- D2. Wymagana liczba dni roboczych = 120
SELECT id, working_days
FROM internship
WHERE working_days <> 120;

-- D3. Poprawność zakresu dat
SELECT id, start_date, end_date
FROM internship
WHERE end_date <= start_date;

-- D4. Suma dni w harmonogramie = 120
SELECT se.program_id, SUM(se.planned_days) AS suma_dni
FROM schedule_entry se
GROUP BY se.program_id
HAVING SUM(se.planned_days) <> 120;

-- D5. Liczba pozycji harmonogramu = 13
SELECT program_id, COUNT(*) AS liczba_pozycji
FROM schedule_entry
GROUP BY program_id
HAVING COUNT(*) <> 13;

-- D6. Pusta nazwa działu w harmonogramie
SELECT program_id, lp
FROM schedule_entry
WHERE TRIM(department) = '' OR department IS NULL;

-- D7. Brak obu opiekunów przypisanych do praktyki
SELECT i.id AS internship_id
FROM internship i
WHERE i.uopz_id IS NULL OR i.zopz_id IS NULL;

-- ------------------------------------------------------------
-- 2. Potwierdzenie efektów uczenia się (Zał. 4)
-- ------------------------------------------------------------

-- D8. Liczba efektów różna od 13
SELECT internship_id, COUNT(*) AS liczba_efektow
FROM learning_outcomes
GROUP BY internship_id
HAVING COUNT(*) <> 13;

-- D9. Efekty bez przypisanej decyzji (achieved = NULL)
SELECT internship_id, outcome_number
FROM learning_outcomes
WHERE achieved IS NULL;

-- D10. Brakujące numery efektów (powinny być 1–13)
SELECT i.id AS internship_id, gs.n AS brakujacy_efekt
FROM internship i
CROSS JOIN generate_series(1, 13) AS gs(n)
LEFT JOIN learning_outcomes lo
    ON lo.internship_id = i.id AND lo.outcome_number = gs.n
WHERE lo.id IS NULL;

-- ------------------------------------------------------------
-- 3. Dziennik praktyki zawodowej (Zał. 6)
-- ------------------------------------------------------------

-- D11. Wpisy bez opisu
SELECT diary_id, day_number
FROM diary_entry
WHERE TRIM(description) = '' OR description IS NULL;

-- D12. Wpisy niepotwierdzone przez ZOPZ
SELECT diary_id, day_number, work_date
FROM diary_entry
WHERE confirmed_by_zopz = FALSE;

-- D13. Liczba wpisów w dzienniku
SELECT d.id AS diary_id, COUNT(de.id) AS liczba_wpisow
FROM diary d
LEFT JOIN diary_entry de ON de.diary_id = d.id
GROUP BY d.id;

-- D14. Wpisy bez przypisanych efektów uczenia się
SELECT diary_id, day_number
FROM diary_entry
WHERE outcome_numbers IS NULL OR TRIM(outcome_numbers) = '';

-- ------------------------------------------------------------
-- 4. Karta praktyki zawodowej (Zał. 3)
-- ------------------------------------------------------------

-- D15. Karta bez oceny ZOPZ
SELECT internship_id
FROM internship_card
WHERE zopz_grade IS NULL;

-- D16. Karta bez opinii ZOPZ
SELECT internship_id
FROM internship_card
WHERE zopz_opinion IS NULL OR TRIM(zopz_opinion) = '';

-- ------------------------------------------------------------
-- 5. Sprawozdanie (Zał. 7)
-- ------------------------------------------------------------

-- D17. Sprawozdanie z brakującymi sekcjami
SELECT internship_id,
    CASE WHEN company_description IS NULL OR TRIM(company_description) = '' THEN 'brak charakterystyki' END AS blad_1,
    CASE WHEN work_description    IS NULL OR TRIM(work_description)    = '' THEN 'brak opisu prac'      END AS blad_2,
    CASE WHEN self_assessment     IS NULL OR TRIM(self_assessment)     = '' THEN 'brak samooceny'       END AS blad_3
FROM report
WHERE company_description IS NULL OR TRIM(company_description) = ''
   OR work_description    IS NULL OR TRIM(work_description)    = ''
   OR self_assessment     IS NULL OR TRIM(self_assessment)     = '';


-- ============================================================
-- CZĘŚĆ C (WALIDACJA MIĘDZY FORMULARZAMI)
-- ============================================================

-- D18. Spójność: student ma wszystkie wymagane dokumenty
SELECT
    i.id AS internship_id,
    u.email AS student,
    CASE WHEN ps.id IS NULL THEN 'BRAK programu'    END AS program,
    CASE WHEN d.id  IS NULL THEN 'BRAK dziennika'   END AS dziennik,
    CASE WHEN ic.id IS NULL THEN 'BRAK karty'        END AS karta,
    CASE WHEN r.id  IS NULL THEN 'BRAK sprawozdania' END AS sprawozdanie,
    CASE WHEN sv.id IS NULL THEN 'BRAK ankiety'      END AS ankieta
FROM internship i
JOIN users u ON u.id = i.student_id
LEFT JOIN program_schedule ps ON ps.internship_id = i.id
LEFT JOIN diary            d  ON d.internship_id  = i.id
LEFT JOIN internship_card  ic ON ic.internship_id = i.id
LEFT JOIN report           r  ON r.internship_id  = i.id
LEFT JOIN survey           sv ON sv.internship_id = i.id
WHERE ps.id IS NULL OR d.id IS NULL OR ic.id IS NULL OR r.id IS NULL OR sv.id IS NULL;

-- D19. Zgodność liczby dni harmonogramu z wymaganiem praktyki
SELECT i.id AS internship_id, i.working_days, SUM(se.planned_days) AS suma_harmonogramu
FROM internship i
JOIN program_schedule ps ON ps.internship_id = i.id
JOIN schedule_entry   se ON se.program_id    = ps.id
GROUP BY i.id, i.working_days
HAVING SUM(se.planned_days) <> i.working_days;

-- D20. Efekty w Zał. 4 vs efekty w dzienniku — niespójność
SELECT lo.internship_id, lo.outcome_number
FROM learning_outcomes lo
WHERE lo.achieved = TRUE
  AND NOT EXISTS (
    SELECT 1
    FROM diary d
    JOIN diary_entry de ON de.diary_id = d.id
    WHERE d.internship_id = lo.internship_id
      AND de.outcome_numbers LIKE '%' || LPAD(lo.outcome_number::TEXT, 2, '0') || '%'
);

-- D21. Ocena pozytywna w protokole egzaminu, ale nie wszystkie efekty osiągnięte
SELECT ep.internship_id, ep.grade
FROM exam_protocol ep
WHERE ep.grade NOT IN ('2')
  AND EXISTS (
    SELECT 1
    FROM learning_outcomes lo
    WHERE lo.internship_id = ep.internship_id
      AND lo.achieved = FALSE
);


-- ============================================================
-- CZĘŚĆ E. DANE TESTOWE — błędne (przypadki brzegowe)
-- ============================================================

-- E1. Duplikat email użytkownika (naruszenie UNIQUE)
-- INSERT INTO users (id, email, password_hash, first_name, last_name, role)
-- VALUES (99, 'jan.kowalski@student.ans.edu.pl', 'hash', 'Jan', 'Duplikat', 'student');
-- Oczekiwany wynik: ERROR: duplicate key value violates unique constraint "users_email_key"

-- E2. Niepoprawna liczba dni roboczych (naruszenie CHECK working_days = 120)
-- INSERT INTO internship (student_id, uopz_id, zopz_id, company_name, start_date, end_date, working_days)
-- VALUES (1, 2, 3, 'Firma testowa', '2026-07-01', '2026-12-15', 80);
-- Oczekiwany wynik: ERROR: new row for relation "internship" violates check constraint

-- E3. Data zakończenia wcześniejsza niż data rozpoczęcia (naruszenie CHECK)
-- INSERT INTO internship (student_id, uopz_id, zopz_id, company_name, start_date, end_date, working_days)
-- VALUES (1, 2, 3, 'Firma testowa', '2026-10-01', '2026-07-01', 120);
-- Oczekiwany wynik: ERROR: new row for relation "internship" violates check constraint

-- E4. Duplikat pozycji harmonogramu (naruszenie UNIQUE program_id, lp)
-- INSERT INTO schedule_entry (program_id, lp, department, planned_days)
-- VALUES (1, 1, 'Dział Duplikat', 5);
-- Oczekiwany wynik: ERROR: duplicate key value violates unique constraint "schedule_entry_program_id_lp_key"

-- E5. Numer efektu poza zakresem 1–13 (naruszenie CHECK)
-- INSERT INTO learning_outcomes (internship_id, outcome_number, outcome_description, achieved)
-- VALUES (1, 14, 'Efekt poza zakresem', TRUE);
-- Oczekiwany wynik: ERROR: new row for relation "learning_outcomes" violates check constraint

-- E6. Duplikat dnia w dzienniku (naruszenie UNIQUE diary_id, day_number)
-- INSERT INTO diary_entry (diary_id, day_number, work_date, description, confirmed_by_zopz)
-- VALUES (1, 1, '2026-07-05', 'Próba duplikatu dnia', FALSE);
-- Oczekiwany wynik: ERROR: duplicate key value violates unique constraint "diary_entry_diary_id_day_number_key"

-- E7. Ocena spoza dozwolonego zakresu (naruszenie CHECK)
-- INSERT INTO internship_card (internship_id, zopz_grade, status)
-- VALUES (1, '6', 'draft');
-- Oczekiwany wynik: ERROR: new row for relation "internship_card" violates check constraint

-- E8. Praktyka zakończona, ale brak protokołu egzaminu
SELECT i.id AS internship_id
FROM internship i
WHERE i.status = 'completed'
  AND NOT EXISTS (
    SELECT 1 FROM exam_protocol ep WHERE ep.internship_id = i.id
);


-- ============================================================
-- PODSUMOWANIE WALIDACJI
-- ============================================================
-- Uruchomienie wszystkich zapytań D1–D21 i E8 pozwala wykryć:
--
-- Formularz                    | Reguły walidacji
-- -----------------------------|------------------------------------------
-- Program i harmonogram        | D1, D2, D3, D4, D5, D6, D7
-- Efekty uczenia się (Zał. 4)  | D8, D9, D10
-- Dziennik (Zał. 6)            | D11, D12, D13, D14
-- Karta praktyki (Zał. 3)      | D15, D16
-- Sprawozdanie (Zał. 7)        | D17
-- Między formularzami          | D18, D19, D20, D21
-- Przypadki brzegowe (struktura)| E1–E8
