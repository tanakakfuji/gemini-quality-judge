import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai import errors
from tqdm import tqdm

load_dotenv(override=True)

def execute_requests(prompts):
  keys = os.getenv('GEMINI_API_KEYS')
  key_list = keys.split(',')
  results = []
  error_count = 0
  for i, prompt in enumerate(tqdm(prompts, desc='execute requests')):
    key=key_list[i % len(key_list)]
    result = _send_request(key, prompt)
    results.append(result)
    # 連続したAPIエラーへの対処
    if result['status'] == 'success':
      error_count = 0
    else:
      error_count += 1
    if error_count == 5:
      raise RuntimeError('API呼び出しが5回連続して失敗したため、処理を停止します')
    if not (i == len(prompts) - 1):
      time.sleep(float(os.getenv('REQUEST_INTERVAL_TIME')))

  return results

def _send_request(key, prompt):
  if not isinstance(key, str) or not key.strip():
    raise ValueError('APIキーが不正です')
  if not prompt:
    raise ValueError('プロンプトが空文字です')
  try:
    client = genai.Client(api_key=key)
    response = client.models.generate_content(
      model=os.getenv('GEMINI_MODEL_NAME'),
      config=types.GenerateContentConfig(
          system_instruction="以下は、タスクを説明する指示です。要求を適切に満たす応答を書きなさい。",
          max_output_tokens=16384,
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
