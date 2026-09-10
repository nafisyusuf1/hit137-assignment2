"""
evaluator.py
HIT137 Group Assignment 2 - Question 2

A recursive-descent mathematical expression evaluator built entirely from
plain functions (no classes are defined anywhere in this module, as required
by the assignment brief).

Grammar (lowest -> highest binding), one function per precedence level:

expression -> term (("+" | "-") term)*      left assoc
term       -> unary (("*" | "/" | "%") unary | implicit-mult)*   left assoc
unary      -> "-" unary | power              prefix
power      -> primary ("^" unary)?           right assoc
primary    -> NUM | "(" expression ")"

Parser state is carried as an explicit integer index (`pos`) that each parse
function receives and returns, so no mutable parser object/class is needed.

Design notes
------------
* Implicit multiplication is only inferred when a parenthesis is involved,
  e.g. "2(3+4)", "(3+4)2", "(2)(3)". Two bare adjacent number tokens such as
  "2 3" are explicitly NOT implicit multiplication (assignment brief), so
  that input is reported as an ERROR.
* Unary "+" is not supported and produces an ERROR.
* Errors are signalled with the built-in ValueError - no custom exception
  class is declared, keeping the module strictly function-based.
"""

import os
import sys
import time
import json

# Token type constants
NUM = "NUM"
OP = "OP"
LPAREN = "LPAREN"
RPAREN = "RPAREN"
END = "END"

OPERATORS = "+-*/%^"

# ---------------------------------------------------------------------------
# 1. Tokeniser
# ---------------------------------------------------------------------------

def tokenize(expression):
    """Convert an expression string into a list of (type, value) tuples.

    A number literal is one or more digits, optionally followed by a single
    '.' and one or more digits. Whitespace is skipped. Any other character
    raises ValueError.
    """
    tokens = []
    i = 0
    length = len(expression)

    while i < length:
        ch = expression[i]

        if ch.isspace():
            i += 1
            continue

        if ch.isdigit():
            start = i
            while i < length and expression[i].isdigit():
                i += 1
            # optional single fractional part
            if i + 1 < length and expression[i] == "." and expression[i + 1].isdigit():
                i += 1
                while i < length and expression[i].isdigit():
                    i += 1
            tokens.append((NUM, expression[start:i]))
            continue

        if ch in OPERATORS:
            tokens.append((OP, ch))
            i += 1
            continue

        if ch == "(":
            tokens.append((LPAREN, "("))
            i += 1
            continue

        if ch == ")":
            tokens.append((RPAREN, ")"))
            i += 1
            continue

        raise ValueError("Unrecognised character: " + repr(ch))

    tokens.append((END, ""))
    return tokens


def tokens_to_string(tokens):
    """Render tokens as '[TYPE:value] ... [END]'."""
    parts = []
    for token_type, token_value in tokens:
        if token_type == END:
            parts.append("[END]")
        else:
            parts.append("[" + token_type + ":" + token_value + "]")
    return " ".join(parts)


# ---------------------------------------------------------------------------
# 2. Recursive-descent parser
#
# Parse tree nodes are plain tuples:
#   ("num", "<literal>")
#   ("neg", operand_node)
#   ("bin", "<op>", left_node, right_node)
#
# Every parse function has the signature f(tokens, pos) -> (node, new_pos).
# ---------------------------------------------------------------------------

def parse(tokens):
    """Parse a full token list and return the root parse-tree node."""
    node, pos = parse_expression(tokens, 0)
    if tokens[pos][0] != END:
        raise ValueError("Unexpected trailing token: " + str(tokens[pos]))
    return node


def parse_expression(tokens, pos):
    """Level 1: '+' and '-' (left associative)."""
    node, pos = parse_term(tokens, pos)
    while tokens[pos][0] == OP and tokens[pos][1] in ("+", "-"):
        operator = tokens[pos][1]
        right, pos = parse_term(tokens, pos + 1)
        node = ("bin", operator, node, right)
    return node, pos


def parse_term(tokens, pos):
    """Level 2: '*', '/', '%' and implicit multiplication (left associative)."""
    node, pos = parse_unary(tokens, pos)

    while True:
        token_type, token_value = tokens[pos]

        if token_type == OP and token_value in ("*", "/", "%"):
            right, pos = parse_unary(tokens, pos + 1)
            node = ("bin", token_value, node, right)
            continue

        # Implicit multiplication: a factor immediately followed by '('
        # e.g. 2(3+4), (1+2)(3+4)
        if token_type == LPAREN:
            right, pos = parse_unary(tokens, pos)
            node = ("bin", "*", node, right)
            continue

        # Implicit multiplication: ')' immediately followed by a number
        # e.g. (3+4)2. Two bare numbers ("2 3") are NOT implicit
        # multiplication, so this only applies straight after a ')'.
        if token_type == NUM and pos > 0 and tokens[pos - 1][0] == RPAREN:
            right, pos = parse_unary(tokens, pos)
            node = ("bin", "*", node, right)
            continue

        break

    return node, pos


def parse_unary(tokens, pos):
    """Level 3: prefix unary minus. Unary plus is an error."""
    token_type, token_value = tokens[pos]

    if token_type == OP and token_value == "-":
        operand, pos = parse_unary(tokens, pos + 1)
        return ("neg", operand), pos

    if token_type == OP and token_value == "+":
        raise ValueError("Unary '+' is not supported")

    return parse_power(tokens, pos)


def parse_power(tokens, pos):
    """Level 4: '^' (right associative, binds tighter than unary minus)."""
    base, pos = parse_primary(tokens, pos)
    if tokens[pos][0] == OP and tokens[pos][1] == "^":
        # Recurse through parse_unary so that 2^-3 and 2^3^2 both work and
        # exponentiation stays right associative.
        exponent, pos = parse_unary(tokens, pos + 1)
        return ("bin", "^", base, exponent), pos
    return base, pos


def parse_primary(tokens, pos):
    """Number literals and parenthesised sub-expressions."""
    token_type, token_value = tokens[pos]

    if token_type == NUM:
        return ("num", token_value), pos + 1

    if token_type == LPAREN:
        node, pos = parse_expression(tokens, pos + 1)
        if tokens[pos][0] != RPAREN:
            raise ValueError("Expected ')'")
        return node, pos + 1

    raise ValueError("Unexpected token: " + token_type + ":" + token_value)


# ---------------------------------------------------------------------------
# 3. Formatting helpers
# ---------------------------------------------------------------------------

def format_value(value):
    """Whole numbers print without a decimal point, otherwise rounded to
    up to 4 decimal places with no padded trailing zeros (e.g. 5.75, not
    5.7500; 33.3333 stays as-is)."""
    if value == int(value):
        return str(int(value))
    rounded = round(value, 4)
    text = "{:.4f}".format(rounded).rstrip("0").rstrip(".")
    return text


def tree_to_string(node):
    """Render a parse tree, e.g. '(+ 3 (* 4 5))' or '(neg (+ 3 4))'."""
    kind = node[0]

    if kind == "num":
        return format_value(float(node[1]))

    if kind == "neg":
        return "(neg " + tree_to_string(node[1]) + ")"

    if kind == "bin":
        operator = node[1]
        return ("(" + operator + " " + tree_to_string(node[2]) + " "
                + tree_to_string(node[3]) + ")")

    raise ValueError("Unknown parse-tree node")


# ---------------------------------------------------------------------------
# 4. Evaluation
# ---------------------------------------------------------------------------

def evaluate_tree(node):
    """Evaluate a parse tree and return a float."""
    kind = node[0]

    if kind == "num":
        return float(node[1])

    if kind == "neg":
        return -evaluate_tree(node[1])

    if kind == "bin":
        operator = node[1]
        left = evaluate_tree(node[2])
        right = evaluate_tree(node[3])

        if operator == "+":
            return left + right
        if operator == "-":
            return left - right
        if operator == "*":
            return left * right
        if operator == "/":
            if right == 0:
                raise ZeroDivisionError("division by zero")
            return left / right
        if operator == "%":
            if right == 0:
                raise ZeroDivisionError("modulo by zero")
            return left % right
        if operator == "^":
            result = left ** right
            if isinstance(result, complex):
                raise ValueError("complex result is not supported")
            return float(result)

    raise ValueError("Unknown parse-tree node")


# ---------------------------------------------------------------------------
# 5. Per-expression driver
# ---------------------------------------------------------------------------

def evaluate_expression(expression):
    """Process one expression and return its result dictionary."""
    entry = {"input": expression, "tree": "ERROR",
             "tokens": "ERROR", "result": "ERROR"}

    try:
        tokens = tokenize(expression)
    except ValueError:
        return entry

    entry["tokens"] = tokens_to_string(tokens)

    try:
        tree = parse(tokens)
        entry["tree"] = tree_to_string(tree)
    except (ValueError, IndexError):
        entry["tree"] = "ERROR"
        return entry

    try:
        value = evaluate_tree(tree)
        if value != value or value in (float("inf"), float("-inf")):
            raise ValueError("non-finite result")
        entry["result"] = value
    except (ZeroDivisionError, ValueError, OverflowError):
        entry["result"] = "ERROR"

    return entry


def result_to_string(result):
    """Render the Result line value."""
    if isinstance(result, str):
        return "ERROR"
    return format_value(result)


def gather_statistics(entries):
    """Gather statistics about processing results."""
    successful = sum(1 for e in entries if e["result"] != "ERROR")
    errors = len(entries) - successful
    avg_tree_depth = 0
    
    def get_tree_depth(tree_str):
        """Estimate parse tree depth from string representation."""
        if tree_str == "ERROR":
            return 0
        return tree_str.count("(")
    
    if successful > 0:
        total_depth = sum(get_tree_depth(e["tree"]) for e in entries if e["tree"] != "ERROR")
        avg_tree_depth = total_depth / successful
    
    return {
        "total": len(entries),
        "successful": successful,
        "errors": errors,
        "avg_tree_depth": avg_tree_depth
    }


def export_to_json(entries, output_path):
    """Export results to JSON format."""
    json_data = []
    for entry in entries:
        json_entry = {
            "input": entry["input"],
            "tokens": entry["tokens"],
            "tree": entry["tree"],
            "result": entry["result"] if entry["result"] == "ERROR" else float(entry["result"])
        }
        json_data.append(json_entry)
    
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(json_data, handle, indent=2)


def validate_expression(expression):
    """Quick validation of expression structure before full parsing."""
    if not expression or not expression.strip():
        return False, "Empty expression"
    
    # Check balanced parentheses
    paren_count = 0
    for ch in expression:
        if ch == "(":
            paren_count += 1
        elif ch == ")":
            paren_count -= 1
            if paren_count < 0:
                return False, "Unbalanced parentheses"
    
    if paren_count != 0:
        return False, "Unbalanced parentheses"
    
    # Check for invalid character sequences
    if "  " in expression:  # double space is not invalid, just checking
        pass
    
    return True, "Valid"


def generate_report(entries):
    """Generate a detailed analysis report of results."""
    report = {}
    report["expressions_by_success"] = {"success": [], "error": []}
    
    for entry in entries:
        if entry["result"] == "ERROR":
            report["expressions_by_success"]["error"].append(entry["input"])
        else:
            report["expressions_by_success"]["success"].append({
                "input": entry["input"],
                "result": entry["result"]
            })
    
    report["error_count"] = len(report["expressions_by_success"]["error"])
    report["success_count"] = len(report["expressions_by_success"]["success"])
    
    return report


def profile_operation(func_name, func, *args, **kwargs):
    """Profile a single operation and return result with timing."""
    start = time.time()
    result = func(*args, **kwargs)
    elapsed = time.time() - start
    return result, elapsed


# ---------------------------------------------------------------------------
# 6. Required public interface
# ---------------------------------------------------------------------------

def evaluate_file(input_path):
    """Read expressions from input_path (one per line), write output.txt to
    the same directory, and return a list of result dictionaries."""
    start_time = time.time()
    
    with open(input_path, "r", encoding="utf-8") as handle:
        lines = [line.strip() for line in handle]

    expressions = [line for line in lines if line != ""]

    entries = []
    blocks = []
    cache = {}
    cache_hits = 0
    validation_checks = 0
    
    # Performance tracking
    time_tokenize = 0
    time_parse = 0
    time_evaluate = 0
    time_format = 0
    
    for expression in expressions:
        if expression in cache:
            entry = cache[expression]
            cache_hits += 1
        else:
            # Pre-validate before full evaluation
            is_valid, validation_msg = validate_expression(expression)
            validation_checks += 1
            
            entry = {"input": expression, "tree": "ERROR",
                     "tokens": "ERROR", "result": "ERROR"}

            if not is_valid:
                entry["tokens"] = "ERROR (" + validation_msg + ")"
                cache[expression] = entry
                entries.append(entry)
                blocks.append(
                    "Input: " + entry["input"] + "\n"
                    + "Tree: " + entry["tree"] + "\n"
                    + "Tokens: " + entry["tokens"] + "\n"
                    + "Result: " + result_to_string(entry["result"])
                )
                continue

            try:
                tokens, t = profile_operation("tokenize", tokenize, expression)
                time_tokenize += t
            except ValueError:
                cache[expression] = entry
                entries.append(entry)
                blocks.append(
                    "Input: " + entry["input"] + "\n"
                    + "Tree: " + entry["tree"] + "\n"
                    + "Tokens: " + entry["tokens"] + "\n"
                    + "Result: " + result_to_string(entry["result"])
                )
                continue

            entry["tokens"], t = profile_operation("tokens_to_string", tokens_to_string, tokens)
            time_format += t

            try:
                tree, t = profile_operation("parse", parse, tokens)
                time_parse += t
                entry["tree"] = tree_to_string(tree)
            except (ValueError, IndexError):
                entry["tree"] = "ERROR"
                cache[expression] = entry
                entries.append(entry)
                blocks.append(
                    "Input: " + entry["input"] + "\n"
                    + "Tree: " + entry["tree"] + "\n"
                    + "Tokens: " + entry["tokens"] + "\n"
                    + "Result: " + result_to_string(entry["result"])
                )
                continue

            try:
                value, t = profile_operation("evaluate_tree", evaluate_tree, tree)
                time_evaluate += t
                if value != value or value in (float("inf"), float("-inf")):
                    raise ValueError("non-finite result")
                entry["result"] = value
            except (ZeroDivisionError, ValueError, OverflowError):
                entry["result"] = "ERROR"
            
            cache[expression] = entry
        
        entries.append(entry)
        blocks.append(
            "Input: " + entry["input"] + "\n"
            + "Tree: " + entry["tree"] + "\n"
            + "Tokens: " + entry["tokens"] + "\n"
            + "Result: " + result_to_string(entry["result"])
        )

    elapsed = time.time() - start_time
    stats = gather_statistics(entries)
    
    output_dir = os.path.dirname(os.path.abspath(input_path))
    output_path = os.path.join(output_dir, "output.txt")
    json_path = os.path.join(output_dir, "output.json")
    report_path = os.path.join(output_dir, "report.json")
    
    summary = (f"\n\nSummary:\n"
               f"  Total expressions: {stats['total']}\n"
               f"  Successful: {stats['successful']}\n"
               f"  Errors: {stats['errors']}\n"
               f"  Avg tree depth: {stats['avg_tree_depth']:.2f}\n"
               f"  Unique expressions: {len(cache)}\n"
               f"  Cache hits: {cache_hits}\n"
               f"  Validations performed: {validation_checks}\n"
               f"  Processing time: {elapsed:.6f}s\n"
               f"\nTiming breakdown:\n"
               f"  Tokenize: {time_tokenize:.6f}s\n"
               f"  Format tokens: {time_format:.6f}s\n"
               f"  Parse: {time_parse:.6f}s\n"
               f"  Evaluate: {time_evaluate:.6f}s")
    
    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write("\n\n".join(blocks))
        handle.write(summary)
    
    # Also export to JSON
    export_to_json(entries, json_path)
    
    # Export detailed report
    report = generate_report(entries)
    with open(report_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)

    return entries


def main():
    """Evaluate input.txt or a path supplied on the command line."""
    here = os.path.dirname(os.path.abspath(__file__))
    if len(sys.argv) == 2 and sys.argv[1] in ("-h", "--help"):
        print("Usage: python evaluator.py [input_file]")
        print("Reads one mathematical expression per line.")
        print("Default input: input.txt next to evaluator.py")
        return
    if len(sys.argv) > 2:
        print("Usage: python evaluator.py [input_file]")
        return
    input_path = sys.argv[1] if len(sys.argv) == 2 else os.path.join(here, "input.txt")

    start = time.time()
    try:
        results = evaluate_file(input_path)
    except FileNotFoundError:
        print(f"Could not find input file: {input_path}")
        print("Provide a valid file path or place input.txt next to evaluator.py.")
        return
    except OSError as error:
        print(f"Could not read input file '{input_path}': {error}")
        return
    elapsed = time.time() - start

    print("Processed " + str(len(results)) + " expression(s).")
    print(f"Total execution time: {elapsed:.6f}s")
    print("Output files:")
    print("  - output.txt (formatted results)")
    print("  - output.json (JSON results)")
    print("  - report.json (detailed report)")


if __name__ == "__main__":
    main()
