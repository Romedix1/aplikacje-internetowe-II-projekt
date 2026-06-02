# Lab 07 — Weryfikacja formularzy praktyk zawodowych za pomocą SQL

> **Projekt:** System Obsługi Praktyk Zawodowych — Instytut Informatyki Stosowanej, ANS Elbląg  
> **Baza danych:** PostgreSQL  
> **Plik schematu:** `schema.sql`

---

## Zadanie 1 — Weryfikacja formularza Programu i harmonogramu praktyki

### Część A. Model ERD (opis encji i relacji)

Encje obsługujące formularz **Zał. 2a** to:

| Encja                 | Tabela w schemacie | Opis                                   |
| --------------------- | ------------------ | -------------------------------------- |
| Użytkownicy/Studenci  | `users`            | Dane studenta, UOPZ, ZOPZ              |
| Praktyka              | `internship`       | Jeden rekord = jedna praktyka studenta |
| Program i harmonogram | `program_schedule` | Nagłówek formularza Zał. 2a            |
| Pozycje harmonogramu  | `schedule_entry`   | Działy / komórki z liczbą dni          |
| Zadania dla efektów   | `program_task`     | 13 efektów kształcenia z opisem prac   |

**Relacje:**

- `users` 1→N `internship` (jeden student, wiele praktyk)
- `internship` 1→1 `program_schedule` (jedna praktyka = jeden formularz programu)
- `program_schedule` 1→N `schedule_entry` (wiele pozycji harmonogramu)
- `program_schedule` 1→13 `program_task` (dokładnie 13 efektów kształcenia)

**Klucze główne:** `id` (SERIAL) w każdej tabeli  
**Klucze obce:** `program_schedule.internship_id → internship.id`, `schedule_entry.program_id → program_schedule.id`, `program_task.program_id → program_schedule.id`

---

### Część B. Normalizacja danych

Schemat jest zgodny z zasadami normalizacji (co najmniej 3NF):

- **1NF** — każda kolumna przechowuje jedną atomową wartość (brak list w jednym polu)
- **2NF** — wszystkie atrybuty zależą od całego klucza głównego
- **3NF** — brak tranzytywnych zależności; dane studenta są w tabeli `users`, dane firmy w tabeli `internship`, harmonogram w osobnej tabeli `schedule_entry`

---

### Część C. Dane testowe

```sql
-- 1. Użytkownicy
INSERT INTO users (id, email, first_name, last_name, role, index_number, auth_provider)
VALUES
  (1, 'jan.kowalski@student.ans.edu.pl', 'Jan',  'Kowalski', 'student',    '123456', 'microsoft'),
  (2, 'anna.nowak@ans.edu.pl',           'Anna', 'Nowak',    'uopz',       NULL,     'microsoft'),
  (3, 'piotr.zielinski@abc.pl',          'Piotr','Zieliński','zopz',       NULL,     'microsoft');

-- 2. Praktyka
INSERT INTO internship
  (id, student_id, uopz_id, zopz_id, company_name, company_address,
   start_date, end_date, working_days, status)
VALUES
  (1, 1, 2, 3, 'ABC Software Sp. z o.o.', 'Elbląg, ul. Informatyczna 1',
   '2026-07-01', '2026-12-15', 120, 'active');

-- 3. Program i harmonogram
INSERT INTO program_schedule (id, internship_id, agreed_date, status)
VALUES (1, 1, '2026-06-15', 'draft');

-- 4. Harmonogram (pozycje) - suma musi = 120 dni
INSERT INTO schedule_entry (program_id, lp, department, planned_days)
VALUES
  (1, 1, 'Dział IT – development',           30),
  (1, 2, 'Dział IT – testowanie',             20),
  (1, 3, 'Dział sieciowy',                    20),
  (1, 4, 'Dział wsparcia technicznego',        15),
  (1, 5, 'Dział projektowy',                  15),
  (1, 6, 'Dokumentacja i wdrożenia',           20);
-- Suma: 30+20+20+15+15+20 = 120

-- 5. Zadania dla 13 efektów kształcenia
INSERT INTO program_task (program_id, outcome_number, description)
VALUES
  (1,  1, 'Tworzenie aplikacji webowych w technologii Flask i React'),
  (1,  2, 'Projektowanie i normalizacja relacyjnych baz danych'),
  (1,  3, 'Konfiguracja serwerów Linux i usług sieciowych'),
  (1,  4, 'Stosowanie metodyk zwinnych (Scrum, Kanban)'),
  (1,  5, 'Testowanie oprogramowania – testy jednostkowe i integracyjne'),
  (1,  6, 'Dokumentowanie kodu i tworzenie specyfikacji technicznej'),
  (1,  7, 'Administrowanie systemami baz danych PostgreSQL'),
  (1,  8, 'Wdrażanie aplikacji w środowisku chmurowym (Docker, CI/CD)'),
  (1,  9, 'Analiza wymagań i komunikacja z klientem'),
  (1, 10, 'Zarządzanie kodem źródłowym z użyciem Git'),
  (1, 11, 'Bezpieczeństwo aplikacji – OWASP, szyfrowanie danych'),
  (1, 12, 'Optymalizacja zapytań SQL i wydajności bazy danych'),
  (1, 13, 'Prezentacja wyników pracy i raportowanie postępów');
```

---

### Część D. Testy poprawności formularza

#### 1. Sprawdzenie kompletności danych podstawowych praktyki

```sql
-- Wynik: 0 wierszy = formularz kompletny
SELECT i.id AS internship_id, ps.id AS program_schedule_id
FROM internship i
JOIN program_schedule ps ON ps.internship_id = i.id
WHERE i.student_id IS NULL
   OR i.company_name IS NULL
   OR i.start_date IS NULL
   OR i.end_date IS NULL
   OR ps.id IS NULL;
```

#### 2. Sprawdzenie wymaganej liczby dni praktyki (musi być 120)

```sql
-- Wynik: 0 wierszy = poprawna liczba dni
SELECT id, working_days
FROM internship
WHERE working_days <> 120;
```

#### 3. Sprawdzenie poprawności zakresu dat

```sql
-- Wynik: 0 wierszy = daty poprawne
SELECT id, start_date, end_date
FROM internship
WHERE end_date <= start_date;
```

#### 4. Sprawdzenie liczby efektów kształcenia (musi być 13 dla każdego formularza)

```sql
-- Wynik: 0 wierszy = każdy formularz ma dokładnie 13 efektów
SELECT ps.id AS program_id, COUNT(pt.id) AS liczba_efektow
FROM program_schedule ps
LEFT JOIN program_task pt ON pt.program_id = ps.id
GROUP BY ps.id
HAVING COUNT(pt.id) <> 13;
```

#### 5. Sprawdzenie pustych opisów efektów

```sql
-- Wynik: 0 wierszy = brak pustych opisów
SELECT pt.program_id, pt.outcome_number
FROM program_task pt
WHERE pt.description IS NULL
   OR TRIM(pt.description) = '';
```

#### 6. Sprawdzenie sumy dni w harmonogramie (musi = 120)

```sql
-- Wynik: 0 wierszy = suma dni poprawna
SELECT se.program_id, SUM(se.planned_days) AS suma_dni
FROM schedule_entry se
GROUP BY se.program_id
HAVING SUM(se.planned_days) <> 120;
```

#### 7. Sprawdzenie duplikatów numerów lp w harmonogramie

```sql
-- Wynik: 0 wierszy = brak duplikatów
SELECT program_id, lp, COUNT(*) AS wystapienia
FROM schedule_entry
GROUP BY program_id, lp
HAVING COUNT(*) > 1;
```

#### 8. Sprawdzenie przypisania opiekunów (UOPZ i ZOPZ) do praktyki

```sql
-- Wynik: 0 wierszy = każda praktyka ma obydwu opiekunów
SELECT id, student_id
FROM internship
WHERE uopz_id IS NULL
   OR zopz_id IS NULL;
```

---

### Część E. Przypadki brzegowe

#### Przypadek 1. Duplikat numeru indeksu studenta

```sql
-- Próba wstawienia dwóch studentów z tym samym nr albumu
INSERT INTO users (email, first_name, last_name, role, index_number, auth_provider)
VALUES ('adam.nowicki@student.ans.edu.pl', 'Adam', 'Nowicki', 'student', '123456', 'microsoft');

-- Oczekiwany rezultat:
-- ERROR: duplicate key value violates unique constraint "users_index_number_key"
-- DETAIL: Key (index_number)=(123456) already exists.
```

#### Przypadek 2. Niepoprawna liczba dni praktyki

```sql
INSERT INTO internship
  (student_id, uopz_id, zopz_id, company_name, start_date, end_date, working_days, status)
VALUES (1, 2, 3, 'Test Sp. z o.o.', '2026-07-01', '2026-09-30', 80, 'pending');

-- Oczekiwany rezultat:
-- ERROR: new row for relation "internship" violates check constraint "internship_working_days_check"
-- DETAIL: Failing row contains (..., 80, ...).
```

#### Przypadek 3. Data zakończenia wcześniejsza niż rozpoczęcia

```sql
INSERT INTO internship
  (student_id, uopz_id, zopz_id, company_name, start_date, end_date, working_days, status)
VALUES (1, 2, 3, 'Test Sp. z o.o.', '2026-10-01', '2026-07-01', 120, 'pending');

-- Oczekiwany rezultat:
-- ERROR: new row for relation "internship" violates check constraint "internship_check"
-- DETAIL: Failing row contains (..., 2026-10-01, 2026-07-01, ...).
```

#### Przypadek 4. Duplikat pozycji harmonogramu (ten sam lp w tym samym programie)

```sql
INSERT INTO schedule_entry (program_id, lp, department, planned_days)
VALUES (1, 1, 'Dział serwisowy', 15);

-- Oczekiwany rezultat:
-- ERROR: duplicate key value violates unique constraint "schedule_entry_program_id_lp_key"
-- DETAIL: Key (program_id, lp)=(1, 1) already exists.
```

#### Przypadek 5. Pusta nazwa działu w harmonogramie

```sql
-- Sprawdzenie wykrywające puste nazwy działów
SELECT program_id, lp
FROM schedule_entry
WHERE department IS NULL
   OR TRIM(department) = '';

-- Oczekiwany rezultat: 0 wierszy (constraint NOT NULL na kolumnie department)
```

#### Przypadek 6. Efekt kształcenia spoza zakresu 1–13

```sql
INSERT INTO program_task (program_id, outcome_number, description)
VALUES (1, 14, 'Dodatkowy efekt');

-- Oczekiwany rezultat:
-- ERROR: new row for relation "program_task" violates check constraint
-- "program_task_outcome_number_check"
```

---

## Zadanie 2 — Walidacja wszystkich formularzy praktyk zawodowych

### Część A. Spójność modelu danych

**Kluczowe zależności spójności:**

- Ten sam `student_id` musi pojawić się we wszystkich dokumentach powiązanych przez `internship.id`
- Daty `start_date` / `end_date` z `internship` obowiązują we wszystkich formularzach
- 13 efektów kształcenia musi być spójne między `program_task`, `diary_entry.outcome_numbers` i `learning_outcomes_items`
- `working_days = 120` musi odpowiadać sumie `schedule_entry.planned_days` i liczbie wpisów w `diary_entry`

---

### Część B. Reguły walidacji dla poszczególnych formularzy

---

#### 1. Karta praktyki zawodowej (Zał. 3) — tabela `internship_card`

**Pola obowiązkowe:** `internship_id`, `status`  
**Możliwe błędy:** brak karty, pusta ocena przy statusie `approved`, brak opiekuna zakładowego

```sql
-- B1.1 Praktyki bez karty praktyki
SELECT i.id AS internship_id, i.student_id
FROM internship i
LEFT JOIN internship_card ic ON ic.internship_id = i.id
WHERE ic.id IS NULL;

-- B1.2 Karta z oceną ZOPZ spoza zakresu 2–5
SELECT ic.id, ic.zopz_grade
FROM internship_card ic
WHERE ic.zopz_grade IS NOT NULL
  AND ic.zopz_grade NOT IN ('2', '3', '3.5', '4', '4.5', '5');

-- B1.3 Karta zatwierdzona bez oceny ZOPZ
SELECT ic.id, ic.status
FROM internship_card ic
WHERE ic.status = 'approved'
  AND (ic.zopz_grade IS NULL OR TRIM(ic.zopz_grade) = '');

-- B1.4 Praktyka bez przypisanego opiekuna zakładowego (ZOPZ)
SELECT id, student_id
FROM internship
WHERE zopz_id IS NULL;
```

---

#### 2. Potwierdzenie efektów uczenia się (Zał. 4) — tabele `learning_outcomes_forms` + `learning_outcomes_items`

**Pola obowiązkowe:** powiązanie z `internship_id`, 13 wierszy w `learning_outcomes_items`  
**Możliwe błędy:** brakujące efekty, efekty bez decyzji (`achieved IS NULL`)

```sql
-- B2.1 Praktyki bez formularza efektów uczenia się
SELECT i.id AS internship_id
FROM internship i
LEFT JOIN learning_outcomes_forms lof ON lof.internship_id = i.id
WHERE lof.id IS NULL;

-- B2.2 Formularze z inną liczbą niż 13 efektów
SELECT lof.id AS form_id, COUNT(loi.id) AS liczba_efektow
FROM learning_outcomes_forms lof
LEFT JOIN learning_outcomes_items loi ON loi.form_id = lof.id
GROUP BY lof.id
HAVING COUNT(loi.id) <> 13;

-- B2.3 Efekty bez przypisanej decyzji (achieved IS NULL)
SELECT loi.form_id, loi.outcome_number
FROM learning_outcomes_items loi
WHERE loi.achieved IS NULL;

-- B2.4 Formularz zatwierdzony, ale nie wszystkie efekty osiągnięte (opcjonalne ostrzeżenie)
SELECT lof.id AS form_id, COUNT(*) FILTER (WHERE loi.achieved = TRUE) AS osiagniete
FROM learning_outcomes_forms lof
JOIN learning_outcomes_items loi ON loi.form_id = lof.id
WHERE lof.status = 'approved'
GROUP BY lof.id
HAVING COUNT(*) FILTER (WHERE loi.achieved = TRUE) < 13;
```

---

#### 3. Dziennik praktyki zawodowej (Zał. 6) — tabele `diary` + `diary_entry`

**Pola obowiązkowe:** `diary_id`, `day_number`, `work_date`, `description`  
**Możliwe błędy:** brak dziennika, liczba wpisów ≠ 120, puste opisy, wpisy niepotwierdzone przez ZOPZ

```sql
-- B3.1 Praktyki bez dziennika
SELECT i.id AS internship_id
FROM internship i
LEFT JOIN diary d ON d.internship_id = i.id
WHERE d.id IS NULL;

-- B3.2 Dzienniki z liczbą wpisów różną od 120
SELECT d.id AS diary_id, COUNT(de.id) AS liczba_wpisow
FROM diary d
LEFT JOIN diary_entry de ON de.diary_id = d.id
GROUP BY d.id
HAVING COUNT(de.id) <> 120;

-- B3.3 Wpisy z pustym opisem
SELECT de.diary_id, de.day_number, de.work_date
FROM diary_entry de
WHERE de.description IS NULL
   OR TRIM(de.description) = '';

-- B3.4 Wpisy niepotwierdzone przez ZOPZ
SELECT de.diary_id, de.day_number, de.work_date
FROM diary_entry de
WHERE de.confirmed_by_zopz = FALSE;

-- B3.5 Wpisy bez przypisanych efektów kształcenia
SELECT de.diary_id, de.day_number
FROM diary_entry de
WHERE de.outcome_numbers IS NULL
   OR TRIM(de.outcome_numbers) = '';

-- B3.6 Duplikaty dat w dzienniku (ta sama data dla dwóch wpisów)
SELECT diary_id, work_date, COUNT(*) AS duplikaty
FROM diary_entry
GROUP BY diary_id, work_date
HAVING COUNT(*) > 1;
```

---

#### 4. Sprawozdanie z praktyki (Zał. 7) — tabela `report`

**Pola obowiązkowe:** `company_description`, `work_description`, `self_assessment`  
**Możliwe błędy:** brak sprawozdania, puste sekcje, zatwierdzone bez treści

```sql
-- B4.1 Praktyki bez sprawozdania
SELECT i.id AS internship_id
FROM internship i
LEFT JOIN report r ON r.internship_id = i.id
WHERE r.id IS NULL;

-- B4.2 Sprawozdanie z pustymi sekcjami (company_description, work_description, self_assessment)
SELECT id, internship_id,
  CASE WHEN company_description IS NULL OR TRIM(company_description) = '' THEN 'brak: charakterystyka firmy' END AS blad_1,
  CASE WHEN work_description    IS NULL OR TRIM(work_description)    = '' THEN 'brak: opis prac'            END AS blad_2,
  CASE WHEN self_assessment     IS NULL OR TRIM(self_assessment)     = '' THEN 'brak: samoocena'            END AS blad_3
FROM report
WHERE company_description IS NULL OR TRIM(company_description) = ''
   OR work_description    IS NULL OR TRIM(work_description)    = ''
   OR self_assessment     IS NULL OR TRIM(self_assessment)     = '';

-- B4.3 Sprawozdanie zatwierdzone, ale brak daty zatwierdzenia
SELECT id, internship_id, status, approved_at
FROM report
WHERE status = 'approved'
  AND approved_at IS NULL;
```

---

### Część C. Walidacja między formularzami (spójność krzyżowa)

#### C1. Ten sam student we wszystkich dokumentach danej praktyki

```sql
-- Sprawdzenie: czy student_id z internship zgadza się z właścicielem dokumentów
-- (tutaj weryfikujemy, czy dokumenty są przypisane do istniejącej praktyki tego studenta)
SELECT
  i.id AS internship_id,
  i.student_id,
  u.first_name || ' ' || u.last_name AS student,
  ps.id  IS NOT NULL AS ma_program,
  ic.id  IS NOT NULL AS ma_karte,
  lof.id IS NOT NULL AS ma_efekty,
  d.id   IS NOT NULL AS ma_dziennik,
  r.id   IS NOT NULL AS ma_sprawozdanie
FROM internship i
JOIN users u ON u.id = i.student_id
LEFT JOIN program_schedule       ps  ON ps.internship_id  = i.id
LEFT JOIN internship_card        ic  ON ic.internship_id  = i.id
LEFT JOIN learning_outcomes_forms lof ON lof.internship_id = i.id
LEFT JOIN diary                  d   ON d.internship_id   = i.id
LEFT JOIN report                 r   ON r.internship_id   = i.id;
```

#### C2. Zgodność sumy dni harmonogramu z working_days (120)

```sql
SELECT i.id AS internship_id, i.working_days,
       SUM(se.planned_days) AS suma_harmonogramu
FROM internship i
JOIN program_schedule ps ON ps.internship_id = i.id
JOIN schedule_entry se   ON se.program_id    = ps.id
GROUP BY i.id, i.working_days
HAVING SUM(se.planned_days) <> i.working_days;
-- Wynik: 0 wierszy = suma harmonogramu zgodna z liczbą dni praktyki
```

#### C3. Zgodność liczby wpisów dziennika z working_days (120)

```sql
SELECT i.id AS internship_id, i.working_days,
       COUNT(de.id) AS wpisy_w_dzienniku
FROM internship i
JOIN diary d         ON d.internship_id = i.id
LEFT JOIN diary_entry de ON de.diary_id = d.id
GROUP BY i.id, i.working_days
HAVING COUNT(de.id) <> i.working_days;
-- Wynik: 0 wierszy = liczba wpisów zgodna z liczbą dni
```

#### C4. Spójność efektów kształcenia między programem a dziennikiem

```sql
-- Efekty zdefiniowane w programie, ale nie wymienione w żadnym wpisie dziennika
SELECT pt.outcome_number
FROM program_task pt
JOIN program_schedule ps ON ps.id = pt.program_id
JOIN internship i         ON i.id  = ps.internship_id
JOIN diary d              ON d.internship_id = i.id
WHERE NOT EXISTS (
    SELECT 1 FROM diary_entry de
    WHERE de.diary_id = d.id
      AND de.outcome_numbers LIKE '%' || pt.outcome_number::TEXT || '%'
);
```

#### C5. Daty wpisów dziennika mieszczą się w okresie praktyki

```sql
SELECT de.diary_id, de.work_date, i.start_date, i.end_date
FROM diary_entry de
JOIN diary d      ON d.id              = de.diary_id
JOIN internship i ON i.id              = d.internship_id
WHERE de.work_date < i.start_date
   OR de.work_date > i.end_date;
-- Wynik: 0 wierszy = wszystkie daty w zakresie praktyki
```

#### C6. Ocena egzaminu istnieje tylko gdy dziennik i sprawozdanie są zatwierdzone

```sql
SELECT ep.internship_id, ep.grade, d.status AS status_dziennika, r.status AS status_sprawozdania
FROM exam_protocol ep
JOIN diary    d ON d.internship_id = ep.internship_id
JOIN report   r ON r.internship_id = ep.internship_id
WHERE d.status <> 'approved'
   OR r.status <> 'approved';
-- Wynik: 0 wierszy = ocena wystawiona tylko po zatwierdzeniu dokumentów
```

---

### Część D. Przypadki brzegowe dla całego systemu

| #   | Przypadek błędny                                  | Zapytanie wykrywające |
| --- | ------------------------------------------------- | --------------------- |
| D1  | Różne daty praktyki w różnych formularzach        | Zapytanie C5 powyżej  |
| D2  | Brak wpisów w dzienniku                           | Zapytanie B3.1 + B3.2 |
| D3  | Brak efektów w formularzu Zał. 4                  | Zapytanie B2.2        |
| D4  | Ocena pozytywna przy braku zatwierdzonych efektów | Zapytanie C6          |
| D5  | Wpisy dziennika niepotwierdzone przez ZOPZ        | Zapytanie B3.4        |
| D6  | Sprawozdanie bez wszystkich sekcji                | Zapytanie B4.2        |
| D7  | Praktyka zakończona, ale brak protokołu egzaminu  | Poniżej               |

```sql
-- D7. Praktyka ze statusem 'completed', ale bez protokołu egzaminu
SELECT i.id AS internship_id, i.student_id, i.status
FROM internship i
LEFT JOIN exam_protocol ep ON ep.internship_id = i.id
WHERE i.status = 'completed'
  AND ep.id IS NULL;
```

```sql
-- D8. Zbiorczy raport kompletności wszystkich dokumentów dla każdej praktyki
SELECT
  i.id                                              AS internship_id,
  u.first_name || ' ' || u.last_name               AS student,
  i.status                                          AS status_praktyki,
  CASE WHEN ps.id  IS NOT NULL THEN '✓' ELSE '✗' END AS program_harmonogram,
  CASE WHEN ic.id  IS NOT NULL THEN '✓' ELSE '✗' END AS karta_praktyki,
  CASE WHEN lof.id IS NOT NULL THEN '✓' ELSE '✗' END AS efekty_uczenia,
  CASE WHEN d.id   IS NOT NULL THEN '✓' ELSE '✗' END AS dziennik,
  CASE WHEN r.id   IS NOT NULL THEN '✓' ELSE '✗' END AS sprawozdanie,
  CASE WHEN s.id   IS NOT NULL THEN '✓' ELSE '✗' END AS ankieta,
  CASE WHEN ep.id  IS NOT NULL THEN '✓' ELSE '✗' END AS protokol_egzaminu
FROM internship i
JOIN users u                    ON u.id               = i.student_id
LEFT JOIN program_schedule       ps  ON ps.internship_id  = i.id
LEFT JOIN internship_card        ic  ON ic.internship_id  = i.id
LEFT JOIN learning_outcomes_forms lof ON lof.internship_id = i.id
LEFT JOIN diary                  d   ON d.internship_id   = i.id
LEFT JOIN report                 r   ON r.internship_id   = i.id
LEFT JOIN survey                 s   ON s.internship_id   = i.id
LEFT JOIN exam_protocol          ep  ON ep.internship_id  = i.id
ORDER BY i.id;
```

---

### Część E. Podsumowanie poprawności formularza

| Obszar walidacji                          | Zapytanie                            | Oczekiwany wynik (poprawny) |
| ----------------------------------------- | ------------------------------------ | --------------------------- |
| Kompletność danych praktyki               | B — pola NULL                        | 0 wierszy                   |
| Liczba dni = 120                          | `working_days <> 120`                | 0 wierszy                   |
| Poprawność dat (end > start)              | `end_date <= start_date`             | 0 wierszy                   |
| Dokładnie 13 efektów w programie          | `COUNT(pt) <> 13`                    | 0 wierszy                   |
| Brak pustych opisów efektów               | `TRIM(description) = ''`             | 0 wierszy                   |
| Suma harmonogramu = 120                   | `SUM(planned_days) <> 120`           | 0 wierszy                   |
| Brak duplikatów lp w harmonogramie        | `GROUP BY ... HAVING COUNT > 1`      | 0 wierszy                   |
| Oboje opiekunowie przypisani              | `uopz_id IS NULL OR zopz_id IS NULL` | 0 wierszy                   |
| Dziennik: 120 wpisów                      | `COUNT(de) <> 120`                   | 0 wierszy                   |
| Dziennik: wszystkie wpisy potwierdzone    | `confirmed_by_zopz = FALSE`          | 0 wierszy                   |
| Sprawozdanie: wszystkie sekcje wypełnione | `NULL / empty sections`              | 0 wierszy                   |
| Efekty uczenia: dokładnie 13 decyzji      | `COUNT(loi) <> 13`                   | 0 wierszy                   |
| Spójność dat wpisów z okresem praktyki    | `work_date < start OR > end`         | 0 wierszy                   |
| Ocena tylko po zatwierdzeniu dokumentów   | `ep + d.approved + r.approved`       | 0 wierszy                   |
