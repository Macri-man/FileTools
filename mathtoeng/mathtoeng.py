import re
from sympy import *
from sympy.parsing.latex import parse_latex
from sympy.core.function import AppliedUndef

def pretty_symbol_name(sym):
    # sym.name might be 'x_i', 'y_bar', 'z_1', etc.
    name = sym.name

    # Handle underscore subscripts:
    if "_" in name:
        base, sub = name.split("_", 1)
        # Special known suffixes
        if sub == "bar":
            return f"{base} bar"
        # Otherwise just spell out base and sub
        return f"{base} {sub}"
    else:
        return name

def translate_latex_to_english(expr) -> str:
    if isinstance(expr, Eq):
        left, right = expr.args
        return f"{translate_latex_to_english(left)} equals {translate_latex_to_english(right)}"

    elif isinstance(expr, Symbol):
        return pretty_symbol_name(expr)

    elif isinstance(expr, (Integer, Float)):
        return str(expr)

    elif isinstance(expr, Add):
        return " plus ".join(translate_latex_to_english(arg) for arg in expr.args)

    elif isinstance(expr, Mul):
        args = expr.args
        parts = []
        for i, arg in enumerate(args):
            if i > 0 and isinstance(args[i - 1], (Integer, Symbol)) and isinstance(arg, Symbol):
                parts.append(translate_latex_to_english(arg))  # skip "times"
            else:
                parts.append(translate_latex_to_english(arg))
        return " ".join(parts)

    elif isinstance(expr, Pow):
        base, exp = expr.args
        if exp == Rational(1, 2):
            return f"square root of {translate_latex_to_english(base)}"
        elif exp == 2:
            return f"{translate_latex_to_english(base)} squared"
        elif exp == 3:
            return f"{translate_latex_to_english(base)} cubed"
        else:
            return f"{translate_latex_to_english(base)} to the power of {translate_latex_to_english(exp)}"

    elif isinstance(expr, Sum):
        fn, (var, lower, upper) = expr.args
        return f"sum of {translate_latex_to_english(fn)} from {translate_latex_to_english(var)} equals {translate_latex_to_english(lower)} to {translate_latex_to_english(upper)}"

    elif isinstance(expr, Integral):
        fn, var = expr.args
        return f"integral of {translate_latex_to_english(fn)} with respect to {translate_latex_to_english(var)}"

    elif isinstance(expr, Derivative):
        fn, var = expr.args
        return f"derivative of {translate_latex_to_english(fn)} with respect to {translate_latex_to_english(var)}"

    elif isinstance(expr, AppliedUndef):
        return f"{expr.func} of {', '.join(translate_latex_to_english(arg) for arg in expr.args)}"

    else:
        return str(expr)
