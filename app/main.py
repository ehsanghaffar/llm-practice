import pathlib
from typing import Optional
from fastapi.responses import JSONResponse, UJSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from langchain.prompts import PromptTemplate
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.llms.llamacpp import LlamaCpp
import uvicorn

from . import (
    config,
    schema,
    utils,
)


# FASTAPI
app = FastAPI(
    title="Personal LLM",
    docs_url="/api/docs",
    redoc_url="/api/redocs",
    openapi_url="/openapi.json",
    default_response_class=UJSONResponse,
    debug=True
)
settings = config.get_settings()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        return JSONResponse(content={"code": 500, "error": {"message": f"{type(exc)} {exc}"}})


app.middleware('http')(catch_exceptions_middleware)

# BASE_DIR = pathlib.Path(__file__).resolve().parent

template = """Question: {question}

Answer: Be sure to give the most correct answer to the question."""

prompt = PromptTemplate(template=template, input_variables=["question"])

# Callbacks support token-wise streaming
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])


# Make sure the model path is correct for your system!
llm = LlamaCpp(
    model_path="static/gpt4all-falcon-q4_0.gguf",
    temperature=0.75,
    max_tokens=2000,
    top_p=1,
    callback_manager=callback_manager,
    verbose=True,  # Verbose is required to pass to the callback manager
    streaming=False,
) # type: ignore

def chat_with_llama2(question: str):
    try:
        prompt = f"Question: {question}"
        result = llm(prompt)
        return result
    except Exception as err:
        print(err)
        return err


@app.get("/")
def read_index(q:Optional[str] = None):
    return {"hello": "world"}

@app.post("/chat")
async def chatting(request: schema.ChatRequest):
    try:
        response = chat_with_llama2(question=request.question)
        return response
    except Exception as error:
        print(error)
        return error


# config = uvicorn.Config(
#         app=app,
#         port=8000,
#         host="localhost",
#         log_level="info",
#         # ssl_keyfile=ssl_keyfile,
#         # ssl_certfile=ssl_certfile,
#         # ssl_keyfile_password=ssl_keyfile_password,
#         ws_max_size=1024 * 1024 * 1024,  # Setting max websocket size to be 1 GB
# )

# server = utils.Server(config=config)
# server.run_in_thread()