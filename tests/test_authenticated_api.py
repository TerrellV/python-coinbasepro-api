import pytest
import json
import pathlib
from decimal import Decimal
from datetime import datetime, timedelta
import types

from cbp_client import AuthAPI
from cbp_client.api import API


SANDBOX_URL = 'https://api-public.sandbox.pro.coinbase.com'


@pytest.fixture
def live_base_api():
    return API(sandbox_mode=False)


@pytest.fixture
def sandbox_auth_api():
    return AuthAPI(
        json.loads(pathlib.Path('credentials.json').read_text())['sandbox'],
        sandbox_mode=True
    )


@pytest.fixture
def live_auth_api():
    creds = json.loads(pathlib.Path('credentials.json').read_text())

    return AuthAPI(
        credentials={
            'api_key': creds['api_key'],
            'secret': creds['secret'],
            'passphrase': creds['passphrase']
        },
        sandbox_mode=False
    )


def test_market_buy(sandbox_auth_api):

    assert sandbox_auth_api.api.base_url == SANDBOX_URL
    purchase_amount = 10

    coin_to_purchase = 'BTC'

    starting_balance = sum(
        Decimal(a.balance)
        for a in sandbox_auth_api._accounts
        if a.currency.upper() == coin_to_purchase
    )

    r = sandbox_auth_api.market_buy(
        funds=purchase_amount,
        product_id=f'{coin_to_purchase}-USD',
        delay=False
    ).json()

    sandbox_auth_api.refresh_accounts()

    ending_balance = sum(
        Decimal(a.balance)
        for a in sandbox_auth_api._accounts
        if a.currency.upper() == coin_to_purchase
    )

    assert r['side'] == 'buy'
    assert int(r['specified_funds']) == purchase_amount
    assert r['type'] == 'market'
    assert ending_balance > starting_balance


def test_market_sell(sandbox_auth_api):

    assert sandbox_auth_api.api.base_url == SANDBOX_URL

    sale_quantity = Decimal('0.01')
    coin_to_purchase = 'BTC'

    starting_balance = sum(
        Decimal(a.balance)
        for a in sandbox_auth_api._accounts
        if a.currency.upper() == coin_to_purchase
    )

    r = sandbox_auth_api.market_sell(
        size=sale_quantity,
        product_id=f'{coin_to_purchase}-USD',
        delay=False
    ).json()

    sandbox_auth_api.refresh_accounts()

    ending_balance = sum(
        Decimal(a.balance)
        for a in sandbox_auth_api._accounts
        if a.currency.upper() == coin_to_purchase
    )

    assert r['side'] == 'sell'
    assert Decimal(r['size']) == sale_quantity
    assert r['type'] == 'market'
    assert ending_balance < starting_balance


def test_balance(sandbox_auth_api):
    api = sandbox_auth_api
    bal = api.balance('btc')
    eth_bal = api.balance('eth')

    assert isinstance(bal, str)
    assert api.balance('BTC') == bal
    assert api.balance('bTc') == bal
    assert isinstance(eth_bal, str)


def test_accounts(sandbox_auth_api):
    btc_act = sandbox_auth_api.accounts(currency='BTC')
    all_accounts = sandbox_auth_api.accounts()

    assert btc_act.currency == 'BTC'
    assert btc_act.id
    assert len(all_accounts) > 0


def test_account_history(sandbox_auth_api):

    btc_account = sandbox_auth_api.accounts(currency='BTC')
    account_id = btc_account.id

    hist = sandbox_auth_api.api.get_paginated_endpoint(
        endpoint=f'accounts/{account_id}/ledger',
        auth=sandbox_auth_api.auth,
        start_date=(datetime.now() - timedelta(days=730)).isoformat()
    )

    assert isinstance(hist, types.GeneratorType)

    for i in range(3):
        next(hist)