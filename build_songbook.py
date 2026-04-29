import html
import base64
import re
from pathlib import Path

SONG_DIR = Path(__file__).parent
SONGS_DIR = SONG_DIR / "songs"
OUTPUT_FILE = SONG_DIR / "songbook.html"

# Global chord color mapping - same chord always gets same color
CHORD_COLORS = {
    "C": "#FF6B6B",      # Red
    "C#": "#FF8E8E",     # Light Red
    "Db": "#FF8E8E",     # Light Red
    "D": "#4ECDC4",      # Teal
    "D#": "#7FE7E0",     # Light Teal
    "Eb": "#7FE7E0",     # Light Teal
    "E": "#FFD93D",      # Yellow
    "F": "#95E1D3",      # Mint
    "F#": "#B3F0DA",     # Light Mint
    "Gb": "#B3F0DA",     # Light Mint
    "G": "#A8D8FF",      # Light Blue
    "G#": "#C7E2FF",     # Lighter Blue
    "Ab": "#C7E2FF",     # Lighter Blue
    "A": "#FF6BA6",      # Pink
    "A#": "#FF94C2",     # Light Pink
    "Bb": "#FF94C2",     # Light Pink
    "B": "#D4A5FF",      # Purple
    # Variations with numbers
    "C7": "#FF6B6B",
    "Cm": "#E85555",
    "D7": "#4ECDC4",
    "Dm": "#2DA49A",
    "E7": "#FFD93D",
    "Em": "#D9B61F",
    "F7": "#95E1D3",
    "Fm": "#5FC4B8",
    "G7": "#A8D8FF",
    "Gm": "#6EB8FF",
    "A7": "#FF6BA6",
    "Am": "#D94A8A",
    "B7": "#D4A5FF",
    "Bm": "#B085E5",
    # Add more variations...
}

def get_chord_color(chord: str) -> str:
    """Get consistent color for a chord."""
    # Try exact match first
    if chord in CHORD_COLORS:
        return CHORD_COLORS[chord]
    
    # Try without slashes (for chords like Am/E)
    base_chord = chord.split("/")[0]
    if base_chord in CHORD_COLORS:
        return CHORD_COLORS[base_chord]
    
    # Default color if not found
    return "#8BD3FF"

DEFAULT_STRUMMING = {
    "Folsom Prison Blues": "Down Down Up Down Up Down",
    "Jambalaya (On the Bayou)": "Down Down Up Down Up Down",
    "Hey Joe": "Down Down (Root note)",
    "You are my Sunshine": "Down Down Up Down Up Down"
}


def load_image_as_base64(filename: str) -> str:
    """Load an image file and convert to base64 data URI."""
    try:
        image_path = SONGS_DIR / filename
        if image_path.exists():
            with open(image_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
                return b64
    except Exception:
        pass
    return ""


THEMES = {
    "Folsom Prison Blues": {
        "slug": "folsom",
        "accent": "#f8a25a",
        "bg1": "#08121f",
        "bg2": "#1d2b45",
        "label": "Prison Blues",
        "note": "Känn tågets rytm när du spelar.",
        "bgImage": load_image_as_base64("Folsom Prison Blues.png"),
        "bpm": 120
    },
    "Hey Joe": {
        "slug": "hey-joe",
        "accent": "#6fb8ff",
        "bg1": "#081a2d",
        "bg2": "#1a2645",
        "label": "Western Rock",
        "note": "Spela tight och drivande.",
        "bgImage": load_image_as_base64("Hey Joe.png"),
        "bpm": 96
    },
    "Jambalaya (On the Bayou)": {
        "slug": "jambalaya",
        "accent": "#ffaf6f",
        "bg1": "#16221d",
        "bg2": "#2f3a2d",
        "label": "Bayou Groove",
        "note": "Låt rytmen svänga med dig.",
        "bgImage": load_image_as_base64("Jambalaya (On the Bayou).png"),
        "bpm": 140
    },
    "You are my Sunshine": {
        "slug": "sunshine",
        "accent": "#FFD700",
        "bg1": "#1a1410",
        "bg2": "#3a2f1a",
        "label": "Classic Ballad",
        "note": "En klassisk väckarklocka för själen.",
        "bgImage": load_image_as_base64("You are my Sunshine.png"),
        "bpm": 80
    },
    "Patience": {
        "slug": "patience",
        "accent": "#e8a87c",
        "bg1": "#1a0e0a",
        "bg2": "#2e1c14",
        "label": "Rock Ballad",
        "note": "Ta det lugnt, känn varje ackord.",
        "bgImage": load_image_as_base64("Patience.png"),
        "bpm": 72
    },
    "default": {
        "slug": "default",
        "accent": "#8bd3ff",
        "bg1": "#081520",
        "bg2": "#132940",
        "label": "Song",
        "note": "Spela med känsla.",
        "bgImage": "none",
        "bpm": 120
    }
}


def render_strumming_visual(pattern: str) -> str:
    tokens = pattern.replace("(", "").replace(")", "").split()
    icons = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        lower = token.lower()
        next_token = tokens[i + 1].lower() if i + 1 < len(tokens) else ""
        if lower.startswith("down"):
            icons.append('<span class="strum-step strum-down">↓</span>')
        elif lower.startswith("up"):
            icons.append('<span class="strum-step strum-up">↑</span>')
        elif lower == "root" and next_token == "note":
            icons.append('<span class="strum-step strum-root">R</span>')
            i += 1
        elif "root" in lower:
            icons.append('<span class="strum-step strum-root">R</span>')
        else:
            icons.append(f'<span class="strum-step">{html.escape(token)}</span>')
        i += 1
    return "".join(icons)


def is_chord_line(line: str) -> bool:
    """Check if a line contains only chords and spacing."""
    stripped = line.strip()
    if not stripped or "[" in stripped or "]" in stripped:
        return False
    
    # Split by whitespace and check if tokens are chord-like
    tokens = stripped.split()
    if len(tokens) < 1:
        return False
    
    # Each token should look like a chord:
    # - Start with A-G (uppercase or lowercase)
    # - Followed only by valid chord characters (m, digits, b, #, /)
    valid_chord_starts = set("ABCDEFGabcdefg")
    valid_chord_chars = set("ABCDEFGabcdefgm0123456789b#/")
    
    for token in tokens:
        if not token:
            continue
        # Must start with A-G
        if token[0] not in valid_chord_starts:
            return False
        # All chars must be valid for chords
        if not all(c in valid_chord_chars for c in token):
            return False
        # Max length for a chord (e.g., "Cmaj7sus4#/E" is very long)
        if len(token) > 8:
            return False
    
    return True


def render_chord_line(line: str) -> str:
    """Render a line of chords with colors and no background/border."""
    # Replace each chord word with a span with its own color
    parts = []
    current_pos = 0
    
    for match in re.finditer(r'\S+', line):
        token = match.group()
        start = match.start()
        
        # Add spaces/tabs before the token
        if start > current_pos:
            parts.append(html.escape(line[current_pos:start]))
        
        # Add the chord as a span with individual color
        color = get_chord_color(token)
        parts.append(f'<span class="chord" style="color: {color};">{html.escape(token)}</span>')
        current_pos = match.end()
    
    # Add any remaining spaces at the end
    if current_pos < len(line):
        parts.append(html.escape(line[current_pos:]))
    
    return "".join(parts)


def render_lyrics_with_chords(lyrics_lines: list[str]) -> str:
    """Render lyrics with colored chord annotations."""
    result = []
    for line in lyrics_lines:
        # Check if this line is all chords
        if is_chord_line(line):
            result.append(render_chord_line(line))
        else:
            # Split by [CHORD] pattern, which also captures the chord names
            parts = re.split(r'\[([^\]]+)\]', line)
            new_line = ""
            for i, part in enumerate(parts):
                if i % 2 == 0:  # Text part - escape it
                    new_line += html.escape(part)
                else:  # Chord part - wrap in span with color
                    color = get_chord_color(part)
                    new_line += f'<span class="chord" style="color: {color};">{part}</span>'
            result.append(new_line)
    return "\n".join(result)


def parse_song(file_path: Path) -> dict:
    text = file_path.read_text(encoding="utf-8")
    lines = [line.rstrip() for line in text.splitlines()]

    title = None
    for line in lines:
        if line.strip():
            title = line.strip()
            break
    if title is None:
        title = file_path.stem

    prog_lines = []
    lyrics_lines = []
    in_prog = False
    in_lyrics = False

    for line in lines:
        low = line.strip().lower()
        if low.startswith("chord progression"):
            in_prog = True
            in_lyrics = False
            continue
        if low.startswith("lyrics"):
            in_lyrics = True
            in_prog = False
            continue

        if in_prog:
            if line.strip():
                prog_lines.append(line)
        elif in_lyrics:
            lyrics_lines.append(line)

    if not prog_lines:
        prog_lines = ["(Ingen chord progression hittad i filen)"]

    if not lyrics_lines:
        lyrics_lines = ["(Ingen lyrics hittad i filen)"]

    song_id = file_path.stem.replace(" ", "-").replace("(", "").replace(")", "").lower()
    return {
        "id": song_id,
        "title": title,
        "chord_progression": prog_lines,
        "lyrics": lyrics_lines,
        "strumming": DEFAULT_STRUMMING.get(title, "Down Down Up Down Up Down")
    }


def render_chord_progression(prog_lines: list[str]) -> str:
    sections = []
    current_label = None
    current_bars = []

    for line in prog_lines:
        stripped = line.strip()
        if not stripped:
            continue
        if '|' in stripped:
            for part in stripped.split('|'):
                chords = part.split()
                if chords:
                    current_bars.append(chords)
        else:
            if current_bars:
                sections.append((current_label, current_bars))
                current_bars = []
            current_label = stripped

    if current_bars:
        sections.append((current_label, current_bars))

    if not sections:
        return "<span>(Ingen chord progression)</span>"

    def make_chip(chords):
        if len(chords) == 1:
            color = get_chord_color(chords[0])
            inner = f'<span style="color:{color};">{html.escape(chords[0])}</span>'
            style = f'border-color:{color};background:color-mix(in srgb,{color} 15%,transparent);'
        else:
            inner = ' '.join(
                f'<span style="color:{get_chord_color(c)};">{html.escape(c)}</span>'
                for c in chords
            )
            style = 'border-color:rgba(255,255,255,0.25);background:rgba(255,255,255,0.07);'
        return f'<span class="prog-chord" style="{style}">{inner}</span>'

    parts = []
    for label, bars in sections:
        chips = "".join(make_chip(b) for b in bars)
        label_html = f'<div class="prog-label">{html.escape(label)}</div>' if label else ''
        parts.append(f'<div class="prog-section">{label_html}<div class="prog-grid">{chips}</div></div>')

    return "\n".join(parts)


def render_song(song: dict) -> str:
    theme = dict(THEMES.get(song["title"], THEMES["default"]))
    if (not theme['bgImage'] or theme['bgImage'] == 'none') and (SONGS_DIR / f"{song['title']}.png").exists():
        theme['bgImage'] = load_image_as_base64(f"{song['title']}.png")
    chords_html = render_chord_progression(song["chord_progression"])
    lyrics_html = render_lyrics_with_chords(song["lyrics"])
    strum_visual = render_strumming_visual(song["strumming"])
    bpm = theme.get("bpm", 120)
    if theme['bgImage'] and theme['bgImage'] != 'none':
        bg_image_css = f"background-image: url('data:image/png;base64,{theme['bgImage']}');"
    else:
        bg_image_css = f"background-image: linear-gradient(135deg, {theme['bg1']} 0%, {theme['bg2']} 100%);"
    return f"""
    <section id="{song['id']}" class="song-section theme-{theme['slug']}" aria-label="{html.escape(song['title'])}" style="--accent: {theme['accent']}; --bg1: {theme['bg1']}; --bg2: {theme['bg2']}; {bg_image_css}">
      <div class="song-overlay"></div>
      <div class="song-frame">
        <div class="song-header">
          <div>
            <p class="song-supertitle">{html.escape(theme['label'])}</p>
            <h1>{html.escape(song['title'])}</h1>
            <p class="song-note">{html.escape(theme['note'])}</p>
          </div>
        </div>
        <div class="song-grid">
          <aside class="song-meta-left">
            <div class="info-card info-card-small">
              <h2>Chord progression</h2>
              <div class="progression">{chords_html}</div>
            </div>
          </aside>
          <article class="song-main">
            <div class="lyrics-box">
              <pre><code>{lyrics_html}</code></pre>
            </div>
          </article>
          <aside class="song-meta-right">
            <div class="info-card info-card-small">
              <h2>Strumming pattern</h2>
              <div class="strumming">{html.escape(song['strumming'])}</div>
              <div class="strum-visual">{strum_visual}</div>
            </div>
            <div class="info-card info-card-small">
              <h2>Tempo</h2>
              <div class="tempo-display">{bpm} BPM</div>
            </div>
          </aside>
        </div>
      </div>
    </section>
    """


def build_html(songs: list[dict]) -> str:
    song_items = "\n".join(
        f"<a href='#{song['id']}' data-index='{i}'>{html.escape(song['title'])}</a>"
        for i, song in enumerate(songs)
    )
    first_title = html.escape(songs[0]['title']) if songs else "Songs"
    sections = "\n".join(render_song(song) for song in songs)
    return f"""
<!DOCTYPE html>
<html lang="sv">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Song Book</title>
  <style>
    :root {{
      color-scheme: dark;
      background: #090b10;
      color: #f4f4f8;
      font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
      line-height: 1.6;
      overflow-x: hidden;
    }}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; padding: 0; height: 100%; overflow: hidden; }}
    body {{ scroll-behavior: smooth; }}
    header {{ position: fixed; top: 0; left: 0; right: 0; background: rgba(12, 14, 22, 0.96); backdrop-filter: blur(14px); border-bottom: 1px solid rgba(255,255,255,.08); padding: 18px 24px; z-index: 20; }}
    .topbar {{ max-width: 1200px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; gap: 16px; }}
    .topbar h1 {{ margin: 0; font-size: 1.1rem; letter-spacing: 0.18em; text-transform: uppercase; color: #9fd7ff; }}
    .song-picker {{ position: relative; }}
    .song-picker-btn {{ display: flex; align-items: center; gap: 8px; color: #f4f4f8; font-size: .95rem; font-weight: 500; padding: 10px 16px; border-radius: 999px; background: rgba(255,255,255,.06); border: none; cursor: pointer; box-shadow: inset 0 0 0 1px rgba(255,255,255,.1); transition: background .2s; }}
    .song-picker-btn:hover, .song-picker-btn.open {{ background: rgba(255,255,255,.12); }}
    .song-picker-menu {{ position: absolute; top: calc(100% + 10px); left: 50%; transform: translateX(-50%) translateY(-6px); background: rgba(12,14,22,0.97); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,.1); border-radius: 16px; padding: 10px; display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 6px; min-width: 320px; opacity: 0; visibility: hidden; transition: opacity .2s ease, transform .2s ease, visibility .2s; z-index: 100; }}
    .song-picker-menu.open {{ opacity: 1; visibility: visible; transform: translateX(-50%) translateY(0); }}
    .song-picker-menu a {{ color: #f4f4f8; text-decoration: none; font-size: .9rem; padding: 9px 14px; border-radius: 10px; background: rgba(255,255,255,.04); transition: background .15s; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
    .song-picker-menu a:hover {{ background: rgba(255,255,255,.1); }}
    .song-picker-menu a.active {{ background: rgba(159,215,255,.15); color: #9fd7ff; }}
    main {{ position: relative; width: 100%; height: calc(100vh - 90px); margin-top: 90px; overflow: hidden; }}
    .song-section {{ position: absolute; inset: 0; opacity: 0; pointer-events: none; display: grid; align-items: stretch; justify-items: center; padding: 32px 24px 42px; transition: opacity .45s ease, transform .45s ease; transform: translateY(35px); background-size: cover; background-position: center; background-repeat: no-repeat; background-attachment: fixed; overflow: hidden; }}
    .song-section.active {{ opacity: 1; pointer-events: auto; transform: translateY(0); }}
    .song-section::before {{ content: ""; position: absolute; inset: 0; background: rgba(0, 0, 0, 0.4); opacity: 0.6; z-index: 0; }}
    .song-section::after {{ content: ""; position: absolute; inset: 0; background: linear-gradient(135deg, rgba(8,18,31,0.68), rgba(29,43,69,0.68)); z-index: 1; pointer-events: none; }}
    .song-overlay {{ position: absolute; inset: 0; background: radial-gradient(circle at top right, rgba(255,255,255,.08), transparent 28%), radial-gradient(circle at bottom left, rgba(255,255,255,.04), transparent 30%); pointer-events: none; z-index: 2; }}
    .song-frame {{ position: relative; width: min(1180px, 100%); max-height: 100%; height: 100%; display: grid; grid-template-rows: auto 1fr; gap: 24px; z-index: 3; }}
    .song-header {{ display: flex; flex-wrap: wrap; justify-content: space-between; gap: 18px; align-items: start; margin-bottom: 8px; }}
    .topbar-actions {{ display: flex; align-items: center; gap: 20px; order: -1; }}
    .song-button.song-toggle-button {{ background: rgba(255,255,255,.04); color: #c8d9e8; border: 1px solid rgba(255,255,255,.1); padding: 8px 14px; font-size: 0.85rem; font-weight: 500; transition: all .25s ease; }}
    .song-button.song-toggle-button:hover {{ background: rgba(255,255,255,.08); border-color: rgba(255,255,255,.2); color: #e8f0f8; }}
    .song-supertitle {{ margin: 0 0 8px; color: var(--accent); text-transform: uppercase; letter-spacing: 0.22em; font-size: 0.9rem; }}
    .song-note {{ margin: 10px 0 0; color: rgba(244,244,248,.72); max-width: 640px; }}
    .song-header h1 {{ margin: 0; font-size: clamp(2rem, 4vw, 3rem); line-height: 1.05; }}
    .song-button {{ padding: 12px 18px; background: var(--accent); color: #09101d; border-radius: 999px; text-decoration: none; font-weight: 700; box-shadow: 0 18px 45px rgba(0,0,0,.18); }}
    .song-grid {{ display: grid; gap: 16px; grid-template-columns: 0.45fr 1.8fr 0.45fr; align-items: stretch; height: 100%; min-height: 0; }}
    .song-main {{ background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.12); border-radius: 34px; padding: 34px; box-shadow: 0 32px 80px rgba(0,0,0,.18); backdrop-filter: blur(14px); display: flex; flex-direction: column; min-height: 0; height: 100%; max-height: 100%; overflow: hidden; }}
    .lyrics-box {{ flex: 1 1 0; min-height: 0; overflow-y: auto; padding-right: 8px; scrollbar-width: thin; scrollbar-color: rgba(255,255,255,.5) transparent; overscroll-behavior: contain; }}
    .lyrics-box pre {{ margin: 0; white-space: pre-wrap; word-break: break-word; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 1.02rem; line-height: 1.78; color: #f4f4f8; }}
    .song-meta-left, .song-meta-right {{ position: sticky; top: 120px; align-self: start; }}
    .chord {{ font-weight: 700; padding: 2px 0; margin: 0 2px; }}
    .song-button.song-toggle-button.active {{ background: rgba(139, 211, 255, .2); color: #8bd3ff; border-color: rgba(139, 211, 255, .4); }}
    .song-meta-left {{ position: relative; display: grid; gap: 12px; }}
    .song-meta-right {{ position: relative; display: grid; gap: 12px; }}
    .info-card {{ background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.12); border-radius: 20px; padding: 20px; box-shadow: inset 0 0 0 1px rgba(255,255,255,.05), 0 20px 60px rgba(0,0,0,.2); backdrop-filter: blur(10px); position: relative; }}
    .info-card-small {{ background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.12); border-radius: 16px; padding: 14px; box-shadow: inset 0 0 0 1px rgba(255,255,255,.05), 0 8px 20px rgba(0,0,0,.15); backdrop-filter: blur(10px); position: relative; }}
    .info-card h2 {{ margin: 0 0 12px; font-size: 0.95rem; color: #e6f1ff; font-weight: 600; }}
    .info-card-small h2 {{ margin: 0 0 8px; font-size: 0.85rem; color: #e6f1ff; font-weight: 600; }}
    .prog-section {{ margin-bottom: 10px; }}
    .prog-section:last-child {{ margin-bottom: 0; }}
    .prog-label {{ font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; color: rgba(255,255,255,0.4); margin-bottom: 5px; }}
    .prog-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; }}
    .prog-chord {{ font-weight: 700; font-size: 0.9rem; padding: 6px 4px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.18); background: rgba(255,255,255,0.06); text-align: center; letter-spacing: 0.02em; }}
    .strumming {{ font-size: 0.9rem; background: rgba(255,255,255,.08); padding: 10px 12px; border-radius: 10px; margin-bottom: 10px; color: #f7fbff; }}
    .strum-visual {{ display: flex; gap: 6px; justify-content: center; flex-wrap: wrap; }}
    .strum-step {{ display: inline-flex; width: 40px; height: 40px; align-items: center; justify-content: center; border-radius: 14px; font-size: 1rem; font-weight: 700; background: rgba(255,255,255,.1); color: #f4f4f8; box-shadow: inset 0 -1px 0 rgba(0,0,0,.2); }}
    .strum-down {{ background: rgba(60, 130, 255, .22); }}
    .strum-up {{ background: rgba(116, 188, 255, .18); }}
    .strum-root {{ background: rgba(255, 206, 86, .24); color: #fff3b2; }}
    .tempo-display {{ font-size: 1.4rem; font-weight: 700; color: var(--accent); text-align: center; padding: 8px; }}
    .song-footer {{ display: flex; justify-content: space-between; gap: 14px; flex-wrap: wrap; margin-top: 8px; color: #b3c4d5; }}
    .song-footer span {{ font-size: 0.95rem; }}
    @keyframes floatNote {{ 0%, 100% {{ transform: translateY(0px) rotate(0deg); opacity: 0.1; }} 50% {{ transform: translateY(-30px) rotate(180deg); opacity: 0.2; }} }}
  </style>
</head>
<body>
  <header id="top">
    <div class="topbar">
      <h1>Song Book</h1>
      <div class="song-picker">
        <button id="song-picker-btn" class="song-picker-btn" type="button">
          <span id="song-picker-label">{first_title}</span>
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M2 4l4 4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </button>
        <div id="song-picker-menu" class="song-picker-menu">
          {song_items}
        </div>
      </div>
      <button id="auto-scroll-toggle" class="song-button song-toggle-button" type="button">Auto-scroll av</button>
    </div>
  </header>
  <main>
    {sections}
  </main>
  <script>
    const sections = Array.from(document.querySelectorAll('.song-section'));
    let currentIndex = 0;
    let isLocked = false;
    let autoScrollEnabled = false;
    let autoScrollAnimationFrame = null;
    const autoScrollSpeed = 0.04;
    let autoScrollAccum = 0;
    const autoScrollToggle = document.getElementById('auto-scroll-toggle');

    function getLyricsBox(section) {{
      return section.querySelector('.lyrics-box');
    }}

    function setActive(index) {{
      if (index < 0 || index >= sections.length) return;
      sections[currentIndex].classList.remove('active');
      currentIndex = index;
      sections[currentIndex].classList.add('active');
      const lyricsBox = getLyricsBox(sections[currentIndex]);
      if (lyricsBox) lyricsBox.scrollTop = 0;
      if (autoScrollEnabled) startAutoScroll();
      updatePickerLabel(index);
    }}

    function startAutoScroll() {{
      stopAutoScroll();
      autoScrollAccum = 0;
      const lyricsBox = getLyricsBox(sections[currentIndex]);
      if (!lyricsBox) return;

      const performScroll = () => {{
        const box = getLyricsBox(sections[currentIndex]);
        if (!box || !autoScrollEnabled) {{
          stopAutoScroll();
          return;
        }}

        if (box.scrollTop + box.clientHeight >= box.scrollHeight - 2) {{
          stopAutoScroll();
          autoScrollEnabled = false;
          autoScrollToggle.textContent = 'Auto-scroll av';
          autoScrollToggle.classList.remove('active');
          return;
        }}

        autoScrollAccum += autoScrollSpeed;
        if (autoScrollAccum >= 1) {{
          const delta = Math.floor(autoScrollAccum);
          box.scrollTop += delta;
          autoScrollAccum -= delta;
        }}
        autoScrollAnimationFrame = requestAnimationFrame(performScroll);
      }};

      autoScrollAnimationFrame = requestAnimationFrame(performScroll);
    }}

    function stopAutoScroll() {{
      if (autoScrollAnimationFrame) {{
        cancelAnimationFrame(autoScrollAnimationFrame);
        autoScrollAnimationFrame = null;
      }}
    }}

    function toggleAutoScroll() {{
      autoScrollEnabled = !autoScrollEnabled;
      autoScrollToggle.textContent = autoScrollEnabled ? 'Auto-scroll på' : 'Auto-scroll av';
      autoScrollToggle.classList.toggle('active', autoScrollEnabled);
      if (autoScrollEnabled) {{
        const lyricsBox = getLyricsBox(sections[currentIndex]);
        if (lyricsBox) lyricsBox.scrollTop = 0;
        startAutoScroll();
      }} else {{
        stopAutoScroll();
      }}
    }}

    function nextSection() {{
      if (isLocked || currentIndex >= sections.length - 1) return;
      isLocked = true;
      stopAutoScroll();
      setActive(currentIndex + 1);
      window.setTimeout(() => isLocked = false, 600);
    }}

    function prevSection() {{
      if (isLocked || currentIndex <= 0) return;
      isLocked = true;
      stopAutoScroll();
      setActive(currentIndex - 1);
      window.setTimeout(() => isLocked = false, 600);
    }}

    document.addEventListener('wheel', event => {{
      if (event.target.closest('.lyrics-box')) return;
      if (event.deltaY > 10) nextSection();
      else if (event.deltaY < -10) prevSection();
    }}, {{ passive: true }});

    document.addEventListener('keydown', event => {{
      if (event.key === 'ArrowDown' || event.key === 'PageDown') nextSection();
      if (event.key === 'ArrowUp' || event.key === 'PageUp') prevSection();
    }});

    const songPickerBtn = document.getElementById('song-picker-btn');
    const songPickerMenu = document.getElementById('song-picker-menu');
    const songPickerLabel = document.getElementById('song-picker-label');
    const songPickerLinks = Array.from(document.querySelectorAll('.song-picker-menu a'));

    function updatePickerLabel(index) {{
      if (songPickerLabel && songPickerLinks[index]) {{
        songPickerLabel.textContent = songPickerLinks[index].textContent;
      }}
      songPickerLinks.forEach((l, i) => l.classList.toggle('active', i === index));
    }}

    songPickerBtn.addEventListener('click', e => {{
      e.stopPropagation();
      songPickerMenu.classList.toggle('open');
      songPickerBtn.classList.toggle('open');
    }});

    document.addEventListener('click', () => {{
      songPickerMenu.classList.remove('open');
      songPickerBtn.classList.remove('open');
    }});

    songPickerLinks.forEach((link, index) => {{
      link.addEventListener('click', event => {{
        event.preventDefault();
        stopAutoScroll();
        setActive(index);
        songPickerMenu.classList.remove('open');
        songPickerBtn.classList.remove('open');
      }});
    }});

    if (autoScrollToggle) {{
      autoScrollToggle.addEventListener('click', toggleAutoScroll);
    }}

    setActive(0);
    updatePickerLabel(0);
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    txt_files = sorted(SONGS_DIR.glob("*.txt"), key=lambda p: p.name.lower())
    songs = [parse_song(file_path) for file_path in txt_files]
    output_html = build_html(songs)
    OUTPUT_FILE.write_text(output_html, encoding="utf-8")
    print(f"Genererad {OUTPUT_FILE}")
