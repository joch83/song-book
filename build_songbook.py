import html
import base64
import re
from pathlib import Path
from urllib.parse import quote

SONG_DIR = Path(__file__).parent
SONGS_DIR = SONG_DIR / "songs"
OUTPUT_FILE = SONG_DIR / "index.html"

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
    if chord in CHORD_COLORS:
        return CHORD_COLORS[chord]
    base_chord = chord.split("/")[0]
    if base_chord in CHORD_COLORS:
        return CHORD_COLORS[base_chord]
    # Strip modifiers (sus2, sus4, maj7, add9, etc.) and try root note
    match = re.match(r'^([A-Ga-g][#b]?)', base_chord)
    if match:
        root = match.group(1)[0].upper() + match.group(1)[1:]
        if root in CHORD_COLORS:
            return CHORD_COLORS[root]
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
    tokens = pattern.split()
    icons = []
    for token in tokens:
        t = token.upper()
        if t == 'D':
            icons.append('<span class="strum-step strum-down" title="Down stroke">↓</span>')
        elif t == 'U':
            icons.append('<span class="strum-step strum-up" title="Up stroke">↑</span>')
        elif t == 'R':
            icons.append('<span class="strum-step strum-root" title="Root note (down)"><span class="strum-root-arrow">↓</span></span>')
        elif t == 'A':
            icons.append('<span class="strum-step strum-alt" title="Alt root note (down)"><span class="strum-root-arrow">↓</span></span>')
        elif t == '-':
            icons.append('<span class="strum-step strum-mute" title="Mute / pause"></span>')
        else:
            icons.append('<span class="strum-step strum-down" title="Down stroke">↓</span>')
    while len(icons) < 8:
        icons.append('<span class="strum-step strum-empty"></span>')
    return f'<div class="strum-visual">{"".join(icons)}</div>'


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
    valid_chord_chars = set("ABCDEFGabcdefgm0123456789b#/suj")
    
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
        if len(token) > 10:
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
    file_bpm = None
    file_strumming = None
    strumming_patterns = []
    spotify_url = None

    for line in lines:
        low = line.strip().lower()
        if low.startswith("bpm:"):
            val = line.strip()[4:].strip()
            if val.isdigit():
                file_bpm = int(val)
            continue
        if low.startswith("strumming"):
            rest = line.strip()[9:].strip()
            if rest.startswith(":"):
                pattern = rest[1:].strip()
                file_strumming = pattern
                strumming_patterns.append({"label": None, "pattern": pattern})
            else:
                colon = rest.find(":")
                if colon != -1:
                    label = rest[:colon].strip()
                    pattern = rest[colon+1:].strip()
                    if not file_strumming:
                        file_strumming = pattern
                    strumming_patterns.append({"label": label, "pattern": pattern})
            continue
        if low.startswith("spotify:"):
            spotify_url = line.strip()[8:].strip()
            continue
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

    pdf_files = sorted(SONGS_DIR.glob(f"{title}*.pdf"))

    song_id = file_path.stem.replace(" ", "-").replace("(", "").replace(")", "").lower()
    return {
        "id": song_id,
        "title": title,
        "chord_progression": prog_lines,
        "lyrics": lyrics_lines,
        "file_bpm": file_bpm,
        "file_strumming": file_strumming,
        "strumming": file_strumming or DEFAULT_STRUMMING.get(title, "Down Down Up Down Up Down"),
        "strumming_patterns": strumming_patterns or [{"label": None, "pattern": file_strumming or DEFAULT_STRUMMING.get(title, "Down Down Up Down Up Down")}],
        "pdf_tabs": [p.name for p in pdf_files],
        "spotify_url": spotify_url,
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
            style = 'border-color:rgba(255,255,255,0.25);background:rgba(255,255,255,0.07);white-space:nowrap;font-size:0.88rem;'
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
    strum_parts = []
    for sp in song["strumming_patterns"]:
        if sp["label"]:
            color = get_chord_color(sp["label"])
            label_html = f'<div class="strum-label" style="color:{color};">{html.escape(sp["label"])}</div>'
        else:
            label_html = ''
        strum_parts.append(label_html + render_strumming_visual(sp["pattern"]))
    strum_visual = "".join(strum_parts)
    bpm = song.get("file_bpm") or theme.get("bpm", 100)

    spotify_html = ""
    if song.get("spotify_url"):
        embed_url = song["spotify_url"].replace("open.spotify.com/", "open.spotify.com/embed/")
        spotify_html = f'''
            <div class="spotify-card">
              <iframe src="{embed_url}?utm_source=generator&theme=0" width="100%" height="80" frameborder="0" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
            </div>'''

    pdf_buttons_html = ""
    pdf_overlays_html = ""
    pdf_inner_buttons = ""
    for pdf_name in song.get("pdf_tabs", []):
        raw_label = pdf_name[len(song['title']):].strip().removesuffix('.pdf').strip()
        label = raw_label if raw_label else "Tab"
        for keyword in ("Intro", "Solo", "Riff"):
            if keyword.lower() in label.lower():
                label = keyword
                break
        pdf_id = f"pdf-{song['id']}-{re.sub(r'[^a-z0-9]', '-', pdf_name.lower())}"
        pdf_path = quote(f"songs/{pdf_name}")
        pdf_inner_buttons += f'<button class="pdf-open-btn" data-pdf-id="{pdf_id}">{html.escape(label)}</button>\n              '
        pdf_overlays_html += f'''
      <div class="pdf-overlay" id="{pdf_id}" style="display:none">
        <div class="pdf-modal">
          <button class="pdf-close-btn" data-pdf-id="{pdf_id}">✕</button>
          <div class="pdf-viewport">
            <embed src="{pdf_path}#zoom=100" type="application/pdf" width="100%" height="100%">
          </div>
        </div>
      </div>'''
    if pdf_inner_buttons:
        pdf_buttons_html = f'''
            <div class="info-card info-card-small">
              <h2>Intro / Solo / Riff</h2>
              <div class="pdf-btn-group">
              {pdf_inner_buttons}</div>
            </div>'''
    if theme['bgImage'] and theme['bgImage'] != 'none':
        bg_image_css = f"background-image: url('data:image/png;base64,{theme['bgImage']}');"
    else:
        bg_image_css = f"background-image: linear-gradient(135deg, {theme['bg1']} 0%, {theme['bg2']} 100%);"
    return f"""
    <section id="{song['id']}" class="song-section theme-{theme['slug']}" aria-label="{html.escape(song['title'])}" style="--accent: {theme['accent']}; --bg1: {theme['bg1']}; --bg2: {theme['bg2']}; {bg_image_css}">
      <div class="song-overlay"></div>
      <div class="song-title-block">
        <h1>{html.escape(song['title'])}</h1>
      </div>
      <div class="song-frame">
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
              {strum_visual}
            </div>
            <div class="info-card info-card-small">
              <button class="tempo-display" data-bpm="{bpm}" type="button">{bpm} <span class="tempo-unit">BPM</span></button>
            </div>
            {spotify_html}
            {pdf_buttons_html}
          </aside>
        </div>
      </div>
      {pdf_overlays_html}
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
    main {{ width: 100%; height: calc(100vh - 90px); margin-top: 90px; }}
    .song-section {{ position: relative; display: none; align-items: stretch; justify-items: center; padding: 4px 24px 24px; background-size: cover; background-position: center; background-repeat: no-repeat; background-attachment: fixed; overflow: hidden; height: 100%; }}
    .song-section.active {{ display: grid; animation: fadeIn .3s ease; }}
    @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    .song-section::before {{ content: ""; position: absolute; inset: 0; background: rgba(0, 0, 0, 0.4); opacity: 0.6; z-index: 0; }}
    .song-section::after {{ content: ""; position: absolute; inset: 0; background: linear-gradient(135deg, rgba(8,18,31,0.68), rgba(29,43,69,0.68)); z-index: 1; pointer-events: none; }}
    .song-overlay {{ position: absolute; inset: 0; background: radial-gradient(circle at top right, rgba(255,255,255,.08), transparent 28%), radial-gradient(circle at bottom left, rgba(255,255,255,.04), transparent 30%); pointer-events: none; z-index: 2; }}
    .song-frame {{ position: relative; width: min(1360px, 100%); height: 100%; z-index: 3; }}
    .song-button.song-toggle-button {{ background: rgba(255,255,255,.04); color: #c8d9e8; border: 1px solid rgba(255,255,255,.1); padding: 8px 14px; font-size: 0.85rem; font-weight: 500; transition: all .25s ease; }}
    .song-button.song-toggle-button:hover {{ background: rgba(255,255,255,.08); border-color: rgba(255,255,255,.2); color: #e8f0f8; }}
    .song-title-block {{ position: absolute; top: 4px; left: 24px; z-index: 4; max-width: 380px; }}
    .song-supertitle {{ margin: 0 0 2px; color: var(--accent); text-transform: uppercase; letter-spacing: 0.22em; font-size: 0.8rem; }}
    .song-title-block h1 {{ margin: 0; font-size: clamp(1.4rem, 2vw, 2.2rem); line-height: 1.4; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
    .song-note {{ margin: 4px 0 0; color: rgba(244,244,248,.6); font-size: 0.85rem; }}
    .song-button {{ padding: 12px 18px; background: var(--accent); color: #09101d; border-radius: 999px; text-decoration: none; font-weight: 700; box-shadow: 0 18px 45px rgba(0,0,0,.18); }}
    .song-grid {{ display: grid; gap: 16px; grid-template-columns: 242px 1fr 210px; height: 100%; min-height: 0; align-items: stretch; }}
    .song-main {{ background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.12); border-radius: 34px; padding: 34px; box-shadow: 0 32px 80px rgba(0,0,0,.18); backdrop-filter: blur(14px); display: flex; flex-direction: column; min-height: 0; min-width: 0; height: 100%; max-height: 100%; overflow: hidden; margin-left: -12px; margin-right: -12px; }}
    .lyrics-box {{ flex: 1 1 0; min-height: 0; overflow-y: auto; padding-right: 8px; scrollbar-width: thin; scrollbar-color: rgba(255,255,255,.5) transparent; overscroll-behavior: contain; }}
    .lyrics-box pre {{ margin: 0; white-space: pre-wrap; word-break: break-word; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 1.02rem; line-height: 1.78; color: #f4f4f8; }}
    .song-meta-left {{ position: relative; display: grid; gap: 12px; min-width: 0; align-self: start; margin-top: 110px; }}
    .song-meta-right {{ position: relative; display: grid; gap: 12px; align-self: start; }}
    .chord {{ font-weight: 700; padding: 2px 0; margin: 0 2px; }}
    .song-button.song-toggle-button.active {{ background: rgba(139, 211, 255, .2); color: #8bd3ff; border-color: rgba(139, 211, 255, .4); }}
    .song-meta-left {{ position: relative; display: grid; gap: 12px; min-width: 0; }}
    .song-meta-right {{ position: relative; display: grid; gap: 12px; }}
    .info-card {{ background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.12); border-radius: 20px; padding: 20px; box-shadow: inset 0 0 0 1px rgba(255,255,255,.05), 0 20px 60px rgba(0,0,0,.2); backdrop-filter: blur(10px); position: relative; }}
    .info-card-small {{ background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.12); border-radius: 16px; padding: 14px; box-shadow: inset 0 0 0 1px rgba(255,255,255,.05), 0 8px 20px rgba(0,0,0,.15); backdrop-filter: blur(10px); position: relative; }}
    .info-card h2 {{ margin: 0 0 12px; font-size: 0.95rem; color: #e6f1ff; font-weight: 600; }}
    .info-card-small h2 {{ margin: 0 0 8px; font-size: 0.85rem; color: #e6f1ff; font-weight: 600; }}
    .prog-section {{ margin-bottom: 10px; }}
    .prog-section:last-child {{ margin-bottom: 0; }}
    .prog-label {{ font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; color: rgba(255,255,255,0.4); margin-bottom: 5px; }}
    .prog-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; }}
    .prog-chord {{ font-weight: 700; font-size: 1.0rem; padding: 8px 6px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.18); background: rgba(255,255,255,0.06); text-align: center; letter-spacing: 0.02em; }}
    .strumming {{ font-size: 0.9rem; background: rgba(255,255,255,.08); padding: 10px 12px; border-radius: 10px; margin-bottom: 10px; color: #f7fbff; }}
    .strum-label {{ font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; margin: 6px 0 3px; }}
    .strum-visual {{ display: grid; grid-template-columns: repeat(8, 1fr); gap: 5px; }}
    .strum-step {{ display: inline-flex; width: 100%; aspect-ratio: 1; align-items: center; justify-content: center; border-radius: 10px; font-size: 1rem; font-weight: 700; background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.08); color: #f4f4f8; }}
    .strum-empty {{ background: transparent; border-color: transparent; pointer-events: none; }}
    .strum-down {{ background: rgba(60, 130, 255, .25); border-color: rgba(60,130,255,.3); }}
    .strum-up {{ background: rgba(116, 188, 255, .2); border-color: rgba(116,188,255,.25); }}
    .strum-root {{ background: rgba(255, 206, 86, .22); border-color: rgba(255,206,86,.3); color: #fff3b2; }}
    .strum-alt {{ background: rgba(255, 150, 50, .25); border-color: rgba(255,150,50,.35); color: #ffd4a0; }}
    .strum-root-arrow {{ font-size: 0.7rem; }}
    .strum-mute {{ background: rgba(255,255,255,.03); border-color: rgba(255,255,255,.06); }}
    .tempo-display {{ font-size: 2.6rem; font-weight: 700; color: var(--accent); text-align: center; padding: 10px 8px; background: none; border: 1px solid transparent; border-radius: 12px; cursor: pointer; width: 100%; transition: border-color .2s, background .2s; }}
    .tempo-display:hover {{ background: rgba(255,255,255,.06); border-color: rgba(255,255,255,.12); }}
    .tempo-display.active {{ background: rgba(255,255,255,.06); border-color: var(--accent); }}
    .tempo-unit {{ font-size: 0.85rem; font-weight: 500; opacity: 0.7; }}
    .pdf-btn-group {{ display: flex; flex-direction: column; gap: 8px; }}
    .pdf-open-btn {{ width: 100%; padding: 8px 10px; background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.18); border-radius: 10px; color: #e6f1ff; font-size: 0.9rem; font-weight: 600; cursor: pointer; transition: background .2s, border-color .2s; }}
    .pdf-open-btn:hover {{ background: rgba(255,255,255,.14); border-color: rgba(255,255,255,.3); }}
    .pdf-overlay {{ position: absolute; inset: 0; z-index: 20; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,.7); backdrop-filter: blur(6px); padding: 20px; }}
    .pdf-modal {{ position: relative; width: 100%; height: 100%; max-width: 900px; max-height: calc(100% - 40px); background: #1a1a2e; border-radius: 16px; overflow: hidden; border: 1px solid rgba(255,255,255,.15); }}
    .pdf-viewport {{ position: absolute; inset: 0; overflow: hidden; }}
    .pdf-viewport embed {{ position: absolute; top: -265px; left: 0; width: 100%; height: calc(100% + 265px); }}
    .pdf-close-btn {{ position: absolute; top: 10px; right: 12px; z-index: 21; background: rgba(0,0,0,.6); border: 1px solid rgba(255,255,255,.2); border-radius: 8px; color: #fff; font-size: 1rem; width: 32px; height: 32px; cursor: pointer; display: flex; align-items: center; justify-content: center; }}
    .spotify-card {{ overflow: hidden; border-radius: 12px; height: 80px; }}
    .spotify-card iframe {{ display: block; width: 100%; height: 80px; border-radius: 12px; }}
    @keyframes metroPulse {{ 0% {{ transform: scale(1); opacity: 1; }} 8% {{ transform: scale(1.18); opacity: 1; }} 30% {{ transform: scale(1); opacity: 1; }} 100% {{ transform: scale(1); opacity: 1; }} }}
    .tempo-display.beat {{ animation: metroPulse calc(var(--beat-ms) * 1ms) linear; }}
    .song-footer {{ display: flex; justify-content: space-between; gap: 14px; flex-wrap: wrap; margin-top: 8px; color: #b3c4d5; }}
    .song-footer span {{ font-size: 0.95rem; }}
    @keyframes floatNote {{ 0%, 100% {{ transform: translateY(0px) rotate(0deg); opacity: 0.1; }} 50% {{ transform: translateY(-30px) rotate(180deg); opacity: 0.2; }} }}
    @media (max-width: 768px) {{
      html, body {{ overflow-y: auto; height: auto; }}
      header {{ padding: 12px 16px; }}
      .topbar h1 {{ font-size: 0.9rem; }}
      .song-picker-btn {{ font-size: 0.85rem; padding: 8px 12px; }}
      #auto-scroll-toggle {{ font-size: 0.8rem; padding: 8px 10px; }}
      .song-picker-menu {{
        position: fixed;
        top: 74px;
        left: 0;
        right: 0;
        width: 100%;
        min-width: 0;
        border-radius: 0 0 16px 16px;
        grid-template-columns: 1fr;
        max-height: calc(100vh - 74px);
        overflow-y: auto;
        transform: translateY(-6px);
      }}
      .song-picker-menu.open {{ transform: translateY(0); }}
      main {{ height: auto; margin-top: 74px; }}
      .song-section {{
        display: none;
        height: auto;
        overflow: visible;
        padding: 12px 12px 48px;
        background-attachment: scroll;
      }}
      .song-section.active {{ display: block; animation: fadeIn .3s ease; }}
      .song-title-block {{
        position: relative;
        top: auto;
        left: auto;
        max-width: 100%;
        margin-bottom: 14px;
        padding-top: 6px;
      }}
      .song-title-block h1 {{ white-space: normal; font-size: clamp(1.3rem, 6vw, 1.8rem); line-height: 1.3; }}
      .song-frame {{ height: auto; }}
      .song-grid {{ grid-template-columns: 1fr; height: auto; gap: 12px; }}
      .song-main {{
        order: -1;
        height: auto;
        max-height: none;
        overflow: visible;
        margin: 0;
        padding: 20px;
      }}
      .lyrics-box {{ flex: none; overflow-y: visible; min-height: 0; height: auto; }}
      .song-meta-left {{ margin-top: 0; }}
      .strum-step {{ font-size: 0.9rem; border-radius: 8px; }}
      .prog-chord {{ font-size: 0.9rem; padding: 6px 4px; }}
      .tempo-display {{ font-size: 2rem; }}
    }}
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
    const songSections = Array.from(document.querySelectorAll('.song-section'));
    let currentIndex = 0;
    let autoScrollEnabled = false;
    let autoScrollAnimationFrame = null;
    const autoScrollSpeed = 0.03;
    let autoScrollAccum = 0;
    const autoScrollToggle = document.getElementById('auto-scroll-toggle');

    function getLyricsBox() {{
      return songSections[currentIndex]?.querySelector('.lyrics-box') || null;
    }}

    function setActive(index) {{
      if (index < 0 || index >= songSections.length) return;
      songSections[currentIndex].classList.remove('active');
      currentIndex = index;
      songSections[currentIndex].classList.add('active');
      const lyricsBox = getLyricsBox();
      if (lyricsBox) lyricsBox.scrollTop = 0;
      if (autoScrollEnabled) startAutoScroll(); else stopAutoScroll();
      updatePickerLabel(index);
      localStorage.setItem('songbook-last-index', index);
    }}

    function startAutoScroll() {{
      stopAutoScroll();
      autoScrollAccum = 0;
      const performScroll = () => {{
        const box = getLyricsBox();
        if (!box || !autoScrollEnabled) {{ stopAutoScroll(); return; }}
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
        const lyricsBox = getLyricsBox();
        if (lyricsBox) lyricsBox.scrollTop = 0;
        startAutoScroll();
      }} else {{
        stopAutoScroll();
      }}
    }}

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

    let metroInterval = null;

    function stopMetronome() {{
      if (metroInterval) {{ clearInterval(metroInterval); metroInterval = null; }}
      document.querySelectorAll('.tempo-display.active').forEach(b => {{
        b.classList.remove('active');
        b.style.removeProperty('--beat-ms');
      }});
    }}

    function startMetronome(btn) {{
      stopMetronome();
      const bpm = parseInt(btn.dataset.bpm, 10);
      const ms = Math.round(60000 / bpm);
      btn.style.setProperty('--beat-ms', ms);
      btn.classList.add('active');
      const pulse = () => {{
        btn.classList.remove('beat');
        void btn.offsetWidth;
        btn.classList.add('beat');
      }};
      pulse();
      metroInterval = setInterval(pulse, ms);
    }}

    document.querySelectorAll('.tempo-display').forEach(btn => {{
      btn.addEventListener('click', e => {{
        e.stopPropagation();
        if (btn.classList.contains('active')) {{
          stopMetronome();
        }} else {{
          startMetronome(btn);
        }}
      }});
    }});

    const savedIndex = parseInt(localStorage.getItem('songbook-last-index') || '0', 10);
    setActive(Math.min(savedIndex, songSections.length - 1));
    updatePickerLabel(currentIndex);

    document.querySelectorAll('.pdf-open-btn').forEach(btn => {{
      btn.addEventListener('click', () => {{
        const overlay = document.getElementById(btn.dataset.pdfId);
        if (overlay) overlay.style.display = 'flex';
      }});
    }});

    document.querySelectorAll('.pdf-close-btn').forEach(btn => {{
      btn.addEventListener('click', () => {{
        const overlay = document.getElementById(btn.dataset.pdfId);
        if (overlay) overlay.style.display = 'none';
      }});
    }});

    document.querySelectorAll('.pdf-overlay').forEach(overlay => {{
      overlay.addEventListener('click', e => {{
        if (e.target === overlay) overlay.style.display = 'none';
      }});
    }});

    document.addEventListener('keydown', e => {{
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
      if (e.key === 'ArrowRight') {{
        stopAutoScroll(); autoScrollEnabled = false;
        autoScrollToggle.textContent = 'Auto-scroll av';
        autoScrollToggle.classList.remove('active');
        setActive(currentIndex + 1);
      }} else if (e.key === 'ArrowLeft') {{
        stopAutoScroll(); autoScrollEnabled = false;
        autoScrollToggle.textContent = 'Auto-scroll av';
        autoScrollToggle.classList.remove('active');
        setActive(currentIndex - 1);
      }} else if (e.key === 'm' || e.key === 'M') {{
        const btn = songSections[currentIndex]?.querySelector('.tempo-display');
        if (!btn) return;
        if (btn.classList.contains('active')) stopMetronome(); else startMetronome(btn);
      }} else if (e.key === 's' || e.key === 'S') {{
        toggleAutoScroll();
      }}
    }});
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
