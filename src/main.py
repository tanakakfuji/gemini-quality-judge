from src.utils import load_csv, save_csv, save_json
from src.evaluator import evaluate
import argparse
import json

def main():
  parser = argparse.ArgumentParser(description='GeminiによるQAタスクの品質評価を実施する自動評価ツール')
  parser.add_argument('--label', type=str, required=True, help='正解ラベルのCSVファイルを指定', metavar='sample_label.csv')
  parser.add_argument('--response', type=str, required=True, help='評価対象のCSVファイルを指定', metavar='sample_response.csv')
  parser.add_argument('--output_dir', type=str, required=True, help='評価結果の出力先を指定', metavar='sample_dir')
  parser.add_argument('--accuracy', type=str, choices=['strict', 'lenient'], required=True, help='正確性において、参考回答と厳密に比較するかどうかを選択')
  args = parser.parse_args()

  label, response = load_csv(args.label), load_csv(args.response)
  data = _build_data(label, response)
  results, avg_scores, error_count = evaluate(args.accuracy == 'strict', data)
  results = [data[i] | results[i] for i in range(len(data))]

  save_csv(results, f'outputs/{args.output_dir}', 'results.csv')
  save_json(avg_scores, f'outputs/{args.output_dir}', 'score.json')
  print(json.dumps(avg_scores, ensure_ascii=False, indent=2))
  print(f'エラー件数: {error_count}')

def _build_data(label, response):
  if len(label) != len(response):
    raise ValueError('正解ラベルと評価対象の要素数が一致しません')
  try:
    lq_idx, la_idx = label[0].index('query'), label[0].index('answer')
    rq_idx, ra_idx = response[0].index('query'), response[0].index('answer')
  except ValueError as e:
    raise KeyError('CSVファイルにはquery、answerキーが必要です')
  data = []
  for i in range(len(label)):
    if i == 0: continue
    if not label[i][lq_idx] or not response[i][rq_idx]:
      raise ValueError(f'{str(i)}行目の正解ラベルのquery、あるいは評価対象のqueryが空です')
    if not label[i][la_idx] or not response[i][ra_idx]:
      raise ValueError(f'{str(i)}行目の正解ラベルのanswer、あるいは評価対象のanswerが空です')
    if not (label[i][lq_idx] == response[i][rq_idx]):
      raise ValueError(f'{str(i)}行目の正解ラベルのqueryと評価対象のqueryが一致しません')
    data.append({
      'query': label[i][lq_idx],
      'response': response[i][ra_idx],
      'reference': label[i][la_idx]
    })
  return data

if __name__ == '__main__':
  main()
