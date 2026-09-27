"""
SF211 — Pygame OOP Refactoring Exam
Autograder for Question 3 (q3.py): Composition & Strategy (Controller, KeyboardController, ChasingController)

Usage:
    # Run standalone grader (grades q3.py by default):
    python q3_grader.py

    # Grade a specific target (e.g. reference solution):
    python q3_grader.py q3_solution.py
    python q3_grader.py --target q3_solution

    # Or run via pytest:
    pytest -v q3_grader.py
    GRADER_TARGET=q3_solution pytest -v q3_grader.py
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

from config import WIDTH, HEIGHT


def get_target_name() -> str:
    target = os.environ.get("GRADER_TARGET", "q3").strip()
    if target.endswith(".py"):
        target = target[:-3]
    return target


def get_q3_components():
    target_name = get_target_name()
    try:
        mod = importlib.import_module(target_name)
    except Exception as err:
        pytest.fail(f"Failed to import target module '{target_name}': {err}")

    Controller = getattr(mod, "Controller", None)
    KeyboardController = getattr(mod, "KeyboardController", None)
    ChasingController = getattr(mod, "ChasingController", None)
    Ball = getattr(mod, "Ball", None)

    if Controller is None:
        pytest.fail(f"Class 'Controller' is not defined in '{target_name}'")
    if KeyboardController is None:
        pytest.fail(f"Class 'KeyboardController' is not defined in '{target_name}'")
    if ChasingController is None:
        pytest.fail(f"Class 'ChasingController' is not defined in '{target_name}'")
    if Ball is None:
        pytest.fail(f"Class 'Ball' is not defined in '{target_name}'")

    return mod, Controller, KeyboardController, ChasingController, Ball


class _FakeKeys:
    """Mock dictionary-like object representing pygame.key.get_pressed()."""
    def __init__(self, held_keys):
        self._held = dict(held_keys)

    def __getitem__(self, key):
        return self._held.get(key, False)


class _DuckTarget:
    """Duck-typed target object exposing center_x and center_y."""
    def __init__(self, x, y):
        self.center_x = x
        self.center_y = y


# ====================================================================
# Test Suite (Rubric: 100 Points Total)
# ====================================================================

def test_classes_defined_and_hierarchy():
    """Verify Controller, KeyboardController, ChasingController, and Ball inheritance (10 pts)."""
    _, Controller, KeyboardController, ChasingController, Ball = get_q3_components()

    assert inspect.isclass(Controller), "Controller must be a class."
    assert inspect.isclass(KeyboardController), "KeyboardController must be a class."
    assert inspect.isclass(ChasingController), "ChasingController must be a class."
    assert inspect.isclass(Ball), "Ball must be a class."

    assert issubclass(KeyboardController, Controller), (
        "KeyboardController must inherit from Controller."
    )
    assert issubclass(ChasingController, Controller), (
        "ChasingController must inherit from Controller."
    )


def test_controller_base_init_and_properties():
    """Verify Controller constructor and x, y properties (10 pts)."""
    _, Controller, _, _, _ = get_q3_components()

    ctrl = Controller(120, 240, speed=5)
    assert hasattr(ctrl, "x"), "Controller must have property 'x'."
    assert hasattr(ctrl, "y"), "Controller must have property 'y'."
    assert ctrl.x == 120, f"Expected ctrl.x == 120, got {ctrl.x}"
    assert ctrl.y == 240, f"Expected ctrl.y == 240, got {ctrl.y}"


def test_keyboard_controller_cardinal_movement(monkeypatch=None):
    """Verify KeyboardController moves by speed in cardinal directions (10 pts)."""
    mod, _, KeyboardController, _, _ = get_q3_components()

    directions = [
        ({pygame.K_d: True}, 5, 0),
        ({pygame.K_RIGHT: True}, 5, 0),
        ({pygame.K_a: True}, -5, 0),
        ({pygame.K_LEFT: True}, -5, 0),
        ({pygame.K_w: True}, 0, -5),
        ({pygame.K_UP: True}, 0, -5),
        ({pygame.K_s: True}, 0, 5),
        ({pygame.K_DOWN: True}, 0, 5),
    ]

    for key_map, exp_dx, exp_dy in directions:
        fake_keys = _FakeKeys(key_map)
        if monkeypatch:
            monkeypatch.setattr(mod.pygame.key, "get_pressed", lambda: fake_keys)
        else:
            orig = mod.pygame.key.get_pressed
            mod.pygame.key.get_pressed = lambda: fake_keys

        try:
            ctrl = KeyboardController(200, 200, speed=5)
            x0, y0 = ctrl.x, ctrl.y
            ctrl.move()
            assert math.isclose(ctrl.x - x0, exp_dx, abs_tol=1e-5), (
                f"Movement with {key_map} expected dx={exp_dx}, got {ctrl.x - x0}"
            )
            assert math.isclose(ctrl.y - y0, exp_dy, abs_tol=1e-5), (
                f"Movement with {key_map} expected dy={exp_dy}, got {ctrl.y - y0}"
            )
        finally:
            if not monkeypatch:
                mod.pygame.key.get_pressed = orig


def test_keyboard_controller_diagonal_normalization(monkeypatch=None):
    """Verify diagonal displacement is normalized to speed, not speed*sqrt(2) (15 pts)."""
    mod, _, KeyboardController, _, _ = get_q3_components()

    diagonals = [
        {pygame.K_w: True, pygame.K_d: True},
        {pygame.K_w: True, pygame.K_a: True},
        {pygame.K_s: True, pygame.K_d: True},
        {pygame.K_s: True, pygame.K_a: True},
    ]

    for diag_keys in diagonals:
        fake_keys = _FakeKeys(diag_keys)
        if monkeypatch:
            monkeypatch.setattr(mod.pygame.key, "get_pressed", lambda: fake_keys)
        else:
            orig = mod.pygame.key.get_pressed
            mod.pygame.key.get_pressed = lambda: fake_keys

        try:
            ctrl = KeyboardController(300, 300, speed=6)
            x0, y0 = ctrl.x, ctrl.y
            ctrl.move()
            displacement = math.hypot(ctrl.x - x0, ctrl.y - y0)
            assert displacement == pytest.approx(6.0, rel=1e-4), (
                f"Diagonal movement with {diag_keys} had displacement {displacement}, expected normalized speed 6.0"
            )
        finally:
            if not monkeypatch:
                mod.pygame.key.get_pressed = orig


def test_keyboard_controller_opposing_keys_and_idle(monkeypatch=None):
    """Verify opposing keys cancel each other and idle keys cause no movement (10 pts)."""
    mod, _, KeyboardController, _, _ = get_q3_components()

    idle_scenarios = [
        {},  # no keys pressed
        {pygame.K_a: True, pygame.K_d: True},  # left + right cancel
        {pygame.K_w: True, pygame.K_s: True},  # up + down cancel
        {pygame.K_a: True, pygame.K_d: True, pygame.K_w: True, pygame.K_s: True},
    ]

    for scenario in idle_scenarios:
        fake_keys = _FakeKeys(scenario)
        if monkeypatch:
            monkeypatch.setattr(mod.pygame.key, "get_pressed", lambda: fake_keys)
        else:
            orig = mod.pygame.key.get_pressed
            mod.pygame.key.get_pressed = lambda: fake_keys

        try:
            ctrl = KeyboardController(400, 300, speed=5)
            x0, y0 = ctrl.x, ctrl.y
            ctrl.move()
            assert ctrl.x == x0 and ctrl.y == y0, (
                f"Controller moved when keys {scenario} should cancel or remain idle: pos was ({ctrl.x}, {ctrl.y})"
            )
        finally:
            if not monkeypatch:
                mod.pygame.key.get_pressed = orig


def test_keyboard_controller_window_clamping(monkeypatch=None):
    """Verify player cannot be driven outside window boundaries (10 pts)."""
    mod, _, KeyboardController, _, _ = get_q3_components()

    # Move left past x=0
    fake_left = _FakeKeys({pygame.K_a: True})
    orig = mod.pygame.key.get_pressed
    mod.pygame.key.get_pressed = lambda: fake_left

    try:
        ctrl = KeyboardController(2, 300, speed=10)
        ctrl.move()
        assert 0 <= ctrl.x <= WIDTH, f"Controller x was not clamped to window min: got {ctrl.x}"

        # Move past WIDTH
        fake_right = _FakeKeys({pygame.K_d: True})
        mod.pygame.key.get_pressed = lambda: fake_right
        ctrl = KeyboardController(WIDTH - 2, 300, speed=10)
        ctrl.move()
        assert 0 <= ctrl.x <= WIDTH, f"Controller x was not clamped to window max: got {ctrl.x}"

        # Move past HEIGHT
        fake_down = _FakeKeys({pygame.K_s: True})
        mod.pygame.key.get_pressed = lambda: fake_down
        ctrl = KeyboardController(400, HEIGHT - 2, speed=10)
        ctrl.move()
        assert 0 <= ctrl.y <= HEIGHT, f"Controller y was not clamped to window max: got {ctrl.y}"
    finally:
        mod.pygame.key.get_pressed = orig


def test_chaser_moves_exact_speed_towards_target():
    """Verify ChasingController steps by exactly speed towards target (10 pts)."""
    _, _, _, ChasingController, _ = get_q3_components()

    target = _DuckTarget(400, 300)
    ctrl = ChasingController(100, 100, speed=4, target=target)

    x0, y0 = ctrl.x, ctrl.y
    ctrl.move()
    step = math.hypot(ctrl.x - x0, ctrl.y - y0)
    assert step == pytest.approx(4.0, rel=1e-4), (
        f"Chaser step distance {step} does not match speed 4.0"
    )


def test_chaser_snap_and_no_oscillation():
    """Verify ChasingController snaps to target within speed and does not oscillate (15 pts)."""
    _, _, _, ChasingController, _ = get_q3_components()

    target = _DuckTarget(400, 300)
    ctrl = ChasingController(398, 299, speed=5, target=target)

    # Initial distance is sqrt(2^2 + 1^2) = sqrt(5) ≈ 2.23 <= 5 (speed)
    ctrl.move()
    assert ctrl.x == pytest.approx(400.0) and ctrl.y == pytest.approx(300.0), (
        f"Chaser did not snap to target on arrival: got ({ctrl.x}, {ctrl.y})"
    )

    # Subsequent frames must stay put without oscillation
    ctrl.move()
    assert ctrl.x == pytest.approx(400.0) and ctrl.y == pytest.approx(300.0), (
        f"Chaser oscillated after snapping: got ({ctrl.x}, {ctrl.y})"
    )


def test_chaser_zero_distance_safety():
    """Verify ChasingController handles zero distance without division by zero (5 pts)."""
    _, _, _, ChasingController, _ = get_q3_components()

    target = _DuckTarget(150, 150)
    ctrl = ChasingController(150, 150, speed=5, target=target)

    # Must not raise ZeroDivisionError
    ctrl.move()
    assert (ctrl.x, ctrl.y) == (150, 150)


def test_ball_delegates_to_controller():
    """Verify Ball delegates movement to controller and synchronizes position (5 pts)."""
    _, _, KeyboardController, _, Ball = get_q3_components()

    ctrl = KeyboardController(250, 180, speed=5)
    ball = Ball(radius=15, color="white", controller=ctrl)

    assert ball.center_x == 250, f"Ball center_x ({ball.center_x}) should sync with controller x (250)"
    assert ball.center_y == 180, f"Ball center_y ({ball.center_y}) should sync with controller y (180)"

    # Calling ball.draw
    surf = pygame.Surface((WIDTH, HEIGHT))
    ball.draw(surf)
    assert surf.get_at((250, 180)) != (0, 0, 0, 255), "Ball.draw did not render on surface."


# ====================================================================
# Rubric Definition & Standalone Grader Runner
# ====================================================================

RUBRIC = [
    (test_classes_defined_and_hierarchy, 10, "Controller hierarchy & Ball class definition"),
    (test_controller_base_init_and_properties, 10, "Controller constructor and position properties (x, y)"),
    (test_keyboard_controller_cardinal_movement, 10, "KeyboardController movement in cardinal directions"),
    (test_keyboard_controller_diagonal_normalization, 15, "Diagonal speed normalization (BUG FIX 1)"),
    (test_keyboard_controller_opposing_keys_and_idle, 10, "Opposing keys cancel out and idle causes no drift"),
    (test_keyboard_controller_window_clamping, 10, "Window boundary clamping (BUG FIX 3)"),
    (test_chaser_moves_exact_speed_towards_target, 10, "Chaser moves at exact speed towards target"),
    (test_chaser_snap_and_no_oscillation, 15, "Chaser snaps to target without oscillation (BUG FIX 2)"),
    (test_chaser_zero_distance_safety, 5, "Safety check against ZeroDivisionError when on target"),
    (test_ball_delegates_to_controller, 5, "Ball delegates move() to controller and syncs coordinates"),
]


def run_grader(target: str = "q3", verbose: bool = False):
    os.environ["GRADER_TARGET"] = target

    sep_width = 72
    print("=" * sep_width)
    print(f" SF211 OOP Exam — Q3 Autograder (Strategy Pattern / Composition)")
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
    parser = argparse.ArgumentParser(description="SF211 Exam Q3 Grader for Controllers & Composition")
    parser.add_argument("target_pos", nargs="?", default=None, help="Target module to grade (default: q3)")
    parser.add_argument("--target", "-t", default=None, help="Target module to grade (e.g. q3, q3_solution)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print verbose tracebacks for failed tests")
    args = parser.parse_args()

    target = args.target or args.target_pos or "q3"
    if target.endswith(".py"):
        target = target[:-3]

    exit_code = run_grader(target=target, verbose=args.verbose)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
