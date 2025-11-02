from src.evaluator import evaluate, _build_prompts, _extract_score
from unittest.mock import patch
from textwrap import dedent

PROMPT_TEMPLATE = '''
[質問]
{question}

[参考回答開始]
{reference}
[参考回答終了]

[AIアシスタント回答開始]
{response}
[AIアシスタント回答終了]
'''

DATA = [
  {
    'query': 'テスト質問1',
    'response': 'テスト回答1',
    'reference': 'テスト参考回答1'
  },
  {
    'query': 'テスト質問2',
    'response': 'テスト回答2',
    'reference': 'テスト参考回答2'
  }
]

def test_evaluate_without_errors():
  results = [
    {
      'text': '''
        正確性(評価理由): 正確性テキスト
        正確性: [[1]]
        流暢性(評価理由): 流暢性テキスト
        流暢性: [[2]]
        詳細性(評価理由): 詳細性テキスト
        詳細性: [[3]]
        関連性(評価理由): 関連性テキスト
        関連性: [[4]]
        総合評価(評価理由): 総合評価テキスト
        総合評価: [[5]]
      ''',
      'status': 'success'
    },
    {
      'text': '''
        正確性(評価理由): 正確性テキスト
        正確性: [[3]]
        流暢性(評価理由): 流暢性テキスト
        流暢性: [[3]]
        詳細性(評価理由): 詳細性テキスト
        詳細性: [[3]]
        関連性(評価理由): 関連性テキスト
        関連性: [[3]]
        総合評価(評価理由): 総合評価テキスト
        総合評価: [[3]]
      ''',
      'status': 'success'
    }
  ]
  with (
    patch('src.evaluator._build_prompts', return_value=[PROMPT_TEMPLATE.format(question=d['query'], response=d['response'], reference=d['reference']) for d in DATA]) as mock_build,
    patch('src.evaluator.execute_requests', return_value=results) as mock_execute
  ):
    assert evaluate(True, DATA) == (
      results,
      {
        '正確性': 2,
        '流暢性': 2.5,
        '詳細性': 3,
        '関連性': 3.5,
        '総合評価': 4
      },
      0
    )
    mock_build.assert_called_once()
    mock_execute.assert_called_once()
    
def test_evaluate_with_api_error():
  results = [
    {
      'text': '''
        正確性(評価理由): 正確性テキスト
        正確性: [[1]]
        流暢性(評価理由): 流暢性テキスト
        流暢性: [[2]]
        詳細性(評価理由): 詳細性テキスト
        詳細性: [[3]]
        関連性(評価理由): 関連性テキスト
        関連性: [[4]]
        総合評価(評価理由): 総合評価テキスト
        総合評価: [[5]]
      ''',
      'status': 'success'
    },
    {
      'text': '',
      'status': 'SERVER_ERROR'
    }
  ]
  with (
    patch('src.evaluator._build_prompts', return_value=[PROMPT_TEMPLATE.format(question=d['query'], response=d['response'], reference=d['reference']) for d in DATA]) as mock_build,
    patch('src.evaluator.execute_requests', return_value=results) as mock_execute
  ):
    assert evaluate(True, DATA) == (
      results,
      {
        '正確性': 1,
        '流暢性': 2,
        '詳細性': 3,
        '関連性': 4,
        '総合評価': 5
      },
      1
    )
    mock_build.assert_called_once()
    mock_execute.assert_called_once()

def test_evaluate_with_api_errors():
  results = [
    {
      'text': '',
      'status': 'SERVER_ERROR'
    },
    {
      'text': '',
      'status': 'SERVER_ERROR'
    }
  ]
  with (
    patch('src.evaluator._build_prompts', return_value=[PROMPT_TEMPLATE.format(question=d['query'], response=d['response'], reference=d['reference']) for d in DATA]) as mock_build,
    patch('src.evaluator.execute_requests', return_value=results) as mock_execute
  ):
    assert evaluate(True, DATA) == (
      results,
      {
        '正確性': None,
        '流暢性': None,
        '詳細性': None,
        '関連性': None,
        '総合評価': None
      },
      2
    )
    mock_build.assert_called_once()
    mock_execute.assert_called_once()

def test_evaluate_with_extract_error():
  results = [
    {
      'text': dedent('''
        正確性(評価理由): 正確性テキスト
        正確性: [[1]]
        流暢性(評価理由): 流暢性テキスト
        流暢性: [[2]]
        詳細性(評価理由): 詳細性テキスト
        詳細性: [[3]]
        関連性(評価理由): 関連性テキスト
        関連性: [[4]]
        総合評価(評価理由): 総合評価テキスト
        総合評価: [[5]]
      '''),
      'status': 'success'
    },
    {
      'text': dedent('''
        正確性(評価理由): 正確性テキスト
        正確性: [[3]]
      '''),
      'status': 'success'
    }
  ]
  with (
    patch('src.evaluator._build_prompts', return_value=[PROMPT_TEMPLATE.format(question=d['query'], response=d['response'], reference=d['reference']) for d in DATA]) as mock_build,
    patch('src.evaluator.execute_requests', return_value=results) as mock_execute
  ):
    assert evaluate(True, DATA) == (
      [
        {
          'text': dedent('''
            正確性(評価理由): 正確性テキスト
            正確性: [[1]]
            流暢性(評価理由): 流暢性テキスト
            流暢性: [[2]]
            詳細性(評価理由): 詳細性テキスト
            詳細性: [[3]]
            関連性(評価理由): 関連性テキスト
            関連性: [[4]]
            総合評価(評価理由): 総合評価テキスト
            総合評価: [[5]]
          '''),
          'status': 'success'
        },
        {
          'text': dedent('''
            正確性(評価理由): 正確性テキスト
            正確性: [[3]]
          '''),
          'status': 'EXTRACT_ERROR'
        }
      ],
      {
        '正確性': 1,
        '流暢性': 2,
        '詳細性': 3,
        '関連性': 4,
        '総合評価': 5
      },
      1
    )
    mock_build.assert_called_once()
    mock_execute.assert_called_once()

def test_evaluate_with_extract_errors():
  results = [
    {
      'text': dedent('''
        正確性(評価理由): 正確性テキスト
        正確性: [[1]]
      '''),
      'status': 'success'
    },
    {
      'text': dedent('''
        正確性(評価理由): 正確性テキスト
        正確性: [[3]]
      '''),
      'status': 'success'
    }
  ]
  with (
    patch('src.evaluator._build_prompts', return_value=[PROMPT_TEMPLATE.format(question=d['query'], response=d['response'], reference=d['reference']) for d in DATA]) as mock_build,
    patch('src.evaluator.execute_requests', return_value=results) as mock_execute
  ):
    assert evaluate(True, DATA) == (
      [
        {
          'text': dedent('''
            正確性(評価理由): 正確性テキスト
            正確性: [[1]]
          '''),
          'status': 'EXTRACT_ERROR'
        },
        {
          'text': dedent('''
            正確性(評価理由): 正確性テキスト
            正確性: [[3]]
          '''),
          'status': 'EXTRACT_ERROR'
        }
      ],
      {
        '正確性': None,
        '流暢性': None,
        '詳細性': None,
        '関連性': None,
        '総合評価': None
      },
      2
    )
    mock_build.assert_called_once()
    mock_execute.assert_called_once()


def test_build_prompts_with_strict_accuracy():
  with patch('src.evaluator.load_text', return_value=PROMPT_TEMPLATE) as mock_load:
    assert _build_prompts(True, DATA) == [
      dedent('''
      [質問]
      テスト質問1

      [参考回答開始]
      テスト参考回答1
      [参考回答終了]

      [AIアシスタント回答開始]
      テスト回答1
      [AIアシスタント回答終了]
      '''),
      dedent('''
      [質問]
      テスト質問2

      [参考回答開始]
      テスト参考回答2
      [参考回答終了]

      [AIアシスタント回答開始]
      テスト回答2
      [AIアシスタント回答終了]
      ''')
    ]

    mock_load.assert_called_once_with('data/prompts/strict_accuracy.txt')

def test_build_prompts_with_lenient_accuracy():
  with patch('src.evaluator.load_text', return_value=PROMPT_TEMPLATE) as mock_load:
    assert _build_prompts(False, DATA) == [
      dedent('''
      [質問]
      テスト質問1

      [参考回答開始]
      テスト参考回答1
      [参考回答終了]

      [AIアシスタント回答開始]
      テスト回答1
      [AIアシスタント回答終了]
      '''),
      dedent('''
      [質問]
      テスト質問2

      [参考回答開始]
      テスト参考回答2
      [参考回答終了]

      [AIアシスタント回答開始]
      テスト回答2
      [AIアシスタント回答終了]
      ''')
    ]

    mock_load.assert_called_once_with('data/prompts/lenient_accuracy.txt')


def test_extract_score_success():
  text = '''
    正確性(評価理由): 正確性テキスト
    正確性: [[1]]
    流暢性(評価理由): 流暢性テキスト
    流暢性: [[2]]
    詳細性(評価理由): 詳細性テキスト
    詳細性: [[3]]
    関連性(評価理由): 関連性テキスト
    関連性: [[4]]
    総合評価(評価理由): 総合評価テキスト
    総合評価: [[5]]
    '''
  assert _extract_score(text) == (
    {
      '正確性': 1,
      '流暢性': 2,
      '詳細性': 3,
      '関連性': 4,
      '総合評価': 5
    },
    'success'
  )

def test_extract_score_text_empty():
  assert _extract_score('') == (
    {
      '正確性': 0,
      '流暢性': 0,
      '詳細性': 0,
      '関連性': 0,
      '総合評価': 0
    },
    'EXTRACT_ERROR'
  )

def test_extract_score_duplicate_metric():
  text = '''
    正確性(評価理由): 正確性テキスト
    正確性: [[1]]
    流暢性(評価理由): 流暢性テキスト
    流暢性: [[2]]
    詳細性(評価理由): 詳細性テキスト
    詳細性: [[3]]
    詳細性(評価理由): 詳細性テキスト
    詳細性: [[3]]
    関連性(評価理由): 関連性テキスト
    関連性: [[4]]
    総合評価(評価理由): 総合評価テキスト
    総合評価: [[5]]
    '''
  assert _extract_score(text) == (
    {
      '正確性': 0,
      '流暢性': 0,
      '詳細性': 0,
      '関連性': 0,
      '総合評価': 0
    },
    'EXTRACT_ERROR'
  )

def test_extract_score_insufficient_metric():
  text = '''
    正確性(評価理由): 正確性テキスト
    正確性: [[1]]
    流暢性(評価理由): 流暢性テキスト
    流暢性: [[2]]
    詳細性(評価理由): 詳細性テキスト
    詳細性: [[3]]
    総合評価(評価理由): 総合評価テキスト
    総合評価: [[5]]
    '''
  assert _extract_score(text) == (
    {
      '正確性': 0,
      '流暢性': 0,
      '詳細性': 0,
      '関連性': 0,
      '総合評価': 0
    },
    'EXTRACT_ERROR'
  )
