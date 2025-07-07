from sympy import *
from sympy.core.function import AppliedUndef
from sympy.parsing.latex import parse_latex

def expr_to_english(expr) -> str:
    if isinstance(expr, Eq):
        left, right = expr.args
        return f"{expr_to_english(left)} equals {expr_to_english(right)}"

    elif isinstance(expr, Symbol):
        return str(expr)

    elif isinstance(expr, Integer) or isinstance(expr, Float):
        return str(expr)

    elif isinstance(expr, Add):
        return " plus ".join(expr_to_english(arg) for arg in expr.args)

    elif isinstance(expr, Mul):
        args = expr.args
        parts = []
        for i, arg in enumerate(args):
            if isinstance(arg, Symbol) and i > 0 and isinstance(args[i-1], (Integer, Symbol)):
                # Skip "times" in 2x or ab
                parts.append(expr_to_english(arg))
            else:
                parts.append(expr_to_english(arg))
        return " ".join(parts)

    elif isinstance(expr, Pow):
        base, exp = expr.args
        if exp == 0.5:
            return f"square root of {expr_to_english(base)}"
        elif exp == 2:
            return f"{expr_to_english(base)} squared"
        elif exp == 3:
            return f"{expr_to_english(base)} cubed"
        else:
            return f"{expr_to_english(base)} to the power of {expr_to_english(exp)}"

    elif isinstance(expr, Sum):
        fn, (var, lower, upper) = expr.args
        return f"sum of {expr_to_english(fn)} from {expr_to_english(var)} equals {expr_to_english(lower)} to {expr_to_english(upper)}"

    elif isinstance(expr, Integral):
        fn, var = expr.args
        return f"integral of {expr_to_english(fn)} with respect to {expr_to_english(var)}"

    elif isinstance(expr, Derivative):
        fn, var = expr.args
        return f"derivative of {expr_to_english(fn)} with respect to {expr_to_english(var)}"

    elif isinstance(expr, AppliedUndef):  # functions like f(x)
        return f"{expr.func} of {', '.join(expr_to_english(arg) for arg in expr.args)}"

    else:
        return str(expr)

def translate_latex_to_english(latex_expr: str) -> str:
    try:
        parsed = parse_latex(latex_expr)
        return expr_to_english(parsed)
    except Exception as e:
        return f"Could not parse: {e}"
