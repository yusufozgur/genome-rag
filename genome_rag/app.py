import streamlit as st

import os
from dotenv import load_dotenv  # Add this import
load_dotenv()  # Load environment variables from .env
gemini_api_key = os.getenv("GOOGLE_API_KEY")

from genome_rag.snpedia.VectorDB import VectorDB
from genome_rag.llm.LLM import LLM
from genome_rag.genotypes.GenotypesFile import GenotypesFile

st.title("🧬 Communicate with your genome.")

with st.sidebar:
    if not gemini_api_key:
        gemini_api_key = st.text_input("gemini API Key", key="file_qa_api_key", type="password")
    file_path = st.text_input("Enter the path to your vcf file.", value="data/sample_big.tsv")

    sample_name = st.text_input("Enter sample name", value="NA00003.GT")

# Check if the provided file path exists
file_exists = os.path.exists(file_path)

if not file_exists and file_path:
    st.error(f"Error: File not found at path: {file_path}")
    st.stop()

# Add a number input for top_n results
choose_top_n_results = st.number_input(
    "Number of top results to consider",
    min_value=1,
    value=10,
    step=1,
    disabled=not file_exists or not file_path,
)

# Update conditions to use file_exists instead of uploaded_file
if not gemini_api_key:
     st.error("Please add your gemini API key to continue.")
     st.stop()

db = VectorDB()

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hi, I'm a chatbot who can search the web. How can I help you?"}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(placeholder="Ask something about your genome"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Processing db...", show_time=True):
            gt = GenotypesFile(file_path)
            snps = gt.get_snp_ids()
            gts = gt.get_individual_genotypes(sample_name)
        llm = LLM(db, gemini_api_key, snps, gts, choose_top_n_results)
        with st.spinner("Thinking...", show_time=True):
            response, context = llm.send_message(prompt)
            with st.expander("Context", expanded=False):
                st.write(context)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.write(response)



