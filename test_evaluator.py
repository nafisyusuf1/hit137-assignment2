"""
test_evaluator.py
Small sanity-check script for evaluator.py.

Runs a handful of expressions through evaluate_expression() and checks
the result against an expected value. This isn't a full test suite,
just a quick way to confirm the parser/evaluator behaves as expected
before submitting.
"""

from evaluator import evaluate_expression

# Each tuple is (expression, expected_result).
# expected_result is a float on success, or the string "ERROR" for
# expressions that should fail.
TEST_CASES = [
    ("3 + 5", 8.0),
    ("2 + 3 * 4", 14.0),
    ("-(3 + 4)", -7.0),
    ("--5", 5.0),
    ("(10 - 2) * 3 + -4 / 2", 22.0),
    ("3 @ 5", "ERROR"),
    ("1 / 0", "ERROR"),
    ("2(3+4)", 14.0),      # implicit multiplication before '('
    ("(3+4)2", 14.0),      # implicit multiplication after ')'
    ("2 3", "ERROR"),      # bare adjacent numbers are NOT implicit multiplication
    ("+5", "ERROR"),       # unary '+' is not supported
    ("-2^2", -4.0),        # unary minus binds looser than '^'
    ("2^3^2", 512.0),      # '^' is right associative
]


def run_tests():
    passed = 0
    failed = 0

    for expression, expected in TEST_CASES:
        entry = evaluate_expression(expression)
        actual = entry["result"]

        if actual == expected:
            print(f"PASS  {expression!r} -> {actual}")
            passed += 1
        else:
            print(f"FAIL  {expression!r} -> got {actual}, expected {expected}")
            failed += 1

    print()
    print(f"{passed} passed, {failed} failed out of {len(TEST_CASES)} cases.")


if __name__ == "__main__":
    run_tests()
