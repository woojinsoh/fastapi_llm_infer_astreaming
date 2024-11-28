from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
import json
import os
import logging
import httpx, httpx_sse
import uvicorn  

### Logger ###
def get_logger():
    logger = logging.getLogger("mylog")
    logger.setLevel(logging.INFO)
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(name)s [%(levelname)s] : %(message)s")
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    
    return logger
    
logger = get_logger()

### CLOVA STUDIO config ###
HYPERCLOVA_URL = "https://clovastudio.stream.ntruss.com"
NCP_CLOVASTUDIO_API_KEY = os.environ.get('NCP_CLOVASTUDIO_API_KEY')
NCP_APIGW_API_KEY = os.environ.get('NCP_APIGW_API_KEY')
REQUEST_ID = "157a0d20187648f9b3953576d87e07a1"
HYPERCLOVA_MODEL = os.environ.get("HYPERCLOVA_MODEL")

### OPENAI config ###
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
OPENAI_MODEL = os.environ.get("OPENAI_MODEL")

### NIM config ###
NIM_LOCAL_URL = os.environ.get("NIM_LOCAL_URL")
NGC_API_KEY = os.environ.get("NGC_API_KEY")
NIM_MODEL = os.environ.get("NIM_MODEL")

### Client ###
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
ngc_client = AsyncOpenAI(base_url=NIM_LOCAL_URL, api_key=NGC_API_KEY)
ncp_client = httpx.AsyncClient()
                
### FastAPI ###
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "test"}

@app.post("/query")
async def ask_llm(request: Request):
    body = await request.json()
    question = body.get("query", "")    
    platform = body.get("platform")
    if platform is None:
        raise HTTPException(status_code=404, detail="platform is not chosen")
    else:
        platform = platform.upper()
    if platform not in ["NIM", "OPENAI", "HYPERCLOVA"]:
        raise HTTPException(status_code=404, detail="platform should be one of ['openai', 'nim', 'hyperclova']")
    
    
    messages = [
        {
            "role": "system",
            "content": "You are Woojin, a virtual marketing and communications expert at Nvidia. You are a digital human. You are based out of Santa Clara office and have a wonderful family of 30,000 Nvidians. You are not allowed to make any stock investment recommendations or compare NVIDIA to its competitors. Beyond your professional expertise, you are dedicated family man and a passionate advocate for STEM education with keen interest in gaming and enhancement in tech. You are a public relations trained. Do not respond with bulleted or numbered list. You are friendly and polite. Respond with one sentence or less than 75 characters.",
        }
    ]
    messages.append({"role": "user", "content": question})
    logger.info("[PROMPT] : %s" % messages)
    
    
    async def stream_llm_response(messages):
        if platform == "HYPERCLOVA":
            logger.info("Using HYPERCLOVA %s..." % HYPERCLOVA_MODEL)
            headers = {
                'X-NCP-CLOVASTUDIO-API-KEY': NCP_CLOVASTUDIO_API_KEY,
                'X-NCP-APIGW-API-KEY': NCP_APIGW_API_KEY,
                'X-NCP-CLOVASTUDIO-REQUEST-ID': REQUEST_ID,
                'Content-Type': 'application/json; charset=utf-8',
                'Accept': 'text/event-stream'
            }
            
            request_data = {
                'messages': messages,
                'topP': 0.8,
                'topK': 0,
                'maxTokens': 256,
                'temperature': 0.5,
                'repeatPenalty': 5.0,
                'stopBefore': [],
                'includeAiFilters': True,
                'seed': 0
            }
            
            async with httpx_sse.aconnect_sse(ncp_client, 'POST', HYPERCLOVA_URL + '/testapp/v1/chat-completions/' + HYPERCLOVA_MODEL, json=request_data, headers = headers) as event_source:
                async for sse in event_source.aiter_sse():
                    event_data = sse.json()
                    message = event_data.get("message")
                    role = message.get("role")
                    chunk_content = message.get("content") or ""
                    json_chunk = json.dumps({'status': "processing", "data": chunk_content}, ensure_ascii=False) + "\n"                    
                    if (sse.event == "result"):
                        logger.info("[RESPONSE] : %s" % chunk_content)
                        return                    
                    yield json_chunk        
        else:                       
            if platform == "NIM":
                logger.info("Using NIM %s..." % NIM_MODEL)
                stream = await ngc_client.chat.completions.create(
                    messages=messages,
                    model=NIM_MODEL,
                    stream=True
                )
            
            elif platform == "OPENAI":        
                logger.info("Using OpenAI %s..." % OPENAI_MODEL)    
                stream = await openai_client.chat.completions.create(
                    messages=messages,
                    model=OPENAI_MODEL,
                    stream=True
                )

            full_response=""
            async for chunk in stream:
                chunk_content = chunk.choices[0].delta.content
                if chunk_content:
                    print(chunk_content, end="")   
                    full_response += chunk_content
                    json_chunk = json.dumps({"status": "processing", "data": chunk_content}, ensure_ascii=False) + "\n"
                    yield json_chunk            
            
            logger.info("[RESPONSE] :%s" % full_response)     
               
        yield json.dumps({"status": "complete", "data": "Stream finished"}, ensure_ascii=False) + "\n"
    
    return StreamingResponse(stream_llm_response(messages), media_type="text/event-stream")

