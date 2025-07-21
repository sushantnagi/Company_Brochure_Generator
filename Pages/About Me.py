import streamlit as st

st.set_page_config(page_title="About Me", page_icon="😎", layout='wide')

# ───────────── Title & Image ─────────────
st.title("About the Creator")
st.image("mypic.gif", )
st.caption("📸 P.S. This photo is AI-generated.")

# ───────────── Bio & Links ─────────────
st.markdown("""
Hi, I'm **Sushant Nagi** — an engineering student, tech enthusiast, and creator of this project.

This Streamlit app is a fun side project that combines web scraping and generative AI to summarize website content. 
It's built purely for fun, learning, and exploration — not for commercial use.


---

📬 **Contact Me:**

- 📧 [sushantnagi667@gmail.com](mailto:sushantnagi667@gmail.com)
- [💼 LinkedIn](https://www.linkedin.com/in/sushant_nagi)  
- [🐱 GitHub](https://github.com/sushantnagi)  
- [📸 Instagram](https://instagram.com/sushant_nagi)
""", unsafe_allow_html=True)

# ───────────── Footer Quote ─────────────
st.markdown("""---""")
st.markdown("""
<small><i>
"Finally, brethren, whatsoever things are true, whatsoever things are honest, \
whatsoever things are just, whatsoever things are pure, whatsoever things are lovely, \
whatsoever things are of good report; if there be any virtue, and if there be any praise, \
think on these things."
<br>— Philippians 4:8
</i></small>
""", unsafe_allow_html=True)