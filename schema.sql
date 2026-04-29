-- TABELE PODSTAWOWE
CREATE TABLE studenci (
    id_studenta SERIAL PRIMARY KEY,
    nr_albumu VARCHAR(20) UNIQUE NOT NULL,
    imie VARCHAR(50) NOT NULL,
    nazwisko VARCHAR(50) NOT NULL,
    kierunek VARCHAR(100) DEFAULT 'Informatyka',
    specjalnosc VARCHAR(100),
    forma_studiow VARCHAR(30) CHECK (forma_studiow IN ('stacjonarne', 'niestacjonarne'))
);

CREATE TABLE firmy (
    id_firmy SERIAL PRIMARY KEY,
    nazwa VARCHAR(255) NOT NULL,
    adres VARCHAR(255) NOT NULL,
    reprezentant VARCHAR(100) -- Osoba do Porozumienia (Zał. 1)
);

CREATE TABLE opiekunowie (
    id_opiekuna SERIAL PRIMARY KEY,
    imie_nazwisko VARCHAR(100) NOT NULL,
    typ VARCHAR(20) CHECK (typ IN ('uczelniany', 'zakladowy')),
    telefon VARCHAR(20),
    email VARCHAR(100)
);

-- FORMULARZ GŁÓWNY (Zał. 3 - Karta)
CREATE TABLE formularze_praktyk (
    id_formularza SERIAL PRIMARY KEY,
    id_studenta INTEGER REFERENCES studenci(id_studenta),
    id_firmy INTEGER REFERENCES firmy(id_firmy),
    data_od DATE NOT NULL,
    data_do DATE NOT NULL,
    liczba_dni_roboczych INT DEFAULT 120 CHECK (liczba_dni_roboczych = 120),
    nr_porozumienia VARCHAR(50),
    data_bhp DATE,
    ocena_z NUMERIC(2,1) CHECK (ocena_z BETWEEN 2 AND 5),
    ocena_u NUMERIC(2,1) CHECK (ocena_u BETWEEN 2 AND 5),
    ocena_s NUMERIC(2,1) CHECK (ocena_s BETWEEN 2 AND 5),
    ocena_e NUMERIC(2,1) CHECK (ocena_e BETWEEN 2 AND 5),
    ocena_k NUMERIC(2,1) CHECK (ocena_k BETWEEN 2 AND 5),
    CHECK (data_do > data_od)
);

-- HARMONOGRAM I PROGRAM (Zał. 2a)
CREATE TABLE harmonogram (
    id_harmonogramu SERIAL PRIMARY KEY,
    id_formularza INTEGER REFERENCES formularze_praktyk(id_formularza),
    lp INT NOT NULL,
    dzial_komorka VARCHAR(255) NOT NULL,
    dni_robocze INT NOT NULL CHECK (dni_robocze > 0),
    UNIQUE(id_formularza, lp)
);

CREATE TABLE efekty_ksztalcenia (
    id_efektu SERIAL PRIMARY KEY,
    kod VARCHAR(2) UNIQUE NOT NULL, -- 01-13
    opis TEXT NOT NULL
);

CREATE TABLE efekty_formularza (
    id_formularza INTEGER REFERENCES formularze_praktyk(id_formularza),
    id_efektu INTEGER REFERENCES efekty_ksztalcenia(id_efektu),
    opis_prac_studenta TEXT NOT NULL,
    czy_uzyskal BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (id_formularza, id_efektu)
);

-- DZIENNIK I SPRAWOZDANIE (Zał. 6 i 7)
CREATE TABLE dziennik_wpisy (
    id_wpisu SERIAL PRIMARY KEY,
    id_formularza INTEGER REFERENCES formularze_praktyk(id_formularza),
    numer_dnia INT CHECK (numer_dnia BETWEEN 1 AND 120),
    data_wpisu DATE NOT NULL,
    opis_prac TEXT NOT NULL,
    podpis_ZOPZ BOOLEAN DEFAULT FALSE
);

CREATE TABLE sprawozdania (
    id_formularza INTEGER PRIMARY KEY REFERENCES formularze_praktyk(id_formularza),
    charakterystyka_miejsca TEXT,
    opis_analiza_prac TEXT,
    samoocena_kompetencji TEXT
);