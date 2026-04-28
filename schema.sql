-- 1. Tabela bazowa: Efekty Uczenia Się
CREATE TABLE efekty_uczenia (
    kod_eus VARCHAR(5) PRIMARY KEY, -- od '01' do '13'
    tresc TEXT NOT NULL
);

-- 2. Dane Studentów
CREATE TABLE studenci (
    nr_albumu VARCHAR(15) PRIMARY KEY,
    imie_nazwisko VARCHAR(100) NOT NULL,
    kierunek VARCHAR(100) DEFAULT 'Informatyka',
    specjalnosc VARCHAR(100),
    forma_studiow VARCHAR(50) -- stacjonarne / niestacjonarne
);

-- 3. Zakłady Pracy
CREATE TABLE zaklady_pracy (
    id SERIAL PRIMARY KEY,
    nazwa_firmy VARCHAR(255) NOT NULL,
    adres TEXT,
    reprezentant_firmy VARCHAR(100), -- osoba do Porozumienia
    zopz_imie_nazwisko VARCHAR(100),
    zopz_funkcja VARCHAR(100),
    zopz_telefon VARCHAR(20),
    zopz_email VARCHAR(100)
);

-- 4. Karta Praktyki i dane ogólne procesu
CREATE TABLE praktyki (
    id SERIAL PRIMARY KEY,
    nr_albumu VARCHAR(15) REFERENCES studenci(nr_albumu),
    id_zakladu INTEGER REFERENCES zaklady_pracy(id),
    termin_od DATE,
    termin_do DATE,
    rok_akademicki VARCHAR(10),
    liczba_dni_roboczych INTEGER DEFAULT 120,
    data_zgloszenia DATE, -- potwierdzenie zgłoszenia się
    data_bhp DATE,
    data_uzgodnienia_programu DATE,
    ou_imie_nazwisko VARCHAR(100), -- Opiekun Uczelniany
    reprezentant_uczelni VARCHAR(100), -- do Porozumienia
    numer_porozumienia VARCHAR(50),
    data_porozumienia DATE,
    -- Oceny (Zal. 3 i 8)
    ocena_zakladowa_opis TEXT,
    ocena_zakladowa_punktowa NUMERIC(2,1), -- Ocena Z
    ocena_uczelniana_opis TEXT,
    ocena_uczelniana_punktowa NUMERIC(2,1), -- Ocena U
    ocena_sprawozdania_punktowa NUMERIC(2,1), -- Ocena S
    ocena_koncowa_punktowa NUMERIC(2,1) -- Ocena K
);

-- 5. Program i Harmonogram (Zał. 2a i Zał. 4)
CREATE TABLE program_realizacja (
    id_praktyki INTEGER REFERENCES praktyki(id),
    kod_eus VARCHAR(5) REFERENCES efekty_uczenia(kod_eus),
    opis_prac_praktykanta TEXT,
    czy_uzyskal VARCHAR(20), -- uzyskał / nie uzyskał
    PRIMARY KEY (id_praktyki, kod_eus)
);

CREATE TABLE harmonogram_etapy (
    id SERIAL PRIMARY KEY,
    id_praktyki INTEGER REFERENCES praktyki(id),
    dzial_komorka VARCHAR(255),
    dni_robocze INTEGER
);

-- 6. Dziennik Praktyki (Zał. 6)
CREATE TABLE dziennik_wpisy (
    id SERIAL PRIMARY KEY,
    id_praktyki INTEGER REFERENCES praktyki(id),
    numer_dnia INTEGER,
    data_wpisu DATE,
    opis_wykonanych_prac TEXT,
    czy_zatwierdzony BOOLEAN DEFAULT FALSE -- Podpis ZOPZ/nadzorującego
);

CREATE TABLE wpis_eus_mapowanie (
    id_wpisu INTEGER REFERENCES dziennik_wpisy(id),
    kod_eus VARCHAR(5) REFERENCES efekty_uczenia(kod_eus),
    PRIMARY KEY (id_wpisu, kod_eus)
);

-- 7. Sprawozdanie (Zał. 7)
CREATE TABLE sprawozdania_tresc (
    id_praktyki INTEGER PRIMARY KEY REFERENCES praktyki(id),
    charakterystyka_miejsca TEXT,
    opis_analiza_prac TEXT,
    samoocena_kompetencji TEXT
);

-- 8. Ankieta Ewaluacyjna (Zał. 5)
CREATE TABLE ankiety_wyniki (
    id_praktyki INTEGER PRIMARY KEY REFERENCES praktyki(id),
    -- Odpowiedzi 1-14 (skala 1-5)
    q1 INTEGER, q2 INTEGER, q3 INTEGER, q4 INTEGER, q5 INTEGER,
    q6 INTEGER, q7 INTEGER, q8 INTEGER, q9 INTEGER, q10 INTEGER,
    q11 INTEGER, q12 INTEGER, q13 INTEGER, q14 INTEGER,
    uwagi_dodatkowe TEXT
);

-- 9. Protokół Egzaminu (Zał. 8)
CREATE TABLE protokoly_egzaminu (
    id_praktyki INTEGER PRIMARY KEY REFERENCES praktyki(id),
    data_zaliczenia DATE,
    przewodniczacy_komisji VARCHAR(100),
    czlonek_komisji_2 VARCHAR(100),
    czlonek_komisji_3 VARCHAR(100),
    pytanie_1 TEXT, ocena_1 NUMERIC(2,1),
    pytanie_2 TEXT, ocena_2 NUMERIC(2,1),
    pytanie_3 TEXT, ocena_3 NUMERIC(2,1),
    ocena_srednia_e NUMERIC(2,1) -- Średnia E
);

-- 10. Wniosek o zaliczenie na podstawie pracy (Zał. 4b)
CREATE TABLE wnioski_praca (
    id_praktyki INTEGER PRIMARY KEY REFERENCES praktyki(id),
    uzasadnienie TEXT, -- 
    czy_zalaczono_umowe BOOLEAN, -- 
    czy_zalaczono_opis_stanowiska BOOLEAN,
    czy_zalaczono_zakres_obowiazkow BOOLEAN,
    czy_zalaczono_ceidg_krs BOOLEAN,
    opinia_komisji TEXT,
    decyzja_dyrektora TEXT
);