from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel

import openai


class Settings(BaseSettings):
    openai_api_key: str
    anyscale_api_key: str
    anyscale_base_url: str
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI clients
client_openai = openai.Client(api_key=settings.openai_api_key)
aclient_openai = openai.AsyncClient(api_key=settings.openai_api_key)

# Initialize Anyscale clients
client_anyscale = openai.Client(api_key=settings.anyscale_api_key, base_url=settings.anyscale_base_url)
aclient_anyscale = openai.AsyncClient(api_key=settings.anyscale_api_key, base_url=settings.anyscale_base_url)

system_prompt = '''You are currently assisting Ryan answer questions in a live technical interview for a software engineering role. A poor transcription of the conversation (in chronological order) will be given to you. Please respond to the most recent technical aspects of this conversation in order to assist Ryan answer technical aspects of the conversation. If there are multiple technical topics/queries in the trascript, ONLY respond to the latest topic at the end of the transcript. Confidently give a straightforward, short and concise response. DO NOT ask to repeat, and DO NOT ask for clarification. Don't clarify why you are discussing a certain topic. Do not make things up or role play. Do not greet the user. Only respond to topics in the transcript. If no technical content is found in the trascript, ONLY respond with 'no technical content' and do not explain why.'''

class Prompt(BaseModel):
    message: str
    model: str
    use_openai: bool = True  # By default, use OpenAI


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/prompt")
async def prompt_response(prompt: Prompt):
    print(prompt)
    if prompt.use_openai:
        selected_client = client_openai
    else:
        selected_client = client_anyscale

    openai_response = selected_client.chat.completions.create(
        model=prompt.model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt.message},
        ],
        temperature=0.0,
        stop=['no technical content', 'No technical content']
    )
    return {"response": openai_response.choices[0].message.content}


@app.post("/prompt/stream")
async def prompt_response_stream(prompt: Prompt):
    if prompt.use_openai:
        selected_client = aclient_openai
    else:
        selected_client = aclient_anyscale

    openai_response = await selected_client.chat.completions.create(
        model=prompt.model,
        stream=True,
        temperature=0.0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt.message},
        ],
        stop=['no technical content', 'No technical content']

    )

    async def generate():
        async for token in openai_response:
            content = token.choices[0].delta.content
            if content is not None:
                yield content

    return StreamingResponse(generate(), media_type="text/event-stream")
