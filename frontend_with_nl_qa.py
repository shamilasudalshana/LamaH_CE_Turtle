import streamlit as st
import requests
import pandas as pd
import yaml
import os
from tutorial_without_promt import ask_natural_language_question  # Import NL Q&A function

# FastAPI backend URL
API_URL = "http://127.0.0.1:8000/run_sparql/"

st.set_page_config(page_title="LamaH-CE SPARQL Query Interface", page_icon="🌍", layout="wide")

# Load questions from YAML
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_PATH = os.path.join(BASE_DIR, "questions_validation.yaml")

def load_questions():
    with open(QUESTIONS_PATH, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)

questions = load_questions()

# ---- Load Images ----
lamaH_logo = "LamaH_CE_logo.png"
nfdi4earth_logo = "NFDI4Earth_logo.png"
hydro_turtle_logo = "Hydro_turtle_logo.png"

# ---- Header Layout: Title on the Left, Logos on the Right ----
header_col1, header_col2 = st.columns([2, 3])

with header_col1:
    st.markdown("<h2 style='text-align: left; margin-bottom: 5px;'>LamaH-CE SPARQL Query Interface</h2>", unsafe_allow_html=True)

with header_col2:
    logo_col1, logo_col2, logo_col3 = st.columns([1, 1, 1])
    with logo_col1:
        st.image(lamaH_logo, width=70)
    with logo_col2:
        st.image(hydro_turtle_logo, width=80)
    with logo_col3:
        st.image(nfdi4earth_logo, width=100)

st.markdown("---")  # Separator

# ---- Tabs for Different Functionalities ----
tab1, tab2 = st.tabs(["🔍 Direct SPARQL Queries", "🤖 Natural Language Q&A"])

# ---- Shared Sidebar for Question Selection ----
st.sidebar.header("📂 Select a Question Category")

selected_category = st.sidebar.selectbox("🗂️ Choose a Main Category:", list(questions.keys()))

if selected_category:
    selected_subcategory = st.sidebar.selectbox("📁 Choose a Subcategory:", list(questions[selected_category].keys()), key=f"{selected_category}_sub")

    if selected_subcategory:
        selected_question = st.sidebar.selectbox(
            "❓ Choose a Question:", 
            list(questions[selected_category][selected_subcategory].keys()), 
            key=f"{selected_subcategory}_question"
        )

        sparql_query = questions[selected_category][selected_subcategory][selected_question]

# ---- TAB 1: Direct SPARQL Query Execution ----
with tab1:
    query_col, result_col = st.columns([3, 2])  # Wider Query Box, Smaller Result Area

    with query_col:
        st.subheader("💡 Selected Question")
        st.markdown(f"**{selected_question}**")  # Preview of the selected question

        st.subheader("📝 SPARQL Query")
        query_text = st.text_area("Modify or review the query:", sparql_query, height=300)

    with result_col:
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
                        row[key] = value["value"]  
                        columns.add(key)
                    rows.append(row)

                return pd.DataFrame(rows, columns=sorted(columns)) if rows else None
            return None

        # Run Query Button
        if st.button("🚀 Run SPARQL Query"):
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
                        st.dataframe(df)  
                    else:
                        st.warning("⚠️ No results found.")
            else:
                st.warning("⚠️ Please enter a SPARQL query.")

# ---- TAB 2: Natural Language Q&A ----
with tab2:
    st.subheader("🤖 Ask a Question in Natural Language")

    # Display the selected NL question (same from the sidebar)
    st.markdown(f"**{selected_question}**")
    
    # Allow user to modify or enter a new NL question
    nl_question = st.text_area("🔍 Modify or Ask a New Question:", selected_question, height=100)

    if st.button("🤖 Generate SPARQL Query & Answer"):
        if nl_question.strip():
            with st.spinner("⏳ Processing..."):
                named_graph = "http://hydroturtle/LamahCE"
                sparql_query_generated, generated_answer, verbalized_ans = ask_natural_language_question(nl_question, named_graph)

            st.success("✅ Answer Generated!")

            # Display the SPARQL Query & Answer Explanation
            st.text_area("📝 Generated SPARQL Query:", sparql_query_generated, height=450)  # Show SPARQL Query
            st.text_area("📝 Generated Answer form SPARQL Query:", generated_answer, height=75)  # Show SPARQL Query
            st.text_area("📖 Verbalized Answer:", verbalized_ans, height=200)  # Show Explanation
        else:
            st.warning("⚠️ Please enter a question.")

