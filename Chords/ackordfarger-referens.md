# Ackordfärger — referens för att skapa ackordbilder

Genererad från `get_chord_color()` i `build_songbook.py` (3-nyanssystemet: Major/Minor/Sus, 2026-10-11).

Reglerna: grundtonens färg (Major) är basen. Minor-ackord (m, m7, m6 — men inte maj7) mörkas 35% mot svart. Sus/add-ackord (sus2, sus4, add9, add11 ...) ljusas 35% mot vitt. Allt annat (7, maj7, 6, 9 osv.) behåller Major-nyansen.

## Fullständig tabell — alla grundtoner

| Grundton | Major | Minor | Sus |
|---|---|---|---|
| A | `#448AFF` | `#2c5aa6` | `#85b3ff` |
| A# / Bb | `#74A8FF` | `#4b6da6` | `#a5c6ff` |
| B | `#FF5252` | `#a63535` | `#ff8f8f` |
| C | `#FFD93D` | `#a68d28` | `#ffe681` |
| C# / Db | `#FFE870` | `#a69749` | `#fff0a2` |
| D | `#4ECDC4` | `#33857f` | `#8cded9` |
| D# / Eb | `#7FE7E0` | `#539692` | `#acefeb` |
| E | `#FF9F43` | `#a6672c` | `#ffc185` |
| F | `#4CAF50` | `#317234` | `#8bcb8d` |
| F# / Gb | `#76C442` | `#4d7f2b` | `#a6d984` |
| G | `#B388FF` | `#7458a6` | `#ceb2ff` |
| G# / Ab | `#CE9EFF` | `#8667a6` | `#dfc0ff` |

## Färg per ackord som redan finns i ackordbanken (CHORD_IMAGES)

| Ackord | Nyans | Färg | Ändrad vid 2026-10-11-justeringen? |
|---|---|---|---|
| A | Major | `#448AFF` | Nej |
| Am | Minor | `#2c5aa6` | **Ja** — var `#1E6FD9` |
| A7 | Major | `#448AFF` | Nej |
| Asus2 | Sus | `#85b3ff` | **Ja** — föll tidigare till ren Major-färg |
| Asus4 | Sus | `#85b3ff` | **Ja** — föll tidigare till ren Major-färg |
| B7 | Major | `#FF5252` | Nej |
| Cadd9 | Sus | `#ffe681` | **Ja** — föll tidigare till ren Major-färg |
| C | Major | `#FFD93D` | Nej |
| Dm | Minor | `#33857f` | **Ja** — var `#2DA49A` |
| D | Major | `#4ECDC4` | Nej |
| D/F# | Major | `#4ECDC4` | Nej |
| D7 | Major | `#4ECDC4` | Nej |
| Dsus2 | Sus | `#8cded9` | **Ja** — föll tidigare till ren Major-färg |
| Dsus4 | Sus | `#8cded9` | **Ja** — föll tidigare till ren Major-färg |
| E | Major | `#FF9F43` | Nej |
| Em | Minor | `#a6672c` | **Ja** — var `#E07B20` |
| E7 | Major | `#FF9F43` | Nej |
| F | Major | `#4CAF50` | Nej |
| Fmaj7 | Major | `#4CAF50` | Nej |
| Fmaj7/C | Major | `#4CAF50` | Nej |
| G | Major | `#B388FF` | Nej |
| G7 | Major | `#B388FF` | Nej |

## Vilka bilder påverkas?

Om ackordbilderna (PNG/JPG i denna mapp) har någon färgkodning som ska matcha appens ackordfärg (t.ex. ram, bakgrund eller accent i bilden), är det **dessa 8 bilder** som nu visar en annan färg än innan och eventuellt bör uppdateras/skapas om:

- `A Minor.png` (Am)
- `Asus2.jpg`, `Asus4.jpg`
- `C Add9.png` (Cadd9)
- `D  Minor.png` (Dm)
- `Dsus2.png`, `Dsus4.png`
- `E Minor.png` (Em)

Alla rena dur-, 7- och maj7-bilder (A, A7, B7, C, D, D/F#, D7, E, E7, F, Fmaj7, Fmaj7/C, G, G7) är oförändrade.
