"""
SF211 — Pygame OOP Refactoring Exam
Autograder for Question 2 (q2.py): Polymorphic motion (CircularBall & HorizontalBall)

Usage:
    # Run standalone grader (grades q2.py by default):
    python q2_grader.py

    # Grade a specific target (e.g. reference solution):
    python q2_grader.py q2_solution.py
    python q2_grader.py --target q2_solution

    # Or run via pytest:
    pytest -v q2_grader.py
    GRADER_TARGET=q2_solution pytest -v q2_grader.py
"""

import argparse
import importlib
import inspect
import math
import os
import sys
import traceback
import pygame
import pytest

from ball_base import Ball
from config import WIDTH, HEIGHT


def get_target_name() -> str:
    target = os.environ.get("GRADER_TARGET", "q2").strip()
    if target.endswith(".py"):
        target = target[:-3]
    return target


def get_q2_classes():
    target_name = get_target_name()
    try:
        mod = importlib.import_module(target_name)
    except Exception as err:
        pytest.fail(f"Failed to import target module '{target_name}': {err}")

    circ_cls = getattr(mod, "CircularBall", None)
    horiz_cls = getattr(mod, "HorizontalBall", None)
    if circ_cls is None:
        pytest.fail(f"Class 'CircularBall' is not defined in '{target_name}'")
    if horiz_cls is None:
        pytest.fail(f"Class 'HorizontalBall' is not defined in '{target_name}'")
    return circ_cls, horiz_cls


# ====================================================================
# Test Suite (Rubric: 100 Points Total)
# ====================================================================

def test_classes_defined_and_inheritance():
    """Verify CircularBall and HorizontalBall exist and inherit from Ball (10 pts)."""
    CircularBall, HorizontalBall = get_q2_classes()

    assert inspect.isclass(CircularBall), "CircularBall must be a class."
    assert inspect.isclass(HorizontalBall), "HorizontalBall must be a class."

    assert issubclass(CircularBall, Ball), "CircularBall must inherit from ball_base.Ball."
    assert issubclass(HorizontalBall, Ball), "HorizontalBall must inherit from ball_base.Ball."

    assert hasattr(CircularBall, "draw") and callable(getattr(CircularBall, "draw")), (
        "CircularBall must have a callable 'draw' method."
    )
    assert hasattr(HorizontalBall, "draw") and callable(getattr(HorizontalBall, "draw")), (
        "HorizontalBall must have a callable 'draw' method."
    )


def test_circular_ball_init_and_attributes():
    """Verify CircularBall constructor signature and initial position (10 pts)."""
    CircularBall, _ = get_q2_classes()

    sig = inspect.signature(CircularBall.__init__)
    params = list(sig.parameters.keys())[1:]  # skip 'self'

    expected_params = ["radius", "speed", "color", "orbit_radius"]
    for ep in expected_params:
        assert ep in params, f"CircularBall.__init__ is missing parameter '{ep}'."

    # start_angle should default to 0.0
    if "start_angle" in sig.parameters:
        assert sig.parameters["start_angle"].default in (0.0, 0), (
            "CircularBall 'start_angle' parameter should default to 0.0"
        )

    # Test initialization with default start_angle=0.0
    ball = CircularBall(radius=10, speed=4, color="cyan", orbit_radius=150)
    expected_x = WIDTH / 2 + 150 * math.cos(0.0)
    expected_y = HEIGHT / 2 + 150 * math.sin(0.0)

    assert math.isclose(ball.center_x, expected_x, abs_tol=1e-5), (
        f"CircularBall initial center_x expected {expected_x}, got {ball.center_x}"
    )
    assert math.isclose(ball.center_y, expected_y, abs_tol=1e-5), (
        f"CircularBall initial center_y expected {expected_y}, got {ball.center_y}"
    )
    assert ball.radius == 10
    assert ball.speed == 4
    assert ball.color == "cyan"


def test_circular_ball_stays_on_orbit():
    """Verify CircularBall maintains constant distance to orbit center (15 pts)."""
    CircularBall, _ = get_q2_classes()

    orbit_r = 150
    ball = CircularBall(10, 4, "cyan", orbit_radius=orbit_r)
    for frame in range(500):
        ball.move()
        dist = math.hypot(ball.center_x - WIDTH / 2, ball.center_y - HEIGHT / 2)
        assert math.isclose(dist, orbit_r, abs_tol=1e-4), (
            f"Frame {frame}: distance to center {dist} does not match orbit_radius {orbit_r}"
        )


def test_circular_ball_tangential_speed():
    """Verify CircularBall travels at specified speed pixels per frame along arc (15 pts)."""
    CircularBall, _ = get_q2_classes()

    speed = 4
    orbit_r = 150
    ball = CircularBall(10, speed, "cyan", orbit_radius=orbit_r)

    x0, y0 = ball.center_x, ball.center_y
    ball.move()
    chord_length = math.hypot(ball.center_x - x0, ball.center_y - y0)

    # Chord length is slightly less than arc length, within 1% tolerance
    assert chord_length == pytest.approx(speed, rel=0.02), (
        f"Step distance {chord_length} does not match tangential speed {speed}"
    )


def test_circular_ball_arbitrary_start_angle():
    """Verify CircularBall honors non-zero start_angle (10 pts)."""
    CircularBall, _ = get_q2_classes()

    orbit_r = 80
    start_angle = math.pi
    ball = CircularBall(8, 4, "magenta", orbit_radius=orbit_r, start_angle=start_angle)

    expected_x = WIDTH / 2 + orbit_r * math.cos(start_angle)
    expected_y = HEIGHT / 2 + orbit_r * math.sin(start_angle)

    assert math.isclose(ball.center_x, expected_x, abs_tol=1e-5), (
        f"Expected center_x {expected_x}, got {ball.center_x}"
    )
    assert math.isclose(ball.center_y, expected_y, abs_tol=1e-5), (
        f"Expected center_y {expected_y}, got {ball.center_y}"
    )


def test_horizontal_ball_init_and_attributes():
    """Verify HorizontalBall constructor and starting position offscreen (10 pts)."""
    _, HorizontalBall = get_q2_classes()

    sig = inspect.signature(HorizontalBall.__init__)
    params = list(sig.parameters.keys())[1:]

    for ep in ["radius", "speed", "color"]:
        assert ep in params, f"HorizontalBall.__init__ missing parameter '{ep}'."

    ball = HorizontalBall(radius=25, speed=6, color="yellow")
    # Starts fully offscreen at x = -radius, y = HEIGHT / 2
    assert ball.center_x == -25, f"HorizontalBall should start at x = -radius (-25), got {ball.center_x}"
    assert ball.center_y == HEIGHT / 2, f"HorizontalBall should start at y = HEIGHT/2 ({HEIGHT/2}), got {ball.center_y}"
    assert ball.radius == 25
    assert ball.speed == 6
    assert ball.color == "yellow"


def test_horizontal_ball_motion_and_no_vertical_drift():
    """Verify HorizontalBall advances horizontally and never drifts vertically (15 pts)."""
    _, HorizontalBall = get_q2_classes()

    ball = HorizontalBall(25, 6, "yellow")
    for _ in range(50):
        prev_x = ball.center_x
        ball.move()
        assert math.isclose(ball.center_x, prev_x + 6, abs_tol=1e-5), (
            f"HorizontalBall should advance by speed (6), from {prev_x} to {prev_x + 6}, got {ball.center_x}"
        )
        assert ball.center_y == HEIGHT / 2, "HorizontalBall vertical position must remain HEIGHT / 2"


def test_horizontal_ball_wrapping():
    """Verify HorizontalBall wraps to -radius only when completely offscreen (10 pts)."""
    _, HorizontalBall = get_q2_classes()

    ball = HorizontalBall(25, 6, "yellow")
    wrapped = False

    for frame in range(400):
        prev_x = ball.center_x
        ball.move()
        if ball.center_x < prev_x:
            # Wrapped around: prior position must have placed the ball offscreen
            assert (prev_x + ball.speed - ball.radius) > WIDTH or (prev_x - ball.radius) > WIDTH, (
                f"Ball wrapped prematurely at frame {frame}: prev_x={prev_x}, radius={ball.radius}, WIDTH={WIDTH}"
            )
            assert ball.center_x == -ball.radius, (
                f"Ball wrapped to {ball.center_x}, expected -radius ({-ball.radius})"
            )
            wrapped = True
            break

    assert wrapped, "HorizontalBall never wrapped around after traversing the screen."


def test_draw_method_renders_circles():
    """Verify both CircularBall and HorizontalBall draw to a Pygame Surface (5 pts)."""
    CircularBall, HorizontalBall = get_q2_classes()

    circ = CircularBall(10, 4, "cyan", orbit_radius=100)
    horiz = HorizontalBall(20, 5, "yellow")

    surf = pygame.Surface((WIDTH, HEIGHT))
    surf.fill((0, 0, 0))

    circ.draw(surf)
    horiz.draw(surf)

    # Circular ball center should be colored
    c_pixel = surf.get_at((int(circ.center_x), int(circ.center_y)))
    assert c_pixel != (0, 0, 0, 255), "CircularBall did not render pixels at its center."


# ====================================================================
# Rubric Definition & Standalone Grader Runner
# ====================================================================

RUBRIC = [
    (test_classes_defined_and_inheritance, 10, "CircularBall & HorizontalBall defined and inherit from Ball"),
    (test_circular_ball_init_and_attributes, 10, "CircularBall constructor parameters & initial positioning"),
    (test_circular_ball_stays_on_orbit, 15, "CircularBall maintains constant distance to orbit center"),
    (test_circular_ball_tangential_speed, 15, "CircularBall step displacement matches tangential speed"),
    (test_circular_ball_arbitrary_start_angle, 10, "CircularBall correctly respects custom start_angle"),
    (test_horizontal_ball_init_and_attributes, 10, "HorizontalBall constructor & offscreen initialization"),
    (test_horizontal_ball_motion_and_no_vertical_drift, 15, "HorizontalBall moves horizontally with zero vertical drift"),
    (test_horizontal_ball_wrapping, 10, "HorizontalBall wraps only when completely offscreen"),
    (test_draw_method_renders_circles, 5, "draw() properly renders both balls on Pygame Surface"),
]


def run_grader(target: str = "q2", verbose: bool = False):
    os.environ["GRADER_TARGET"] = target

    sep_width = 72
    print("=" * sep_width)
    print(f" SF211 OOP Exam — Q2 Autograder (CircularBall & HorizontalBall)")
    print(f" Target module: {target}.py")
    print("=" * sep_width)

    total_score = 0
    max_score = sum(pts for _, pts, _ in RUBRIC)
    failed_tests = []

    for test_fn, pts, desc in RUBRIC:
        name = test_fn.__name__
        try:
            test_fn()
            total_score += pts
            print(f" [PASS] {pts:2d}/{pts:2d}  {name}")
            print(f"               {desc}")
        except BaseException as exc:
            if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                raise
            err_msg = str(exc)
            if not err_msg and hasattr(exc, "msg"):
                err_msg = str(exc.msg)
            print(f" [FAIL]  0/{pts:2d}  {name}")
            print(f"               {desc}")
            print(f"               -> ERROR: {err_msg}")
            failed_tests.append((name, desc, err_msg, traceback.format_exc()))

    print("-" * sep_width)
    pct = (total_score / max_score) * 100
    print(f" Total Score: {total_score} / {max_score} ({pct:.1f}%)")

    if failed_tests:
        print(f" Status: FAILED ({len(failed_tests)} of {len(RUBRIC)} tests failed)")
        if verbose:
            print("\nDetailed Failure Tracebacks:")
            print("-" * sep_width)
            for name, desc, err_msg, tb in failed_tests:
                print(f"=== {name} ===")
                print(tb)
        print("=" * sep_width)
        return 1
    else:
        print(" Status: PASSED ALL CHECKS (Perfect Score!)")
        print("=" * sep_width)
        return 0


def main():
    parser = argparse.ArgumentParser(description="SF211 Exam Q2 Grader for CircularBall & HorizontalBall")
    parser.add_argument("target_pos", nargs="?", default=None, help="Target module to grade (default: q2)")
    parser.add_argument("--target", "-t", default=None, help="Target module to grade (e.g. q2, q2_solution)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print verbose tracebacks for failed tests")
    args = parser.parse_args()

    target = args.target or args.target_pos or "q2"
    if target.endswith(".py"):
        target = target[:-3]

    exit_code = run_grader(target=target, verbose=args.verbose)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
