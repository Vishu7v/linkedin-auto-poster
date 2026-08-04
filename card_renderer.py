"""
card_renderer.py — renders LinkedIn code-card images (dark editor-style cards)
for three layouts: cheat sheet (numbered list), compare (wrong vs right),
and single block (one code panel + explanation).
"""
import os
import re
from PIL import Image, ImageDraw, ImageFont

# ── FONTS (bundled first, system fallback) ────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_FONT_DIR = os.path.join(_HERE, "fonts")

def _font(name, system_fallback):
    local = os.path.join(_FONT_DIR, name)
    return local if os.path.exists(local) else system_fallback

MONO      = _font("DejaVuSansMono.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")
MONO_BOLD = _font("DejaVuSansMono-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf")
SANS      = _font("DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
SANS_BOLD = _font("DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")

f_title  = ImageFont.truetype(SANS_BOLD, 40)
f_sub    = ImageFont.truetype(SANS, 26)
f_label  = ImageFont.truetype(MONO_BOLD, 24)
f_code   = ImageFont.truetype(MONO, 26)
f_tip    = ImageFont.truetype(SANS, 24)
f_footer = ImageFont.truetype(SANS_BOLD, 24)

# ── THEME ──────────────────────────────────────────────────────
BG        = (30, 31, 46)
WINDOW_BG = (40, 42, 58)
HEADER_BG = (24, 25, 38)
BORDER    = (58, 60, 82)
RED       = (255, 95, 87)
YELLOW    = (255, 189, 46)
GREEN     = (39, 201, 63)
TEXT_MAIN = (240, 240, 245)
TEXT_SUB  = (170, 172, 190)
ACCENT    = (137, 180, 250)
KEYWORD   = (198, 146, 233)
STRING    = (166, 227, 161)
COMMENT   = (108, 112, 134)
FUNC      = (137, 180, 250)
DEFAULT_C = (224, 226, 240)

KEYWORDS = {"from","import","def","return","if","else","elif","for","while","as",
            "class","with","in","is","not","and","or","lambda","None","True","False"}

MIN_WIDTH, MAX_WIDTH = 1000, 1500


def _highlight_tokens(line: str):
    tokens = []
    pattern = re.compile(r'(".*?"|\'.*?\'|#.*$|\s+|\w+|[^\w\s])')
    prev_nonspace = None
    for m in pattern.finditer(line):
        tok = m.group(0)
        if tok.isspace():
            tokens.append((tok, DEFAULT_C))
            continue
        if tok.startswith('#'):
            tokens.append((tok, COMMENT))
        elif tok.startswith('"') or tok.startswith("'"):
            tokens.append((tok, STRING))
        elif tok in KEYWORDS:
            tokens.append((tok, KEYWORD))
        elif re.match(r'^[A-Za-z_]\w*$', tok) and prev_nonspace == '.':
            tokens.append((tok, FUNC))
        else:
            tokens.append((tok, DEFAULT_C))
        prev_nonspace = tok
    return tokens


def _draw_code_line(draw, x, y, line, font):
    if not line.strip():
        return
    cx = x
    for tok, color in _highlight_tokens(line):
        draw.text((cx, y), tok, font=font, fill=color)
        cx += draw.textlength(tok, font=font)


def _wrap_text(draw, text, font, max_width):
    words = text.split(' ')
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=font) <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _wrap_code_lines(lines, max_chars=66):
    """Soft-wraps any code line longer than max_chars so it can never run
    off the edge of the card, even if the model ignores the length hint.
    Breaks at the last space/comma before the limit when possible."""
    wrapped = []
    for line in lines:
        if len(line) <= max_chars:
            wrapped.append(line)
            continue
        remaining = line
        first = True
        while len(remaining) > max_chars:
            cut = max_chars
            # prefer breaking at a space or comma near the limit
            for sep in (', ', ' '):
                idx = remaining.rfind(sep, 0, max_chars)
                if idx > max_chars * 0.4:
                    cut = idx + len(sep)
                    break
            piece = remaining[:cut].rstrip()
            wrapped.append(piece if first else "  " + piece)
            remaining = remaining[cut:].lstrip()
            first = False
        if remaining:
            wrapped.append(remaining if first else "  " + remaining)
    return wrapped


def _dynamic_width(code_line_groups, pad, win_pad, extra=60):
    """Pick an image width wide enough for the longest code line, clamped."""
    dummy = Image.new("RGB", (10, 10))
    d = ImageDraw.Draw(dummy)
    max_w = 0
    for lines in code_line_groups:
        for line in lines:
            w = d.textlength(line, font=f_code)
            max_w = max(max_w, w)
    needed = int(max_w) + 2 * pad + 2 * win_pad + extra
    return max(MIN_WIDTH, min(MAX_WIDTH, needed))


# ── LAYOUT 1: CHEAT SHEET (numbered list) ─────────────────────
def render_cheat_sheet_card(title, subtitle, items, footer_line, out_path):
    pad, win_pad, line_h, header_h = 60, 36, 40, 64
    items = [{**it, "code_lines": _wrap_code_lines(it["code_lines"])} for it in items]
    width = _dynamic_width([it["code_lines"] for it in items], pad, win_pad)

    dummy = Image.new("RGB", (10, 10))
    d = ImageDraw.Draw(dummy)
    content_w = width - 2*pad - 2*win_pad

    y_est = pad + 70 + 50 + header_h + 20
    for item in items:
        y_est += line_h
        wrapped = _wrap_text(d, item["explanation"], f_tip, content_w - 20)
        y_est += len(wrapped) * 32 + 6
        y_est += len(item["code_lines"]) * line_h + 18
    height = y_est + 70 + pad

    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)

    y = pad
    draw.text((pad, y), title, font=f_title, fill=TEXT_MAIN)
    y += 54
    draw.text((pad, y), subtitle, font=f_sub, fill=TEXT_SUB)
    y += 60

    win_x0, win_y0, win_x1 = pad, y, width - pad
    draw.rounded_rectangle([win_x0, win_y0, win_x1, height - pad], radius=18,
                            fill=WINDOW_BG, outline=BORDER, width=2)
    draw.rounded_rectangle([win_x0, win_y0, win_x1, win_y0 + header_h], radius=18, fill=HEADER_BG)
    draw.rectangle([win_x0, win_y0 + header_h - 18, win_x1, win_y0 + header_h], fill=HEADER_BG)
    dot_y = win_y0 + header_h // 2
    for i, c in enumerate([RED, YELLOW, GREEN]):
        draw.ellipse([win_x0+26+i*30-8, dot_y-8, win_x0+26+i*30+8, dot_y+8], fill=c)
    draw.text((win_x0 + 130, dot_y - 12), "data_engineer.py", font=f_label, fill=TEXT_SUB)

    cy = win_y0 + header_h + 20
    cx = win_x0 + win_pad
    for idx, item in enumerate(items, start=1):
        draw.text((cx, cy), f"{idx}. {item['label']}", font=f_label, fill=ACCENT)
        cy += line_h
        for wline in _wrap_text(draw, item["explanation"], f_tip, content_w - 20):
            draw.text((cx + 6, cy), wline, font=f_tip, fill=TEXT_SUB)
            cy += 32
        cy += 6
        for cline in item["code_lines"]:
            _draw_code_line(draw, cx + 6, cy, cline, f_code)
            cy += line_h
        cy += 18

    draw.line([win_x0+win_pad, height-pad-46, win_x1-win_pad, height-pad-46], fill=BORDER, width=2)
    draw.text((win_x0+win_pad, height-pad-30), footer_line, font=f_footer, fill=GREEN)

    img.save(out_path)
    return out_path


# ── LAYOUT 2: COMPARE (wrong vs right) ─────────────────────────
def render_compare_card(title, subtitle, wrong_label, wrong_code, right_label, right_code,
                         insight_label, insight_text, footer_line, out_path):
    pad, win_pad, line_h, header_h = 60, 30, 40, 56
    wrong_code = _wrap_code_lines(wrong_code)
    right_code = _wrap_code_lines(right_code)
    width = _dynamic_width([wrong_code, right_code], pad, win_pad)

    dummy = Image.new("RGB", (10, 10))
    d = ImageDraw.Draw(dummy)
    content_w = width - 2*pad - 2*win_pad

    y = pad + 54 + 60
    wrong_h = header_h + 24 + len(wrong_code) * line_h + 20
    right_h = header_h + 24 + len(right_code) * line_h + 20
    y += wrong_h + 26 + right_h + 20
    wrapped_insight = _wrap_text(d, insight_text, f_tip, content_w - 20)
    y += 34 + len(wrapped_insight) * 32 + 20 + 60
    height = y + pad

    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)

    cy = pad
    draw.text((pad, cy), title, font=f_title, fill=TEXT_MAIN)
    cy += 54
    draw.text((pad, cy), subtitle, font=f_sub, fill=TEXT_SUB)
    cy += 60

    def code_panel(y0, label, code_lines, accent, bg):
        h = header_h + 24 + len(code_lines) * line_h + 20
        x0, x1 = pad, width - pad
        draw.rounded_rectangle([x0, y0, x1, y0 + h], radius=16, fill=bg, outline=accent, width=2)
        draw.rounded_rectangle([x0, y0, x1, y0 + header_h], radius=16, fill=accent)
        draw.rectangle([x0, y0 + header_h - 16, x1, y0 + header_h], fill=accent)
        draw.text((x0 + 24, y0 + 14), label, font=f_label, fill=(20, 20, 25))
        cyy = y0 + header_h + 20
        for line in code_lines:
            _draw_code_line(draw, x0 + win_pad, cyy, line, f_code)
            cyy += line_h
        return y0 + h

    cy = code_panel(cy, wrong_label, wrong_code, (255, 120, 120), (46, 32, 36))
    cy += 26
    cy = code_panel(cy, right_label, right_code, (120, 220, 150), (30, 42, 36))
    cy += 30

    draw.text((pad, cy), insight_label, font=f_label, fill=ACCENT)
    cy += 34
    for wline in wrapped_insight:
        draw.text((pad + 6, cy), wline, font=f_tip, fill=TEXT_SUB)
        cy += 32
    cy += 20

    draw.line([pad, cy, width - pad, cy], fill=BORDER, width=2)
    draw.text((pad, cy + 16), footer_line, font=f_footer, fill=GREEN)

    img.save(out_path)
    return out_path


# ── LAYOUT 3: SINGLE BLOCK (one code panel) ─────────────────────
def render_single_block_card(title, subtitle, filename, code_lines, insight_label,
                              insight_text, tip_text, footer_line, out_path):
    pad, win_pad, line_h, header_h = 60, 30, 40, 56
    code_lines = _wrap_code_lines(code_lines)
    width = _dynamic_width([code_lines], pad, win_pad)

    dummy = Image.new("RGB", (10, 10))
    d = ImageDraw.Draw(dummy)
    content_w = width - 2*pad - 2*win_pad

    wrapped_insight = _wrap_text(d, insight_text, f_tip, content_w - 20)
    wrapped_tip = _wrap_text(d, tip_text, f_tip, content_w - 20) if tip_text else []

    y = pad + 54 + 60
    win_h = header_h + 24 + len(code_lines) * line_h + 20
    y += win_h + 30
    y += 34 + len(wrapped_insight) * 32
    if wrapped_tip:
        y += 20 + 34 + len(wrapped_tip) * 32
    y += 20 + 60
    height = y + pad

    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)

    cy = pad
    draw.text((pad, cy), title, font=f_title, fill=TEXT_MAIN)
    cy += 54
    draw.text((pad, cy), subtitle, font=f_sub, fill=TEXT_SUB)
    cy += 60

    x0, x1 = pad, width - pad
    draw.rounded_rectangle([x0, cy, x1, cy + win_h], radius=16, fill=WINDOW_BG, outline=BORDER, width=2)
    draw.rounded_rectangle([x0, cy, x1, cy + header_h], radius=16, fill=HEADER_BG)
    draw.rectangle([x0, cy + header_h - 16, x1, cy + header_h], fill=HEADER_BG)
    dot_y = cy + header_h // 2
    for i, c in enumerate([RED, YELLOW, GREEN]):
        draw.ellipse([x0+26+i*30-8, dot_y-8, x0+26+i*30+8, dot_y+8], fill=c)
    draw.text((x0 + 130, dot_y - 12), filename, font=f_label, fill=TEXT_SUB)
    cyy = cy + header_h + 20
    for line in code_lines:
        _draw_code_line(draw, x0 + win_pad, cyy, line, f_code)
        cyy += line_h
    cy += win_h + 30

    draw.text((pad, cy), insight_label, font=f_label, fill=ACCENT)
    cy += 34
    for wline in wrapped_insight:
        draw.text((pad + 6, cy), wline, font=f_tip, fill=TEXT_SUB)
        cy += 32

    if wrapped_tip:
        cy += 20
        draw.text((pad, cy), "PRO TIP", font=f_label, fill=YELLOW)
        cy += 34
        for wline in wrapped_tip:
            draw.text((pad + 6, cy), wline, font=f_tip, fill=TEXT_SUB)
            cy += 32

    cy += 20
    draw.line([pad, cy, width - pad, cy], fill=BORDER, width=2)
    draw.text((pad, cy + 16), footer_line, font=f_footer, fill=GREEN)

    img.save(out_path)
    return out_path
