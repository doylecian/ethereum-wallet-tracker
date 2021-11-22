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

def list_token_txns(wallet_address, token_symbol, ascending):

    api_params.update({
        'module': 'account',
        'action': 'tokentx',
        'address': wallet_address,
        'sort': order,
    })

    r = requests.get(url = api_url, params = api_params)
    txns = r.json()

    for txn in txns['result']:
        if txn['tokenSymbol'] == 'SYN':
            if txn['to'] == wallet_address:
                print("Purchased " + token_symbol + " at block " + txn['blockHash'])
            else:
                print("Sold " + tokenSymbol + "at block " + txn['blockHash'])

            tx_receipt = get_transaction_receipt(txn['hash'])
            print(tx_receipt['result']['logs'][-1]['data'])


def get_transaction_receipt(txhash):

    api_params.update({
        'module': 'proxy',
        'action': 'eth_getTransactionReceipt',
        'txhash': txhash,
    })

    r = requests.get(url = api_url, params = api_params)
    return r.json()


def last_hash_value(hash): # TODO implement this function



def hex_to_decimal(hex):
    return int(hex, 16) # length = len(str(decimal))


list_token_txns('0xf76219cecc4329707d2188934f3fec3edb306e2c', 'SYN', False)
hex_to_decimal("171e8f0f9991aaf4bf62")
