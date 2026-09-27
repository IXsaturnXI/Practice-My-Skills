"""
SF211 — Pygame OOP Refactoring Exam
Autograder for Question 4 (q4.py): Scene integration & uniform polymorphic dispatch

Usage:
    # Run standalone grader (grades q4.py by default):
    python q4_grader.py

    # Grade a specific target (e.g. reference solution):
    python q4_grader.py q4_solution.py
    python q4_grader.py --target q4_solution

    # Or run via pytest:
    pytest -v q4_grader.py
    GRADER_TARGET=q4_solution pytest -v q4_grader.py
"""

import argparse
import ast
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
    target = os.environ.get("GRADER_TARGET", "q4").strip()
    if target.endswith(".py"):
        target = target[:-3]
    return target


def get_q4_module():
    target_name = get_target_name()
    try:
        mod = importlib.import_module(target_name)
    except Exception as err:
        pytest.fail(f"Failed to import target module '{target_name}': {err}")

    build_scene = getattr(mod, "build_scene", None)
    if build_scene is None:
        pytest.fail(f"Function 'build_scene' is not defined in '{target_name}'")
    return mod, build_scene


# ====================================================================
# Test Suite (Rubric: 100 Points Total)
# ====================================================================

def test_build_scene_defined_and_returns_list():
    """Verify build_scene() is defined and returns a list (10 pts)."""
    _, build_scene = get_q4_module()

    assert callable(build_scene), "build_scene must be a callable function."
    balls = build_scene()
    assert isinstance(balls, list), f"build_scene() must return a list, got {type(balls).__name__}"


def test_build_scene_contains_seven_objects():
    """Verify build_scene() returns exactly 7 objects as specified (15 pts)."""
    _, build_scene = get_q4_module()

    balls = build_scene()
    assert len(balls) == 7, (
        f"build_scene() should contain exactly 7 objects (3 BouncingBall + 1 CircularBall "
        f"+ 1 HorizontalBall + 1 Player + 1 Chaser), but got {len(balls)} objects."
    )


def test_scene_contains_required_ball_types():
    """Verify scene contains 3 Bouncing, 1 Circular, 1 Horizontal, and 2 composite Balls (20 pts)."""
    _, build_scene = get_q4_module()

    balls = build_scene()
    class_names = [b.__class__.__name__ for b in balls]

    bouncing_count = sum(1 for name in class_names if "BouncingBall" in name)
    circular_count = sum(1 for name in class_names if "CircularBall" in name)
    horizontal_count = sum(1 for name in class_names if "HorizontalBall" in name)

    assert bouncing_count == 3, f"Expected 3 BouncingBall instances in scene, found {bouncing_count}"
    assert circular_count == 1, f"Expected 1 CircularBall instance in scene, found {circular_count}"
    assert horizontal_count == 1, f"Expected 1 HorizontalBall instance in scene, found {horizontal_count}"


def test_player_and_chaser_controllers():
    """Verify one ball has KeyboardController and another has ChasingController targeting player (15 pts)."""
    _, build_scene = get_q4_module()

    balls = build_scene()

    player_ball = None
    chaser_ball = None
    chaser_controller = None

    for b in balls:
        ctrl = getattr(b, "_controller", getattr(b, "controller", None))
        if ctrl is not None:
            ctrl_name = ctrl.__class__.__name__
            if "Keyboard" in ctrl_name:
                player_ball = b
            elif "Chasing" in ctrl_name:
                chaser_ball = b
                chaser_controller = ctrl

    assert player_ball is not None, (
        "Scene must contain a keyboard-controlled player ball (using KeyboardController)."
    )
    assert chaser_ball is not None, (
        "Scene must contain a chaser ball (using ChasingController)."
    )

    # Chaser target check: chaser's target must be the player ball (or have its coordinates)
    target = getattr(chaser_controller, "_target", getattr(chaser_controller, "target", None))
    assert target is not None, "ChasingController must have a target object."
    assert (target is player_ball) or (
        hasattr(target, "center_x") and hasattr(target, "center_y")
    ), "ChasingController target must expose player position (center_x, center_y)."


def test_uniform_polymorphic_interface():
    """Verify all objects in scene provide uniform move(), draw(), and position interface (15 pts)."""
    _, build_scene = get_q4_module()

    balls = build_scene()
    for idx, b in enumerate(balls):
        assert hasattr(b, "move") and callable(getattr(b, "move")), (
            f"Object at index {idx} ({b.__class__.__name__}) is missing callable 'move()' method."
        )
        assert hasattr(b, "draw") and callable(getattr(b, "draw")), (
            f"Object at index {idx} ({b.__class__.__name__}) is missing callable 'draw()' method."
        )
        assert hasattr(b, "center_x"), f"Object at index {idx} is missing 'center_x'."
        assert hasattr(b, "center_y"), f"Object at index {idx} is missing 'center_y'."


def test_uniform_simulation_and_drawing():
    """Verify uniform update and draw loops execute without any exceptions (15 pts)."""
    _, build_scene = get_q4_module()

    pygame.init()
    surface = pygame.Surface((WIDTH, HEIGHT))
    surface.fill((0, 0, 0))

    balls = build_scene()

    # Test uniform move loop (Constraint: single uniform loop, no type checks)
    for frame in range(60):
        for b in balls:
            b.move()

    # Test uniform draw loop
    for b in balls:
        b.draw(surface)

    # Surface should have rendered colors
    drawn_something = any(
        surface.get_at((int(b.center_x), int(b.center_y))) != (0, 0, 0, 255)
        for b in balls
        if 0 <= b.center_x < WIDTH and 0 <= b.center_y < HEIGHT
    )
    assert drawn_something, "Balls should render pixels onto the surface."


def test_no_isinstance_or_type_branching():
    """Verify main() and build_scene() contain no isinstance/type checks (constraint check) (10 pts)."""
    target_name = get_target_name()
    target_file = f"{target_name}.py"

    if not os.path.exists(target_file):
        pytest.skip(f"Source file {target_file} not found for AST inspection.")

    with open(target_file, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=target_file)

    disallowed_calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in ("isinstance", "issubclass", "type"):
                disallowed_calls.append((func.id, getattr(node, "lineno", "?")))

    assert not disallowed_calls, (
        f"Found forbidden type inspection in {target_file}: {disallowed_calls}. "
        f"The exam requires pure polymorphic dispatch without type-branching."
    )


# ====================================================================
# Rubric Definition & Standalone Grader Runner
# ====================================================================

RUBRIC = [
    (test_build_scene_defined_and_returns_list, 10, "build_scene() defined and returns a list"),
    (test_build_scene_contains_seven_objects, 15, "Scene contains exactly 7 objects as specified"),
    (test_scene_contains_required_ball_types, 20, "Scene contains 3 Bouncing, 1 Circular, 1 Horizontal, 2 Composite"),
    (test_player_and_chaser_controllers, 15, "Player has KeyboardController and Enemy has ChasingController"),
    (test_uniform_polymorphic_interface, 15, "All objects expose uniform move(), draw(), and position interface"),
    (test_uniform_simulation_and_drawing, 15, "Uniform update and draw loops execute without errors"),
    (test_no_isinstance_or_type_branching, 10, "No isinstance() or type branching in source (constraint check)"),
]


def run_grader(target: str = "q4", verbose: bool = False):
    os.environ["GRADER_TARGET"] = target

    sep_width = 72
    print("=" * sep_width)
    print(f" SF211 OOP Exam — Q4 Autograder (Integrated Scene & Polymorphism)")
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
    parser = argparse.ArgumentParser(description="SF211 Exam Q4 Grader for Scene Integration")
    parser.add_argument("target_pos", nargs="?", default=None, help="Target module to grade (default: q4)")
    parser.add_argument("--target", "-t", default=None, help="Target module to grade (e.g. q4, q4_solution)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print verbose tracebacks for failed tests")
    args = parser.parse_args()

    target = args.target or args.target_pos or "q4"
    if target.endswith(".py"):
        target = target[:-3]

    exit_code = run_grader(target=target, verbose=args.verbose)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
