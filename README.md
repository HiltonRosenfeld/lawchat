# LawChat

**Use natural language to query a library of previosuly cited legal cases**

We make use of LangChain for:

- managing the Vector Store: Cassandra
- managing the embeddings: OpenAIEmbeddings
- loading data from web pages
- FLARE chain


### Content

In this Github repo, there is
- a Jupyter notebook that you can use to run the end to end process.
- a FastAPI app that includes a GUI for better demoing.


### Problems
As mentioned, the FLARE chain is flawed. Even though I have defined a 16K model, the chain throws errors if I provide more than 4096 tokens. The only way I have found to control that is to limit the number of results returns from the Retriever (using kwargs) or by reducing the chunk size to approx 200 tokens. Both of these compromise the quality of the outcome.


### References:

https://betterprogramming.pub/harnessing-retrieval-augmented-generation-with-langchain-2eae65926e82

https://github.com/hemidactylus/langchain-flare-pdf-qa-demo/blob/main/README.md
