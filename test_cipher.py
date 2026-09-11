"""
test_cipher.py
Small sanity-check script for cipher.py.

Runs encrypt -> decrypt -> verify across a handful of different
shift1/shift2 values and reports whether each round trip succeeded.
This isn't a full test suite, just a quick way to confirm the cipher
is reversible before submitting.
"""

from cipher import encrypt_text, decrypt_text

SAMPLE_TEXT = (
    "Hello, World! 123\tTest\nNew Line. Symbols: @#$%^&*()"
)

# A handful of shift1/shift2 pairs to check, including the edge case
# of both shifts being 0.
TEST_CASES = [
    (0, 0),
    (1, 1),
    (3, 5),
    (7, 9),
    (10, 2),
    (15, 15),
]


def run_tests():
    passed = 0
    failed = 0

    for shift1, shift2 in TEST_CASES:
        encrypted = encrypt_text(SAMPLE_TEXT, shift1, shift2)
        decrypted = decrypt_text(encrypted, shift1, shift2)

        if decrypted == SAMPLE_TEXT:
            print(f"PASS  shift1={shift1}, shift2={shift2}")
            passed += 1
        else:
            print(f"FAIL  shift1={shift1}, shift2={shift2}")
            print(f"      original : {SAMPLE_TEXT!r}")
            print(f"      decrypted: {decrypted!r}")
            failed += 1

    print()
    print(f"{passed} passed, {failed} failed out of {len(TEST_CASES)} cases.")


if __name__ == "__main__":
    run_tests()
