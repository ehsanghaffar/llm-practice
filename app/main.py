import logging
from typing import Optional
from fastapi.responses import JSONResponse, UJSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from langchain.prompts import PromptTemplate
from langchain.callbacks.base import BaseCallbackManager
from langchain.llms.llamacpp import LlamaCpp
import asyncio
from concurrent.futures import ProcessPoolExecutor
from app.callback_manager import LoggingCallbackHandler

from app.logger import configure_logging


from . import (
    config,
    schema,
)

settings = config.get_settings()

def create_app() -> FastAPI:
    configure_logging()
    
    app = FastAPI(
        title="Ein LLM",
        docs_url="/api/docs",
        redoc_url="/api/redocs",
        openapi_url="/openapi.json",
        default_response_class=UJSONResponse,
        debug=True
    )
    return app

app = create_app()

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
# callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
callback_manager = BaseCallbackManager([LoggingCallbackHandler()])


sbertmodel = None

def create_model():
    
    return LlamaCpp(
        model_path="static/replit-code-v1_5-3b-q4_0.gguf", # Path to downloaded LLM
        temperature=0.75,
        # max_tokens=2000,
        top_p=1,
        callback_manager=callback_manager,
        verbose=True,  # Verbose is required to pass to the callback manager
        streaming=False,
    ) # type: ignore


pool = ProcessPoolExecutor(max_workers=1, initializer=create_model)

# async def simulateIO(vector):
#     # simulate I/O call (e.g. Vector Similarity Search using a VectorDB)
#     await asyncio.sleep(0.005)

def model_predict(question: str):
    prompt = f"Question: {question}"
    llm = create_model()
    result = llm(prompt)
    logging.log(10, f"{result}")
    return result


@app.get("/")
def read_index(q:Optional[str] = None):
    return {"hello": "world"}

@app.post("/chat")
async def chatting(request: schema.ChatRequest):
    try:
        loop = asyncio.get_event_loop()
        answer = await loop.run_in_executor(pool, model_predict(question=request.question))
        return {
            "answer": f"{answer}",
            "status": status.HTTP_200_OK
        }
    except Exception as error:
        logging.log(40, f"{error}")
        return {
            "error": f"{error}",
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR
        }


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