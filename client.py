import httpx
import asyncio
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-q", "--query", default="who is the president of Korea?")
parser.add_argument("-p", "--platform", default="nim")
args = parser.parse_args()

QUERY = args.query
PLATFORM = args.platform

headers = { 
    'Content-Type': 'application/json; charset=utf-8',
    'Accept': 'application/json'
}

data = {
    "query": QUERY,
    "platform": PLATFORM
}

async def main():
    print("[PLATFORM]:", PLATFORM.upper())
    print("[QUERY]:", QUERY)
    async with httpx.AsyncClient() as client:
        response = await client.post("http://127.0.0.1:8000/query", headers=headers, json=data)
        print("[STATUS CODE]:", response.status_code)
        print("[STREAMING RESPONSES]")
        print(response.text)
            
        full_text = response.text        
        print("[FULL RESPONSE]")
        content = full_text.split('\n')
        
    full_response = ''.join([json.loads(i)['data'] for i in content[:-2]])
    print(full_response)

asyncio.run(main())
    
