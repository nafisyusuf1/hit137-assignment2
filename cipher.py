"""
HIT137 Assignment 2 - Question 1
Multi-rule shift cipher: encrypts/decrypts raw_text.txt using two
user-supplied shift amounts (shift1, shift2), then verifies the
round trip worked.

Design notes (read this before you present it to your group):
- Every character is classified once, by *what it is* (lowercase
  first/second half, uppercase first/second half, digit, other),
  and a different shift amount is applied depending on that class.
- Because two different rules both act on the 26-letter lowercase
  alphabet (a-n forward, o-z backward) and two different rules both
  act on the 26-letter uppercase alphabet (A-M backward, N-Z
  forward), decryption cannot simply "know" which rule produced a
  given encrypted letter. Instead, decrypt_char() tries the
  candidate that assumes the letter came from the first half; if
  reversing that shift lands back inside the first half, it's the
  right answer. Otherwise it falls back to the second-half rule.
  This is the standard way to make a "two-branch" shift cipher like
  this one reversible.
"""

ALPHABET_SIZE = 26
DIGIT_SIZE = 10


def shift_char_encrypt(ch, shift1, shift2):
    """Apply the forward (encryption) rule to a single character."""
    if ch.islower():
        if 'a' <= ch <= 'n':
            amount = (shift1 * shift2) % ALPHABET_SIZE
            return chr((ord(ch) - ord('a') + amount) % ALPHABET_SIZE + ord('a'))
        else:  # o-z
            amount = (shift1 + shift2) % ALPHABET_SIZE
            return chr((ord(ch) - ord('a') - amount) % ALPHABET_SIZE + ord('a'))
    elif ch.isupper():
        if 'A' <= ch <= 'M':
            amount = shift1 % ALPHABET_SIZE
            return chr((ord(ch) - ord('A') - amount) % ALPHABET_SIZE + ord('A'))
        else:  # N-Z
            amount = (shift2 ** 2) % ALPHABET_SIZE
            return chr((ord(ch) - ord('A') + amount) % ALPHABET_SIZE + ord('A'))
    elif ch.isdigit():
        amount = (shift1 - shift2) % DIGIT_SIZE
        return chr((ord(ch) - ord('0') + amount) % DIGIT_SIZE + ord('0'))
    else:
        return ch


def shift_char_decrypt(ch, shift1, shift2):
    """Apply the reverse (decryption) rule to a single character."""
    if ch.islower():
        amount_first = (shift1 * shift2) % ALPHABET_SIZE
        candidate_first = chr((ord(ch) - ord('a') - amount_first) % ALPHABET_SIZE + ord('a'))
        if 'a' <= candidate_first <= 'n':
            return candidate_first
        amount_second = (shift1 + shift2) % ALPHABET_SIZE
        return chr((ord(ch) - ord('a') + amount_second) % ALPHABET_SIZE + ord('a'))
    elif ch.isupper():
        amount_first = shift1 % ALPHABET_SIZE
        candidate_first = chr((ord(ch) - ord('A') + amount_first) % ALPHABET_SIZE + ord('A'))
        if 'A' <= candidate_first <= 'M':
            return candidate_first
        amount_second = (shift2 ** 2) % ALPHABET_SIZE
        return chr((ord(ch) - ord('A') - amount_second) % ALPHABET_SIZE + ord('A'))
    elif ch.isdigit():
        amount = (shift1 - shift2) % DIGIT_SIZE
        return chr((ord(ch) - ord('0') - amount) % DIGIT_SIZE + ord('0'))
    else:
        return ch


def encrypt_file(shift1: int, shift2: int, input_path: str, output_path: str) -> None:
    """Reads from input_path and writes encrypted content to output_path."""
    # newline='' stops Python's universal-newline translation from silently
    # turning \r\n into \n -- carriage returns are "other characters" too,
    # and the spec says those must pass through unchanged.
    with open(input_path, 'r', encoding='utf-8', newline='') as f:
        content = f.read()
    encrypted = ''.join(shift_char_encrypt(ch, shift1, shift2) for ch in content)
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        f.write(encrypted)


def decrypt_file(shift1: int, shift2: int, input_path: str, output_path: str) -> None:
    """Reads from input_path (the encrypted file) and writes the decrypted content to output_path."""
    with open(input_path, 'r', encoding='utf-8', newline='') as f:
        content = f.read()
    decrypted = ''.join(shift_char_decrypt(ch, shift1, shift2) for ch in content)
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
        print("  This happens when two different letters land on the same encrypted letter for this shift1/shift2 pair.")
    return success

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


def main():
    shift1 = _read_nonnegative_int("Enter shift1 (non-negative integer): ")
    shift2 = _read_nonnegative_int("Enter shift2 (non-negative integer): ")

    raw_path = "raw_text.txt"
    encrypted_path = "encrypted_text.txt"
    decrypted_path = "decrypted_text.txt"

    try:
        encrypt_file(shift1, shift2, raw_path, encrypted_path)
        print(f"Encrypted '{raw_path}' -> '{encrypted_path}'")

        decrypt_file(shift1, shift2, encrypted_path, decrypted_path)
        print(f"Decrypted '{encrypted_path}' -> '{decrypted_path}'")

        verify_files(raw_path, decrypted_path)
    except FileNotFoundError as e:
        print(f"Could not find file: {e.filename}. Make sure raw_text.txt is in the same folder as cipher.py.")

if __name__ == "__main__":
    main()