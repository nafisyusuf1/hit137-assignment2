"""
HIT137 Assignment 2 - Question 1
Multi-rule shift cipher: encrypts/decrypts raw_text.txt using two
user-supplied shift amounts (shift1, shift2), then verifies the
round trip worked.

Design notes (read this before you present it to your group):
- Every character is classified once, by *what it is* (lowercase
  first/second half, uppercase first/second half, digit, other),
  and a different shift amount is applied depending on that class.
- Each rule shifts within its own source range (a-n, o-z, A-M, or
    N-Z), so encrypted characters never cross between ranges. This
    keeps the two-branch cipher reversible without needing to guess
    which rule produced an encrypted character.
"""

import os
import sys


ALPHABET_SIZE = 26
DIGIT_SIZE = 10
LOWER_FIRST_START = ord('a')
LOWER_FIRST_SIZE = 14  # a-n
LOWER_SECOND_START = ord('o')
LOWER_SECOND_SIZE = 12  # o-z
UPPER_FIRST_START = ord('A')
UPPER_FIRST_SIZE = 13  # A-M
UPPER_SECOND_START = ord('N')
UPPER_SECOND_SIZE = 13  # N-Z


def _validate_shifts(shift1: int, shift2: int) -> None:
    """Reject shift values that cannot be used by the cipher."""
    if not isinstance(shift1, int) or isinstance(shift1, bool):
        raise TypeError("shift1 must be an integer")
    if not isinstance(shift2, int) or isinstance(shift2, bool):
        raise TypeError("shift2 must be an integer")
    if shift1 < 0 or shift2 < 0:
        raise ValueError("shift values must be non-negative")


def _validate_character(ch: str) -> None:
    """Reject values that are not exactly one character long."""
    if not isinstance(ch, str) or len(ch) != 1:
        raise TypeError("ch must be a single character")


def _validate_text(text: str) -> None:
    """Reject values that cannot be processed as text."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")


def shift_char_encrypt(ch: str, shift1: int, shift2: int) -> str:
    """Apply the forward (encryption) rule to a single character."""
    _validate_character(ch)
    if 'a' <= ch <= 'n':
        amount = (shift1 * shift2) % LOWER_FIRST_SIZE
        return chr((ord(ch) - LOWER_FIRST_START + amount) % LOWER_FIRST_SIZE + LOWER_FIRST_START)
    elif 'o' <= ch <= 'z':
        amount = (shift1 + shift2) % LOWER_SECOND_SIZE
        return chr((ord(ch) - LOWER_SECOND_START - amount) % LOWER_SECOND_SIZE + LOWER_SECOND_START)
    elif 'A' <= ch <= 'M':
        amount = shift1 % UPPER_FIRST_SIZE
        return chr((ord(ch) - UPPER_FIRST_START - amount) % UPPER_FIRST_SIZE + UPPER_FIRST_START)
    elif 'N' <= ch <= 'Z':
        amount = (shift2 ** 2) % UPPER_SECOND_SIZE
        return chr((ord(ch) - UPPER_SECOND_START + amount) % UPPER_SECOND_SIZE + UPPER_SECOND_START)
    elif '0' <= ch <= '9':
        amount = (shift1 - shift2) % DIGIT_SIZE
        return chr((ord(ch) - ord('0') + amount) % DIGIT_SIZE + ord('0'))
    else:
        return ch


def shift_char_decrypt(ch: str, shift1: int, shift2: int) -> str:
    """Apply the reverse (decryption) rule to a single character."""
    _validate_character(ch)
    if 'a' <= ch <= 'n':
        amount = (shift1 * shift2) % LOWER_FIRST_SIZE
        return chr((ord(ch) - LOWER_FIRST_START - amount) % LOWER_FIRST_SIZE + LOWER_FIRST_START)
    elif 'o' <= ch <= 'z':
        amount = (shift1 + shift2) % LOWER_SECOND_SIZE
        return chr((ord(ch) - LOWER_SECOND_START + amount) % LOWER_SECOND_SIZE + LOWER_SECOND_START)
    elif 'A' <= ch <= 'M':
        amount = shift1 % UPPER_FIRST_SIZE
        return chr((ord(ch) - UPPER_FIRST_START + amount) % UPPER_FIRST_SIZE + UPPER_FIRST_START)
    elif 'N' <= ch <= 'Z':
        amount = (shift2 ** 2) % UPPER_SECOND_SIZE
        return chr((ord(ch) - UPPER_SECOND_START - amount) % UPPER_SECOND_SIZE + UPPER_SECOND_START)
    elif '0' <= ch <= '9':
        amount = (shift1 - shift2) % DIGIT_SIZE
        return chr((ord(ch) - ord('0') - amount) % DIGIT_SIZE + ord('0'))
    else:
        return ch


def encrypt_text(text: str, shift1: int, shift2: int) -> str:
    """Return encrypted text without requiring temporary files."""
    _validate_text(text)
    _validate_shifts(shift1, shift2)
    return ''.join(shift_char_encrypt(ch, shift1, shift2) for ch in text)


def decrypt_text(text: str, shift1: int, shift2: int) -> str:
    """Return decrypted text without requiring temporary files."""
    _validate_text(text)
    _validate_shifts(shift1, shift2)
    return ''.join(shift_char_decrypt(ch, shift1, shift2) for ch in text)


def encrypt_file(shift1: int, shift2: int, input_path: str, output_path: str) -> None:
    """Reads from input_path and writes encrypted content to output_path."""
    _validate_shifts(shift1, shift2)
    # newline='' stops Python's universal-newline translation from silently
    # turning \r\n into \n -- carriage returns are "other characters" too,
    # and the spec says those must pass through unchanged.
    with open(input_path, 'r', encoding='utf-8', newline='') as f:
        content = f.read()
    encrypted = encrypt_text(content, shift1, shift2)
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        f.write(encrypted)


def decrypt_file(shift1: int, shift2: int, input_path: str, output_path: str) -> None:
    """Reads from input_path (the encrypted file) and writes the decrypted content to output_path."""
    _validate_shifts(shift1, shift2)
    with open(input_path, 'r', encoding='utf-8', newline='') as f:
        content = f.read()
    decrypted = decrypt_text(content, shift1, shift2)
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        f.write(decrypted)


def verify_files(original_path: str, decrypted_path: str) -> bool:
    """Compares original_path with decrypted_path and prints/returns whether they match."""
    with open(original_path, 'r', encoding='utf-8', newline='') as f:
        original = f.read()
    with open(decrypted_path, 'r', encoding='utf-8', newline='') as f:
        decrypted = f.read()

    success = original == decrypted
    if success:
        print("Verification successful: decrypted text matches the original.")
    else:
        mismatches = sum(1 for a, b in zip(original, decrypted) if a != b)
        mismatches += abs(len(original) - len(decrypted))
        first_index = next((i for i, (a, b) in enumerate(zip(original, decrypted)) if a != b), min(len(original), len(decrypted)))
        print("Verification failed: decrypted text does NOT match the original.")
        print(f"  {mismatches} character(s) differ (first difference at position {first_index}).")
        print("  Check that the same shift1/shift2 values were used for encryption and decryption.")
    return success


def process_files(shift1: int, shift2: int, raw_path: str,
                  encrypted_path: str, decrypted_path: str) -> bool:
    """Encrypt, decrypt, and verify a file round trip."""
    _validate_shifts(shift1, shift2)
    paths = [os.path.normcase(os.path.abspath(path))
             for path in (raw_path, encrypted_path, decrypted_path)]
    if len(set(paths)) != len(paths):
        raise ValueError("raw, encrypted, and decrypted paths must be different")
    encrypt_file(shift1, shift2, raw_path, encrypted_path)
    decrypt_file(shift1, shift2, encrypted_path, decrypted_path)
    return verify_files(raw_path, decrypted_path)


def _read_nonnegative_int(prompt: str) -> int:
    """Keeps asking until the user types a valid non-negative integer."""
    while True:
        raw = input(prompt)
        try:
            value = int(raw)
        except ValueError:
            print("Please enter a whole number.")
            continue
        if value < 0:
            print("Please enter a non-negative integer.")
            continue
        return value


def main() -> int:
    if len(sys.argv) == 2 and sys.argv[1] in ("-h", "--help"):
        print("Usage: python cipher.py [shift1 shift2 [input_file]]")
        print("Encrypts and decrypts a text file using two non-negative shifts.")
        print("The optional input file defaults to raw_text.txt.")
        print("Without arguments, the shifts are requested interactively.")
        return 0
    if len(sys.argv) == 1:
        shift1 = _read_nonnegative_int("Enter shift1 (non-negative integer): ")
        shift2 = _read_nonnegative_int("Enter shift2 (non-negative integer): ")
    elif len(sys.argv) in (3, 4):
        try:
            shift1 = int(sys.argv[1])
            shift2 = int(sys.argv[2])
            _validate_shifts(shift1, shift2)
        except (TypeError, ValueError):
            print("Usage: python cipher.py [shift1 shift2 [input_file]]")
            print("Both shifts must be non-negative integers.")
            return 2
    else:
        print("Usage: python cipher.py [shift1 shift2 [input_file]]")
        return 2

    here = os.path.dirname(os.path.abspath(__file__))
    raw_path = os.path.abspath(sys.argv[3]) if len(sys.argv) == 4 else os.path.join(here, "raw_text.txt")
    output_dir = os.path.dirname(raw_path)
    encrypted_path = os.path.join(output_dir, "encrypted_text.txt")
    decrypted_path = os.path.join(output_dir, "decrypted_text.txt")

    try:
        encrypt_file(shift1, shift2, raw_path, encrypted_path)
        print(f"Encrypted '{raw_path}' -> '{encrypted_path}'")

        decrypt_file(shift1, shift2, encrypted_path, decrypted_path)
        print(f"Decrypted '{encrypted_path}' -> '{decrypted_path}'")

        return 0 if verify_files(raw_path, decrypted_path) else 1
    except FileNotFoundError as e:
        print(f"Could not find input file: {e.filename}")
        return 1
    except UnicodeError as e:
        print(f"Could not decode cipher file as UTF-8: {e}")
        return 1
    except OSError as e:
        print(f"Could not process cipher files: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())