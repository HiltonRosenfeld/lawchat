import sys

import langchain
from langchain.chains import FlareChain
from langchain.vectorstores import Cassandra
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.embeddings.openai import OpenAIEmbeddings


from astra import get_astra



langchain.verbose = True

#
# define Embedding model
#
embeddings = OpenAIEmbeddings()


#
# set up the vector store and make a retriever out of it
#
session, keyspace = get_astra()
vectorstore = Cassandra(
    embedding=embeddings,
    session=session,
    keyspace=keyspace,
    table_name="nswsc",
)
#retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
retriever = vectorstore.as_retriever()

#
# Used OpenAI LLM for comparison
#
llm = OpenAI()


#
# Define FLARE chain
#

flare = FlareChain.from_llm(
    ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k"),
    retriever=retriever,
    max_generation_len=164,
    min_prob=0.3,
)

if sys.argv[1:] == []:
    query = "What are the sentencing guidleines to follow"
else:
    query = " ".join(sys.argv[1:])

flare_result = flare.run(query)
#llm_result = llm(query)

print(f"QUERY: {query}\n\n")
print(f"FLARE RESULT:\n    {flare_result}\n\n")
#print(f"LLM RESULT:\n    {llm_result}\n\n")