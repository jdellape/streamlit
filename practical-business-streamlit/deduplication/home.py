import streamlit as st

st.set_page_config(
    page_title="Home"
)

st.header("Practical Business Streamlit: Data Deduplication")
st.subheader("Scenarios Explored")

st.markdown("1. **Exact Duplication**: Find rows in which all column values are identical across rows.")
st.image('images/exact_duplication.png')
st.markdown("2. **Partial Duplication**: Find rows in which an ID column which we anticipate to be unique is repeated across rows. We know there is a difference in one or more column values causing ID field duplication.")
st.image('images/partial_duplication.png')
st.markdown("3. **Fuzzy Duplication**: Find rows where two or more rows are similar enough that they appear to be duplicates. Resolution requires a more technically involved process such as string similarity scoring across multiple columns.")
st.image('images/fuzzy_duplication.png')








