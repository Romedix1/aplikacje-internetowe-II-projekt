# System Obsługi Praktyk Zawodowych

> Aplikacja internetowa wspomagająca cyfrowy obieg dokumentacji praktyk zawodowych — Instytut Informatyki Stosowanej, ANS Elbląg

---

## Opis projektu

System zastępuje tradycyjny, papierowy obieg dokumentów praktyk zawodowych (dziennik praktyk, karta praktyki, potwierdzenie efektów uczenia się, sprawozdanie) procesem w pełni cyfrowym. Umożliwia studentom, opiekunom uczelnianym (UOPZ) i zakładowym (ZOPZ) oraz sekretariatowi współpracę online z możliwością generowania dokumentów PDF.

Projekt realizowany w ramach przedmiotu **Aplikacje Internetowe 2** (lab04 — Inżynieria Wymagań).

---

## Aktorzy systemu

| Aktor | Rola |
|---|---|
| **Student** | Wypełnia dziennik, składa dokumenty, śledzi status praktyki |
| **Opiekun Uczelniany (UOPZ)** | Zatwierdza program, weryfikuje dokumenty, wystawia ocenę końcową |
| **Opiekun Zakładowy (ZOPZ)** | Potwierdza zadania w dzienniku, wystawia opinię w Karcie praktyki |
| **Sekretariat / Dziekanat** | Archiwizuje dokumentację, rejestruje wynik egzaminu w USOS |

---

## Wymagania funkcjonalne

| ID | Nazwa | Opis | Priorytet (MoSCoW) |
|---|---|---|---|
| F-01 | Rejestracja miejsca praktyki | System umożliwia studentowi zgłoszenie miejsca odbywania praktyki do akceptacji UOPZ | Must |
| F-02 | Uzgodnienie programu i harmonogramu | System umożliwia UOPZ i studentowi wspólne opracowanie Programu i harmonogramu (Zał. 2a) | Must |
| F-03 | Prowadzenie Dziennika Praktyk | System umożliwia studentowi codzienne wpisywanie wykonanych zadań w dynamicznej tabeli Dziennika (Zał. 6) | Must |
| F-04 | Potwierdzanie wpisów przez ZOPZ | System umożliwia Opiekunowi Zakładowemu elektroniczne potwierdzanie poszczególnych wpisów w Dzienniku | Must |
| F-05 | Blokowanie edycji po przesłaniu | System automatycznie blokuje edycję dokumentu po przesłaniu go do weryfikacji przez UOPZ | Must |
| F-06 | Dodawanie uwag przez opiekunów | System umożliwia UOPZ i ZOPZ dodawanie uwag do poszczególnych sekcji dokumentów | Should |
| F-07 | Składanie sprawozdania | System umożliwia studentowi wypełnienie i przesłanie Sprawozdania z praktyki (Zał. 7) wraz z samooceną | Must |
| F-08 | Potwierdzenie efektów uczenia się | System umożliwia UOPZ oznaczenie osiągniętych efektów uczenia się (Zał. 4) | Must |
| F-09 | Generowanie dokumentów PDF | System umożliwia wygenerowanie kompletnego zestawu dokumentów (Dziennik, Karta, Sprawozdanie) w formacie PDF | Must |
| F-10 | Wniosek o zaliczenie na podstawie pracy zawodowej | System umożliwia studentowi złożenie wniosku (Zał. 4b) o zaliczenie praktyki na podstawie zatrudnienia/stażu | Should |
| F-11 | Wypełnienie ankiety | System umożliwia studentowi wypełnienie Kwestionariusza ankiety (Zał. 5) po zakończeniu praktyki | Should |
| F-12 | Rejestracja oceny końcowej | System umożliwia UOPZ wprowadzenie oceny po egzaminie ustnym i eksport danych do USOS | Must |
| F-13 | Panel statusu dokumentów | System umożliwia każdemu aktorowi podgląd aktualnego statusu wszystkich dokumentów danej praktyki | Should |
| F-14 | Powiadomienia e-mail | System automatycznie wysyła powiadomienia e-mail przy zmianie statusu dokumentu | Could |

---

## Wymagania niefunkcjonalne

### Bezpieczeństwo
- Dane studenta (dziennik, oceny, dokumenty) są dostępne wyłącznie dla studenta, jego UOPZ i ZOPZ przypisanych do danej praktyki.
- Uwierzytelnianie realizowane przez konto uczelniane (SSO / LDAP ANS).
- Wszystkie dane przesyłane są szyfrowanym połączeniem HTTPS.

### Użyteczność
- Interfejs jest responsywny i poprawnie wyświetla się na urządzeniach mobilnych (min. 320 px szerokości).
- Formularze walidują dane po stronie klienta i zwracają czytelne komunikaty błędów w języku polskim.

### Wydajność
- Generowanie dokumentu PDF trwa nie dłużej niż 5 sekund dla pojedynczego zestawu dokumentów.
- Strona ładuje się w czasie poniżej 3 sekund przy standardowym łączu (10 Mbit/s).

### Archiwizacja i trwałość danych
- Dane przechowywane są w relacyjnej bazie danych (np. PostgreSQL) z codzienną kopią zapasową.
- Możliwy eksport danych studenta do formatu JSON.
- Dokumenty PDF archiwizowane są przez minimum 5 lat po zakończeniu studiów.

---

## Przepływ dokumentacji — Obieg Praktyki Zawodowej (Workflow)

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
12. [ZOPZ → Student]    Potwierdzenie efektów uczenia się (Zał. nr 4)
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
- **Baza danych:** PostgreSQL

---

## Dokumenty źródłowe (załączniki)

| Załącznik | Opis |
|---|---|
| Zał. 2a | Program i harmonogram praktyki |
| Zał. 3 | Karta praktyki zawodowej |
| Zał. 4 | Potwierdzenie efektów uczenia się |
| Zał. 4b | Wniosek o zaliczenie na podstawie pracy zawodowej |
| Zał. 5 | Kwestionariusz ankiety |
| Zał. 6 | Dziennik praktyki zawodowej |
| Zał. 7 | Sprawozdanie z praktyki zawodowej |

---
