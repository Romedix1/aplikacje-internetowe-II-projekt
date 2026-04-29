-- Przypadek 1: Powielony numer albumu (Błąd UNIQUE)
INSERT INTO studenci VALUES (2, 'Adam', 'Nowicki', '123456', 'Informatyka', 'Sieci');

-- Przypadek 2: Błędna liczba dni (Inna niż 120 - Błąd CHECK)
INSERT INTO formularze_praktyk (id_formularza, id_studenta, id_firmy, data_od, data_do, liczba_dni_roboczych)
VALUES (2, 1, 1, '2026-07-01', '2026-09-30', 80);

-- Przypadek 3: Data zakończenia przed rozpoczęciem (Błąd CHECK)
INSERT INTO formularze_praktyk (id_formularza, id_studenta, id_firmy, data_od, data_do, liczba_dni_roboczych)
VALUES (3, 1, 1, '2026-10-01', '2026-07-01', 120);

-- Przypadek 4: Powielona pozycja LP w harmonogramie (Błąd UNIQUE)
INSERT INTO harmonogram_praktyki (id_harmonogramu, id_formularza, lp, dzial_komorka, planowana_liczba_dni)
VALUES (1, 1, 1, 'Serwis', 15);