# file: math2english_sympy.py
from sympy import *
from sympy.parsing.latex import parse_latex
from sympy.abc import _clash
from sympy.core.function import AppliedUndef

def expr_to_english(expr) -> str:
    if isinstance(expr, Symbol):
        return str(expr)

    elif isinstance(expr, Integer) or isinstance(expr, Float):
        return str(expr)

    elif isinstance(expr, Add):
        return " plus ".join(expr_to_english(arg) for arg in expr.args)

    elif isinstance(expr, Mul):
        return " times ".join(expr_to_english(arg) for arg in expr.args)

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
        return str(expr)  # fallback

def translate_latex_to_english(latex_expr: str) -> str:
    try:
        parsed = parse_latex(latex_expr)
        return expr_to_english(parsed)
    except Exception as e:
        return f"Could not parse: {e}"
