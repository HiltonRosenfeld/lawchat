from contextlib import asynccontextmanager
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from typing_extensions import Annotated
import logging
from cassandra.query import SimpleStatement
from cassandra.cqlengine import connection

from langchain.chains import FlareChain
from langchain.vectorstores import Cassandra
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.embeddings.openai import OpenAIEmbeddings

from astra import get_astra, initSession



# globally-accessible objects:
DBSession = connection


# Define startup & shutdown logic using lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    logging.basicConfig(level=logging.INFO)
    logging.info('     API Startup begins')

    # Database
    #logging.info('     DB initialization')
    #DBSession = initSession()
    
    # define Embedding model
    embeddings = OpenAIEmbeddings()
    
    # set up the vector store and make a retriever out of it
    session, keyspace = get_astra()
    vectorstore = Cassandra(
        embedding=embeddings,
        session=session,
        keyspace=keyspace,
        table_name="nswsc",
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    #retriever = vectorstore.as_retriever()

    # define Flare chain
    global flare
    flare = FlareChain.from_llm(
        ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k"),
        retriever=retriever,
        max_generation_len=164,
        min_prob=0.3,
    )


    # Used OpenAI LLM for comparison
    llm = OpenAI()
    
    logging.info('     API Startup completed.')

    yield
    
    # SHUTDOWN
    ##



# Initialise FastAPI instance
app = FastAPI(lifespan=lifespan)



# HTML GET METHOD
#   GET form
@app.get("/", response_class=HTMLResponse)
async def root():
    m  = showHead()
    m += showForm('','v')
    m += showFoot()
    return HTMLResponse(content=m, status_code=200)




# HTML FORM POST METHOD
#   Recommendation from search
@app.post("/lawchat", response_class=HTMLResponse)
async def login(text: Annotated[str, Form()], opts: Annotated[str, Form()]):
    # return results
    m  = showHead()
    m += showForm(text,opts)

    # run Flare chain
    flare_result = flare.run(text)
    
    m += "<h2>Vector Search Results</h2>"
    m += '<p>'.join(flare_result.splitlines())

    m += showFoot()

    return HTMLResponse(content=m, status_code=200)







def showHead():
    m = "<html>"
    m += """
        <style>
            body {
                font-family: sans-serif;
                margin: 0px;
            }
            td {vertical-align:top;}
            .navbar {
                background-color: black;
                color: white;
                padding: 20px;
            }
            .prompt {
                padding: 20px;
                background-color: lightgrey;
            }
            .userinput {
                padding-top: 1px;
                padding-bottom: 10px;
                padding-left: 20px;
                padding-right: 20px;
                background-color: #7f3aa4;
                color: white;
            }
            .response {
                margin: 20px;
            }
            input {
                font-size: 12pt;
            }
        </style>
    """
    m += """
        <body>
        <div class="navbar">
        <svg width="11.41em" height="1.06em" viewBox="0 0 183 17" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M109.189 2.94031V0H95.0865L91.2567 2.94031V6.97789L95.0865 9.9182H107.377V14.0627H92.0184V17H106.502L110.332 14.0627V9.9182L106.502 6.97789H94.2112V2.94031H109.189Z" fill="currentColor"></path><path d="M35.3706 0H32.6803L22.8126 17H26.2247L34.0316 3.55466L41.8293 17H45.2383L35.3706 0Z" fill="currentColor"></path><path d="M64.7034 0H45.6284V2.94031H53.6902V17H56.6416V2.94031H64.7034V0Z" fill="currentColor"></path><path d="M134.146 0H115.074V2.94031H123.132V17H126.087V2.94031H134.146V0Z" fill="currentColor"></path><path d="M15.2453 0H0V17H15.2453L19.075 14.0597V2.94031L15.2453 0ZM2.95447 2.94031H16.1206V14.0627H2.95447V2.94031Z" fill="currentColor"></path><path d="M169.034 8.5L167.327 5.55969V5.56275L164.099 0H160.687L165.622 8.5L160.687 17H164.099L167.327 11.4403L169.034 8.5Z" fill="currentColor"></path><path d="M173.887 8.5L175.594 5.55969V5.56275L178.825 0H182.234L177.302 8.5L182.234 17H178.825L175.594 11.4403L173.887 8.5Z" fill="currentColor"></path><path d="M74.9611 0H77.6515L87.5191 17H84.1071L76.3001 3.55466L68.5024 17H65.0934L74.9611 0Z" fill="currentColor"></path><path d="M144.403 0H147.094L156.961 17H153.552L145.742 3.55466L137.948 17H134.536L144.403 0Z" fill="currentColor"></path></svg>
        </div>
    """

    return m


def showForm(text,opts):
    v  = "checked" if opts=="v" else ""
    l  = "checked" if opts=="l" else ""
    vl = "checked" if opts=="vl" else ""
    m = f"""
        <div class="userinput">
        <h1>Query our catalogue using natural language</h1>
        <form method="POST" action="/lawchat">
            <input type="text" name="text" value="{text}" size="100">
            <input type="hidden" name="opts" value="v">
            <p>
            <input type="submit" value="Submit">
        </form>
        </div>
        <div class="response">
    """
    return m
"""
            <p>
            <input type="radio" name="opts" value="v" {v}> Vector Only &nbsp;
            <input type="radio" name="opts" value="l" {l}> LLM Only &nbsp;
            <input type="radio" name="opts" value="vl" {vl}> Vector and LLM
"""


def showFoot():
    m = "</div></body></html>"
    return m

