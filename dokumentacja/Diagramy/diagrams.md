# Diagramy Mermaid — System Obsługi Praktyk Zawodowych

---

## Diagram 1: Sekwencja — Obieg dokumentacji praktyki (proces biznesowy)

```mermaid
sequenceDiagram
    autonumber
    actor S as Student
    actor OU as Opiekun Uczelniany (UOPZ)
    actor SEK as Dziekanat / Dyrektor
    actor OZ as Opiekun Zakładowy (ZOPZ)

    Note over S, OZ: FAZA 1: INICJACJA I DOKUMENTACJA WSTĘPNA
    S->>OU: Zgłoszenie i uzgodnienie miejsca praktyki
    S->>SEK: Dostarczenie Oświadczenia instytucji (Zał. nr 9)
    SEK->>OZ: Wysłanie Porozumienia (Zał. nr 1) wraz z regulaminem
    S->>OU: Uzgodnienie Programu i harmonogramu (Zał. nr 2a) z udziałem ZOPZ
    SEK->>S: Wydanie Skierowania (część Karty praktyki - Zał. nr 3)

    Note over S, OZ: FAZA 2: REALIZACJA PRAKTYKI I NADZÓR (120 DNI)
    S->>OZ: Zgłoszenie się w firmie, szkolenie BHP
    S->>S: Wykonywanie prac i prowadzenie Dziennika Praktyki (Zał. nr 6)
    OZ->>S: Bieżące potwierdzanie zadań w Dzienniku (Zał. nr 6)
    OU->>OZ: Hospitacja przebiegu praktyki w firmie (min. 1 raz)

    Note over S, SEK: FAZA 3: OCENA ZAKŁADOWA (ZAKOŃCZENIE)
    OZ->>S: Weryfikacja Dziennika Praktyki (Zał. nr 6)
    OZ->>S: Wystawienie opinii i oceny na Karcie praktyki (Zał. nr 3)
    OZ->>S: Potwierdzenie uzyskanych efektów uczenia się (Zał. nr 4)
    S->>S: Opracowanie Sprawozdania z praktyki (Zał. nr 7)
    OZ->>S: Zatwierdzenie opinii i Sprawozdania (Zał. nr 7)

    Note over S, SEK: FAZA 4: ZALICZENIE UCZELNIANE I EGZAMIN
    S->>S: Wypełnienie Kwestionariusza ankiety (Zał. nr 5)
    S->>OU: Złożenie kompletu dokumentów (max 7 dni po zakończeniu praktyki)
    SEK->>OU: Powołanie Komisji egzaminacyjnej przez Dyrektora
    OU->>S: Egzamin ustny z oceną przed Komisją
    OU->>SEK: Sporządzenie Protokołu egzaminu (Zał. nr 8)
    OU->>OU: Wpis oceny do systemu USOS
```

---

## Diagram 2: Sekwencja — Weryfikacja Dziennika Praktyk (przepływ techniczny)

```mermaid
sequenceDiagram
    autonumber
    participant S as Student
    participant B as Backend (Flask)
    participant DB as Baza danych
    participant OU as Opiekun Uczelniany (UOPZ)

    S->>B: Wyślij Dziennik do weryfikacji
    B->>B: Walidacja danych (kompletność wpisów, 120 dni)

    alt dane niekompletne
        B-->>S: Zwróć błąd (brak wpisów / niepełne dane)
    else dane poprawne
        B->>DB: Zmień status na 'submitted'
        B->>OU: Powiadom o nowym dokumencie do weryfikacji

        alt Opiekun zatwierdza
            OU->>B: Zatwierdź dokument
            B->>DB: Zapisz status 'approved'
            B-->>S: Powiadom o zatwierdzeniu
        else Opiekun odrzuca z uwagami
            OU->>B: Dodaj uwagi i odrzuć
            B->>DB: Zapisz uwagi i status 'rejected'
            B-->>S: Powiadom o konieczności poprawy
            S->>B: Wprowadź poprawki i wyślij ponownie
            B->>DB: Zmień status na 'submitted'
        end
    end
```

---

## Diagram 3: Stany dokumentu — Cykl życia dokumentu praktyki

```mermaid
stateDiagram-v2
    [*] --> Draft : Utworzenie dokumentu

    Draft --> Submitted : Student wysyła do weryfikacji
    Submitted --> Under_Review : Opiekun otwiera dokument

    Under_Review --> Approved : Opiekun zatwierdza
    Under_Review --> Rejected : Opiekun odrzuca z uwagami

    Rejected --> Draft : Student wprowadza poprawki
    Approved --> Closed : Praktyka zaliczona / archiwizacja

    Closed --> [*]
```

---

## Diagram 4: Flowchart — Logika uprawnień edycji dokumentu

```mermaid
flowchart TD
    A([Użytkownik próbuje edytować dokument]) --> B{Czy użytkownik\njest zalogowany?}
    B -- Nie --> C[Przekieruj do strony logowania]
    B -- Tak --> D{Czy rola użytkownika\nto Student?}
    D -- Nie --> E[Wyświetl tylko podgląd\nRead-only]
    D -- Tak --> F{Czy status dokumentu\nto Draft lub Rejected?}
    F -- Nie --> E
    F -- Tak --> G[Udostępnij formularz edycji]
    G --> H([Użytkownik edytuje dokument])
```

---

## Diagram 5: Flowchart — Przepływ danych przy zapisie wpisu w Dzienniku

```mermaid
flowchart TD
    A([Student dodaje wpis do Dziennika]) --> B[Wypełnienie formularza\ndata, opis prac, nr efektu]
    B --> C{Walidacja po\nstronie klienta}
    C -- błąd --> D[Wyświetl komunikat błędu\nużytkownikowi]
    D --> B
    C -- OK --> E[POST /api/diary/entry]
    E --> F{Walidacja po\nstronie serwera}
    F -- błąd 400 --> G[Zwróć JSON z błędem]
    G --> D
    F -- OK --> H[Zapisz wpis w bazie danych]
    H --> I[Zwróć 201 Created]
    I --> J([Wpis widoczny w Dzienniku\noczekuje na potwierdzenie ZOPZ])
```

---

## Diagram 6: Flowchart — Logika biznesowa generowania PDF

```mermaid
flowchart TD
    A([Użytkownik żąda generowania PDF]) --> B{Czy użytkownik\njest zalogowany?}
    B -- Nie --> C[Błąd 401 Unauthorized]
    B -- Tak --> D{Czy praktyka\nistnieje?}
    D -- Nie --> E[Błąd 404 Not Found]
    D -- Tak --> F{Czy wszystkie dokumenty\nmają status Approved?}
    F -- Nie --> G[Informuj o brakujących\nzatwierdzeniach]
    F -- Tak --> H[Pobierz dane z bazy danych]
    H --> I[Wygeneruj PDF\nreportlab / weasyprint]
    I --> J{Generowanie\nukończone?}
    J -- błąd --> K[Zwróć błąd 500\nz opisem]
    J -- OK --> L[Zwróć plik PDF\ndo pobrania]
    L --> M([Użytkownik pobiera dokument])
```
