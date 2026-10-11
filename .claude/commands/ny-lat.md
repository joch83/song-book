# Skapa en ny låt i Song Book

Hjälp användaren att skapa en ny sångfil i rätt format och lägg till den i Song Book-appen.

## Steg 1 — Samla information

Fråga användaren om dessa uppgifter (ställ alla frågor på en gång):
- **Låttitel** och **artist**
- **BPM** (tempo)
- **Strummingmönster** — se särskild sektion nedan för hur detta ska härledas. Fråga om det finns flera mönster (t.ex. vers/refräng).
- **Spotify-länk** (valfri)
- **Lyrics med ackord** — be användaren klistra in texten direkt i chatten (t.ex. kopierad från tabs.ultimate-guitar.com eller liknande sajt). **Försök inte hämta sidan själv via länk** — tab-sajter renderas med JavaScript så webbverktygen ser bara sidtiteln, och även om det gick vägrar de återge fullständig låttext pga upphovsrätt. Att slå upp ackordprogression/BPM/generell info om låten via sök är dock okej — bara inte kopiera hela texten den vägen.

Om användaren nämner att flera versioner/tabs finns för låten: föreslå att de väljer den vars ackord redan finns i ackordbanken (se steg 2). Enstaka nya ackord i en annars bra version är helt okej — de kan läggas till i banken.

**Chord progression finns aldrig färdig i källan** — den måste härledas manuellt i steg 3.

## Steg 2 — Kontrollera ackord mot ackordbanken

Läs `CHORD_IMAGES`-dictionaryn i `build_songbook.py` för att se **aktuell** lista över ackord som har diagram-bilder (listan växer över tid, så slå aldrig upp den från minnet eller en tidigare session).

Jämför låtens ackord mot nycklarna i `CHORD_IMAGES`. Om låten innehåller ackord som INTE finns där — informera användaren och fråga om de vill lägga till en bild senare (bilden läggs då i `Chords/`-mappen och en ny rad läggs till i `CHORD_IMAGES`, se ihågkomna regler om `/` i filnamn).

## Steg 3 — Härled ackordföljden (Chord progression)

Källan ger bara ackord utskrivna ovanför varje textrad, inte en färdig progression. Bygg den själv:

1. Gå igenom ackorden rad för rad per sektion (vers, refräng, brygga, etc).
2. Hitta det återkommande mönstret i ackorden — om samma sekvens upprepas genom sektionen ska den bara skrivas ut **en gång** i `Chord progression:`.
3. Vers och refräng har ofta **olika** mönster — härled dem separat, en rad per sektion.
4. **Om samma mönster gäller för hela låten** (vers, refräng, solo etc. delar exakt samma ackordföljd) — skriv bara ut det **en gång**, under en enda etikett. Lägg inte till separata identiska rader per sektion i onödan.
5. Om en sektion har ett avvikande stick (t.ex. sista raden i sista refrängen) räcker det med huvudmönstret — avvikelser hanteras i lyrics-delen, inte i chord progression.

## Steg 3b — Härled strummingmönstret

Strummingmönstret bygger alltid på ett fast växelvis rutnät av handrörelser: **udda positioner (1, 3, 5, 7, …) = nedslag** (`D`, eller `R`/`A` för rot-/altrot-betonat nedslag), **jämna positioner (2, 4, 6, 8, …) = uppslag** (`U`). Detta gäller alla låtar i katalogen utom rena arpeggio-/fingerpicking-mönster (t.ex. House of the Rising Sun: `D R R D R R`, som inte är växelvis).

Om ett nedslag eller uppslag inte faktiskt utförs, tas det **inte bort** — det ersätts med `-` så att udda/jämna-positionerna inte förskjuts. Exempel (verifierat mot befintliga låtar):
- `D - D U D U D U` (Too Cold At Home) — position 2:s uppslag är skippat.
- `D - D - D - - U - U D - D U - U` (Every Rose Has Its Thorn, 16-delar) — flera nedslag/uppslag skippade men rutnätet är intakt.

**Så här gör du:** Användaren beskriver bara vilka slag som faktiskt spelas (t.ex. "nedslag, nedslag, uppslag, nedslag"). Du placerar varje beskrivet nedslag på nästa lediga udda position och varje uppslag på nästa lediga jämna position, och fyller alla positioner däremellan med `-`. Använd 8 positioner (åttondelar) som standard om inget annat anges; gå upp till 16 (sextondelar) om mönstret är mer synkoperat/tätt (jämför med `Every Rose Has Its Thorn.txt` eller `You Can't Always Get What You Want.txt`).

**Validera alltid innan du skriver filen:** kör `grep '^Strumming' songs/*.txt` för att jämföra mot befintliga mönster, och kontrollera token för token att udda index ∈ {D, R, A, -} och jämna index ∈ {U, -}. Stämmer det inte — fråga användaren istället för att gissa.

### Rhythm push (tidigt ackordbyte)

Om användaren nämner att ett ackordbyte sker tidigt — t.ex. på ett specifikt uppslag innan nästa takt egentligen börjar (synkoperad "push", som i La Bamba där bytet till G7 sker på sista upphaket i F-ackordet) — markera den exakta positionen i strumming-raden med `>ChordName` direkt efter bokstaven, t.ex. `U>G7`.

### Accent (betonat slag)

Om användaren nämner att ett specifikt ned- eller uppslag ska betonas hårdare — lägg till `!` direkt efter bokstaven, t.ex. `D!` eller `U!`. Renderas som en tyngre pilglyf (`⬇`/`⬆` istället för `↓`/`↑`) i större storlek. Kan kombineras med push-markören: `D!>G7`.

Fråga alltid användaren **vilken position** (räknat från 1, eller "n:te nedslaget/uppslaget") accenten gäller — gissa inte. Exempel: Dance The Night Away har accent på 2:a och 4:e downstrum i mönstret `d U D U D U D U`, vilket blev `d U D! U D U D! U` (position 3 och 7).

Detta renderas som en ring i målackordets färg runt just den pilen, plus en uppdaterad tooltip ("Up stroke – ackordbyte till G7"). Fråga alltid användaren vilken exakt position (räknat från 1) det gäller — gissa inte utifrån antaganden om hur takten delas upp mellan ackorden.

## Steg 4 — Skapa sångfilen

Skapa filen `songs/<Låttitel>.txt` med detta format:

```
<Låttitel>
BPM: <bpm>
Strumming: <mönster>
[Strumming <Label>: <mönster>]   ← lägg till fler rader om flera mönster

Spotify:<url>                    ← utelämna raden om ingen länk

Chord progression:
<Sektionsnamn>
| <ackord> | <ackord> | ... |

Lyrics:
[Vers/Refräng/etc]
         <ackord>              <ackord>
Textraden med ackord ovanför rätt stavelse
```

**Regler:**
- Filnamn = låttitel exakt som den skrivs (inklusive specialtecken som `'`)
- Tomrad mellan ackordföljden och Lyrics
- Sektionsetiketter i hakparenteser: `[Verse]`, `[Chorus]`, `[Bridge]`, `[Intro]`, `[Outro]`, `[Instrumental]`
- Ackord i lyrics ska stå ovanför rätt ord/stavelse med mellanslag för justering

## Steg 5 — Bygg om appen

Kör:
```
python build_songbook.py
```

Kontrollera att det inte blev några fel. Om `index.html` uppdaterades — berätta det för användaren.

## Steg 6 — Fråga om commit

Fråga om användaren vill committa och pusha till GitHub Pages. Om ja:
```
git add "songs/<Låttitel>.txt" index.html
git commit -m "Lägg till <Låttitel> av <Artist>"
git push
```

Avsluta commit-meddelandet med den attribution-rad som gäller för aktuell session.
