import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai import errors

load_dotenv(override=True)

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