"""Manim scenes for the Gujarati GSET quiz video. Reads one clip spec from $QUIZ_CLIP_JSON."""
import os, json, glob, textwrap
from manim import *
import manimpango

for _ttf in glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "*.ttf")):
    manimpango.register_font(_ttf)

with open(os.environ["QUIZ_CLIP_JSON"], encoding="utf-8") as f:
    CFG = json.load(f)

# ---- theme -------------------------------------------------------------------
BG = "#0B1220"
PANEL = "#131C2E"
BORDER = "#2A3650"
SAFFRON = "#FF9933"
GREEN = "#22C55E"
GREEN_TINT = "#0F2A1C"
WHITE = "#F3F4F6"
GRAY = "#9CA3AF"
DIM = "#4B5563"
FONT = "Hind Vadodara"
FW, FH = 14.222, 8.0
CW = 12.8                      # content width
LABELS = "ABCD"


def wrap(s, n):
    return "\n".join(textwrap.fill(line, width=n) if line.strip() else " "
                     for line in s.split("\n"))


SYMBOLS = "Σσ→∛─│●✔"            # glyphs Hind Vadodara lacks -> Segoe UI Symbol
SYMBOL_FONT = "Segoe UI Symbol"


def sym(s):
    return {ch: SYMBOL_FONT for ch in set(s) if ch in SYMBOLS}


def txt(s, size=30, color=WHITE, n=60, weight=NORMAL):
    s = wrap(s, n)
    return Text(s, font=FONT, font_size=size, color=color, weight=weight,
                line_spacing=0.9, t2f=sym(s))


def fit(m, w, h):
    if m.width > w:
        m.scale_to_fit_width(w)
    if m.height > h:
        m.scale_to_fit_height(h)
    return m


def background():
    base = Rectangle(width=FW + 1, height=FH + 1, fill_color=BG, fill_opacity=1, stroke_width=0)
    g1 = Circle(radius=4.5, stroke_width=0, fill_color=SAFFRON, fill_opacity=0.035).to_corner(UL, buff=-2.8)
    g2 = Circle(radius=4.5, stroke_width=0, fill_color=GREEN, fill_opacity=0.035).to_corner(DR, buff=-2.8)
    return VGroup(base, g1, g2)


def sound(scene, beat):
    if beat.get("audio"):
        scene.add_sound(beat["audio"])
    return float(beat.get("dur", 1.0))


def say_with(scene, beat, anims, run_time=0.6):
    """Start beat audio, play the entrance animations, then hold for the rest of the audio."""
    dur = sound(scene, beat)
    if anims:
        scene.play(*anims, run_time=min(run_time, max(0.3, dur * 0.4)))
        dur -= min(run_time, max(0.3, dur * 0.4))
    scene.wait(max(0.15, dur + 0.25))


def top_bar(section, idx, total):
    brand = Text("GSET ડિસેમ્બર 2024 • પેપર-1", font=FONT, font_size=22, color=SAFFRON, weight=BOLD)
    brand.to_corner(UL, buff=0.35)
    sec = Text(section, font=FONT, font_size=22, color=GRAY)
    sec.next_to(brand, RIGHT, buff=0.5)
    parts = [brand, sec]
    if idx:
        prog = Text(f"પ્રશ્ન {idx}/{total}", font=FONT, font_size=24, color=WHITE, weight=BOLD)
        prog.to_corner(UR, buff=0.35)
        parts.append(prog)
    track = Line(LEFT * (FW / 2 - 0.35), RIGHT * (FW / 2 - 0.35), color=DIM, stroke_width=5)
    track.next_to(brand, DOWN, buff=0.18).set_x(0)
    parts.append(track)
    if idx:
        frac = idx / total
        fill = Line(track.get_left(), track.get_left() + RIGHT * (FW - 0.7) * frac,
                    color=SAFFRON, stroke_width=5)
        parts.append(fill)
    return VGroup(*parts)


# ---- title / section / passage / outro ------------------------------------------
class IntroScene(Scene):
    def construct(self):
        self.add(background())
        c = CFG
        t1 = Text("GSET પેપર-1", font=FONT, font_size=72, color=SAFFRON, weight=BOLD)
        t2 = Text("ડિસેમ્બર 2024 — સંપૂર્ણ ઉકેલ", font=FONT, font_size=46, color=WHITE, weight=BOLD)
        t3 = Text("50 પ્રશ્નો • વિકલ્પો • સાચો જવાબ • વિગતવાર સમજૂતી", font=FONT, font_size=28, color=GRAY)
        g = VGroup(t1, t2, t3).arrange(DOWN, buff=0.45)
        line = Line(LEFT * 3, RIGHT * 3, color=SAFFRON, stroke_width=4).next_to(g, DOWN, buff=0.5)
        say_with(self, c["beats"][0], [FadeIn(g, shift=UP * 0.3), Create(line)], 1.0)
        self.wait(0.3)


class SectionScene(Scene):
    def construct(self):
        self.add(background())
        c = CFG
        tag = Text(f"વિભાગ {c['num']}", font=FONT, font_size=30, color=GRAY, weight=BOLD)
        name = Text(c["title"], font=FONT, font_size=56, color=SAFFRON, weight=BOLD)
        fit(name, CW, 2)
        rng = Text(c["range"], font=FONT, font_size=28, color=WHITE)
        g = VGroup(tag, name, rng).arrange(DOWN, buff=0.4)
        line = Line(LEFT * 2.5, RIGHT * 2.5, color=SAFFRON, stroke_width=4).next_to(g, DOWN, buff=0.4)
        say_with(self, c["beats"][0], [FadeIn(g, shift=UP * 0.2), Create(line)], 0.8)
        self.wait(0.2)


class PassageScene(Scene):
    def construct(self):
        self.add(background())
        c = CFG
        self.add(top_bar(c["section"], 0, 0))
        head = Text(c["title"], font=FONT, font_size=34, color=SAFFRON, weight=BOLD)
        head.to_edge(UP, buff=0.95)
        self.play(FadeIn(head), run_time=0.4)
        area_top = head.get_bottom()[1] - 0.3
        for beat in c["beats"]:
            body = txt(beat["show"], size=27, n=78, color=WHITE)
            fit(body, CW, area_top - (-FH / 2 + 0.4))
            body.next_to(head, DOWN, buff=0.35).set_x(0)
            say_with(self, beat, [FadeIn(body)])
            self.play(FadeOut(body), run_time=0.3)


class OutroScene(Scene):
    def construct(self):
        self.add(background())
        c = CFG
        t1 = Text("અભિનંદન! પેપર પૂર્ણ થયું", font=FONT, font_size=60, color=SAFFRON, weight=BOLD)
        t2 = Text("ખોટા પડેલા પ્રશ્નોની સમજૂતી ફરી જુઓ • GSET માટે શુભેચ્છાઓ", font=FONT, font_size=30, color=WHITE)
        g = VGroup(t1, t2).arrange(DOWN, buff=0.5)
        fit(g, CW, 3)
        say_with(self, c["beats"][0], [FadeIn(g, shift=UP * 0.2)], 1.0)
        self.wait(0.8)


# ---- question ------------------------------------------------------------------
def option_card(label, text, width, size=28, n=40):
    badge = Circle(radius=0.28, color=GRAY, stroke_width=2, fill_color=BG, fill_opacity=1)
    letter = Text(label, font=FONT, font_size=24, color=GRAY, weight=BOLD).move_to(badge)
    body = txt(text, size=size, n=n, color=WHITE)
    fit(body, width - 1.2, 2.2)
    h = max(0.62, body.height + 0.34)
    rect = RoundedRectangle(width=width, height=h, corner_radius=0.14, fill_color=PANEL,
                            fill_opacity=1, stroke_color=BORDER, stroke_width=2)
    VGroup(badge, letter).move_to(rect).align_to(rect, LEFT).shift(RIGHT * 0.22)
    body.move_to(rect).align_to(rect, LEFT).shift(RIGHT * 0.95)
    card = VGroup(rect, badge, letter, body)
    card.rect, card.badge, card.letter, card.body = rect, badge, letter, body
    return card


class QuestionScene(Scene):
    def construct(self):
        self.add(background())
        c = CFG
        beats = c["beats"]
        get = lambda role: [b for b in beats if b["role"] == role]
        bar = top_bar(c["section"], c["n"], c["total"])
        self.add(bar)

        # question
        qtag = Text(f"પ્રશ્ન {c['n']}", font=FONT, font_size=32, color=SAFFRON, weight=BOLD)
        qtag.next_to(bar, DOWN, buff=0.3).to_edge(LEFT, buff=0.7)
        qtext = txt(c["q"], size=35, n=c.get("qwrap", 56), color=WHITE)
        fit(qtext, CW, c.get("qmaxh", 3.2))
        qtext.next_to(qtag, DOWN, buff=0.18, aligned_edge=LEFT)

        # options
        short = all(len(o) <= 26 for o in c["opts"])
        bottom_reserve = -FH / 2 + 1.55          # keep space for countdown / badge
        avail = qtext.get_bottom()[1] - 0.4 - bottom_reserve
        # shrink the font (not the card width) until the options fit; long options that
        # don't fit as a list fall back to a 2x2 grid of wrapped cards
        tries = [(s, short) for s in (32, 30, 28, 26)] + [(s, True) for s in (26, 24, 22)] \
            if not short else [(s, True) for s in (32, 30, 28, 26, 24, 22)]
        for size, grid in tries:
            if grid:
                w = (CW - 0.4) / 2
                cards = [option_card(LABELS[i], o, w, size=size, n=int(24 * 32 / size))
                         for i, o in enumerate(c["opts"])]
                hmax = max(k.height for k in cards)
                for k in cards:
                    k.rect.stretch_to_fit_height(hmax)
                group = VGroup(VGroup(cards[0], cards[1]).arrange(RIGHT, buff=0.4),
                               VGroup(cards[2], cards[3]).arrange(RIGHT, buff=0.4)).arrange(DOWN, buff=0.25)
            else:
                cards = [option_card(LABELS[i], o, CW, size=size, n=int(66 * 30 / size))
                         for i, o in enumerate(c["opts"])]
                group = VGroup(*cards).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
            if group.height <= avail:
                break
        fit(group, CW, max(1.6, avail))
        group.next_to(qtext, DOWN, buff=0.4).set_x(0)
        # centre the question+options block in the free vertical space
        slack = group.get_bottom()[1] - bottom_reserve
        if slack > 0.2:
            VGroup(qtag, qtext, group).shift(DOWN * min(slack / 2, 0.9))

        say_with(self, get("question")[0], [FadeIn(qtag), FadeIn(qtext, shift=UP * 0.15)])
        for i, b in enumerate(get("option")):
            say_with(self, b, [FadeIn(cards[i], shift=RIGHT * 0.2)], 0.45)

        # 3-second think time
        self.countdown()

        # reveal
        ai = LABELS.index(c["ans"])
        anims = []
        for i, k in enumerate(cards):
            if i == ai:
                anims += [k.rect.animate.set_stroke(GREEN, width=4).set_fill(GREEN_TINT, 1),
                          k.badge.animate.set_stroke(GREEN, width=3).set_fill(GREEN, 1),
                          k.letter.animate.set_color(BG), k.body.animate.set_color(GREEN)]
            else:
                anims.append(k.animate.set_opacity(0.28))
        badge_s = f"✔  સાચો જવાબ: ({c['ans']})"
        badge_t = Text(badge_s, font=FONT, font_size=30, color=BG, weight=BOLD, t2f=sym(badge_s))
        badge = VGroup(SurroundingRectangle(badge_t, color=GREEN, fill_color=GREEN, fill_opacity=1,
                                            buff=0.18, corner_radius=0.1), badge_t)
        badge.to_edge(DOWN, buff=0.35)
        say_with(self, get("reveal")[0], anims + [FadeIn(badge, scale=1.2)], 0.7)

        # explanation
        self.play(FadeOut(group), FadeOut(badge), FadeOut(qtag),
                  qtext.animate.scale(min(0.62, 1.3 / qtext.height)).next_to(bar, DOWN, buff=0.28).to_edge(LEFT, buff=0.7).set_opacity(0.55),
                  run_time=0.6)
        ans_line = txt(f"✔ સાચો જવાબ: ({c['ans']})  {c['opts'][ai]}", size=28, n=80, color=GREEN, weight=BOLD)
        fit(ans_line, CW, 0.9)
        ans_line.next_to(qtext, DOWN, buff=0.25, aligned_edge=LEFT)
        head = Text("સમજૂતી", font=FONT, font_size=30, color=SAFFRON, weight=BOLD)
        head.next_to(ans_line, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(FadeIn(ans_line), FadeIn(head), run_time=0.4)

        top = head.get_bottom()[1] - 0.2
        bottom = -FH / 2 + 0.35
        shown = []
        y = top
        for b in get("step"):
            blk = self.step_block(b)
            if blk.height > top - bottom:
                fit(blk, CW, top - bottom)
            if y - blk.height < bottom and shown:       # page break
                self.play(*[FadeOut(s) for s in shown], run_time=0.3)
                shown, y = [], top
            blk.move_to([0, 0, 0]).to_edge(LEFT, buff=0.7)
            blk.shift(UP * (y - blk.get_top()[1]))
            shown.append(blk)
            y = blk.get_bottom()[1] - 0.22
            say_with(self, b, [FadeIn(blk, shift=UP * 0.1)], 0.5)
        self.wait(0.6)

    def step_block(self, b):
        kind = b.get("kind", "text")
        if kind == "math":
            t = txt(b["show"], size=34, n=64, color=SAFFRON, weight=BOLD)
            box = SurroundingRectangle(t, color=BORDER, fill_color=PANEL, fill_opacity=1,
                                       buff=0.2, corner_radius=0.1)
            return fit(VGroup(box, t), CW, 3.0)
        dot = Dot(radius=0.07, color=SAFFRON)
        t = txt(b["show"], size=30, n=70, color=WHITE)
        fit(t, CW - 0.5, 3.2)
        dot.next_to(t, LEFT, buff=0.22).align_to(t, UP).shift(DOWN * 0.13)
        return VGroup(dot, t)

    def countdown(self):
        ring_bg = Circle(radius=0.55, color=DIM, stroke_width=8).to_edge(DOWN, buff=0.45)
        center = ring_bg.get_center()
        t = ValueTracker(1.0)
        arc = always_redraw(lambda: Arc(radius=0.55, start_angle=PI / 2,
                                        angle=-TAU * max(t.get_value(), 0.001),
                                        color=SAFFRON, stroke_width=8, arc_center=center))
        digits = {n: Text(n, font=FONT, font_size=44, color=WHITE, weight=BOLD).move_to(center)
                  for n in "123"}
        num = always_redraw(lambda: digits[str(min(3, int(t.get_value() * 3 - 1e-6) + 1))].copy())
        label = Text("વિચારો…", font=FONT, font_size=26, color=GRAY).next_to(ring_bg, LEFT, buff=0.35)
        self.add(ring_bg, arc, num, label)
        self.play(t.animate.set_value(0.0), run_time=3.0, rate_func=linear)
        self.remove(ring_bg, arc, num, label)
