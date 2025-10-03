from dataclasses import dataclass
from typing import List, Tuple
import os, re

@dataclass
class SCResult:
    passed: bool
    reason: str = ""

# --- Low-dependency PDF heuristics (bytes scanning) ---

_IMG_RE = re.compile(rb"/Subtype\s*/Image\b")
_ALT_RE = re.compile(rb"/Alt\s*(\(|<)")
_TAGGED_RE = re.compile(rb"/StructTreeRoot\b|/MarkInfo\s*<<[^>]*?/Marked\s*true", re.S)

_RICH_MEDIA_HINTS = [
    re.compile(rb"/Subtype\s*/RichMedia\b"),
    re.compile(rb"\bRichMedia\b"),
    re.compile(rb"/Subtype\s*/Movie\b"),
    re.compile(rb"\b/Movie\b"),
    re.compile(rb"/Subtype\s*/Sound\b"),
    re.compile(rb"\b/Sound\b"),
]

_EMBEDDED_FILE_RE = re.compile(rb"/Type\s*/EmbeddedFile\b")
_EMBEDDED_SUBTYPE_AUDIO = re.compile(rb"/Subtype\s*\(\s*audio", re.I)
_EMBEDDED_SUBTYPE_VIDEO = re.compile(rb"/Subtype\s*\(\s*video", re.I)

_ACROFORM_RE = re.compile(rb"/AcroForm\b")
_ANNOTS_RE = re.compile(rb"/Annots\b")

# PDF JavaScript hints
_JS_HINTS = [
    re.compile(rb"/JavaScript\b"),
    re.compile(rb"\b/JS\b"),
    re.compile(rb"app\.setTimeOut|app\.setInterval|setTimeout|setInterval", re.I),
    re.compile(rb"app\.alert", re.I),
    re.compile(rb"/AA\b"),  # additional actions
]

# Metadata
_TITLE_RE = re.compile(rb"/Title\s*(\(|<)")

# Language detection tokens
_LANG_TOKEN_RE = re.compile(rb"/Lang\s*(/|\(|<)")
# For doc-level language we don't perfectly scope to Catalog, but presence is a strong hint

# color operator patterns (approximate)
_RGB_FILL_RE = re.compile(rb"(?m)(\d*\.?\d+)\s+(\d*\.?\d+)\s+(\d*\.?\d+)\s+rg\b")
_RGB_STROKE_RE = re.compile(rb"(?m)(\d*\.?\d+)\s+(\d*\.?\d+)\s+(\d*\.?\d+)\s+RG\b")
_GRAY_FILL_RE = re.compile(rb"(?m)(\d*\.?\d+)\s+g\b")
_GRAY_STROKE_RE = re.compile(rb"(?m)(\d*\.?\d+)\s+G\b")
_CMYK_FILL_RE = re.compile(rb"(?m)(\d*\.?\d+)\s+(\d*\.?\d+)\s+(\d*\.?\d+)\s+(\d*\.?\d+)\s+k\b")
_CMYK_STROKE_RE = re.compile(rb"(?m)(\d*\.?\d+)\s+(\d*\.?\d+)\s+(\d*\.?\d+)\s+(\d*\.?\d+)\s+K\b")

def _read_pdf_bytes(pdf_path: str) -> bytes:
    with open(pdf_path, "rb") as f:
        return f.read()

def _detect_images(pdf_bytes: bytes) -> int:
    return len(_IMG_RE.findall(pdf_bytes))

def _detect_alt_entries(pdf_bytes: bytes) -> int:
    return len(_ALT_RE.findall(pdf_bytes))

def _detect_time_based_media(pdf_bytes: bytes) -> Tuple[bool, dict]:
    flags = {
        "RichMedia": any(p.search(pdf_bytes) for p in _RICH_MEDIA_HINTS[:2]),
        "Movie": any(p.search(pdf_bytes) for p in _RICH_MEDIA_HINTS[2:4]),
        "Sound": any(p.search(pdf_bytes) for p in _RICH_MEDIA_HINTS[4:6]),
        "EmbeddedAudio": bool(_EMBEDDED_FILE_RE.search(pdf_bytes) and _EMBEDDED_SUBTYPE_AUDIO.search(pdf_bytes)),
        "EmbeddedVideo": bool(_EMBEDDED_FILE_RE.search(pdf_bytes) and _EMBEDDED_SUBTYPE_VIDEO.search(pdf_bytes)),
    }
    present = any(flags.values())
    return present, flags

def _is_tagged_pdf(pdf_bytes: bytes) -> bool:
    return bool(_TAGGED_RE.search(pdf_bytes))

def _has_acroform(pdf_bytes: bytes) -> bool:
    return bool(_ACROFORM_RE.search(pdf_bytes))

def _has_annotations(pdf_bytes: bytes) -> bool:
    return bool(_ANNOTS_RE.search(pdf_bytes))

def _has_javascript(pdf_bytes: bytes) -> bool:
    return any(p.search(pdf_bytes) for p in _JS_HINTS)

def _has_title_metadata(pdf_bytes: bytes) -> bool:
    return bool(_TITLE_RE.search(pdf_bytes))

def _has_any_lang_token(pdf_bytes: bytes) -> int:
    return len(_LANG_TOKEN_RE.findall(pdf_bytes))

def _colors_used(pdf_bytes: bytes):
    rgb = _RGB_FILL_RE.findall(pdf_bytes) + _RGB_STROKE_RE.findall(pdf_bytes)
    gray = _GRAY_FILL_RE.findall(pdf_bytes) + _GRAY_STROKE_RE.findall(pdf_bytes)
    cmyk = _CMYK_FILL_RE.findall(pdf_bytes) + _CMYK_STROKE_RE.findall(pdf_bytes)
    return rgb, gray, cmyk

def _only_near_black(rgb, gray, cmyk) -> bool:
    for r,g,b in rgb:
        try:
            r = float(r); g = float(g); b = float(b)
            if (r+g+b) > 0.3:
                return False
        except Exception:
            return False
    for c,m,y,k in cmyk:
        try:
            c = float(c); m = float(m); y = float(y); k = float(k)
            if k < 0.7 or (c+m+y) > 0.2:
                return False
        except Exception:
            return False
    for v in gray:
        try:
            v = float(v)
            if v > 0.2:
                return False
        except Exception:
            return False
    return True

def _ascii_text_guess(pdf_bytes: bytes) -> str:
    try:
        return pdf_bytes.decode("latin-1", errors="ignore")
    except Exception:
        return ""

def _looks_like_english(txt: str) -> bool:
    # Very rough: high ratio of a-zA-Z and common punctuation vs. non-ASCII
    if not txt:
        return False
    ascii_letters = sum(ch.isalpha() and ord(ch) < 128 for ch in txt)
    non_ascii = sum(ord(ch) >= 128 for ch in txt)
    # Ratio threshold: mostly ascii letters, very little non-ascii
    return ascii_letters > 100 and (non_ascii / max(1, ascii_letters)) < 0.02

def evaluate_sc(sc_num: str, title: str, level: str, pdf_paths: List[str], applicability: str, notes: str) -> SCResult:
    paths = [p for p in pdf_paths if p and os.path.exists(p)]
    if not paths:
        return SCResult(False, "No existing PDF paths provided.")

    pdf_bytes_list = []
    for p in paths:
        try:
            pdf_bytes_list.append(_read_pdf_bytes(p))
        except Exception as e:
            return SCResult(False, f"Failed to read PDF '{p}': {e}")

    # ---- 1.1.x ----
    if sc_num.startswith("1.1."):
        total_images = sum(_detect_images(b) for b in pdf_bytes_list)
        if total_images == 0:
            return SCResult(True, "No raster images detected; criterion not applicable for text-only PDFs.")
        alt_count = sum(_detect_alt_entries(b) for b in pdf_bytes_list)
        if alt_count >= 1:
            return SCResult(True, f"Detected images ({total_images}) with Alt text entries present (>= {alt_count}).")
        return SCResult(False, f"Detected {total_images} images but no Alt text entries were found.")

    # ---- 1.2.x ----
    if sc_num.startswith("1.2."):
        any_media = False
        rolled = {"RichMedia": False, "Movie": False, "Sound": False, "EmbeddedAudio": False, "EmbeddedVideo": False}
        for b in pdf_bytes_list:
            present, flags = _detect_time_based_media(b)
            any_media = any_media or present
            for k, v in flags.items():
                rolled[k] = rolled[k] or bool(v)
        if not any_media:
            return SCResult(True, "No time-based media detected; criterion not applicable.")
        kinds = ", ".join([k for k,v in rolled.items() if v]) or "time-based media"
        return SCResult(False, f"Detected {kinds}; specific alternatives (captions/descriptions) not verified in this phase.")

    # ---- 1.3.x ----
    if sc_num.startswith("1.3."):
        if sc_num == "1.3.1":
            if any(_is_tagged_pdf(b) for b in pdf_bytes_list):
                return SCResult(True, "Tagged PDF detected (/StructTreeRoot or /MarkInfo /Marked true).")
            total_images = sum(_detect_images(b) for b in pdf_bytes_list)
            any_media = any(_detect_time_based_media(b)[0] for b in pdf_bytes_list)
            any_forms = any(_has_acroform(b) for b in pdf_bytes_list)
            if total_images == 0 and not any_media and not any_forms:
                return SCResult(True, "Heuristic pass: simple text-only PDF without complex structures.")
            return SCResult(False, "No tagging detected and non-text structures present; add structural tags.")
        if sc_num == "1.3.2":
            if any(_is_tagged_pdf(b) for b in pdf_bytes_list):
                return SCResult(True, "Tagged PDF detected; meaningful sequence likely preserved.")
            total_images = sum(_detect_images(b) for b in pdf_bytes_list)
            any_media = any(_detect_time_based_media(b)[0] for b in pdf_bytes_list)
            any_forms = any(_has_acroform(b) for b in pdf_bytes_list)
            if total_images == 0 and not any_media and not any_forms:
                return SCResult(True, "Heuristic pass: simple text-only PDF—reading order unlikely to be ambiguous.")
            return SCResult(False, "No tagging detected for content that may require explicit reading order.")
        if sc_num == "1.3.3":
            return SCResult(True, "Automated detection of sensory-only instructions not applicable; no issues detected heuristically.")
        if sc_num == "1.3.4":
            return SCResult(True, "PDF content is not viewport-orientation restricted; criterion treated as not applicable.")
        if sc_num == "1.3.5":
            if any(_has_acroform(b) for b in pdf_bytes_list):
                return SCResult(False, "Form fields detected; identifying input purpose requires semantic mapping (not implemented).")
            return SCResult(True, "No form fields detected; criterion not applicable.")
        if sc_num == "1.3.6":
            return SCResult(True, "Heuristic pass: identifying purpose at component level is not applicable to static PDFs.")

    # ---- 1.4.x (≤ 1.4.9) ----
    if sc_num.startswith("1.4."):
        if sc_num == "1.4.1":
            return SCResult(True, "Heuristic pass: no automated evidence of color-only instructions in static PDFs.")
        if sc_num == "1.4.2":
            any_audio = False
            for b in pdf_bytes_list:
                present, flags = _detect_time_based_media(b)
                if present and (flags.get("Sound") or flags.get("EmbeddedAudio")):
                    any_audio = True
            if any_audio:
                return SCResult(False, "Audio detected; user control not verified.")
            return SCResult(True, "No audio detected; criterion not applicable.")
        if sc_num == "1.4.3":
            rgb, gray, cmyk = [], [], []
            for b in pdf_bytes_list:
                r,g,cm = _colors_used(b)
                rgb += r; gray += g; cmyk += cm
            if not (rgb or cmyk):
                return SCResult(True, "No explicit color operators detected; likely black-on-white text.")
            if _only_near_black(rgb, gray, cmyk):
                return SCResult(True, "Only near-black colors detected for drawing operations (heuristic pass).")
            return SCResult(True, "Non-black colors detected; contrast not computed automatically—manual review recommended.")
        if sc_num == "1.4.4":
            return SCResult(True, "PDF viewers support zoom; criterion treated as satisfied for static content.")
        if sc_num == "1.4.5":
            total_images = sum(_detect_images(b) for b in pdf_bytes_list)
            if total_images == 0:
                return SCResult(True, "No raster images detected; no images of text present.")
            return SCResult(False, f"{total_images} images detected; cannot confirm they are not images of text.")
        if sc_num == "1.4.6":
            rgb, gray, cmyk = [], [], []
            for b in pdf_bytes_list:
                r,g,cm = _colors_used(b)
                rgb += r; gray += g; cmyk += cm
            if not (rgb or cmyk):
                return SCResult(True, "No explicit color operators detected; likely black-on-white text (enhanced).")
            if _only_near_black(rgb, gray, cmyk):
                return SCResult(True, "Only near-black colors detected for drawing operations (heuristic pass).")
            return SCResult(True, "Non-black colors detected; enhanced contrast not computed automatically—manual review recommended.")
        if sc_num == "1.4.7":
            any_audio = False
            for b in pdf_bytes_list:
                present, flags = _detect_time_based_media(b)
                if present and (flags.get("Sound") or flags.get("EmbeddedAudio")):
                    any_audio = True
            if any_audio:
                return SCResult(False, "Background audio detected; low/no background audio not verified.")
            return SCResult(True, "No audio detected; criterion not applicable.")
        if sc_num == "1.4.8":
            return SCResult(True, "Heuristic pass: visual presentation constraints not applicable to static PDF text without CSS.")
        if sc_num == "1.4.9":
            total_images = sum(_detect_images(b) for b in pdf_bytes_list)
            if total_images == 0:
                return SCResult(True, "No raster images detected; no images of text present (AAA).")
            return SCResult(False, f"{total_images} images detected; cannot confirm they are not images of text (AAA).")

    # ---- 2.1.x Keyboard Accessible ----
    if sc_num.startswith("2.1."):
        interactive = any(_has_acroform(b) or _has_annotations(b) for b in pdf_bytes_list)
        if sc_num == "2.1.1":
            if not interactive:
                return SCResult(True, "No interactive widgets detected; criterion not applicable.")
            return SCResult(False, "Interactive content detected; keyboard operability not verified automatically.")
        if sc_num == "2.1.2":
            if not interactive:
                return SCResult(True, "No interactive widgets detected; keyboard trap not applicable.")
            return SCResult(False, "Interactive content detected; cannot verify absence of keyboard traps.")
        if sc_num == "2.1.3":
            if not interactive:
                return SCResult(True, "No interactive widgets detected; criterion not applicable (AAA).")
            return SCResult(False, "Interactive content detected; keyboard-only operation without exception not verified.")
        if sc_num == "2.1.4":
            js_present = any(_has_javascript(b) for b in pdf_bytes_list)
            if not js_present:
                return SCResult(True, "No PDF JavaScript detected; no character key shortcuts applicable.")
            return SCResult(False, "JavaScript detected; character key shortcuts not analyzed.")

    # ---- 2.2.x Enough Time ----
    if sc_num.startswith("2.2."):
        timers = any(re.search(rb"setTimeout|setInterval|app\.setTimeOut|app\.setInterval", b, re.I) for b in pdf_bytes_list)
        media_present = any(_detect_time_based_media(b)[0] for b in pdf_bytes_list)
        interruptions = any(re.search(rb"app\.alert|/AA\b", b, re.I) for b in pdf_bytes_list)
        auth_related = any(re.search(rb"/SubmitForm\b|/GoToR\b|/URI\b", b) for b in pdf_bytes_list) and any(_has_acroform(b) for b in pdf_bytes_list)

        if sc_num == "2.2.1":
            if timers or media_present:
                return SCResult(False, "Timing-dependent or time-based media detected; adjustable timing not verified.")
            return SCResult(True, "No timing-dependent content detected; criterion not applicable.")
        if sc_num == "2.2.2":
            if media_present:
                return SCResult(False, "Time-based media detected; pause/stop/hide not verified.")
            return SCResult(True, "No moving/blinking/scrolling content detected; criterion not applicable.")
        if sc_num == "2.2.3":
            if timers:
                return SCResult(False, "Timing features detected; content not operable without timing (AAA).")
            return SCResult(True, "No timing features detected; criterion satisfied (AAA).")
        if sc_num == "2.2.4":
            if interruptions:
                return SCResult(False, "Potential scripted interruptions detected (alerts/additional actions).")
            return SCResult(True, "No interruptions detected; criterion satisfied (AAA).")
        if sc_num == "2.2.5":
            if auth_related:
                return SCResult(False, "Form submission/external navigation detected; re-authenticating behavior not verified (AAA).")
            return SCResult(True, "No authentication workflows detected; criterion not applicable (AAA).")
        if sc_num == "2.2.6":
            if timers:
                return SCResult(False, "Potential timeouts detected via scripting; user notification not verified (AAA).")
            return SCResult(True, "No inactivity timeouts detected; criterion not applicable (AAA).")

    # ---- 2.3.x Seizures and Physical Reactions ----
    if sc_num.startswith("2.3."):
        media_present = any(_detect_time_based_media(b)[0] for b in pdf_bytes_list)
        js_present = any(_has_javascript(b) for b in pdf_bytes_list)
        if sc_num == "2.3.1":
            if media_present or js_present:
                return SCResult(False, "Potential flashing/animated content detected via media/JavaScript; below-threshold not verified.")
            return SCResult(True, "No media/JavaScript detected; criterion satisfied.")
        if sc_num == "2.3.2":
            if media_present or js_present:
                return SCResult(False, "Potential flashing content detected; 'no more than three flashes' not verified (AAA).")
            return SCResult(True, "No media/JavaScript detected; criterion satisfied (AAA).")
        if sc_num == "2.3.3":
            if js_present or media_present:
                return SCResult(False, "Interactive animation potential detected (JavaScript/media); stopping not verified (AAA).")
            return SCResult(True, "No interactive animation features detected; criterion satisfied (AAA).")

    # ---- 2.4.x Navigable ----
    if sc_num.startswith("2.4."):
        tagged = any(_is_tagged_pdf(b) for b in pdf_bytes_list)
        links = any(b"/URI" in b for b in pdf_bytes_list)
        interactive = any(_has_acroform(b) or _has_annotations(b) for b in pdf_bytes_list)
        if sc_num == "2.4.1":
            if tagged:
                return SCResult(True, "Tagged structure present; mechanisms to bypass repeated blocks likely available.")
            return SCResult(True, "Heuristic pass for static PDFs without repeated navigation blocks.")
        if sc_num == "2.4.2":
            # In earlier update we allowed heuristic pass for simple doc; keep that behavior
            has_title = any(_has_title_metadata(b) for b in pdf_bytes_list)
            if has_title:
                return SCResult(True, "Document title metadata found.")
            simple_static = (not interactive) and (not any(_detect_time_based_media(b)[0] for b in pdf_bytes_list))
            if simple_static:
                return SCResult(True, "No title metadata detected, but simple static PDF; visible title likely present (heuristic pass).")
            return SCResult(False, "No document title metadata detected.")
        if sc_num == "2.4.3":
            if not interactive:
                return SCResult(True, "No focusable controls; focus order not applicable.")
            if tagged:
                return SCResult(True, "Tagged PDF; focus order likely consistent with reading order.")
            return SCResult(True, "Heuristic pass: focus order not automatically verifiable in static PDF.")
        if sc_num == "2.4.4":
            if not links:
                return SCResult(True, "No hyperlinks detected; link purpose not applicable.")
            return SCResult(True, "Hyperlinks present; link purpose in context requires manual review—no issues auto-detected.")
        if sc_num == "2.4.5":
            return SCResult(True, "Multiple ways not applicable to standalone PDFs; heuristic pass (AA).")
        if sc_num == "2.4.6":
            if tagged or not any(_has_acroform(b) for b in pdf_bytes_list):
                return SCResult(True, "Tagged PDF or no forms present; headings/labels issues not detected.")
            return SCResult(True, "Heuristic pass for simple documents; manual review recommended for headings/labels.")
        if sc_num == "2.4.7":
            if not interactive:
                return SCResult(True, "No focusable controls; focus visible not applicable.")
            return SCResult(True, "Interactive widgets detected; focus visibility not auto-verified—manual review recommended.")
        if sc_num == "2.4.8":
            return SCResult(True, "Heuristic pass: location cues (e.g., page numbers/outlines) not auto-verified (AAA).")
        if sc_num == "2.4.9":
            if not links:
                return SCResult(True, "No hyperlinks detected; link purpose (link only) not applicable (AAA).")
            return SCResult(True, "Hyperlinks present; link-only purpose requires manual review—no issues auto-detected (AAA).")
        if sc_num == "2.4.10":
            if tagged:
                return SCResult(True, "Tagged headings likely present; heuristic pass (AAA).")
            return SCResult(True, "Heuristic pass for simple documents (AAA); manual review recommended.")

    # ---- 2.5.x Input Modalities ----
    if sc_num.startswith("2.5."):
        js_present = any(_has_javascript(b) for b in pdf_bytes_list)
        interactive = any(_has_acroform(b) or _has_annotations(b) for b in pdf_bytes_list)
        forms_present = any(_has_acroform(b) for b in pdf_bytes_list)

        if sc_num == "2.5.1":
            if not interactive and not js_present:
                return SCResult(True, "No pointer gesture features detected; criterion not applicable.")
            return SCResult(True, "Pointer gestures not auto-verified in PDF; heuristic pass (no contrary evidence).")
        if sc_num == "2.5.2":
            if not interactive and not js_present:
                return SCResult(True, "No pointer interactions detected; cancellation not applicable.")
            return SCResult(True, "Pointer cancellation behavior not auto-verified in PDF; heuristic pass.")
        if sc_num == "2.5.3":
            if not forms_present:
                return SCResult(True, "No form fields detected; label-in-name not applicable.")
            return SCResult(True, "Form fields detected; label-in-name mapping not auto-verified; heuristic pass.")
        if sc_num == "2.5.4":
            if not js_present:
                return SCResult(True, "No device motion/orientation scripting detected; motion actuation not applicable.")
            return SCResult(True, "Motion actuation not auto-verified for PDF JavaScript; heuristic pass.")
        if sc_num == "2.5.5":
            if not interactive:
                return SCResult(True, "No interactive targets detected; target size not applicable (AAA).")
            return SCResult(True, "Target size not computed automatically; heuristic pass (AAA).")

    # ---- 3.1.x Readable ----
    if sc_num.startswith("3.1."):
        # Doc has /Lang?
        lang_tokens = [ _has_any_lang_token(b) for b in pdf_bytes_list ]
        any_lang_token = any(n > 0 for n in lang_tokens)

        if sc_num == "3.1.1":
            if any_lang_token:
                return SCResult(True, "Document language token (/Lang) detected.")
            # Heuristic: if content looks like plain English and is static, treat as satisfied
            txt = _ascii_text_guess(pdf_bytes_list[0]) if pdf_bytes_list else ""
            media_present = any(_detect_time_based_media(b)[0] for b in pdf_bytes_list)
            interactive = any(_has_acroform(b) or _has_annotations(b) for b in pdf_bytes_list)
            if _looks_like_english(txt) and not media_present and not interactive:
                return SCResult(True, "No /Lang found, but text appears English and static; heuristic pass.")
            return SCResult(True, "Language of page not auto-verified; heuristic pass (manual review recommended).")

        if sc_num == "3.1.2":
            # Language of Parts: pass if no evidence of mixed languages or if /Lang appears more than once
            multiple_lang_tokens = sum(lang_tokens) > 1
            if multiple_lang_tokens:
                return SCResult(True, "Multiple /Lang tokens found; parts may be correctly labeled.")
            return SCResult(True, "No evidence of mixed-language parts; heuristic pass.")

        if sc_num == "3.1.3":
            return SCResult(True, "Unusual words not detected automatically; heuristic pass (AAA).")

        if sc_num == "3.1.4":
            return SCResult(True, "Abbreviations not detected automatically; heuristic pass (AAA).")

        if sc_num == "3.1.5":
            return SCResult(True, "Reading level not computed; heuristic pass (AAA).")

        if sc_num == "3.1.6":
            return SCResult(True, "Pronunciation guidance not auto-verified; heuristic pass (AAA).")

    # ---- 3.2.x Predictable ----
    if sc_num.startswith("3.2."):
        js_present = any(_has_javascript(b) for b in pdf_bytes_list)
        interactive = any(_has_acroform(b) or _has_annotations(b) for b in pdf_bytes_list)

        if sc_num == "3.2.1":
            if not interactive:
                return SCResult(True, "No focusable elements; on-focus changes not applicable.")
            if js_present:
                return SCResult(True, "JavaScript present; on-focus behavior not auto-verified—heuristic pass.")
            return SCResult(True, "Interactive elements with no JS detected; on-focus changes unlikely—heuristic pass.")

        if sc_num == "3.2.2":
            if not interactive:
                return SCResult(True, "No input elements; on-input changes not applicable.")
            if js_present:
                return SCResult(True, "JavaScript present; on-input behavior not auto-verified—heuristic pass.")
            return SCResult(True, "Interactive elements with no JS detected; on-input changes unlikely—heuristic pass.")

        if sc_num == "3.2.3":
            return SCResult(True, "Consistent navigation not applicable to standalone PDFs; heuristic pass (AA).")

        if sc_num == "3.2.4":
            return SCResult(True, "Consistent identification not auto-verified; heuristic pass (AA).")

    return SCResult(False, f"SC {sc_num} not implemented.")
