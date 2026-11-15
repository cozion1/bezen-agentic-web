# Builds the Open Agentic Web video: Cozio's Hebrew voice notes + live-site screenshots + burned-in English subtitles.
# Run: python make_video.py
import os, re, subprocess
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS, VOICE, B = (os.path.join(HERE, d) for d in ("shots", "voice", "build"))
os.makedirs(B, exist_ok=True)
P = lambda name: os.path.join(B, name)
TEMPO = 1.06            # keeps the whole video under two minutes
END_HOLD = 2.0

REG, BOLD, MONO = r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\consola.ttf"
W, H, TOP = 1920, 1080, 900
BG, FG, BONE, GREEN, BROWN, MUTED = (20, 26, 23), (236, 241, 237), (250, 250, 246), (95, 196, 163), (224, 160, 122), (150, 165, 156)

def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]).decode())

def frame(src, box, out, highlight=None):
    im = Image.open(os.path.join(SHOTS, src)).convert("RGB")
    if highlight:
        ImageDraw.Draw(im).rounded_rectangle(highlight, radius=8, outline=(217, 119, 6), width=4)
    im = im.crop(box)
    s = min((W - 80) / im.width, (TOP - 50) / im.height)
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    c = Image.new("RGB", (W, H), BG)
    c.paste(im, ((W - im.width) // 2, 25 + (TOP - 50 - im.height) // 2))
    c.save(out)

def card(lines, out):
    c = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(c)
    blocks = [(t, ImageFont.truetype(f, sz), col, int(sz * 1.4)) for t, sz, col, f in lines]
    y = (TOP - sum(h for *_, h in blocks)) // 2
    for t, f, col, h in blocks:
        d.text(((W - d.textlength(t, font=f)) // 2, y), t, font=f, fill=col); y += h
    c.save(out)

S = lambda t, sz=52, col=FG, f=REG: (t, sz, col, f)

# ── frames ─────────────────────────────────────────────────────────────
card([S("BEZEN Reader", 104, BONE, BOLD), S("", 16),
      S("An open agentic website that reads the person", 46, MUTED),
      S("before an agent answers them.", 46, MUTED), S("", 30),
      S("Open Agentic Web Challenge 2026", 40, GREEN)], P("title.png"))
card([S("A customer writes to a shop:", 48, MUTED), S("", 20),
      S("\u201cWhere did you get my email?", 84, BONE, BOLD),
      S("Take me off your list.\u201d", 84, BONE, BOLD), S("", 30),
      S("A normal bot sees a question, and keeps selling.", 48, BROWN)], P("question.png"))
frame("home.jpg", (0, 0, 1456, 420), P("home.png"))
frame("typed.jpg", (90, 50, 1456, 820), P("typed.png"), highlight=(100, 772, 890, 802))
frame("consent.jpg", (90, 180, 1060, 400), P("consent.png"), highlight=(104, 291, 778, 391))
frame("result.jpg", (95, 380, 960, 595), P("result.png"))
frame("monthly.jpg", (95, 180, 1060, 550), P("monthly.png"), highlight=(110, 437, 300, 455))

def code_card(out):
    c = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(c)
    f, fm = ImageFont.truetype(BOLD, 60), ImageFont.truetype(MONO, 38)
    t = "Connect BEZEN to any agentic site: one line"
    d.text(((W - d.textlength(t, font=f)) // 2, 120), t, font=f, fill=BONE)
    d.rounded_rectangle([260, 260, 1660, 640], radius=16, fill=(12, 16, 14), outline=(60, 75, 68), width=3)
    lines = [('{', FG), ('  "name": "your_front_agent",', FG), ('  "tools": [', FG),
             ('    "your_other_agents",', MUTED), ('    "https://bezen-reader.netlify.app/bezen_reader"', GREEN), ('  ]', FG), ('}', FG)]
    y = 290
    for s, col in lines:
        d.text((320, y), s, font=fm, fill=col); y += 48
    s = "Runs in the browser. The visitor approves every cross-site call."
    fr = ImageFont.truetype(REG, 40)
    d.text(((W - d.textlength(s, font=fr)) // 2, 720), s, font=fr, fill=MUTED)
    c.save(out)
code_card(P("code.png"))
card([S("BEZEN Reader", 104, BONE, BOLD), S("", 16),
      S("Understand the person first. Then answer.", 54, GREEN), S("", 40),
      S("bezen-reader.netlify.app", 46, FG, MONO),
      S("saltbox-coffee-demo.netlify.app", 46, FG, MONO),
      S("github.com/cozion1/bezen-agentic-web", 46, FG, MONO), S("", 30),
      S("Zion Cohen  \u00b7  Open Agentic Web Challenge 2026", 40, MUTED)], P("end.png"))

# ── timeline: shot -> [(frame, seconds of the ORIGINAL tight voice, None = rest)] ──
plan = {1: [("title.png", 3.5), ("question.png", None)],
        2: [("home.png", None)],
        3: [("typed.png", 13), ("consent.png", 21), ("result.png", None)],
        4: [("monthly.png", None)],
        5: [("code.png", 10), ("end.png", None)]}

html = open(os.path.join(HERE, "..", "video-script.html"), encoding="utf-8").read()
en = [re.sub(r"<[^>]+>", " ", t) for t in re.findall(r'<p class="en">(.*?)</p>', html, re.S)]
en = [re.sub(r"\s+", " ", t).strip() for t in en]
assert len(en) == 5, len(en)

def ts(t):
    h, r = divmod(t, 3600); m, s = divmod(r, 60)
    return f"{int(h):02}:{int(m):02}:{s:06.3f}".replace(".", ",")

concat, subs, audio, t0 = [], [], [], 0.0
for n in range(1, 6):
    src, fast = os.path.join(VOICE, f"shot{n}_tight.ogg"), os.path.join(VOICE, f"shot{n}_fast.ogg")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af", f"atempo={TEMPO}", fast], check=True)
    audio.append(fast)
    d = dur(fast)
    d_frames = d + (END_HOLD if n == 5 else 0)
    fixed = sum(s / TEMPO for _, s in plan[n] if s)
    for img, s in plan[n]:
        concat += [(P(img), s / TEMPO if s else d_frames - fixed)]
    sents = [x for x in re.split(r"(?<=[.?!\u201d\"])\s+", en[n - 1]) if x]
    parts = []
    for x in sents:
        while len(x) > 95:
            cut = max(x.rfind(", ", 0, 85), x.rfind(": ", 0, 85))
            if cut < 25: break
            parts.append(x[:cut + 1]); x = x[cut + 2:]
        parts.append(x)
    total = sum(len(x) for x in parts); t = t0 + 0.15
    for x in parts:
        span = (d - 0.3) * len(x) / total
        subs.append((t, t + span, x)); t += span
    t0 += d
open(P("subs.srt"), "w", encoding="utf-8").write(
    "\n".join(f"{i}\n{ts(a)} --> {ts(b)}\n{x}\n" for i, (a, b, x) in enumerate(subs, 1)))
open(P("audio.txt"), "w").write("\n".join(f"file '{a}'" for a in audio).replace("\\", "/"))
print("voice", round(t0, 1), "video", round(t0 + END_HOLD, 1))

clips, made = [], 0
for i, (img, secs) in enumerate(concat):
    clip = P(f"clip{i:02}.mp4"); frames = round(secs * 30)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", "30", "-i", img,
                    "-frames:v", str(frames), "-c:v", "libx264", "-crf", "20", "-preset", "medium",
                    "-pix_fmt", "yuv420p", clip], check=True)
    clips.append(clip); made += frames
open(P("clips.txt"), "w").write("\n".join(f"file '{c}'" for c in clips).replace("\\", "/"))
print("image track", round(made / 30, 2))

out = os.path.join(HERE, "BEZEN_Reader_Open_Agentic_Web_2026.mp4")
style = "FontName=Arial,FontSize=11,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=1,Shadow=0,MarginV=14,MarginL=20,MarginR=20"
subprocess.run(["ffmpeg", "-v", "error", "-y",
                "-f", "concat", "-safe", "0", "-i", "clips.txt",
                "-f", "concat", "-safe", "0", "-i", "audio.txt",
                "-filter_complex", f"[0:v]subtitles=subs.srt:force_style='{style}'[v];[1:a]apad=pad_dur={END_HOLD}[a]",
                "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "20", "-preset", "medium",
                "-c:a", "aac", "-b:a", "160k", "-shortest", out], cwd=B, check=True)
print("built", out, round(dur(out), 1))
