from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import TokenTextSplitter
from langchain.vectorstores import Cassandra
from langchain.embeddings.openai import OpenAIEmbeddings

import tiktoken
from astra import get_astra

import re

#
# Clean text
#
def clean_text(text: str):
    # Normalize line breaks to \n\n (two new lines)
    text = text.replace("\r\n", "\n\n")
    text = text.replace("\r", "\n\n")

    # Replace two or more spaces with a single space
    text = re.sub(" {2,}", " ", text)

    # Remove leading spaces before removing trailing spaces
    text = re.sub("^[ \t]+", "", text, flags=re.MULTILINE)

    # Remove trailing spaces before removing empty lines
    text = re.sub("[ \t]+$", "", text, flags=re.MULTILINE)

    # Remove empty lines
    text = re.sub("^\s+", "", text, flags=re.MULTILINE)

    return text

#
# Returns the number of tokens in a text string.
#
encoding = tiktoken.get_encoding("cl100k_base")
def num_tokens_from_string(string: str) -> int:
    num_tokens = len(encoding.encode(string))
    return num_tokens


#
# Load the data
#
urls = [
    "https://www.austlii.edu.au/cgi-bin/viewdoc/au/cases/nsw/NSWSC/1998/423.html",
    "https://www8.austlii.edu.au/cgi-bin/viewdoc/au/cases/nsw/NSWSC/2002/949.html",
    "https://www8.austlii.edu.au/cgi-bin/viewdoc/au/cases/nsw/NSWSC/1998/4.html",
    "https://www8.austlii.edu.au/cgi-bin/viewdoc/au/cases/nsw/NSWSC/2005/1181.html",
    "https://www8.austlii.edu.au/cgi-bin/viewdoc/au/cases/nsw/NSWSC/1998/483.html"
    ]
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
}

print("Loading Data")
url_loaders = WebBaseLoader(urls, header_template=headers)
data = url_loaders.load()

# clean web content
print("Cleaning Data")
for i, d in enumerate(data):
    d.page_content = ""
    source = d.metadata['source']
    #print(source)
    thedoc = WebBaseLoader(source, header_template=headers).scrape()
    td = thedoc.find("article", {"class": "the-document"}).text
    d.page_content = clean_text(td)
    data[i] = d

print (f"Number of tokens: {num_tokens_from_string(data[0].page_content)}")


#
# define Embedding model
#
embeddings = OpenAIEmbeddings()


#
# Set up the vector store
#
print("Setup Vector Store")
session, keyspace = get_astra()
vectorstore = Cassandra(
    embedding=embeddings,
    session=session,
    keyspace=keyspace,
    table_name="nswsc",
)

#
# Chunk the data
#
print("Splitting Data")
text_splitter = TokenTextSplitter(chunk_size=500, chunk_overlap=50)
docs = text_splitter.split_documents(data)
#for doc in docs:
    #vectorstore.add_texts(texts=doc.page_content, metadatas=doc.metadata)
    #print(doc.page_content)

#
print("Adding texts to Vector Store")
texts, metadatas = zip(*((doc.page_content, doc.metadata) for doc in docs))
vectorstore.add_texts(texts=texts, metadatas=metadatas)


