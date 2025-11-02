from src.utils import load_text
from src.gemini import execute_requests
from collections import defaultdict
import re

METRICS = ['正確性', '流暢性', '詳細性', '関連性', '総合評価']
SCORE_REGEX = rf'({'|'.join(METRICS)}):\s?\[\[([1-5])\]\]'

def evaluate(strict_ac, data):
  prompts = _build_prompts(strict_ac, data)
  results = execute_requests(prompts)
  error_count = 0
  scores = defaultdict(list)
  for result in results:
    if result['status'] == 'success':
      score, result['status'] = _extract_score(result['text'])
    else:
      score = {m: 0 for m in METRICS}
    if result['status'] != 'success':
      error_count += 1
    for metric, point in score.items():
      scores[metric].append(point)
  avg_scores = {
    m: sum(points) / (len(points) - error_count)
    if len(points) - error_count else None
    for m, points in scores.items()
  }
  return results, avg_scores, error_count
  
def _build_prompts(strict_ac, data):
  if strict_ac:
    prompt_template = load_text('data/prompts/strict_accuracy.txt')
  else:
    prompt_template = load_text('data/prompts/lenient_accuracy.txt')
  prompts = [prompt_template.format(question=d['query'], response=d['response'], reference=d['reference']) for d in data]
  return prompts

def _extract_score(text):
  score = {}
  error_flag = False
  for metric, point in re.findall(SCORE_REGEX, text):
    if metric in score:
      error_flag = True
    score[metric] = int(point)
  if not error_flag and set(score.keys()) == set(METRICS):
    status = 'success'
  else:
    score = {m: 0 for m in METRICS}
    status = 'EXTRACT_ERROR'
  return score, status

# data = [
#   {"id": 1, "query": "Pythonでリストの長さを取得する方法は？", "response": "アプリケーションをコンテナとして分離・実行するための仮想化技術です。", "reference": "len関数を使います"},
#   {"id": 2, "query": "HTMLでリンクを作成するタグは？", "response": "<link>タグを使用します。", "reference": "<a>タグを使用します。例：<a href='https://example.com'>リンク</a>"}
# ]

# print(_build_prompts(True, data))