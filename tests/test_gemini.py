from src.gemini import execute_requests, _send_request
import pytest
from unittest.mock import Mock
from unittest.mock import patch
from unittest.mock import call
from google.genai import errors

def test_execute_requests_success(monkeypatch):
  monkeypatch.setenv('GEMINI_API_KEYS', 'k1,k2,k3')
  monkeypatch.setenv('REQUEST_INTERVAL_TIME', '5.0')
  prompts = ['プロンプト1', 'プロンプト2', 'プロンプト3', 'プロンプト4', 'プロンプト5', 'プロンプト6']
  with (
    patch('src.gemini._send_request', return_value={'text': 'サンプルテキスト', 'status': 'success'}) as mock_send,
    patch('src.gemini.time.sleep') as mock_sleep
  ):
    assert execute_requests(prompts) == [
      { 'text': 'サンプルテキスト', 'status': 'success' },
      { 'text': 'サンプルテキスト', 'status': 'success' },
      { 'text': 'サンプルテキスト', 'status': 'success' },
      { 'text': 'サンプルテキスト', 'status': 'success' },
      { 'text': 'サンプルテキスト', 'status': 'success' },
      { 'text': 'サンプルテキスト', 'status': 'success' },
    ]
    mock_send.assert_has_calls(calls=[
      call('k1', 'プロンプト1'),
      call('k2', 'プロンプト2'),
      call('k3', 'プロンプト3'),
      call('k1', 'プロンプト4'),
      call('k2', 'プロンプト5'),
      call('k3', 'プロンプト6'),
    ])
    mock_sleep.assert_has_calls(calls=[
      call(5.0),
      call(5.0),
      call(5.0),
      call(5.0),
      call(5.0),
    ])

def test_execute_requests_continuous_api_error(monkeypatch):
  monkeypatch.setenv('GEMINI_API_KEYS', 'k1,k2,k3')
  monkeypatch.setenv('REQUEST_INTERVAL_TIME', '5.0')
  prompts = ['プロンプト1', 'プロンプト2', 'プロンプト3', 'プロンプト4', 'プロンプト5', 'プロンプト6']
  with (
    patch('src.gemini._send_request', return_value={'text': '', 'status': 'SERVER_ERROR'}) as mock_send,
    patch('src.gemini.time.sleep') as mock_sleep,
    pytest.raises(RuntimeError, match='API呼び出しが5回連続して失敗したため、処理を停止します')
  ):
    execute_requests(prompts)
    mock_send.assert_has_calls(calls=[
      call('k1', 'プロンプト1'),
      call('k2', 'プロンプト2'),
      call('k3', 'プロンプト3'),
      call('k1', 'プロンプト4'),
      call('k2', 'プロンプト5'),
    ])
    mock_sleep.assert_has_calls(calls=[
      call(5.0),
      call(5.0),
      call(5.0),
      call(5.0),
    ])

def test_send_request_success():
  mock_response = Mock(text='テストテキスト')
  with patch('src.gemini.genai.Client') as mock_client:
    mock_client.return_value.models.generate_content.return_value = mock_response
    key = 'k1'
    prompt = 'テストプロンプト'
    assert _send_request(key, prompt) == {
    'text': 'テストテキスト',
    'status': 'success'
    }
    mock_client.assert_called_once_with(api_key='k1')
    mock_client.return_value.models.generate_content.assert_called_once()

def test_send_request_api_error():
  with patch('src.gemini.genai.Client') as mock_client:
    mock_client.return_value.models.generate_content.side_effect = errors.ServerError('API error',
    {
      'error': {
        'code': 500,
        'message': '',
        'status': 'SERVER_ERROR'
      }
    })
    key = 'k1'
    prompt = 'テストプロンプト'
    assert _send_request(key, prompt) == {
      'text': '',
      'status': 'SERVER_ERROR'
    }
    mock_client.assert_called_once_with(api_key='k1')
    mock_client.return_value.models.generate_content.assert_called_once()

def test_send_request_key_empty():
  key = ''
  prompt = 'テストプロンプト'
  with pytest.raises(ValueError, match='APIキーが不正です'):
    _send_request(key, prompt)

def test_send_request_key_invalid_type():
  key = []
  prompt = 'テストプロンプト'
  with pytest.raises(ValueError, match='APIキーが不正です'):
    _send_request(key, prompt)

def test_send_request_prompt_empty():
  key = 'k1'
  prompt = ''
  with pytest.raises(ValueError, match='プロンプトが空文字です'):
    _send_request(key, prompt)
