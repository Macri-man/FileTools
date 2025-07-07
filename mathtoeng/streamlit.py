# file: app.py
import streamlit as st
from mathtoeng import translate_latex_to_english

st.set_page_config(page_title="LaTeX Math to English")
st.title("LaTeX → English Math Translator")

latex_input = st.text_input("Enter a LaTeX math expression (e.g. `\\sum_{i=1}^n i^2`)", value="\\sum_{i=1}^n i^2")

if st.button("Translate"):
    english_output = translate_latex_to_english(latex_input)
    st.success("✅ English Translation")
    st.write(english_output)
