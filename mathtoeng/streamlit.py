import streamlit as st
from mathtoeng import translate_latex_to_english

# Session state for history
if "history" not in st.session_state:
    st.session_state.history = []

st.set_page_config(page_title="LaTeX Math to English", layout="centered")
st.title("📘 LaTeX → English Translator")

st.markdown("Enter a LaTeX math expression and receive a natural language description.")

latex_input = st.text_input("🔢 LaTeX Expression", value="\\sum_{i=1}^n i^2")

if st.button("🔍 Translate"):
    english = translate_latex_to_english(latex_input)
    st.session_state.history.append((latex_input, english))
    st.success("✅ English Translation")
    st.markdown(f"**Result:** {english}")

# Divider
st.markdown("---")

# 🕓 History
with st.expander("🕓 Translation History"):
    for idx, (latex, eng) in enumerate(reversed(st.session_state.history), 1):
        st.markdown(f"**{idx}.** `{latex}` → *{eng}*")
        col1, col2 = st.columns([3, 1])
        with col2:
            st.button("📋 Copy", key=f"copy_{idx}", on_click=st.experimental_set_query_params, args=(), kwargs={"latex": latex, "eng": eng})
