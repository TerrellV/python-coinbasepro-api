import pytest
from cbp_client.pagination import handle_pagination
from cbp_client.auth import Auth
from datetime import datetime, timedelta
from cbp_client.api import _http_get
import pathlib
import json

def test_pagination():
    now = datetime.now()
    thirty_days_ago = now - timedelta(days=30)
    creds = json.loads(pathlib.Path('credentials.json').read_text())

    data = handle_pagination(
        start_date=thirty_days_ago.isoformat(),
        date_field='created_at',
        url='https://api.pro.coinbase.com/orders',
        params={'status': 'all'},
        get_method=_http_get,
        auth=Auth(creds['api_key'], creds['secret'], creds['passphrase'])
    )

    # for now the fact that this runs without failing is enough of a test.
    # Need to think through a true way to test this
    data = list(data)
