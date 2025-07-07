import streamlit as st
import re

# Reuse same mapping
SYMBOLS_TO_ENGLISH = {
    r'\bsum\b|∑': "sum of",
    r'\bprod\b|∏': "product of",
    r'd/d([a-zA-Z])': r"derivative with respect to \1",
    r'∫': "integral of",
    r'dx': "with respect to x",
    r'dy': "with respect to y",
    r'√': "square root of",
    r'\^2\b': " squared",
    r'\^3\b': " cubed",
    r'\^(\d+)': r" to the power of \1",
    r'≠': "not equal to",
    r'≤': "less than or equal to",
    r'≥': "greater than or equal to",
    r'→|⇒': "implies",
    r'↔': "if and only if",
    r'∀': "for all",
    r'∃': "there exists",
    r'f\((.*?)\)': r"f of \1"
}

def translate_math(expr: str) -> str:
    for pattern, replacement in SYMBOLS_TO_ENGLISH.items():
        expr = re.sub(pattern, replacement, expr)
    return expr

st.title("🧠 Math-to-English Translator")
math_input = st.text_input("Enter a math expression (LaTeX or plain):", value="∑_{i=1}^n i^2")

if st.button("Translate"):
    english_output = translate_math(math_input)
    st.success("✅ English Translation")
    st.write(english_output)
