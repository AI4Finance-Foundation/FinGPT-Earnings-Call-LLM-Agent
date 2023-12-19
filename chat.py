from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.llms import openai

def get_openai_answer(question,context):
    earnings_call_prompt_template = """Use the following pieces of context which has the speaker name followed what he speaked separated by semi-colon, to answer the question at the end.\n
        Answer the question by citing the speaker name and what he/she said. Be very diligent in using all the information and answering extensively. Also, don't miss out any numerical figures if there are any.\n

        {context}

        Question: {question}
        """
    
    prompt_template = PromptTemplate(
        input_variables=["context","question"],template=earnings_call_prompt_template
    )

    llm_prompt = prompt_template.format(
        question=question,context=context
    )

    earnings_call_llm = ChatOpenAI(temperature=0.0,model="gpt-3.5-turbo-16k",streaming=False)

    output = earnings_call_llm.predict(llm_prompt)
    return output