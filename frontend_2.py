import streamlit as st
import requests
import pandas as pd
import yaml
import os

# FastAPI backend URL
API_URL = "http://127.0.0.1:8000/run_sparql/"

st.set_page_config(page_title="LamaH-CE SPARQL Query Interface", page_icon="🌍", layout="wide")

# Load questions from YAML
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_PATH = os.path.join(BASE_DIR, "questions.yaml")

def load_questions():
    with open(QUESTIONS_PATH, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)

questions = load_questions()

# ---- Load Images ----
lamaH_logo = "LamaH_CE_logo.png"
nfdi4earth_logo = "NFDI4Earth_logo.png"
hydro_turtle_logo = "Hydro_turtle_logo.png"

# ---- UI Header with Title ----
st.markdown("<h1 style='text-align: center;'>LamaH-CE SPARQL Query Interface</h1>", unsafe_allow_html=True)

# ---- Logo Row (All in One Line Below the Title) ----
col1, col2, col3 = st.columns([1, 2, 1])  # Adjust the middle column to be wider

with col1:
    st.image(lamaH_logo, width=150, use_column_width=False)

with col2:
    st.image(hydro_turtle_logo, width=200, use_column_width=False)  # Center logo

with col3:
    st.image(nfdi4earth_logo, width=150, use_column_width=False)  # Adjusted size

st.markdown("---")  # Separator

# ---- Sidebar for Question Selection ----
st.sidebar.header("📂 Select a Question Category")

# Icons for categories (Customize as needed)
CATEGORY_ICONS = {
    "Category 1": "🌍",
    "Category 2": "📊",
    "Category 3": "📌",
}

selected_category = st.sidebar.selectbox("🗂️ Choose a Category:", list(questions.keys()))

if selected_category:
    selected_subcategory = st.sidebar.selectbox("📁 Choose a Subcategory:", list(questions[selected_category].keys()), key=f"{selected_category}_sub")

    if selected_subcategory:
        selected_question = st.sidebar.selectbox(
            "❓ Choose a Question:", 
            list(questions[selected_category][selected_subcategory].keys()), 
            key=f"{selected_subcategory}_question"
        )

        sparql_query = questions[selected_category][selected_subcategory][selected_question]

# ---- Main Content: Query & Results ----
col1, col2 = st.columns([2, 3])  # Adjust column width (query area larger)

with col1:
    st.subheader("📝 SPARQL Query")
    query_text = st.text_area("Modify or review the query:", sparql_query, height=300)

with col2:
    st.subheader("📊 Query Results")

    # Function to format results as DataFrame
    def format_results(data):
        """Converts SPARQL JSON results to a Pandas DataFrame"""
        if "results" in data and "bindings" in data["results"]:
            rows = []
            columns = set()
            
            for item in data["results"]["bindings"]:
                row = {}
                for key, value in item.items():
                    row[key] = value["value"]  # Extract actual value
                    columns.add(key)
                rows.append(row)

            return pd.DataFrame(rows, columns=sorted(columns)) if rows else None
        return None

    # Run Query Button
    if st.button("🚀 Run Query"):
        if query_text.strip():
            with st.spinner("⏳ Running SPARQL query..."):
                response = requests.post(API_URL, json={"query": query_text})
                data = response.json()

            if "error" in data:
                st.error(f"❌ Error: {data['error']}")
            else:
                df = format_results(data)
                if df is not None:
                    st.success("✅ Query executed successfully!")
                    st.dataframe(df)  # Display results in table format
                else:
                    st.warning("⚠️ No results found.")
        else:
            st.warning("⚠️ Please enter a SPARQL query.")