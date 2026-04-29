-- 1. Sprawdzenie kompletności pól obowiązkowych
SELECT * FROM formularze_praktyk WHERE id_studenta IS NULL OR data_od IS NULL;

-- 2. Sprawdzenie poprawności liczby dni w Karcie
SELECT id_formularza FROM formularze_praktyk WHERE liczba_dni_roboczych <> 120;

-- 3. Weryfikacja liczby efektów kształcenia (musi być 13)
SELECT id_formularza, COUNT(*) FROM efekty_formularza 
GROUP BY id_formularza HAVING COUNT(*) <> 13;

-- 4. Weryfikacja sumy dni w Harmonogramie (musi być 120)
SELECT id_formularza, SUM(planowana_liczba_dni) 
FROM harmonogram_praktyki 
GROUP BY id_formularza HAVING SUM(planowana_liczba_dni) <> 120;

-- 5. Wykrywanie braku któregokolwiek z opiekunów
SELECT f.id_formularza FROM formularze_praktyk f
WHERE NOT EXISTS (SELECT 1 FROM formularz_opiekunowie fo 
    JOIN opiekunowie o ON fo.id_opiekuna = o.id_opiekuna 
    WHERE fo.id_formularza = f.id_formularza AND o.typ_opiekuna = 'uczelniany');