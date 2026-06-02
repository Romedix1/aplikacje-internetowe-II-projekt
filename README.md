# System Obsługi Praktyk Zawodowych

> Aplikacja internetowa wspomagająca cyfrowy obieg dokumentacji praktyk zawodowych — Instytut Informatyki Stosowanej, ANS Elbląg

---

## Opis projektu

System zastępuje tradycyjny, papierowy obieg dokumentów praktyk zawodowych (dziennik praktyk, karta praktyki, potwierdzenie efektów uczenia się, sprawozdanie) procesem w pełni cyfrowym. Umożliwia studentom, opiekunom uczelnianym (UOPZ) i zakładowym (ZOPZ) oraz sekretariatowi współpracę online z możliwością generowania dokumentów PDF.

Projekt realizowany w ramach przedmiotu **Aplikacje Internetowe 2**.

---

## Aktorzy systemu

| Aktor                         | Rola                                                              |
| ----------------------------- | ----------------------------------------------------------------- |
| **Student**                   | Wypełnia dziennik, składa dokumenty, śledzi status praktyki       |
| **Opiekun Uczelniany (UOPZ)** | Zatwierdza program, weryfikuje dokumenty, wystawia ocenę końcową  |
| **Opiekun Zakładowy (ZOPZ)**  | Potwierdza zadania w dzienniku, wystawia opinię w Karcie praktyki |
| **Sekretariat / Dziekanat**   | Archiwizuje dokumentację, rejestruje wynik egzaminu w USOS        |

---

## Wymagania funkcjonalne

| ID   | Nazwa                                             | Opis                                                                                                         | Priorytet (MoSCoW) |
| ---- | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | ------------------ |
| F-01 | Rejestracja miejsca praktyki                      | System umożliwia studentowi zgłoszenie miejsca odbywania praktyki do akceptacji UOPZ                         | Must               |
| F-02 | Uzgodnienie programu i harmonogramu               | System umożliwia UOPZ i studentowi wspólne opracowanie Programu i harmonogramu (Zał. 2a)                     | Must               |
| F-03 | Prowadzenie Dziennika Praktyk                     | System umożliwia studentowi codzienne wpisywanie wykonanych zadań w dynamicznej tabeli Dziennika (Zał. 6)    | Must               |
| F-04 | Potwierdzanie wpisów przez ZOPZ                   | System umożliwia Opiekunowi Zakładowemu elektroniczne potwierdzanie poszczególnych wpisów w Dzienniku        | Must               |
| F-05 | Blokowanie edycji po przesłaniu                   | System automatycznie blokuje edycję dokumentu po przesłaniu go do weryfikacji przez UOPZ                     | Must               |
| F-06 | Dodawanie uwag przez opiekunów                    | System umożliwia UOPZ i ZOPZ dodawanie uwag do poszczególnych sekcji dokumentów                              | Should             |
| F-07 | Składanie sprawozdania                            | System umożliwia studentowi wypełnienie i przesłanie Sprawozdania z praktyki (Zał. 7) wraz z samooceną       | Must               |
| F-08 | Potwierdzenie efektów uczenia się                 | System umożliwia UOPZ oznaczenie osiągniętych efektów uczenia się (Zał. 4)                                   | Must               |
| F-09 | Generowanie dokumentów PDF                        | System umożliwia wygenerowanie kompletnego zestawu dokumentów (Dziennik, Karta, Sprawozdanie) w formacie PDF | Must               |
| F-10 | Wniosek o zaliczenie na podstawie pracy zawodowej | System umożliwia studentowi złożenie wniosku (Zał. 4b) o zaliczenie praktyki na podstawie zatrudnienia/stażu | Should             |
| F-11 | Wypełnienie ankiety                               | System umożliwia studentowi wypełnienie Kwestionariusza ankiety (Zał. 5) po zakończeniu praktyki             | Should             |
| F-12 | Rejestracja oceny końcowej                        | System umożliwia UOPZ wprowadzenie oceny po egzaminie ustnym i eksport danych do USOS                        | Must               |
| F-13 | Panel statusu dokumentów                          | System umożliwia każdemu aktorowi podgląd aktualnego statusu wszystkich dokumentów danej praktyki            | Should             |

---

## User Stories

| #     | Jako                      | Chcę                                                  | Aby                                                                               |
| ----- | ------------------------- | ----------------------------------------------------- | --------------------------------------------------------------------------------- |
| US-01 | Student                   | codziennie uzupełniać wpisy w Dzienniku Praktyk       | dokumentować wykonane zadania na bieżąco i mieć potwierdzenie realizacji praktyki |
| US-02 | Opiekun Uczelniany (UOPZ) | weryfikować przesłane dokumenty studenta w systemie   | szybko przystąpić do weryfikacji i nie opóźniać procesu zaliczenia                |
| US-03 | Opiekun Zakładowy (ZOPZ)  | elektronicznie potwierdzać wpisy w dzienniku studenta | uniknąć papierowego obiegu dokumentów i mieć wgląd w historię potwierdzeń         |

---

## Wymagania niefunkcjonalne

### Bezpieczeństwo

- Dane studenta (dziennik, oceny, dokumenty) są dostępne wyłącznie dla studenta, jego UOPZ i ZOPZ przypisanych do danej praktyki.
- Uwierzytelnianie realizowane przez konto uczelniane (SSO / LDAP ANS). #TODO: DO SPRAWDZENIA
- Wszystkie dane przesyłane są szyfrowanym połączeniem HTTPS.

### Użyteczność

- Interfejs jest responsywny i poprawnie wyświetla się na urządzeniach mobilnych (min. 320 px szerokości).
- Formularze walidują dane po stronie klienta i zwracają czytelne komunikaty błędów w języku polskim.

### Wydajność

- Generowanie dokumentu PDF trwa nie dłużej niż 5 sekund dla pojedynczego zestawu dokumentów.
- Strona ładuje się w czasie poniżej 3 sekund przy standardowym łączu (10 Mbit/s).

### Archiwizacja i trwałość danych

- Dane przechowywane są w relacyjnej bazie danych PostgreSQL.
- Możliwy eksport danych studenta do formatu JSON.

---

## Przepływ dokumentacji — Obieg Praktyki Zawodowej (Workflow)

TODO: POROWNAC Z DIAGRAMS

```
FAZA 1 – INICJACJA
1. [Student → UOPZ]     Zgłoszenie i uzgodnienie miejsca praktyki
2. [Student → Dziekanat] Dostarczenie Oświadczenia instytucji (Zał. nr 9)
3. [Dziekanat → ZOPZ]   Wysłanie Porozumienia (Zał. nr 1) wraz z regulaminem
4. [Student → UOPZ]     Uzgodnienie Programu i harmonogramu (Zał. nr 2a)
5. [Dziekanat → Student] Wydanie Skierowania (Zał. nr 3)

FAZA 2 – REALIZACJA (120 dni)
6. [Student → ZOPZ]     Zgłoszenie się w firmie, szkolenie BHP
7. [Student]             Codzienne prowadzenie Dziennika Praktyki (Zał. nr 6)
8. [ZOPZ → Student]     Bieżące potwierdzanie zadań w Dzienniku
9. [UOPZ → ZOPZ]       Hospitacja w firmie (min. 1 raz)

FAZA 3 – OCENA ZAKŁADOWA
10. [ZOPZ → Student]    Weryfikacja i podpisanie Dziennika (Zał. nr 6)
11. [ZOPZ → Student]    Wystawienie opinii na Karcie praktyki (Zał. nr 3)
12. [ZOPZ → UOPZ]    Potwierdzenie efektów uczenia się (Zał. nr 4)
12. [UOPZ → Student]    Zatwierdzenie efektów uczenia się (Zał. nr 4)
13. [Student]            Opracowanie Sprawozdania (Zał. nr 7)
14. [ZOPZ → Student]    Zatwierdzenie Sprawozdania (Zał. nr 7)

FAZA 4 – ZALICZENIE UCZELNIANE
15. [Student]            Wypełnienie Kwestionariusza ankiety (Zał. nr 5)
16. [Student → UOPZ]    Złożenie kompletu dokumentów (max 7 dni po praktyce)
17. [Dyrektor → UOPZ]   Powołanie Komisji egzaminacyjnej
18. [UOPZ → Student]    Egzamin ustny z oceną przed Komisją
19. [UOPZ → Dziekanat]  Sporządzenie Protokołu egzaminu (Zał. nr 8)
20. [UOPZ]               Wpis oceny do systemu USOS
```

---

## Technologie

- **Backend:** Python 3.x + Flask
- **Frontend:** HTML + css
- **Baza danych:** PostgreSQL + DBeaver

### Uzasadnienie wyboru PostgreSQL

PostgreSQL wybrano jako system zarządzania bazą danych zarówno na etapie prototypu, jak i docelowego wdrożenia, ponieważ:

- obsługuje natywne typy `ENUM`, `SERIAL`, `BOOLEAN`, `TIMESTAMP` użyte w `schema.sql`,
- zapewnia pełną współbieżność i izolację transakcji (ACID) — niezbędne przy równoczesnej pracy wielu użytkowników (student, UOPZ, ZOPZ, sekretariat),
- umożliwia zarządzanie uprawnieniami na poziomie tabel i użytkowników,
- jest darmowy, open-source i powszechnie stosowany w aplikacjach Flask,
- Flask-SQLAlchemy obsługuje PostgreSQL przez sterownik `psycopg2`.

### Uzasadnienie wyboru DBeaver Community

DBeaver Community wybrano jako narzędzie do prototypowania i przeglądania bazy danych (alternatywa dla MySQL Workbench), ponieważ:

- obsługuje PostgreSQL natywnie — bezpośrednie połączenie z bazą projektu,
- posiada graficzny edytor SQL z podpowiadaniem składni,
- automatycznie generuje diagram ERD na podstawie kluczy obcych zdefiniowanych w `schema.sql`,
- umożliwia import i wykonanie pliku `.sql` jednym kliknięciem,
- jest darmowy i dostępny na Windows, macOS i Linux.

### Uzasadnienie wyboru Mermaid

Mermaid wybrano jako narzędzie do organizacji i dokumentowania projektu bazy danych, ponieważ:

- kod źródłowy diagramu to zwykły tekst — wersjonowany w repozytorium Git razem z kodem projektu,
- nie wymaga instalacji — działa w przeglądarce przez [mermaid.live](https://mermaid.live) lub jako wtyczka VS Code,
- obsługuje diagramy ERD, sekwencji, stanów i flowcharty — wszystkie wykorzystane w projekcie,
- diagramy eksportuje się do PNG/SVG i dołącza do dokumentacji,
- integruje się z GitHub — diagramy renderują się bezpośrednio w plikach `.md`.

---

## Dokumenty źródłowe (załączniki)

| Załącznik | Opis                                                  |
| --------- | ----------------------------------------------------- |
| Zał. 2a   | Program i harmonogram praktyki                        |
| Zał. 3    | Karta praktyki zawodowej                              |
| Zał. 4    | Potwierdzenie efektów uczenia się                     |
| Zał. 4b   | Wniosek o zaliczenie na podstawie pracy zawodowej     |
| Zał. 5    | Kwestionariusz ankiety                                |
| Zał. 6    | Dziennik praktyki zawodowej                           |
| Zał. 7    | Sprawozdanie z praktyki zawodowej                     |
| Zał. 9    | Oświadczenie w sprawie przyjęcia studenta na praktykę |

---

## Modelowanie systemu — Diagramy (lab05)

Diagramy wykonane w narzędziu **Mermaid**. Kod źródłowy w pliku `diagrams.md`, eksport PNG/SVG w katalogu `docs/diagrams/`.

### Diagram 1 — Sekwencja obiegu dokumentacji (proces biznesowy)

Przedstawia pełny przepływ komunikacji między aktorami systemu w 4 fazach praktyki zawodowej (inicjacja, realizacja, ocena zakładowa, zaliczenie uczelniane).

### Diagram 2 — Sekwencja weryfikacji Dziennika Praktyk (przepływ techniczny)

Przedstawia interakcję między Studentem, Backendem Flask, Bazą danych i Opiekunem Uczelnianym podczas procesu składania i weryfikacji dziennika.

Scenariusze:

- dane niekompletne → błąd walidacji zwrócony do studenta,
- dane poprawne → status `submitted`, opiekun weryfikuje,
- opiekun zatwierdza → status `approved`, student powiadamiany,
- opiekun odrzuca → status `rejected` z uwagami, student poprawia i składa ponownie.

### Diagram 3 — Stany dokumentu

Modeluje cykl życia dokumentu praktyki:

`Draft` → `Submitted` → `Under_Review` → `Approved` / `Rejected` → (powrót do `Draft` przy odrzuceniu) → `Closed`

### Diagram 4 — Flowchart logiki uprawnień edycji

Algorytm wykonywany przy próbie edycji dokumentu:

- Czy użytkownik jest zalogowany?
- Czy rola to `Student`?
- Czy status dokumentu to `Draft` lub `Rejected`?
- Tak → formularz edycji / Nie → podgląd (read-only)

### Diagram 5 — Flowchart przepływu danych przy zapisie wpisu w Dzienniku

Przedstawia przepływ od wypełnienia formularza przez studenta, przez walidację po stronie klienta i serwera, aż do zapisu w bazie danych.

### Diagram 6 — Flowchart logiki biznesowej generowania PDF

Przedstawia algorytm generowania dokumentu PDF: weryfikacja uprawnień, sprawdzenie statusów dokumentów, generowanie i zwrot pliku do pobrania.

## Uruchomienie lokalne

### 1. Pobranie repozytorium

```bash
git clone https://github.com/Romedix1/aplikacje-internetowe-II-projekt.git
cd aplikacje-internetowe-II-projekt/aplikacja
```

---

### 2. Środowisko wirtualne i zależności Pythona

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

---

### 3. Zmienne środowiskowe

Utwórz plik `.env` w głównym katalogu projektu na podstawie dołączonego szablonu:

```bash
cp .env.example .env
```

Następnie uzupełnij wartości w `.env`

---

### 4. Baza danych PostgreSQL

#### 4.1 Utworzenie bazy i użytkownika

Zaloguj się do PostgreSQL i wykonaj:

```sql
CREATE USER uzytkownik WITH PASSWORD 'haslo';
CREATE DATABASE praktyki OWNER uzytkownik;
```

#### 4.2 Zastosowanie schematu

```bash
psql -U uzytkownik -d praktyki -f app/db/schema.sql
```

Skrypt `schema.sql` tworzy wszystkie tabele, typy `ENUM` i powiązania kluczami obcymi wymagane do działania systemu.

#### 4.3 Dane testowe (opcjonalnie)

Aby załadować przykładowe dane (studentów, opiekunów, praktyki) na potrzeby deweloperskie:

```bash
psql -U uzytkownik -d praktyki -f app/db/pdf_test_data.sql
```

> Plik `pdf_test_data.sql` zawiera fikcyjne rekordy przeznaczone wyłącznie do testów lokalnych.

---

### 5. Uruchomienie aplikacji

```bash
python app.py
```

Aplikacja będzie dostępna pod adresem: [http://localhost:5000](http://localhost:5000)

---

### Szybki start — podsumowanie poleceń

```bash
git clone https://github.com/Romedix1/aplikacje-internetowe-II-projekt.git && cd aplikacje-internetowe-II-projekt/aplikacja
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
psql -U uzytkownik -d praktyki -f app/db/schema.sql
psql -U uzytkownik -d praktyki -f app/db/seed_data.sql   # opcjonalnie
python app.py
```
