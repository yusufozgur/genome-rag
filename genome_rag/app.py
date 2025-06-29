import streamlit as st

import os
from dotenv import load_dotenv  # Add this import
load_dotenv()  # Load environment variables from .env
api_key = os.getenv("GOOGLE_API_KEY")

from genome_rag.snpedia.VectorDB import VectorDB
from genome_rag.llm.LLM import LLM
from genome_rag.genotypes.GenotypesFile import GenotypesFile

with st.sidebar:
    gemini_api_key = st.text_input("gemini API Key", value=api_key, key="file_qa_api_key", type="password")

st.title("🧬 Communicate with your genome.")

# Replace st.file_uploader with st.text_input
# uploaded_file = st.file_uploader("Upload a vcf file.", type=("vcf", ".vcf.gz"))
file_path = st.text_input("Enter the path to your vcf file.", value="data/sample.tsv")

sample_name = st.text_input("Enter sample name", value="NA00003.GT")


# Check if the provided file path exists
file_exists = os.path.exists(file_path)

if not file_exists and file_path:
    st.error(f"Error: File not found at path: {file_path}")


question = st.text_input(
    "Ask something about your genome",
    placeholder="Can you give me a short summary?",
    # Disable if file doesn't exist or path is empty
    disabled=not file_exists or not file_path,
)

# Update conditions to use file_exists instead of uploaded_file
if not gemini_api_key:
     st.info("Please add your gemini API key to continue.")

# Update conditions to use file_exists instead of uploaded_file
if file_exists and question and gemini_api_key:
    db = VectorDB()
    with st.spinner("Processing db...", show_time=True):
        gt = GenotypesFile(file_path)
        snps = gt.get_snp_ids()
        db.add_snps_to_db_if_not_added(snps)
        gts = gt.get_individual_genotypes(sample_name)
    llm = LLM(db, api_key, snps)
    with st.spinner("Processing...", show_time=True):
        response, context = llm.send_message(question)
        st.write(context)
        st.write(response)
    #st.write("### Answer")
#    st.write(response.completion)
    pass