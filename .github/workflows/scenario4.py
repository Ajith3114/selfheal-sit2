# scenario4.py  —  6F School of IT  |  Scenario 4: CI/CD with GitHub Actions, that fixes itself
#
# SETUP (one time):
#   pip install manim
#   (Manim also needs ffmpeg + a LaTeX install is optional; we avoid LaTeX by using Text, not Tex)
#
# RENDER:
#   manim -pqh scenario4.py Scenario4        # high quality, opens when done
#   manim -pql scenario4.py Scenario4        # low quality, fast preview
#   python scenario4.py                      # or just hit Run in VS Code
#
# Same theme and helpers as scenario1.py / scenario2.py, so all three cut together.
#
# WHO THIS IS FOR: a fresher who has never seen a pipeline. So every command shown
# on screen is a command they could actually type. No jargon in the captions.
#
# THE LOOP THIS SCENE DRAWS:
#   You -> GitHub -> Actions -> Live Site -> Health Check
#                                  |              |
#                                  |              +-- fails? roll back, site stays up
#                                  +-- AI Agent -> Fix PR -> back to GitHub

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


def tick(color=GREEN, w=8):
    """A green check mark, drawn from two strokes - no icon font needed."""
    t = VMobject(stroke_color=color, stroke_width=w)
    t.set_points_as_corners([LEFT * 0.20 + UP * 0.04, DOWN * 0.18, RIGHT * 0.32 + UP * 0.30])
    return t


def terminal(cmds, note=None, w=7.6):
    """A little terminal window. Returns (group, rows) where each row is
    VGroup(prompt, command) - so the caller can show the "$" and then type."""
    n_rows = len(cmds) + (1 if note else 0)
    h = 0.95 + 0.44 * n_rows
    panel = RoundedRectangle(width=w, height=h, corner_radius=0.16,
                             fill_color="#0a1026", fill_opacity=1,
                             stroke_color=NAVY2, stroke_width=2)
    # the three little window buttons
    dots = VGroup(*[Dot(radius=0.055, color=c) for c in (PINK, GOLD, GREEN)])
    dots.arrange(RIGHT, buff=0.14)
    dots.move_to(panel.get_corner(UL) + RIGHT * 0.34 + DOWN * 0.3)

    lines, rows = VGroup(), []
    for i, c in enumerate(cmds):
        prompt = Text("$", font="monospace", weight=BOLD, color=GREEN).scale(0.34)
        body   = Text(c, font="monospace", color=INK).scale(0.34)
        body.next_to(prompt, RIGHT, buff=0.22)
        row = VGroup(prompt, body)
        row.move_to(panel.get_corner(UL) + RIGHT * 0.42 + DOWN * (0.82 + 0.44 * i),
                    aligned_edge=LEFT)
        lines.add(row)
        rows.append(row)

    group = VGroup(panel, dots, lines)
    if note:
        n = Text(note, font="sans-serif", color=GOLD).scale(0.3)
        n.move_to(panel.get_corner(UL) + RIGHT * 0.42 + DOWN * (0.86 + 0.44 * len(cmds)),
                  aligned_edge=LEFT)
        group.add(n)
    return group, rows


class Scenario4(Scene):
    def construct(self):
        self.camera.background_color = NAVY

        # ---------- title ----------
        brand = Text("6F School of IT", font="sans-serif", weight=BOLD, color=GOLD).scale(0.42)
        brand.to_corner(UL).shift(DOWN * 0.1 + RIGHT * 0.1)
        # keep this short - a longer string runs into the brand mark at top-left
        title = Text("Scenario 4 · A Pipeline That Fixes Itself",
                     font="sans-serif", weight=BOLD, color=WHITE).scale(0.50)
        title.to_edge(UP).shift(DOWN * 0.35)
        underline = Line(LEFT, RIGHT, color=GOLD, stroke_width=3).set_width(title.width)
        underline.next_to(title, DOWN, buff=0.12)

        self.play(FadeIn(brand, shift=RIGHT * 0.2), run_time=0.6)
        self.play(Write(title), run_time=1.0)
        self.play(GrowFromEdge(underline, LEFT), run_time=0.6)
        self.wait(0.3)

        # ---------- beat 1: the only three commands you type ----------
        cap = caption("You finished a change. Three commands send it off.")
        term, cmds = terminal([
            "git add .",
            'git commit -m "new homepage"',
            "git push",
        ], note="that is all you type. really.")
        term.move_to(DOWN * 0.35)

        self.play(FadeIn(cap), FadeIn(term[0]), FadeIn(term[1]), run_time=0.8)
        for prompt, body in cmds:
            self.play(FadeIn(prompt), run_time=0.15)
            self.play(AddTextLetterByLetter(body, run_time=0.7))
            self.wait(0.15)
        self.play(FadeIn(term[3]), run_time=0.5)
        self.wait(1.0)

        cap2 = caption("git push is the only button you press. The rest is automatic.", GOLD, s=0.38)
        self.play(Transform(cap, cap2), run_time=0.8)
        self.wait(1.0)
        self.play(FadeOut(term), run_time=0.6)

        # ---------- nodes ----------
        you    = chip("You",          "your laptop",          GOLD,   w=2.2)
        github = chip("GitHub",       "your code lives here", TEAL,   w=2.9)
        gha    = chip("Actions",      "the robot worker",     BLUE,   w=2.9)
        live   = chip("Live Site",    "what users see",       ORANGE, w=2.8)
        health = chip("Health Check", "is it really up?",     GOLD,   w=2.9, h=0.95)
        agent  = chip("AI Agent",     "reads the logs",       PINK,   w=3.2, h=0.95)
        fixpr  = chip("Fix PR",       "one-line change",      GREEN,  w=2.6, h=0.95)

        you.move_to(LEFT * 5.6 + UP * 1.5)
        github.move_to(LEFT * 2.18 + UP * 1.5)
        gha.move_to(RIGHT * 1.59 + UP * 1.5)
        live.move_to(RIGHT * 5.31 + UP * 1.5)
        health.move_to(RIGHT * 5.31 + DOWN * 0.55)
        # keep this row above y=-2.9: the caption lane lives at about y=-3.2
        agent.move_to(RIGHT * 1.59 + DOWN * 2.35)
        fixpr.move_to(LEFT * 3.0 + DOWN * 2.35)

        # ---------- beat 2: push reaches GitHub, GitHub wakes the robot ----------
        cap3 = caption("Your laptop pushes the code up to GitHub.")
        self.play(FadeIn(you, scale=0.7), Transform(cap, cap3), run_time=0.9)
        arr_yg = Arrow(you.get_right(), github.get_left(), buff=0.15,
                       color=GOLD, stroke_width=5, max_tip_length_to_length_ratio=0.14)
        self.play(GrowArrow(arr_yg), run_time=0.6)
        self.play(FadeIn(github, scale=0.7), run_time=0.8)
        d = flow_dot(GOLD).move_to(you.get_right())
        self.play(MoveAlongPath(d, arr_yg), run_time=0.6, rate_func=linear)
        self.remove(d)
        self.wait(0.4)

        cap4 = caption("GitHub sees the push and starts Actions for you.")
        arr_ga = Arrow(github.get_right(), gha.get_left(), buff=0.15,
                       color=TEAL, stroke_width=5, max_tip_length_to_length_ratio=0.14)
        self.play(Transform(cap, cap4), GrowArrow(arr_ga), run_time=0.8)
        self.play(FadeIn(gha, scale=0.7), run_time=0.8)
        self.wait(0.5)

        # ---------- beat 3: what the robot actually runs (plain commands) ----------
        diagram = VGroup(you, github, gha, arr_yg, arr_ga)
        cap5 = caption("Actions is not magic. It runs commands you already know.", s=0.38)
        term2, cmds2 = terminal([
            'grep -q "SITE-OK" index.html',
            "aws s3 cp index.html s3://my-bucket",
            "curl https://my-site.com | grep SITE-OK",
        ], note="check the file · upload it · prove it is really live")
        term2.move_to(DOWN * 0.6)

        self.play(diagram.animate.set_opacity(0.22), Transform(cap, cap5), run_time=0.7)
        self.play(FadeIn(term2[0]), FadeIn(term2[1]), run_time=0.5)
        for prompt, body in cmds2:
            self.play(FadeIn(prompt), run_time=0.15)
            self.play(AddTextLetterByLetter(body, run_time=0.75))
            self.wait(0.1)
        self.play(FadeIn(term2[3]), run_time=0.5)
        self.wait(1.4)
        self.play(FadeOut(term2), diagram.animate.set_opacity(1), run_time=0.7)

        # ---------- beat 4: it goes live, then gets checked for real ----------
        cap6 = caption("It uploads your file. Your new version is live.")
        arr_al = Arrow(gha.get_right(), live.get_left(), buff=0.15,
                       color=BLUE, stroke_width=5, max_tip_length_to_length_ratio=0.14)
        self.play(Transform(cap, cap6), GrowArrow(arr_al), run_time=0.8)
        self.play(FadeIn(live, scale=0.7), run_time=0.8)
        d = flow_dot(BLUE).move_to(gha.get_right())
        self.play(MoveAlongPath(d, arr_al), run_time=0.6, rate_func=linear)
        self.remove(d)
        self.wait(0.4)

        # down arrow = the check, up arrow = the rollback. Two lanes, no confusion.
        arr_check = Arrow(live.get_bottom() + LEFT * 0.38, health.get_top() + LEFT * 0.38,
                          buff=0.12, color=GOLD, stroke_width=4,
                          max_tip_length_to_length_ratio=0.2)
        lbl_check = Text("curl", font="monospace", color=GOLD).scale(0.28)
        lbl_check.next_to(arr_check, LEFT, buff=0.12)

        cap7 = caption("Then it opens your real URL and looks for a marker word.", s=0.38)
        self.play(Transform(cap, cap7), GrowArrow(arr_check), FadeIn(lbl_check), run_time=0.8)
        self.play(FadeIn(health, scale=0.7), run_time=0.8)
        self.wait(0.6)

        # ---------- beat 5: it fails - and the site is saved ----------
        cap8 = caption("The marker is missing. This build is bad.", PINK)
        cross = Cross(health[0], stroke_color=PINK, stroke_width=6).scale(0.85)
        self.play(Transform(cap, cap8), Create(cross),
                  health[0].animate.set_fill(PINK), run_time=0.9)
        self.wait(0.8)

        arr_back = Arrow(health.get_top() + RIGHT * 0.38, live.get_bottom() + RIGHT * 0.38,
                         buff=0.12, color=GREEN, stroke_width=5,
                         max_tip_length_to_length_ratio=0.2)
        lbl_back = Text("rollback", font="monospace", weight=BOLD, color=GREEN).scale(0.28)
        lbl_back.next_to(arr_back, RIGHT, buff=0.12)

        cap9 = caption("So Actions puts the last good version back, by itself.", GREEN, s=0.38)
        self.play(Transform(cap, cap9), GrowArrow(arr_back), FadeIn(lbl_back), run_time=0.9)
        d = flow_dot(GREEN).move_to(health.get_top() + RIGHT * 0.38)
        self.play(MoveAlongPath(d, arr_back), run_time=0.6, rate_func=linear)
        self.remove(d)
        self.play(Indicate(live, color=GREEN, scale_factor=1.06), run_time=0.7)

        cap10 = caption("Your visitors never saw the broken version. Nothing to panic about.",
                        GOLD, s=0.36)
        self.play(Transform(cap, cap10), run_time=0.8)
        self.wait(1.2)

        # ---------- beat 6: the AI agent picks up the failure ----------
        cap11 = caption("The red run wakes an AI agent. Rollback saved the site;", s=0.38)
        arr_ha = Arrow(health.get_bottom(), agent.get_right(), buff=0.18,
                       color=PINK, stroke_width=4, max_tip_length_to_length_ratio=0.12)
        self.play(Transform(cap, cap11), GrowArrow(arr_ha), run_time=0.8)
        self.play(FadeIn(agent, scale=0.7), run_time=0.8)
        cap12 = caption("the agent's job is to fix the code that caused it.", s=0.38)
        self.play(Transform(cap, cap12), run_time=0.6)
        self.wait(0.5)

        cap13 = caption("It reads the failed logs and your files, like you would.", s=0.38)
        self.play(Transform(cap, cap13), Circumscribe(agent, color=GOLD, run_time=1.2))
        self.wait(0.4)

        cap14 = caption("It finds the cause: the marker word was deleted from the page.",
                        GOLD, s=0.36)
        self.play(Transform(cap, cap14), Indicate(agent, color=GOLD, scale_factor=1.08),
                  run_time=0.9)
        self.wait(0.8)

        # ---------- beat 7: it opens a PR, a human merges it ----------
        cap15 = caption("It writes the one-line fix and opens a pull request.")
        arr_ap = Arrow(agent.get_left(), fixpr.get_right(), buff=0.15,
                       color=GREEN, stroke_width=4, max_tip_length_to_length_ratio=0.14)
        self.play(Transform(cap, cap15), GrowArrow(arr_ap), run_time=0.8)
        self.play(FadeIn(fixpr, scale=0.7), run_time=0.8)
        self.wait(0.5)

        cap16 = caption("It cannot deploy. It can only suggest. You stay in charge.", GOLD, s=0.38)
        self.play(Transform(cap, cap16), run_time=0.8)
        self.wait(1.1)

        arr_pg = Arrow(fixpr.get_top(), github.get_bottom(), buff=0.15,
                       color=GREEN, stroke_width=4, max_tip_length_to_length_ratio=0.1)
        cap17 = caption("You read it, you merge it. The loop closes.")
        self.play(Transform(cap, cap17), GrowArrow(arr_pg), run_time=0.9)
        d = flow_dot(GREEN).move_to(fixpr.get_top())
        self.play(MoveAlongPath(d, arr_pg), run_time=0.7, rate_func=linear)
        self.remove(d)
        self.wait(0.6)

        # ---------- beat 8: the run goes green ----------
        cap18 = caption("The merge starts the pipeline again. Watch it from your terminal.",
                        s=0.36)
        term3, cmds3 = terminal(["gh run watch"], w=4.6)
        term3.move_to(LEFT * 3.4 + DOWN * 0.7)
        self.play(Transform(cap, cap18), FadeIn(term3[0]), FadeIn(term3[1]), run_time=0.7)
        self.play(FadeIn(cmds3[0][0]), run_time=0.15)
        self.play(AddTextLetterByLetter(cmds3[0][1], run_time=0.6))
        self.wait(0.6)

        self.play(FadeOut(cross), health[0].animate.set_fill(GOLD), run_time=0.5)
        # (gold = "checking again"; it goes green once the marker is found, below)
        for arr in (arr_ga, arr_al, arr_check):
            d = flow_dot(GREEN).move_to(arr.get_start())
            self.play(MoveAlongPath(d, arr), run_time=0.45, rate_func=linear)
            self.remove(d)

        ok = tick(WHITE).scale(1.25).move_to(health.get_center() + DOWN * 0.24)
        cap19 = caption("Marker found. Green run. Fixed.", GREEN)
        # NOT FadeOut(health[2]): the parent VGroup is still in the scene, so the
        # subtitle keeps rendering, and FadeOut restores its opacity on cleanup.
        # A plain opacity change sticks.
        self.play(health[2].animate.set_opacity(0),
                  health[0].animate.set_fill(GREEN), run_time=0.4)
        self.play(Create(ok), Transform(cap, cap19),
                  Indicate(health, color=GREEN, scale_factor=1.08), run_time=1.0)
        self.wait(1.0)
        self.play(FadeOut(term3), run_time=0.5)

        # ---------- closing line ----------
        done = Text("It rolls back on its own, then fixes itself — that's Scenario 4.",
                    font="sans-serif", weight=BOLD, color=WHITE).scale(0.44)
        done.to_edge(DOWN).shift(UP * 0.2)
        self.play(Transform(cap, done), run_time=0.8)
        self.wait(1.8)


# ---------- so the VS Code "Run" button works ----------
# A Manim scene is only a class definition - plain `python scenario4.py` defines it
# and exits without rendering. This hands the file to the manim CLI instead.
#   python scenario4.py           -> high quality, plays when done
#   python scenario4.py -ql       -> fast preview (any manim flags pass straight through)
if __name__ == "__main__":
    import pathlib
    import subprocess
    import sys

    here = pathlib.Path(__file__).resolve()
    flags = sys.argv[1:] or ["-pqh"]
    sys.exit(subprocess.call(
        [sys.executable, "-m", "manim", *flags, str(here), "Scenario4"],
        cwd=here.parent,   # media/ lands next to the script, same as the CLI does
    ))
