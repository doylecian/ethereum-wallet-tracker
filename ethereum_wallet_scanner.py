import requests
from textwrap import wrap

api_url = 'https://api.etherscan.io/api'
api_key = ''
startblock = '0'
endblock = '999999999'

api_params = {
    'startblock': startblock,
    'endblock': endblock,
    'apikey': api_key
}

eth_function_hashes = {
    '0xe1fffcc4923d04b559f4d29a8bfc6cda04eb5b0d3c460751c2402c5c5cc9109c': 'Deposit',
    '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef': 'Transfer',
    '0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822': 'Swap',
    '0x1c411e9a96e071241c2f21f7726b17ae89e3cab4c78be50e062b03a9fffbbad1': 'Sync',
    '0x7ff36ab5': 'swapExactETHForTokens'
}

token_contract_decimals = {
    'SYN': 18
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

    print("Incoming token transactions for " + wallet_address + "\n")
    for txn in txns['result']:
        if query_count < query_limit or query_limit == 0:
            if txn['tokenSymbol'] == token_symbol: # If it's a transaction we care about
                transaction_hash = txn['hash']
                amount = get_tx_amount(transaction_hash, wallet_address)
                amount = hex_to_value(amount, token_symbol)
                transaction_info = get_transaction_info(transaction_hash)
                transaction_input = transaction_info['input']
                value_wei = hex_to_decimal(strip_zeros(transaction_info['value']))
                value_eth = wei_to_eth(value_wei)
                input_method = transaction_input[0:10] # Extract first 10 bytes for method hash
                stripped_input = transaction_input[10:] # Remove method hash
                input_method_params = split_hash(stripped_input) # Get passed parameters

                if txn['to'] == wallet_address:
                    print("[" + eth_function_hashes[input_method] +  "] " + value_eth + " " + "ETH -> " + amount + " " + token_symbol)
                else:
                    print("[TX_OUT] " + amount + " " + token_symbol + " -> " + value_eth + " ETH")

                query_count += 1

def get_tx_amount(txhash, wallet_address):
    tx_receipt = get_transaction_receipt(txhash)

    for log in tx_receipt['result']['logs']:
        args = log['topics']
        function_name = eth_function_hashes[args[0]]
        if function_name == 'Transfer':
            address_to = strip_zeros(args[2])
            if address_to == wallet_address: # If transfer event is to wallet_address
                return hex_to_decimal(log['data'])

def list_transaction_events(txhash):
    tx_receipt = get_transaction_receipt(txhash)
    print("Transaction events: \n")

    for log in tx_receipt['result']['logs']:
        print("Method: " + eth_function_hashes[log['topics'][0]])
        if len(log['topics']) > 1:
            print("\nData: " + log['topics'][1] + "\n")

def get_transaction_receipt(txhash):

    api_params.update({
        'module': 'proxy',
        'action': 'eth_getTransactionReceipt',
        'txhash': txhash,
    })

    r = requests.get(url = api_url, params = api_params)
    return r.json()

def get_transaction_info(txhash):

    api_params.update({
        'module': 'proxy',
        'action': 'eth_getTransactionByHash',
        'txhash': txhash,
    })

    r = requests.get(url = api_url, params = api_params)
    return r.json()['result']


def first_hash_value(hash): # Returns first hash value of a string
    hash = hash.replace('0x','')
    hash_value = ""
    for char in hash:
        if char != '0':
            hash_value += char
        else:
            return hash_value

def split_hash(hash, bytes=64): # Splits a hash string by every bytes characters (default 64 bytes)
    return wrap(hash, bytes)

def strip_zeros(hex): # Remove leading zeros on hex addresses
    return  '0x' + hex.lstrip('0x0')

def hex_to_decimal(hex): # Converts hex string to decimal string
    return str(int(hex, 16)) # length = len(str(decimal))

def hex_to_value(hex, token_symbol): # Converts hex value to reflect amount of tokens based on the decimals of the token contract
    return str(float(hex) / 10 ** token_contract_decimals[token_symbol])

def wei_to_eth(wei): # Converts values in wei to eth equivalent
    return str(int(wei) / (10**18))

list_token_txns('0xf76219cecc4329707d2188934f3fec3edb306e2c', 'SYN', query_limit=3)
#list_transaction_events("0x1c5df1fd206c6d2d17ee353babf3bdd8ad1c6473505fe893421074bb04a9391c")
#TODO redo list_token_txns to return list of txsn rather than printing
