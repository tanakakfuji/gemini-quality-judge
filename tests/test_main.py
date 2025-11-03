from src.main import _build_data
import pytest

def test_build_data_success():
  label = [['query', 'answer'],['テスト質問1', 'テスト正解ラベル1'],['テスト質問2', 'テスト正解ラベル2']]
  response = [['query', 'answer'],['テスト質問1', 'テスト回答1'],['テスト質問2', 'テスト回答2']]
  assert _build_data(label, response) == [
    {
      'query': 'テスト質問1',
      'response': 'テスト回答1',
      'reference': 'テスト正解ラベル1'
    },
    {
      'query': 'テスト質問2',
      'response': 'テスト回答2',
      'reference': 'テスト正解ラベル2'
    }
  ]

def test_build_data_label_size_longer():
  label = [['query', 'answer'],['テスト質問1', 'テスト正解ラベル1'],['テスト質問2', 'テスト正解ラベル2']]
  response = [['query', 'answer'],['テスト質問1', 'テスト回答1']]
  with pytest.raises(ValueError, match='正解ラベルと評価対象の要素数が一致しません'):
    _build_data(label, response)

def test_build_data_response_size_longer():
  label = [['query', 'answer'],['テスト質問1', 'テスト正解ラベル1']]
  response = [['query', 'answer'],['テスト質問1', 'テスト回答1'],['テスト質問2', 'テスト回答2']]
  with pytest.raises(ValueError, match='正解ラベルと評価対象の要素数が一致しません'):
    _build_data(label, response)

def test_build_data_query_missing():
  label = [['question', 'answer'],['テスト質問1', 'テスト正解ラベル1'],['テスト質問2', 'テスト正解ラベル2']]
  response = [['query', 'answer'],['テスト質問1', 'テスト回答1'],['テスト質問2', 'テスト回答2']]
  with pytest.raises(KeyError, match='CSVファイルにはquery、answerキーが必要です'):
    _build_data(label, response)

def test_build_data_answer_missing():
  label = [['query', 'answer'],['テスト質問1', 'テスト正解ラベル1'],['テスト質問2', 'テスト正解ラベル2']]
  response = [['query', 'reply'],['テスト質問1', 'テスト回答1'],['テスト質問2', 'テスト回答2']]
  with pytest.raises(KeyError, match='CSVファイルにはquery、answerキーが必要です'):
    _build_data(label, response)

def test_build_data_query_empty():
  label = [['query', 'answer'],['テスト質問1', 'テスト正解ラベル1'],['', 'テスト正解ラベル2']]
  response = [['query', 'answer'],['テスト質問1', 'テスト回答1'],['テスト質問2', 'テスト回答2']]
  with pytest.raises(ValueError, match='2行目の正解ラベルのquery、あるいは評価対象のqueryが空です'):
    _build_data(label, response)

def test_build_data_answer_empty():
  label = [['query', 'answer'],['テスト質問1', 'テスト正解ラベル1'],['テスト質問2', 'テスト正解ラベル2']]
  response = [['query', 'answer'],['テスト質問1', 'テスト回答1'],['テスト質問2', '']]
  with pytest.raises(ValueError, match='2行目の正解ラベルのanswer、あるいは評価対象のanswerが空です'):
    _build_data(label, response)

def test_build_data_query_mismatch():
  label = [['query', 'answer'],['テスト質問1', 'テスト正解ラベル1'],['テスト質問2', 'テスト正解ラベル2']]
  response = [['query', 'answer'],['テスト質問1', 'テスト回答1'],['テスト問題2', 'テスト回答2']]
  with pytest.raises(ValueError, match='行目の正解ラベルのqueryと評価対象のqueryが一致しません'):
    _build_data(label, response)
