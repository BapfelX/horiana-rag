from langchain_aws import ChatBedrock
from langchain_core.prompts import ChatPromptTemplate

from src.healthdraft.rag.prompt_setup import (
    create_final_prompt,
)

def create_llama_instance(model_id="meta.llama3-8b-instruct-v1:0"):
    llm = ChatBedrock(
        model_id=model_id,
        model_kwargs=dict(temperature=0),
        region_name="us-east-1"
    )
    return llm

def create_final_prompt(system, user):
    user_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("user", user),
        ]
    )
    print(user_prompt)
    return user_prompt

if __name__ == "__main__":
    llm = create_llama_instance()
    print(llm)

    system="You are a medical assistant."
    user="What is asthma?"

    p = create_final_prompt(system, user)
    chain = p | llm

    print(chain.invoke())