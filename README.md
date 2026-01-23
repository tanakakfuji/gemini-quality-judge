# gemini-quality-judge
GeminiによるQAタスクの生成品質評価（正確性、流暢性、詳細性、関連性、総合評価）を実施する自動評価ツール

## クイックスタート
- 仮想環境の作成

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

- [Google AI Studio](https://aistudio.google.com/api-keys) より、APIキーを作成・コピー

- `.env` ファイルを作成

```bash
cp .env.example .env
nano .env
```

- APIキーを設定

```bash
GEMINI_MODEL_NAME=gemini-2.5-flash
GEMINI_API_KEYS=【作成したAPIキー】
REQUEST_INTERVAL_TIME=2.0
```

- 実行例

```bash
python -m src.main --label data/labels/sample_label.csv --response data/responses/sample_response.csv --prompt data/prompts/eval_prompt.txt --output_dir sample_dir
```

## 背景
「日本語LLM-as-a-Judgeを統合的に扱うためのツール」として、[llm-jp-judge](https://github.com/llm-jp/llm-jp-judge) が公開されています。このツールは、生成品質評価、マルチターン対話評価、応答の安全性評価に対応しています。

しかし、llm-jp-judgeには以下の3つの問題点があります。

- 評価用LLMにGeminiを使用できない
- 生成品質評価に参考回答を利用できない
- 入力にcsvファイルが想定されていない

そこで、評価用LLMにGeminiを使用できる自動評価ツールを提案します。本ツールは、実際のQAタスクで得られる回答結果と正解ラベルをまとめたcsvファイルから、参考回答付きの評価を実施することができます。

※ 実際のQAタスクの生成結果を評価することが目的のため、品質評価のみを行います。評価用プロンプトは、参考回答の利用に伴い、llm-jp-judgeのものを一部改変しています。

## ドキュメント

### 入力ファイルのデータ形式
`data/labels` 配下に正解ラベルのcsvファイルを、`data/responses` 配下に回答結果のcsvファイルを配置します。

ただし、以下の形式では、エラーが生じます。

- 必須のカラム名（queryとanswer）が存在しない
- queryまたはanswerの値が空文字の行が存在する
- 2つのファイル間で要素数が一致しない
- 2つのファイル間でqueryの値が一致しない行が存在する

### 評価用プロンプト
`data/prompts` 配下には、`eval_prompt.txt` という評価用プロンプトがあり、以下の5つの観点で評価します。

- 正確性
- 流暢性
- 詳細性
- 関連性
- 総合評価

### オプション
実行時に利用できるオプションは以下の通りです。

|オプション名|必要性|説明|
|--|--|--|
|--label|required|正解ラベルのcsvファイルを指定|
|--response|required|評価対象のcsvファイルを指定|
|--prompt|required|評価用プロンプトのテキストファイルを指定|
|--output_dir|required|評価結果の出力先を指定|

### 環境変数
実行時に指定する環境変数は以下の通りです。

|変数名|説明|
|--|--|
|GEMINI_MODEL_NAME|`curl "https://generativelanguage.googleapis.com/v1beta/models?key=【作成したAPIキー】"` で取得できるモデル名を指定|
|GEMINI_API_KEYS|APIキーを指定. 複数ある場合はカンマ区切りで指定|
|REQUEST_INTERVAL_TIME|リクエストを送信する間隔を秒数で指定|

※ Geminiのレート制限（無料枠）の回避を目的として、APIキーを複数指定することが可能です。

### 出力結果
`outputs/{output_dir}` 配下に`results.csv` と`avg_scores.json` が出力されます。それぞれのデータ形式は以下の通りです。

- results.csv (text列に評価結果が格納)

```
query,response,reference,正確性,流暢性,詳細性,関連性,総合評価,text,status
```

- avg_scores.json

```
{
  "正確性": x,
  "流暢性": x,
  "詳細性": x,
  "関連性": x,
  "総合評価": x
}
```

### テスト
`tests` 配下にテストファイルがあり、以下の通りテストを実行できます。

```bash
pytest --cov=src --cov-report=term-missing
```