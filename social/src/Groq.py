import httpx
from social.db.settings import settings

api_key = settings.groq_api_key

async def call_groq(post: str, api_key: str = api_key):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "Summarize the input and answer questions. do not make it more than 200 words and answer in a savage way and add a little bot of roasting also write in a single line do not break it into new lines or add special characters or symbols and do not ask questions"},
                    {"role": "user", "content": post}
                ]
            },
            timeout=30.0
        )
        response_dictionary = response.json()
        return response_dictionary['choices'][0]['message']['content']