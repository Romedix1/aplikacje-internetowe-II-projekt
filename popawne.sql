-- 1. Dodanie studenta i firmy
INSERT INTO studenci (id_studenta, imie, nazwisko, nr_albumu, kierunek, specjalnosc, forma_studiow)
VALUES (1, 'Jan', 'Kowalski', '123456', 'Informatyka', 'Aplikacje internetowe', 'stacjonarne');

INSERT INTO firmy (id_firmy, nazwa, adres, reprezentant)
VALUES (1, 'test Sp. z o.o.', 'ul. Wojska Polskiego 1, Elbląg', 'Marek Prezes');

INSERT INTO opiekunowie (id_opiekuna, imie_nazwisko, typ, email)
VALUES 
(1, 'Anna Nowak', 'uczelniany', 'a.nowak@ans-elblag.pl'),
(2, 'Piotr Zieliński', 'zakladowy', 'p.zielinski@test.pl');

INSERT INTO efekty_ksztalcenia (id_efektu, kod, opis) VALUES 
(1, '01', 'Wiedza o standardach inżynierskich'), (2, '02', 'Znajomość technologii IT'),
(3, '03', 'Ekonomiczne i prawne skutki działań'), (4, '04', 'Zasady BHP i ergonomii'),
(5, '05', 'Pozyskiwanie informacji technicznych'), (6, '06', 'Podnoszenie kompetencji inżynierskich'),
(7, '07', 'Opracowywanie dokumentacji'), (8, '08', 'Identyfikacja problemów IT'),
(9, '09', 'Rozwiązywanie zadań inżynierskich'), (10, '10', 'Praca w zespole IT'),
(11, '11', 'Etyka zawodowa'), (12, '12', 'Komunikacja z osobami spoza branży'),
(13, '13', 'Dostrzeganie zmian w wiedzy IT');

INSERT INTO formularze_praktyk (id_formularza, id_studenta, id_firmy, data_od, data_do, liczba_dni_roboczych)
VALUES (1, 1, 1, '2026-07-01', '2026-12-15', 120);

INSERT INTO efekty_formularza (id_formularza, id_efektu, opis_prac_studenta)
SELECT 1, id_efektu, 'Realizacja zadań w projekcie' FROM efekty_ksztalcenia;

INSERT INTO harmonogram (id_formularza, lp, dzial_komorka, dni_robocze)
VALUES 
(1, 1, 'Dział Frontend', 60),
(1, 2, 'Dział Backend', 60);
