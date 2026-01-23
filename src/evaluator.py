from src.gemini import execute_requests
from collections import defaultdict
import re

METRICS = ['正確性', '流暢性', '詳細性', '関連性', '総合評価']
SCORE_REGEX = rf'({'|'.join(METRICS)}):\s?\[\[([1-5])\]\]'

def evaluate(prompt_template, data):
  prompts = _build_prompts(prompt_template, data)
  results = execute_requests(prompts)
  error_count = 0
  scores = defaultdict(list)
  for i in range(len(results)):
    if results[i]['status'] == 'success':
      score, results[i]['status'] = _extract_score(results[i]['text'])
    else:
      score = {m: 0 for m in METRICS}
    results[i] = score | results[i]
    if results[i]['status'] != 'success':
      error_count += 1
    for metric, point in score.items():
      scores[metric].append(point)
  avg_scores = {
    m: round(sum(points) / (len(points) - error_count), 2)
    if len(points) - error_count else None
    for m, points in scores.items()
  }
  return results, avg_scores, error_count
  
def _build_prompts(prompt_template, data):
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
