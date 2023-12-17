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

# with tab2:
    def generate_response(input_text):
        relevant_text = query_database(input_text,qdrant_client,encoder,speakers_list)

        res = get_openai_answer(input_text,relevant_text)
        return res, relevant_text
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content": "Hi, how can I help you?"}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if prompt := st.chat_input():
        # Display user message in chat message container
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Answering..."):
                docs,relevant_text = generate_response(prompt) 
                expander = st.expander("See relevant IMDB movie review links")
                
                expander.write(relevant_text)
        message = {"role": "assistant", "content": docs['result']}
        st.session_state.messages.append(message)