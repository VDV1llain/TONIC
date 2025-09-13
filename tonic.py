# Tonic Interpreter
#
# This interpreter executes Tonic language scripts, supporting:
# - Variable binding with `bind` statements
# - Emitting output with `emit`
# - Conditional execution using `if`, `orif`, and `else` branches
# - Looping constructs with `repeat` loops, including indexed loops (`repeat x in N`) and simple count loops (`repeat N`)
# - Expression evaluation including literals (strings, integers), variable lookups, basic arithmetic, and string concatenation fallback

variables = {}

def emit(value):
    print(value)

# --------------------------
# Expression Evaluation
# --------------------------
def eval_expr(expr):
    """
    Evaluate an expression in the current variable context.
    Supports:
    - Variable lookup
    - String literals enclosed in double quotes
    - Integer literals
    - Basic arithmetic expressions evaluated with eval()
    - Fallback concatenation of strings and integers for '+' operator
    """
    expr = expr.strip()

    # Variable lookup
    if expr in variables:
        return variables[expr]

    # String literal
    if expr.startswith('"') and expr.endswith('"'):
        return expr[1:-1]

    # Integer literal
    if expr.isdigit():
        return int(expr)

    # Try to eval directly (e.g., arithmetic expressions)
    try:
        result = eval(expr, {}, variables)
        if isinstance(result, (int, str)):
            return result
        else:
            return str(result)
    except Exception:
        # Fallback: handle concatenation of strings and integers separated by '+'
        if '+' in expr:
            parts = expr.split('+')
            vals = [eval_expr(part.strip()) for part in parts]
            # Concatenate all parts as strings
            return ''.join(str(v) for v in vals)
        raise ValueError(f"Invalid expression: {expr}")

# --------------------------
# Command Execution
# --------------------------
def execute_lines(lines):
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            # Skip empty lines and comments
            i += 1
            continue

        # --------------------------
        # Variable Binding: bind x = 5
        # --------------------------
        if stripped.startswith("bind "):
            # Parse variable name and value expression
            parts = stripped[5:].split("=", 1)
            name = parts[0].strip()
            value = eval_expr(parts[1].strip())
            variables[name] = value
            i += 1
            continue

        # --------------------------
        # Output Emission: emit x
        # --------------------------
        if stripped.startswith("emit "):
            # Evaluate expression and print the result
            expr = stripped[5:].strip()
            emit(eval_expr(expr))
            i += 1
            continue

        # --------------------------
        # Conditional Execution: if / orif / else
        # --------------------------
        if stripped.startswith("if ") and stripped.endswith(":"):
            branches = []
            # Collect the initial if branch condition and block
            cond = stripped[3:-1].strip()
            block = []
            i += 1
            # Collect indented block lines for this branch
            while i < len(lines) and lines[i].startswith("    "):
                block.append(lines[i][4:])
                i += 1
            branches.append((cond, block))

            # Collect subsequent orif and else branches at the same indentation level
            while i < len(lines):
                next_line = lines[i].rstrip()
                next_stripped = next_line.strip()
                # orif branch with condition
                if next_stripped.startswith("orif ") and next_stripped.endswith(":") and not next_line.startswith("    "):
                    cond = next_stripped[5:-1].strip()
                    block = []
                    i += 1
                    while i < len(lines) and lines[i].startswith("    "):
                        block.append(lines[i][4:])
                        i += 1
                    branches.append((cond, block))
                # else branch without condition
                elif next_stripped == "else:" and not next_line.startswith("    "):
                    block = []
                    i += 1
                    while i < len(lines) and lines[i].startswith("    "):
                        block.append(lines[i][4:])
                        i += 1
                    branches.append((None, block))
                    break
                else:
                    # No more conditional branches at this level
                    break

            branch_executed = False
            # Evaluate each branch condition in order and execute first matching block
            for cond, block in branches:
                if cond is None:
                    # else branch: execute only if no prior branch executed
                    if not branch_executed:
                        execute_lines(block)
                        branch_executed = True
                else:
                    # if/orif branch: evaluate condition and execute if true and no prior executed
                    if not branch_executed and eval_expr(cond):
                        execute_lines(block)
                        branch_executed = True
            continue

        # --------------------------
        # Looping: repeat x in N:
        # Indexed loop where variable x iterates from 0 to N-1
        # --------------------------
        if stripped.startswith("repeat ") and " in " in stripped and stripped.endswith(":"):
            loop_part = stripped[7:-1].strip()
            var, count_str = loop_part.split(" in ")
            var = var.strip()
            count = eval_expr(count_str.strip())

            block = []
            i += 1
            # Collect indented block lines for the loop body
            while i < len(lines) and lines[i].startswith("    "):
                block.append(lines[i][4:])
                i += 1

            # Execute loop with variable set for each iteration
            for val in range(count):
                variables[var] = val
                execute_lines(block)
            continue

        # --------------------------
        # Looping: repeat N:
        # Simple loop that repeats block N times without loop variable
        # --------------------------
        if stripped.startswith("repeat ") and stripped.endswith(":"):
            count_str = stripped[7:-1].strip()
            count = eval_expr(count_str)

            block = []
            i += 1
            # Collect indented block lines for the loop body
            while i < len(lines) and lines[i].startswith("    "):
                block.append(lines[i][4:])
                i += 1

            # Execute loop body count times
            for _ in range(count):
                execute_lines(block)
            continue

        # --------------------------
        # Unknown command encountered
        # --------------------------
        raise ValueError(f"Unknown command: {stripped}")

def run_file(filename):
    with open(filename, "r") as f:
        lines = f.readlines()
    execute_lines(lines)

if __name__ == "__main__":
    run_file("examples/test5.tnc")