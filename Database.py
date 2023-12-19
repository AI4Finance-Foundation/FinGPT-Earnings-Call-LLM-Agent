from build_database import create_database,query_database
import streamlit as st
from dotenv import load_dotenv
import openai
import os
from chat import get_openai_answer

load_dotenv()

openai.api_key = os.environ['OPENAI_API_KEY']
# tab1, tab2 = st.tabs(["Database","Chat"])

# with tab1:
ticker = st.text_input(label="Ticker")
quarter = st.selectbox(label="Quarter",options=["Q4","Q3","Q2","Q1"])
year = st.text_input(label="Year")

if year!="":
    int_year = float(year)

if ticker!="" and quarter!="" and year!="":
    qdrant_client,encoder,speakers_list = create_database(quarter=quarter,ticker=ticker,year=int_year)
    st.write("Created the database")
    
    st.session_state['qdrant_client'] = qdrant_client
    st.session_state['encoder'] = encoder
    st.session_state['speakers_list'] = speakers_list