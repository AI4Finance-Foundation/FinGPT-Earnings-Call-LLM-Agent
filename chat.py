from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI

def get_openai_answer(question,context):
    prompt_template = """Use the following pieces of context which has the speaker name followed what he speaked separated by semi-colon, to answer the question at the end.\n
        Answer the question by citing the speaker name and what he/she said.\n

        {context}

        Question: {question}
        """
    # PROMPT = PromptTemplate(
    #     template=prompt_template, input_variables=["context", "question"]
    # )
    PROMPT = PromptTemplate.from_template(
        prompt_template
    )
    # PROMPT = PROMPT.format(context=context,question=question)

    # # PROMPT.format(context=context, question=question)
    # print()
    chat = ChatOpenAI(temperature=0.1)
    # res = chat(PROMPT)
    # return res
    chat(
        PROMPT.format_prompt(
            context=context, question=question, text="I love programming."
        ).to_messages()
    )
