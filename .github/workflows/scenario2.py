# scenario2.py  —  6F School of IT  |  Scenario 2: S3 -> CloudFront -> WAF -> ACM -> Route 53
#
# SETUP (one time):
#   pip install manim
#   (Manim also needs ffmpeg + a LaTeX install is optional; we avoid LaTeX by using Text, not Tex)
#
# RENDER:
#   manim -pqh scenario2.py Scenario2        # high quality, opens when done
#   manim -pql scenario2.py Scenario2        # low quality, fast preview
#
# Same theme and helpers as scenario1.py, so the two videos cut together.
#
# NOTE ON DIRECTION - this is the whole point of the scene:
#   You BUILD it   S3 -> CloudFront -> WAF -> ACM -> Route 53   (origin first, door last)
#   Traffic FLOWS  Route 53 -> CloudFront -> S3                 (the other way round)
# The scene assembles in build order, then reverses to show a live request.

from manim import *

# ---- 6F theme palette ----
NAVY   = "#16224d"   # background
NAVY2  = "#1e2f63"   # panels
PINK   = "#ef476f"
ORANGE = "#f78c1e"
TEAL   = "#2ec4b6"
BLUE   = "#118ab2"
GOLD   = "#ffd166"
GREEN  = "#06a77d"
INK    = "#e9f1fc"   # light text


def chip(label, sub, color, w=2.6, h=1.05):
    """A rounded service box with a title and a small subtitle, grouped together."""
    box = RoundedRectangle(width=w, height=h, corner_radius=0.16,
                           fill_color=color, fill_opacity=1, stroke_width=0)
    title = Text(label, font="sans-serif", weight=BOLD, color=WHITE).scale(0.42)
    subt  = Text(sub,   font="sans-serif", color=INK).scale(0.28)
    title.move_to(box.get_center() + UP * 0.15)
    subt.move_to(box.get_center() + DOWN * 0.22)
    return VGroup(box, title, subt)


def flow_dot(color=GOLD):
    return Dot(radius=0.09, color=color)


def caption(txt, color=INK, s=0.4):
    """One line of plain English, parked at the bottom of the frame."""
    t = Text(txt, font="sans-serif", color=color).scale(s)
    t.to_edge(DOWN).shift(UP * 0.2)
    return t


def padlock(color=GREEN):
    """A tiny padlock built from primitives - no icon font, no LaTeX."""
    body = RoundedRectangle(width=0.52, height=0.42, corner_radius=0.09,
                            fill_color=color, fill_opacity=1, stroke_width=0)
    shackle = Arc(radius=0.16, start_angle=0, angle=PI, color=color, stroke_width=6)
    shackle.next_to(body, UP, buff=-0.03)
    return VGroup(body, shackle)


def back(arrow):
    """Same arrow, walked backwards - for return traffic."""
    return arrow.copy().reverse_points()


class Scenario2(Scene):
    def construct(self):
        self.camera.background_color = NAVY

        # ---------- title ----------
        brand = Text("6F School of IT", font="sans-serif", weight=BOLD, color=GOLD).scale(0.42)
        brand.to_corner(UL).shift(DOWN * 0.1 + RIGHT * 0.1)
        # keep this short - a longer string runs into the brand mark at top-left
        title = Text("Scenario 2 · A Static Site, Served Worldwide",
                     font="sans-serif", weight=BOLD, color=WHITE).scale(0.50)
        title.to_edge(UP).shift(DOWN * 0.35)
        underline = Line(LEFT, RIGHT, color=GOLD, stroke_width=3).set_width(title.width)
        underline.next_to(title, DOWN, buff=0.12)

        self.play(FadeIn(brand, shift=RIGHT * 0.2), run_time=0.6)
        self.play(Write(title), run_time=1.0)
        self.play(GrowFromEdge(underline, LEFT), run_time=0.6)
        self.wait(0.3)

        # ---------- nodes ----------
        # Left to right is the path a request takes. We build them right to left.
        user = chip("User",       "visitor",          GOLD,   w=2.0)
        r53  = chip("Route 53",   "your domain name", TEAL,   w=2.8)
        cf   = chip("CloudFront", "the edge cache",   BLUE,   w=3.0)
        s3   = chip("S3",         "the origin",       ORANGE, w=2.7)
        waf  = chip("WAF",        "the bouncer",      PINK,   w=2.6, h=0.95)
        acm  = chip("ACM",        "the HTTPS cert",   GREEN,  w=2.9, h=0.95)

        user.move_to(LEFT * 5.5)
        r53.move_to(LEFT * 2.2)
        cf.move_to(RIGHT * 1.6)
        s3.move_to(RIGHT * 5.3)
        waf.move_to(RIGHT * 1.6 + UP * 2.05)      # sits on top of CloudFront
        acm.move_to(RIGHT * 1.6 + DOWN * 2.05)    # feeds CloudFront from below

        # ---------- build it, in the order you actually create it ----------

        # 1. S3 - the files
        cap = caption("Your website is just files. They sit in an S3 bucket.")
        self.play(FadeIn(s3, scale=0.7), FadeIn(cap), run_time=0.9)
        self.wait(0.6)

        note = Text("private · not public", font="sans-serif", color=INK).scale(0.26)
        note.next_to(s3, DOWN, buff=0.18)
        self.play(FadeIn(note, shift=UP * 0.1), run_time=0.5)
        self.wait(0.4)

        # 2. CloudFront - the edge cache
        arr_cs = Arrow(cf.get_right(), s3.get_left(), buff=0.15,
                       color=ORANGE, stroke_width=5, max_tip_length_to_length_ratio=0.12)
        cap2 = caption("CloudFront copies those files to edge locations worldwide.")
        self.play(FadeIn(cf, scale=0.7), Transform(cap, cap2), run_time=0.9)
        self.play(GrowArrow(arr_cs), run_time=0.7)
        self.wait(0.5)

        cap3 = caption("Only CloudFront is allowed to read the bucket. Nobody else.", s=0.38)
        self.play(Transform(cap, cap3), Indicate(note, color=GOLD, scale_factor=1.15), run_time=0.9)
        self.wait(0.6)

        # 3. WAF - inspects every request on the way in
        arr_wc = DoubleArrow(waf.get_bottom(), cf.get_top(), buff=0.15,
                             color=PINK, stroke_width=4, max_tip_length_to_length_ratio=0.14)
        cap4 = caption("WAF stands in front and inspects every request that arrives.", s=0.38)
        self.play(FadeIn(waf, scale=0.7), Transform(cap, cap4), run_time=0.9)
        self.play(GrowArrow(arr_wc), run_time=0.6)
        self.wait(0.5)

        # 4. ACM - the certificate that turns http into https
        arr_ac = Arrow(acm.get_top(), cf.get_bottom(), buff=0.15,
                       color=GREEN, stroke_width=4, max_tip_length_to_length_ratio=0.14)
        cap5 = caption("ACM hands CloudFront the certificate. That is the s in https.", s=0.38)
        self.play(FadeIn(acm, scale=0.7), Transform(cap, cap5), run_time=0.9)
        self.play(GrowArrow(arr_ac), run_time=0.6)

        # the padlock travels up from ACM and clips onto CloudFront
        lock = padlock(GREEN).move_to(acm.get_top() + UP * 0.1)
        self.play(FadeIn(lock, scale=0.5), run_time=0.4)
        # park it just OUTSIDE the top-left corner - inside the box it reads as a blob
        self.play(lock.animate.move_to(cf.get_corner(UL) + RIGHT * 0.32 + UP * 0.34), run_time=0.8)
        https = Text("https", font="sans-serif", weight=BOLD, color=GREEN).scale(0.26)
        https.next_to(lock, RIGHT, buff=0.12)
        self.play(FadeIn(https, shift=RIGHT * 0.1), run_time=0.4)
        self.wait(0.5)

        # 5. Route 53 - the name that points at all of it
        arr_rc = Arrow(r53.get_right(), cf.get_left(), buff=0.15,
                       color=TEAL, stroke_width=5, max_tip_length_to_length_ratio=0.12)
        cap6 = caption("Route 53 points your domain name at CloudFront.")
        self.play(FadeIn(r53, scale=0.7), Transform(cap, cap6), run_time=0.9)
        self.play(GrowArrow(arr_rc), run_time=0.7)
        self.wait(0.6)

        # ---------- now flip it: the request travels the other way ----------
        cap7 = caption("You built it right to left. Traffic runs left to right.", GOLD)
        self.play(Transform(cap, cap7), run_time=0.8)
        self.wait(0.8)

        arr_ur = Arrow(user.get_right(), r53.get_left(), buff=0.15,
                       color=GOLD, stroke_width=5, max_tip_length_to_length_ratio=0.12)
        cap8 = caption("A visitor types your domain into a browser.")
        self.play(FadeIn(user, scale=0.7), Transform(cap, cap8), run_time=0.9)
        self.play(GrowArrow(arr_ur), run_time=0.7)
        self.wait(0.4)

        # ---------- request 1: cache MISS, all the way to S3 ----------
        cap9 = caption("First the browser asks Route 53: where does this domain live?", s=0.38)
        self.play(Transform(cap, cap9), run_time=0.5)
        d = flow_dot(GOLD).move_to(user.get_right())
        self.play(MoveAlongPath(d, arr_ur), run_time=0.7, rate_func=linear)
        self.play(Indicate(r53, color=WHITE, scale_factor=1.06), run_time=0.5)
        self.remove(d)

        cap10 = caption("Route 53 answers: CloudFront. The request heads there.")
        self.play(Transform(cap, cap10), run_time=0.5)
        d = flow_dot(TEAL).move_to(r53.get_right())
        self.play(MoveAlongPath(d, arr_rc), run_time=0.7, rate_func=linear)

        # WAF gets a look at it first
        cap11 = caption("WAF checks it. Clean request, so it passes.", GREEN)
        self.play(Transform(cap, cap11), Indicate(waf, color=GREEN, scale_factor=1.1), run_time=0.8)
        self.remove(d)

        cap12 = caption("Nothing cached yet, so CloudFront fetches the file from S3.", s=0.38)
        self.play(Transform(cap, cap12), run_time=0.5)
        d = flow_dot(ORANGE).move_to(cf.get_right())
        self.play(MoveAlongPath(d, arr_cs), run_time=0.7, rate_func=linear)
        self.remove(d)
        d = flow_dot(ORANGE).move_to(s3.get_left())
        self.play(MoveAlongPath(d, back(arr_cs)), run_time=0.7, rate_func=linear)
        self.remove(d)
        self.play(Indicate(cf, color=WHITE, scale_factor=1.06), run_time=0.5)

        # ...and back to the visitor
        d = flow_dot(GREEN).move_to(cf.get_left())
        self.play(MoveAlongPath(d, back(arr_rc)), run_time=0.6, rate_func=linear)
        self.remove(d)
        d = flow_dot(GREEN).move_to(r53.get_left())
        self.play(MoveAlongPath(d, back(arr_ur)), run_time=0.6, rate_func=linear)
        self.remove(d)
        self.wait(0.5)

        # ---------- request 2: cache HIT, S3 is never touched ----------
        cap13 = caption("Now the file is cached at the edge. Watch the next visitor.", GOLD, s=0.38)
        self.play(Transform(cap, cap13), run_time=0.6)

        cached = Text("cached", font="sans-serif", weight=BOLD, color=GOLD).scale(0.26)
        cached.next_to(cf, UP, buff=0.16).shift(RIGHT * 0.95)
        self.play(FadeIn(cached, shift=DOWN * 0.1), run_time=0.4)

        self.play(arr_cs.animate.set_opacity(0.2), s3.animate.set_opacity(0.4),
                  note.animate.set_opacity(0.3), run_time=0.6)

        for _ in range(2):
            d = flow_dot(GOLD).move_to(user.get_right())
            self.play(MoveAlongPath(d, arr_ur), run_time=0.45, rate_func=linear)
            self.remove(d)
            d = flow_dot(TEAL).move_to(r53.get_right())
            self.play(MoveAlongPath(d, arr_rc), run_time=0.45, rate_func=linear)
            self.remove(d)
            d = flow_dot(GREEN).move_to(cf.get_left())
            self.play(MoveAlongPath(d, back(arr_rc)), run_time=0.45, rate_func=linear)
            self.remove(d)
            d = flow_dot(GREEN).move_to(r53.get_left())
            self.play(MoveAlongPath(d, back(arr_ur)), run_time=0.45, rate_func=linear)
            self.remove(d)

        cap14 = caption("Served from the edge. S3 was never touched — and never billed.", s=0.38)
        self.play(Transform(cap, cap14), run_time=0.7)
        self.wait(0.9)

        self.play(arr_cs.animate.set_opacity(1), s3.animate.set_opacity(1),
                  note.animate.set_opacity(1), FadeOut(cached), run_time=0.6)

        # ---------- the payoff: WAF stops an attack at the edge ----------
        cap15 = caption("Now a bad request comes in.", PINK)
        self.play(Transform(cap, cap15), run_time=0.6)

        bad = flow_dot(PINK).scale(1.3).move_to(user.get_right())
        self.play(MoveAlongPath(bad, arr_ur), run_time=0.5, rate_func=linear)
        self.play(MoveAlongPath(bad, arr_rc), run_time=0.5, rate_func=linear)

        blocked = Cross(bad, stroke_color=PINK, stroke_width=6).scale(2.2)
        cap16 = caption("WAF blocks it at the edge. It never reaches your bucket.", PINK, s=0.38)
        self.play(Indicate(waf, color=PINK, scale_factor=1.15),
                  Create(blocked), Transform(cap, cap16), run_time=0.9)
        self.wait(0.8)
        self.play(FadeOut(bad), FadeOut(blocked), run_time=0.5)

        # ---------- closing line ----------
        done = Text("One private bucket, served worldwide, over HTTPS — that's Scenario 2.",
                    font="sans-serif", weight=BOLD, color=WHITE).scale(0.44)
        done.to_edge(DOWN).shift(UP * 0.2)
        self.play(Transform(cap, done), run_time=0.8)
        self.wait(1.5)

# ---------- so the VS Code "Run" button works ----------
# A Manim scene is only a class definition - plain `python scenario2.py` defines it
# and exits without rendering. This hands the file to the manim CLI instead.
#   python scenario2.py           -> high quality, plays when done
#   python scenario2.py -ql       -> fast preview (any manim flags pass straight through)
if __name__ == "__main__":
    import pathlib
    import subprocess
    import sys

    here = pathlib.Path(__file__).resolve()
    flags = sys.argv[1:] or ["-pqh"]
    sys.exit(subprocess.call(
        [sys.executable, "-m", "manim", *flags, str(here), "Scenario2"],
        cwd=here.parent,   # media/ lands next to the script, same as the CLI does
    ))
