# scenario3.py  —  6F School of IT  |  Scenario 3: S3 -> Lambda -> Bedrock -> DynamoDB
#
# SETUP (one time):
#   pip install manim
#   (Manim also needs ffmpeg + a LaTeX install is optional; we avoid LaTeX by using Text, not Tex)
#
# RENDER:
#   manim -pqh scenario3.py Scenario3        # high quality, opens when done
#   manim -pql scenario3.py Scenario3        # low quality, fast preview
#   python scenario3.py                      # or just hit Run in VS Code
#
# Same theme and helpers as the other scenarios, so all four cut together.
#
# WHO THIS IS FOR: a fresher. Two rules I held to while writing the captions:
#   1. The words NoSQL, partition key, schema and RDS never appear. DynamoDB is
#      introduced only as "S3 holds the file, DynamoDB holds the answer" - a
#      contrast against the S3 they already met in Scenario 2.
#   2. Serverless is shown, not defined. Lambda literally sits on screen dimmed
#      and asleep until the upload wakes it, then goes back to sleep at the end.
#
# THE SHAPE THIS SCENE DRAWS:
#   You -> S3 -> Lambda <-> Bedrock
#                   |
#                   v
#               DynamoDB --> back to you, when you look it up

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


def terminal(cmds, out=None, w=8.0):
    """A little terminal window. `cmds` get a green $ prompt and are meant to be
    typed in; `out` lines are printed output, no prompt.
    Returns (group, rows, out_rows) so the caller can reveal them in order."""
    n_rows = len(cmds) + len(out or [])
    h = 0.95 + 0.44 * n_rows
    panel = RoundedRectangle(width=w, height=h, corner_radius=0.16,
                             fill_color="#0a1026", fill_opacity=1,
                             stroke_color=NAVY2, stroke_width=2)
    # the three little window buttons
    dots = VGroup(*[Dot(radius=0.055, color=c) for c in (PINK, GOLD, GREEN)])
    dots.arrange(RIGHT, buff=0.14)
    dots.move_to(panel.get_corner(UL) + RIGHT * 0.34 + DOWN * 0.3)

    def place(mob, i):
        mob.move_to(panel.get_corner(UL) + RIGHT * 0.42 + DOWN * (0.82 + 0.44 * i),
                    aligned_edge=LEFT)

    lines, rows, out_rows = VGroup(), [], []
    for i, c in enumerate(cmds):
        prompt = Text("$", font="monospace", weight=BOLD, color=GREEN).scale(0.34)
        body   = Text(c, font="monospace", color=INK).scale(0.34)
        body.next_to(prompt, RIGHT, buff=0.22)
        row = VGroup(prompt, body)
        place(row, i)
        lines.add(row)
        rows.append(row)

    for j, o in enumerate(out or []):
        line = Text(o, font="monospace", color=GOLD).scale(0.32)
        place(line, len(cmds) + j)
        lines.add(line)
        out_rows.append(line)

    return VGroup(panel, dots, lines), rows, out_rows


class Scenario3(Scene):
    def construct(self):
        self.camera.background_color = NAVY

        # ---------- title ----------
        brand = Text("6F School of IT", font="sans-serif", weight=BOLD, color=GOLD).scale(0.42)
        brand.to_corner(UL).shift(DOWN * 0.1 + RIGHT * 0.1)
        # keep this short - a longer string runs into the brand mark at top-left
        title = Text("Scenario 3 · A Resume Reader, Serverless",
                     font="sans-serif", weight=BOLD, color=WHITE).scale(0.50)
        title.to_edge(UP).shift(DOWN * 0.35)
        underline = Line(LEFT, RIGHT, color=GOLD, stroke_width=3).set_width(title.width)
        underline.next_to(title, DOWN, buff=0.12)

        self.play(FadeIn(brand, shift=RIGHT * 0.2), run_time=0.6)
        self.play(Write(title), run_time=1.0)
        self.play(GrowFromEdge(underline, LEFT), run_time=0.6)
        self.wait(0.3)

        # ---------- nodes ----------
        you = chip("You",      "one resume.pdf",     GOLD,   w=2.4)
        s3  = chip("S3",       "holds the file",     ORANGE, w=2.7)
        lam = chip("Lambda",   "runs for 3 seconds", BLUE,   w=2.8)
        bed = chip("Bedrock",  "the AI, on AWS",     PINK,   w=2.6)
        ddb = chip("DynamoDB", "one row per resume", TEAL,   w=3.4, h=0.95)

        you.move_to(LEFT * 5.5 + UP * 1.5)
        s3.move_to(LEFT * 2.1 + UP * 1.5)
        lam.move_to(RIGHT * 1.55 + UP * 1.5)
        bed.move_to(RIGHT * 5.55 + UP * 1.5)   # right-shifted: the arrow needs room
        ddb.move_to(RIGHT * 1.55 + DOWN * 1.6)

        # ---------- beat 1: one command starts everything ----------
        cap = caption("You have one resume, and one command.")
        term, cmds, _ = terminal(["aws s3 cp resume.pdf s3://my-resumes/"])
        term.move_to(DOWN * 0.3)

        self.play(FadeIn(cap), FadeIn(term[0]), FadeIn(term[1]), run_time=0.8)
        self.play(FadeIn(cmds[0][0]), run_time=0.15)
        self.play(AddTextLetterByLetter(cmds[0][1], run_time=0.9))
        self.wait(0.8)

        cap2 = caption("That upload is not just an upload. It is the trigger.", GOLD, s=0.38)
        self.play(Transform(cap, cap2), run_time=0.8)
        self.wait(1.1)
        self.play(FadeOut(term), run_time=0.6)

        # ---------- beat 2: the file lands in a bucket ----------
        cap3 = caption("The file lands in a bucket. Same S3 you met in Scenario 2.", s=0.38)
        arr_ys = Arrow(you.get_right(), s3.get_left(), buff=0.15,
                       color=GOLD, stroke_width=5, max_tip_length_to_length_ratio=0.14)
        self.play(FadeIn(you, scale=0.7), Transform(cap, cap3), run_time=0.9)
        self.play(GrowArrow(arr_ys), run_time=0.6)
        self.play(FadeIn(s3, scale=0.7), run_time=0.8)
        d = flow_dot(GOLD).move_to(you.get_right())
        self.play(MoveAlongPath(d, arr_ys), run_time=0.6, rate_func=linear)
        self.remove(d)
        self.wait(0.5)

        # ---------- beat 3: meet Lambda, asleep ----------
        # It arrives dimmed on purpose. This is the whole idea of serverless, shown
        # rather than defined - so don't "fix" the low opacity here.
        lam.set_opacity(0.3)
        asleep = Text("asleep · costs you nothing", font="sans-serif", color=INK).scale(0.28)
        asleep.next_to(lam, UP, buff=0.16)

        cap4 = caption("Next door sits Lambda. Right now it is not running at all.", s=0.38)
        self.play(FadeIn(lam), Transform(cap, cap4), run_time=0.9)
        self.play(FadeIn(asleep, shift=DOWN * 0.1), run_time=0.5)
        self.wait(0.7)

        cap5 = caption("In Scenario 1, two servers ran all night waiting. Here, nothing waits.",
                       GOLD, s=0.36)
        self.play(Transform(cap, cap5), run_time=0.8)
        self.wait(1.3)

        # ---------- beat 4: the upload wakes it ----------
        arr_sl = Arrow(s3.get_right(), lam.get_left(), buff=0.15,
                       color=ORANGE, stroke_width=5, max_tip_length_to_length_ratio=0.14)
        cap6 = caption("S3 tells Lambda a file arrived. That message wakes it up.", s=0.38)
        self.play(Transform(cap, cap6), GrowArrow(arr_sl), run_time=0.8)
        d = flow_dot(ORANGE).move_to(s3.get_right())
        self.play(MoveAlongPath(d, arr_sl), run_time=0.6, rate_func=linear)
        self.remove(d)
        self.play(lam.animate.set_opacity(1), FadeOut(asleep),
                  Flash(lam, color=GOLD, flash_radius=1.9, num_lines=14), run_time=0.9)

        cap7 = caption("No cron job. No server sitting idle. The upload did it.", GOLD, s=0.38)
        self.play(Transform(cap, cap7), run_time=0.7)
        self.wait(1.1)

        # ---------- beat 5: Lambda asks the model ----------
        arr_lb = DoubleArrow(lam.get_right(), bed.get_left(), buff=0.15,
                             color=PINK, stroke_width=4, max_tip_length_to_length_ratio=0.16)
        cap8 = caption("Lambda sends the resume text to Bedrock and asks it to judge.", s=0.37)
        self.play(Transform(cap, cap8), GrowArrow(arr_lb), run_time=0.8)
        self.play(FadeIn(bed, scale=0.7), run_time=0.8)
        d = flow_dot(PINK).move_to(lam.get_right())
        self.play(MoveAlongPath(d, arr_lb), run_time=0.5, rate_func=linear)
        self.remove(d)
        self.wait(0.4)

        cap9 = caption("Bedrock is just AWS's door to the AI. No API key to keep safe.",
                       s=0.37)
        self.play(Transform(cap, cap9), Indicate(bed, color=WHITE, scale_factor=1.06),
                  run_time=0.9)
        self.wait(0.8)

        cap10 = caption("The answer comes back: skills found, skills missing, a score.", s=0.37)
        d = flow_dot(GREEN).move_to(bed.get_left())
        self.play(Transform(cap, cap10), run_time=0.5)
        self.play(MoveAlongPath(d, arr_lb.copy().reverse_points()), run_time=0.5,
                  rate_func=linear)
        self.remove(d)
        self.wait(0.5)

        # ---------- beat 6: where the answer goes - the one DynamoDB line ----------
        arr_ld = Arrow(lam.get_bottom(), ddb.get_top(), buff=0.15,
                       color=TEAL, stroke_width=5, max_tip_length_to_length_ratio=0.16)
        cap11 = caption("S3 holds the file. DynamoDB holds the answer.", GOLD)
        self.play(Transform(cap, cap11), GrowArrow(arr_ld), run_time=0.9)
        self.play(FadeIn(ddb, scale=0.7), run_time=0.8)
        d = flow_dot(TEAL).move_to(lam.get_bottom())
        self.play(MoveAlongPath(d, arr_ld), run_time=0.6, rate_func=linear)
        self.remove(d)
        self.wait(0.6)

        cap12 = caption("One resume in, one row out. That is all you need to know for now.",
                        s=0.36)
        self.play(Transform(cap, cap12), Indicate(ddb, color=WHITE, scale_factor=1.06),
                  run_time=0.9)
        self.wait(1.1)

        # ---------- beat 7: Lambda goes back to sleep ----------
        cap13 = caption("Lambda's work is done, so Lambda disappears.", s=0.38)
        asleep2 = Text("asleep again · billed for 3 seconds",
                       font="sans-serif", color=GOLD).scale(0.28)
        asleep2.next_to(lam, UP, buff=0.16)
        self.play(Transform(cap, cap13), lam.animate.set_opacity(0.3),
                  FadeIn(asleep2, shift=DOWN * 0.1), run_time=0.9)
        self.wait(0.5)

        cap14 = caption("You paid for three seconds. Not for a month of an idle server.",
                        GOLD, s=0.37)
        self.play(Transform(cap, cap14), run_time=0.8)
        self.wait(1.3)

        # ---------- beat 8: you look the answer up ----------
        arr_dy = Arrow(ddb.get_left(), you.get_bottom(), buff=0.2,
                       color=GOLD, stroke_width=4, max_tip_length_to_length_ratio=0.08)
        lookup = Text("look it up", font="sans-serif", color=GOLD).scale(0.28)
        lookup.move_to(arr_dy.get_center() + UP * 0.28 + LEFT * 0.1)

        cap15 = caption("The answer waits in the table until you ask for it.", s=0.38)
        self.play(Transform(cap, cap15), GrowArrow(arr_dy), FadeIn(lookup), run_time=0.9)
        d = flow_dot(GOLD).move_to(ddb.get_left())
        self.play(MoveAlongPath(d, arr_dy), run_time=0.8, rate_func=linear)
        self.remove(d)
        self.wait(0.5)

        diagram = VGroup(you, s3, lam, bed, ddb, arr_ys, arr_sl, arr_lb, arr_ld,
                         arr_dy, lookup, asleep2)
        term2, cmds2, outs2 = terminal(
            ["aws dynamodb scan --table-name resumes"],
            out=["resume.pdf · score 78 · missing: docker, terraform"],
        )
        term2.move_to(DOWN * 0.3)

        cap16 = caption("One command reads it back.", s=0.38)
        self.play(diagram.animate.set_opacity(0.22), Transform(cap, cap16), run_time=0.7)
        self.play(FadeIn(term2[0]), FadeIn(term2[1]), run_time=0.5)
        self.play(FadeIn(cmds2[0][0]), run_time=0.15)
        self.play(AddTextLetterByLetter(cmds2[0][1], run_time=0.9))
        self.wait(0.4)
        self.play(FadeIn(outs2[0], shift=UP * 0.1), run_time=0.5)
        self.wait(1.6)

        self.play(FadeOut(term2), run_time=0.6)
        # NOT set_opacity(1) on the whole group: Lambda is asleep and must stay dim.
        self.play(VGroup(you, s3, bed, ddb, arr_ys, arr_sl, arr_lb, arr_ld,
                         arr_dy, lookup, asleep2).animate.set_opacity(1), run_time=0.6)
        self.play(lam.animate.set_opacity(0.3), run_time=0.3)

        # ---------- closing line ----------
        done = Text("Upload a file, get an answer, pay for seconds — that's Scenario 3.",
                    font="sans-serif", weight=BOLD, color=WHITE).scale(0.44)
        done.to_edge(DOWN).shift(UP * 0.2)
        self.play(Transform(cap, done), run_time=0.8)
        self.wait(1.8)


# ---------- so the VS Code "Run" button works ----------
# A Manim scene is only a class definition - plain `python scenario3.py` defines it
# and exits without rendering. This hands the file to the manim CLI instead.
#   python scenario3.py           -> high quality, plays when done
#   python scenario3.py -ql       -> fast preview (any manim flags pass straight through)
if __name__ == "__main__":
    import pathlib
    import subprocess
    import sys

    here = pathlib.Path(__file__).resolve()
    flags = sys.argv[1:] or ["-pqh"]
    sys.exit(subprocess.call(
        [sys.executable, "-m", "manim", *flags, str(here), "Scenario3"],
        cwd=here.parent,   # media/ lands next to the script, same as the CLI does
    ))
