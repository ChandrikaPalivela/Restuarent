import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# -----------------------------
# API Key (hardcoded)
# -----------------------------
os.environ["GOOGLE_API_KEY"] = "AQ.Ab8RN6JWdpPh5xKPtxK_AYvLtnvf5LqPcdiCgW1RQUcqpDm7zg"

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="Restaurant and Menu Generator", layout="wide")

st.markdown(
    """
    <style>
    .card {
        padding: 16px 20px;
        border-radius: 8px;
        font-size: 18px;
        margin-bottom: 10px;
    }
    .card-blue {
        background-color: #16324a;
        color: #6cb6ff;
        border: 1px solid #234b6e;
    }
    .card-green {
        background-color: #0f3d2e;
        color: #4ade80;
        border: 1px solid #1c5c45;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# LLM
# -----------------------------
@st.cache_resource
def get_llm():
    return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.6)


def get_restaurant_name(cuisine: str) -> str:
    llm = get_llm()
    prompt = PromptTemplate(
        input_variables=["cuisine"],
        template="I want to open a restaurant for {cuisine} food. Suggest only ONE fancy name for this. Return only the name, nothing else.",
    )
    chain = prompt | llm
    return chain.invoke({"cuisine": cuisine}).content.strip().strip('"')


def get_menu_items(restaurant_name: str, cuisine: str) -> list[str]:
    llm = get_llm()
    prompt = PromptTemplate(
        input_variables=["restaurant_name", "cuisine"],
        template=(
            "Suggest only 7 famous {cuisine} menu item names for a restaurant "
            "called {restaurant_name}. Return them as a plain list, one item "
            "per line, no numbering, no bullets, no descriptions."
        ),
    )
    chain = prompt | llm
    raw = chain.invoke({"restaurant_name": restaurant_name, "cuisine": cuisine}).content
    return [line.strip("-•* ").strip() for line in raw.splitlines() if line.strip()]


# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.markdown("## 🍽️ Choose Cuisine")
countries = ["Indian", "Chinese", "Russian", "Italian", "Mexican", "Japanese", "French", "Thai"]
cuisine = st.sidebar.selectbox("Select a cuisine", countries)
generate_clicked = st.sidebar.button("Generate")

# -----------------------------
# Session state
# -----------------------------
if "cuisine_result" not in st.session_state:
    st.session_state.cuisine_result = None
    st.session_state.restaurant_name = None
    st.session_state.menu_items = None

if generate_clicked:
    with st.spinner("Generating..."):
        name = get_restaurant_name(cuisine)
        items = get_menu_items(name, cuisine)
    st.session_state.cuisine_result = cuisine
    st.session_state.restaurant_name = name
    st.session_state.menu_items = items

# -----------------------------
# Main content
# -----------------------------
st.markdown("# 🍲🧑🏼‍🍳 Restaurant and Menu Generator")

if st.session_state.cuisine_result:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Selected Cuisine")
        st.markdown(f'<div class="card card-blue">{st.session_state.cuisine_result}</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("### Suggested Restaurant Name")
        st.markdown(f'<div class="card card-green">{st.session_state.restaurant_name}</div>', unsafe_allow_html=True)

    st.markdown("### Menu Items")
    for item in st.session_state.menu_items:
        st.markdown(f"- {item}")
else:
    st.info("Select a cuisine in the sidebar and click **Generate**.")