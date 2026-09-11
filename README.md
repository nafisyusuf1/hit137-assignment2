# HIT137 Assignment 2

This repository contains the Question 1 multi-rule shift cipher and the
Question 2 recursive-descent expression evaluator.

## Running the scripts

Run the cipher from the repository folder:

```text
python cipher.py shift1 shift2
```

It reads `raw_text.txt`, writes `encrypted_text.txt`, decrypts that file to
`decrypted_text.txt`, and verifies that the original and decrypted text match.
An optional input path can be supplied as a third argument:

```text
python cipher.py shift1 shift2 input.txt
```

Run the evaluator with one expression per line:

```text
python evaluator.py input.txt
```

It writes `output.txt` beside the input file. Each expression produces exactly
four lines: `Input`, `Tree`, `Tokens`, and `Result`. Blank input lines are
ignored. Without an argument, the evaluator looks for `input.txt` beside the
script.

## Cipher rules

Each character stays in its own character range. Lowercase `a-n` is shifted
forward by `shift1 * shift2`; lowercase `o-z` is shifted backward by
`shift1 + shift2`. Uppercase `A-M` is shifted backward by `shift1`, while
uppercase `N-Z` is shifted forward by `shift2 ** 2`. Digits are shifted forward
by `shift1 - shift2`, wrapping from `9` to `0`. Punctuation, whitespace, and
other characters are unchanged. All shifts wrap within their range, and the
decryption rules reverse the corresponding encryption rule.

## Evaluator grammar

The evaluator accepts integer and decimal numbers, parentheses, binary
operators, and unary minus. Parentheses may imply multiplication in `2(3+4)`
and `(3+4)2`; two adjacent bare numbers are not implicit multiplication.

| Precedence | Grammar | Associativity |
| --- | --- | --- |
| Lowest | `expression -> term (('+' \| '-') term)*` | Left |
|  | `term -> unary (('*' \| '/' \| '%' \| implicit-mult) unary)*` | Left |
|  | `unary -> '-' unary \| power` | Prefix |
| Highest | `power -> primary ('^' unary)?` | Right |
| Primary | `primary -> NUM \| '(' expression ')'` | |

Division or modulo by zero, unsupported characters, unmatched parentheses, and
other malformed expressions are reported as `ERROR` without crashing.

## Example

For an `input.txt` containing:

```text
2(3+4)
2^3^2
1/0
```

`output.txt` contains:

```text
Input: 2(3+4)
Tree: (* 2 (+ 3 4))
Tokens: [NUM:2] [LPAREN:(] [NUM:3] [OP:+] [NUM:4] [RPAREN:)] [END]
Result: 14

Input: 2^3^2
Tree: (^ 2 (^ 3 2))
Tokens: [NUM:2] [OP:^] [NUM:3] [OP:^] [NUM:2] [END]
Result: 512

Input: 1/0
Tree: (/ 1 0)
Tokens: [NUM:1] [OP:/] [NUM:0] [END]
Result: ERROR
```

## Contributions

- **Nafis** — Created the GitHub repository and set up the project structure.
  Wrote the initial implementation of `cipher.py` (Question 1). Added
  documentation and basic test scripts (`test_cipher.py`, `test_evaluator.py`)
  to verify both programs.
- **Andrew & Hashir** — Developed `evaluator.py` (Question 2), including the
  tokenizer, recursive-descent parser, and evaluator.
- **Hashir** — Reviewed and fixed a bug in the cipher's shift logic, added
  input validation and command-line argument support to `cipher.py`.

All contributions are recorded in the commit history of this repository.




