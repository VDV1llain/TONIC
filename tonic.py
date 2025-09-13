# Tonic Interpreter

variables = {}

def emit(value):
    print(value)

def eval_expr(expr):
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

    # Expression (supports +, -, *, /, %, ==, <, >, and, or)
    try:
        return eval(expr, {}, variables)
    except Exception as e:
        raise ValueError(f"Invalid expression: {expr} ({e})")

def execute_lines(lines):
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            i += 1
            continue

        # bind x = 5
        if stripped.startswith("bind "):
            parts = stripped[5:].split("=", 1)
            name = parts[0].strip()
            value = eval_expr(parts[1].strip())
            variables[name] = value
            i += 1
            continue

        # emit x
        if stripped.startswith("emit "):
            expr = stripped[5:].strip()
            emit(eval_expr(expr))
            i += 1
            continue


        # Unified if/orif/else chain handling
        if stripped.startswith("if ") and stripped.endswith(":"):
            branches = []
            # Collect the initial if branch
            cond = stripped[3:-1].strip()
            block = []
            i += 1
            while i < len(lines) and lines[i].startswith("    "):
                block.append(lines[i][4:])
                i += 1
            branches.append((cond, block))

            # Collect subsequent orif/else branches at the same indentation level
            while i < len(lines):
                next_line = lines[i].rstrip()
                next_stripped = next_line.strip()
                # Check if line starts with orif or else: without indentation
                if next_stripped.startswith("orif ") and next_stripped.endswith(":") and not next_line.startswith("    "):
                    cond = next_stripped[5:-1].strip()
                    block = []
                    i += 1
                    while i < len(lines) and lines[i].startswith("    "):
                        block.append(lines[i][4:])
                        i += 1
                    branches.append((cond, block))
                elif next_stripped == "else:" and not next_line.startswith("    "):
                    block = []
                    i += 1
                    while i < len(lines) and lines[i].startswith("    "):
                        block.append(lines[i][4:])
                        i += 1
                    branches.append((None, block))
                    break
                else:
                    break

            branch_executed = False
            for cond, block in branches:
                if cond is None:
                    if not branch_executed:
                        execute_lines(block)
                        branch_executed = True
                else:
                    if not branch_executed and eval_expr(cond):
                        execute_lines(block)
                        branch_executed = True
            continue

        # repeat x in N:
        if stripped.startswith("repeat ") and " in " in stripped and stripped.endswith(":"):
            loop_part = stripped[7:-1].strip()
            var, count_str = loop_part.split(" in ")
            var = var.strip()
            count = eval_expr(count_str.strip())

            block = []
            i += 1
            while i < len(lines) and lines[i].startswith("    "):
                block.append(lines[i][4:])
                i += 1

            for val in range(count):
                variables[var] = val
                execute_lines(block)
            continue

        # repeat N:
        if stripped.startswith("repeat ") and stripped.endswith(":"):
            count_str = stripped[7:-1].strip()
            count = eval_expr(count_str)

            block = []
            i += 1
            while i < len(lines) and lines[i].startswith("    "):
                block.append(lines[i][4:])
                i += 1

            for _ in range(count):
                execute_lines(block)
            continue

        # Unknown command
        raise ValueError(f"Unknown command: {stripped}")

def run_file(filename):
    with open(filename, "r") as f:
        lines = f.readlines()
    execute_lines(lines)

if __name__ == "__main__":
    run_file("examples/test5.tnc")