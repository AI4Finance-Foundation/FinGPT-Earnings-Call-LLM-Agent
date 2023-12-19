from utils import get_earnings_transcript
import re
from langchain.schema import Document
from config import *
from langchain.text_splitter import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from sentence_transformers import SentenceTransformer
import numpy as np
import json
import pandas as pd
from tqdm.notebook import tqdm
import torch
from qdrant_client import models, QdrantClient
from qdrant_client.models import VectorParams, Distance, Field, FieldCondition, MatchAny, Filter, Match

def clean_speakers(speaker):
    speaker = re.sub("\n","",speaker)
    speaker = re.sub(":","",speaker)
    return speaker

def create_database(quarter:str,ticker:str, year:int):
    """Build the database to query from it

    Args:
        quarter (str): The quarter of the earnings call
        ticker (str): The ticker of the company
        year (int): The year of the earnings call
    """
    resp_dict = get_earnings_transcript(
            quarter, ticker, year
        )
    
    content = resp_dict['content']
    pattern = re.compile(r"\n(.*?):")
    matches = pattern.finditer(content)

    speakers_list = []
    ranges = []
    for match_ in matches:
        # print(match.span())
        span_range = match_.span()
        # first_idx = span_range[0]
        # last_idx = span_range[1]
        ranges.append(span_range)
        speakers_list.append(match_.group())
    speakers_list = [clean_speakers(sl) for sl in speakers_list]

    docs = []

    for idx,speaker in enumerate(speakers_list[:-1]):
        start_range = ranges[idx][1]
        end_range = ranges[idx+1][0]
        speaker_text =  content[start_range+1:end_range]

        docs.append(
            Document(page_content=speaker_text,metadata={"speaker":speaker})
        )
        
    docs.append(
            Document(page_content=content[ranges[-1][1]:],metadata={"speaker":speakers_list[-1]})
        )
    
    text_splitter = RecursiveCharacterTextSplitter(
    # Set a really small chunk size, just to show.
        chunk_size = CHUNK_SIZE,
        chunk_overlap  = CHUNK_OVERLAP,
        length_function = len,
        # is_separator_regex = False,
    )
    split_docs = text_splitter.split_documents(docs)
    split_docs_qdrant = [{"speaker_text":doc.page_content,"speaker":doc.metadata['speaker']} for doc in split_docs]

    qdrant_client = QdrantClient("http://localhost:6333")

    device = "cuda" if torch.cuda.is_available() else "cpu"

    encoder = SentenceTransformer(
        ENCODER_NAME, device=device
    )  # or device="cpu" if you don't have a GPU

    qdrant_client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=encoder.get_sentence_embedding_dimension(), distance=Distance.COSINE),
    )

    qdrant_client.upload_records(
        collection_name=COLLECTION_NAME,
        records=[
            models.Record(
                id=idx, vector=encoder.encode(doc["speaker_text"]).tolist(), payload=doc
            )
            for idx, doc in enumerate(split_docs_qdrant)
        ],
    )

    return qdrant_client,encoder,speakers_list

def query_database(question:str,qdrant_client,encoder,speakers_list):
    req_speaker_list = []
    for sl in speakers_list:
        if sl in question:
            req_speaker_list.append(sl)
    
    if len(req_speaker_list)==0: req_speaker_list = speakers_list

    hits = qdrant_client.search(
    collection_name=COLLECTION_NAME,
    query_vector=encoder.encode(question).tolist(),
    limit=RETURN_LIMIT,
    query_filter=models.Filter(
        must=[
            models.FieldCondition(
                key="speaker",
                match=models.MatchAny(
                    any=req_speaker_list,
                ),
            )
        ]
    ),
    search_params=models.SearchParams(hnsw_ef=256,exact=True)
    )

    relevant_docs = []
    for hit in hits:
        relevant_docs.append(hit.payload)
    
    relevant_docs_speaker_list = []
    for rd in relevant_docs:
        curr_speaker = rd['speaker']
        if curr_speaker not in relevant_docs_speaker_list:
            relevant_docs_speaker_list.append(rd['speaker'])
    
    relevant_speaker_dict = {k:"" for k in relevant_docs_speaker_list}
    for rd in relevant_docs:
        relevant_speaker_dict[rd['speaker']]+=rd['speaker_text']

    relevant_speaker_text = ""
    for speaker,text in relevant_speaker_dict.items():
        relevant_speaker_text+=speaker+": "
        relevant_speaker_text+=text + "\n\n"
        
    return relevant_speaker_text