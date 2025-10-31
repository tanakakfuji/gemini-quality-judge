import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai import errors

load_dotenv(override=True)

def execute_requests(prompts):
  keys = os.getenv('GEMINI_API_KEYS')
  if not keys:
    raise ValueError('GEMINI_API_KEYSが空文字です')
  key_list = keys.split(',')
  results = []
  for i, prompt in enumerate(prompts):
    client = genai.Client(api_key=key_list[i % len(key_list)])
    result = _send_request(client, prompt)
    results.append(result)
    time.sleep(float(os.getenv('REQUEST_INTERVAL_TIME')))

  return results

def _send_request(client, prompt):
  try:
    response = client.models.generate_content(
      model=os.getenv('GEMINI_MODEL_NAME'),
      config=types.GenerateContentConfig(
          system_instruction="以下は、タスクを説明する指示です。要求を適切に満たす応答を書きなさい。",
          max_output_tokens=1024,
          seed=1234,
          top_p=0.95,
          temperature=1.0,
          frequency_penalty=0.0,
      ),
      contents=prompt
    )
  except errors.APIError as e:
    result = {
      'text': '',
      'status': e.status
    }
  else:
    result = {
      'text': response.text,
      'status': 'success'
    }

  return result
