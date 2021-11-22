import requests

api_url = 'https://api.etherscan.io/api'
api_key = ''
startblock = '0'
endblock = '999999999'

api_params = {
    'startblock': startblock,
    'endblock': endblock,
    'apikey': api_key
}

def list_token_txns(wallet_address, token_symbol, ascending=False, query_limit=0):

    if (ascending):
        order = 'asc'
    else:
        order = 'desc'

    api_params.update({
        'module': 'account',
        'action': 'tokentx',
        'address': wallet_address,
        'sort': order,
    })

    r = requests.get(url = api_url, params = api_params)
    txns = r.json()

    query_count = 0
    for txn in txns['result']:
        if query_count < query_limit or query_limit == 0:
            if txn['tokenSymbol'] == token_symbol:
                if txn['to'] == wallet_address:
                    print("Purchased " + token_symbol + " at block " + txn['blockHash'])
                else:
                    print("Sold " + token_symbol + "at block " + txn['blockHash'])

                tx_receipt = get_transaction_receipt(txn['hash'])
                print(tx_receipt['result']['logs'][-1]['data'])
                query_count += 1


def get_transaction_receipt(txhash):

    api_params.update({
        'module': 'proxy',
        'action': 'eth_getTransactionReceipt',
        'txhash': txhash,
    })

    r = requests.get(url = api_url, params = api_params)
    return r.json()


def last_hash_value(hash): # TODO implement this function
    print('tes')


def hex_to_decimal(hex):
    return int(hex, 16) # length = len(str(decimal))


list_token_txns('0xf76219cecc4329707d2188934f3fec3edb306e2c', 'SYN')
hex_to_decimal("171e8f0f9991aaf4bf62")
