import os
import json
import importlib.util
from pathlib import Path


def _load_handler():
    # load the handler module directly from file to avoid package path issues in CI
    handler_path = Path(__file__).parents[1] / 'handler.py'
    spec = importlib.util.spec_from_file_location('handler', str(handler_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_create_ticket_no_table(monkeypatch):
    handler = _load_handler()
    monkeypatch.delenv('TICKETS_TABLE', raising=False)
    event = {'body': json.dumps({'title': 'Test'})}
    resp = handler.lambda_handler(event, None)
    assert resp['statusCode'] == 200
    data = json.loads(resp['body'])
    assert 'ticket' in data
    assert data['ticket']['title'] == 'Test'
