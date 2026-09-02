# scenario1.py  —  6F School of IT  |  Scenario 1: GitHub -> EC2 -> Load Balancer
#
# SETUP (one time):
#   pip install manim
#   (Manim also needs ffmpeg + a LaTeX install is optional; we avoid LaTeX by using Text, not Tex)
#
# RENDER:
#   manim -pqh scenario1.py Scenario1        # high quality, opens when done
#   manim -pql scenario1.py Scenario1        # low quality, fast preview
#
# The -p flag plays it, -q sets quality (l/m/h/k). Output .mp4 lands in ./media/videos/...

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


class Scenario1(Scene):
    def construct(self):
        self.camera.background_color = NAVY

        # ---------- title ----------
        brand = Text("6F School of IT", font="sans-serif", weight=BOLD, color=GOLD).scale(0.42)
        brand.to_corner(UL).shift(DOWN * 0.1 + RIGHT * 0.1)
        title = Text("Scenario 1 · Deploy a Highly-Available Web App",
                     font="sans-serif", weight=BOLD, color=WHITE).scale(0.52)
        title.to_edge(UP).shift(DOWN * 0.35)
        underline = Line(LEFT, RIGHT, color=GOLD, stroke_width=3).set_width(title.width)
        underline.next_to(title, DOWN, buff=0.12)

        self.play(FadeIn(brand, shift=RIGHT * 0.2), run_time=0.6)
        self.play(Write(title), run_time=1.0)
        self.play(GrowFromEdge(underline, LEFT), run_time=0.6)
        self.wait(0.3)

        # ---------- nodes ----------
        # Runtime path:  User -> Load Balancer -> EC2 (x2)
        # Deploy path:   GitHub -> EC2 (code is pushed to the servers, NOT through the LB)
        user   = chip("User", "visitor", GOLD, w=2.2)
        alb    = chip("Load Balancer", "splits traffic", ORANGE, w=3.0)
        ec2a   = chip("EC2 · Zone A", "web server 1", TEAL, w=2.9, h=0.95)
        ec2b   = chip("EC2 · Zone B", "web server 2", TEAL, w=2.9, h=0.95)
        github = chip("GitHub", "deploys code", PINK, w=2.6)

        user.move_to(LEFT * 5.2)
        alb.move_to(LEFT * 1.2)
        ec2a.move_to(RIGHT * 3.6 + UP * 1.4)
        ec2b.move_to(RIGHT * 3.6 + DOWN * 1.4)
        github.move_to(RIGHT * 3.6 + DOWN * 3.0)   # sits below, deploys UP into the servers

        # ---------- build the diagram, one node at a time (Edureka-style) ----------
        cap = Text("A user opens your site.", font="sans-serif", color=INK).scale(0.4)
        cap.to_edge(DOWN).shift(UP * 0.2)
        self.play(FadeIn(user, scale=0.7), FadeIn(cap), run_time=0.9)
        self.wait(0.6)

        arr1 = Arrow(user.get_right(), alb.get_left(), buff=0.15,
                     color=GOLD, stroke_width=5, max_tip_length_to_length_ratio=0.12)
        cap2 = Text("The Load Balancer receives every request.", font="sans-serif", color=INK).scale(0.4)
        cap2.to_edge(DOWN).shift(UP * 0.2)
        self.play(GrowArrow(arr1), run_time=0.7)
        self.play(FadeIn(alb, scale=0.7), Transform(cap, cap2), run_time=0.9)
        self.wait(0.6)

        arr2 = Arrow(alb.get_right(), ec2a.get_left(), buff=0.15,
                     color=TEAL, stroke_width=5, max_tip_length_to_length_ratio=0.12)
        arr3 = Arrow(alb.get_right(), ec2b.get_left(), buff=0.15,
                     color=TEAL, stroke_width=5, max_tip_length_to_length_ratio=0.12)
        cap3 = Text("It spreads traffic across two servers, in two zones.",
                    font="sans-serif", color=INK).scale(0.4)
        cap3.to_edge(DOWN).shift(UP * 0.2)
        self.play(GrowArrow(arr2), GrowArrow(arr3), run_time=0.8)
        self.play(FadeIn(ec2a, scale=0.7), FadeIn(ec2b, scale=0.7),
                  Transform(cap, cap3), run_time=0.9)
        self.wait(0.8)

        # ---------- deploy path: GitHub -> EC2 (separate from user traffic) ----------
        dep_a = Arrow(github.get_top(), ec2b.get_bottom(), buff=0.15,
                      color=PINK, stroke_width=4, max_tip_length_to_length_ratio=0.1)
        cap_dep = Text("GitHub deploys your code straight to the servers — not through the LB.",
                       font="sans-serif", color=INK).scale(0.38)
        cap_dep.to_edge(DOWN).shift(UP * 0.2)
        self.play(FadeIn(github, scale=0.7), Transform(cap, cap_dep), run_time=0.9)
        self.play(GrowArrow(dep_a), run_time=0.7)
        # a code packet travelling up into the server
        cd = flow_dot(PINK).move_to(github.get_top())
        self.play(MoveAlongPath(cd, dep_a), run_time=0.7, rate_func=linear)
        self.remove(cd)
        self.wait(0.8)

        # ---------- animate request flow (moving dots): User -> LB -> EC2 ----------
        cap4 = Text("A live request flows: User to Load Balancer to a server.",
                    font="sans-serif", color=INK).scale(0.4)
        cap4.to_edge(DOWN).shift(UP * 0.2)
        self.play(Transform(cap, cap4), run_time=0.5)

        for _ in range(2):
            d1 = flow_dot(GOLD).move_to(user.get_right())
            self.play(MoveAlongPath(d1, arr1), run_time=0.6, rate_func=linear)
            d2 = flow_dot(TEAL).move_to(alb.get_right())
            d3 = flow_dot(TEAL).move_to(alb.get_right())
            self.play(MoveAlongPath(d2, arr2), MoveAlongPath(d3, arr3),
                      run_time=0.6, rate_func=linear)
            self.remove(d1, d2, d3)
        self.wait(0.4)

        # ---------- the payoff: one server crashes, site stays up ----------
        cross = Cross(ec2b[0], stroke_color=PINK, stroke_width=6).scale(0.9)
        cap5 = Text("One server crashes — the Load Balancer reroutes. Site stays up.",
                    font="sans-serif", color=GOLD).scale(0.4)
        cap5.to_edge(DOWN).shift(UP * 0.2)
        self.play(ec2b.animate.set_opacity(0.35), Create(cross),
                  arr3.animate.set_opacity(0.25), Transform(cap, cap5), run_time=0.9)

        # traffic now only to the healthy server
        for _ in range(2):
            d1 = flow_dot(GOLD).move_to(user.get_right())
            self.play(MoveAlongPath(d1, arr1), run_time=0.5, rate_func=linear)
            d2 = flow_dot(GREEN).move_to(alb.get_right())
            self.play(MoveAlongPath(d2, arr2), run_time=0.5, rate_func=linear)
            self.remove(d1, d2)
        self.wait(0.6)

        # ---------- closing line ----------
        done = Text("High Availability — that's Scenario 1.",
                    font="sans-serif", weight=BOLD, color=WHITE).scale(0.5)
        done.to_edge(DOWN).shift(UP * 0.2)
        self.play(Transform(cap, done), run_time=0.8)
        self.wait(1.5)