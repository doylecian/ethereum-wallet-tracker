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

event_hashes = {
    '0xe1fffcc4923d04b559f4d29a8bfc6cda04eb5b0d3c460751c2402c5c5cc9109c': 'Deposit',
    '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef': 'Transfer',
    '0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822': 'Swap',
    '0x1c411e9a96e071241c2f21f7726b17ae89e3cab4c78be50e062b03a9fffbbad1': 'Sync'
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

    print("Incoming token transactions for " + wallet_address + "\n\n")
    for txn in txns['result']:
        if query_count < query_limit or query_limit == 0:
            if txn['tokenSymbol'] == token_symbol: # If it's a transaction we care about
                amount = get_tx_amount(txn['hash'], wallet_address)
                amount = hex_to_value(amount, token_symbol)
                if txn['to'] == wallet_address:
                    print("Purchased " + amount + " " + token_symbol + " at block " + txn['blockHash'])
                else:
                    print("Sold " + amount + " " + token_symbol + "at block " + txn['blockHash'])

                query_count += 1

def get_tx_amount(txhash, wallet_address):
    tx_receipt = get_transaction_receipt(txhash)

    for log in tx_receipt['result']['logs']:
        args = log['topics']
        function_name = event_hashes[args[0]]
        if function_name == 'Transfer':
            address_to = strip_zeros(args[2])
            if address_to == wallet_address: # If transfer event is to wallet_address
                return hex_to_decimal(log['data'])

def list_transaction_events(txhash):
    tx_receipt = get_transaction_receipt(txhash)
    print("Transaction events: \n")

    for log in tx_receipt['result']['logs']:
        print("Method: " + event_hashes[log['topics'][0]])
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

def split_hash_values(hash):
    hash = hash.replace('0x','')
    current_substring = ""
    hash_values = []
    for char in hash:
        if char != '0':
            print("Adding char " + char)
            current_substring += char

        elif current_substring:
            hash_values.append(current_substring)
            current_substring = ""

    return hash_values

def strip_zeros(hex): # Remove rleading zeros on hex addresses
    return  '0x' + hex.lstrip('0x0')

def hex_to_decimal(hex):
    return str(int(hex, 16)) # length = len(str(decimal))

def hex_to_value(hex, token_symbol): # Converts hex value to reflect amount of tokens based on the decimals of the to
    return str(float(hex) / 10 ** token_contract_decimals[token_symbol])

list_token_txns('0xf76219cecc4329707d2188934f3fec3edb306e2c', 'SYN', query_limit=10)
#list_transaction_events("0x1c5df1fd206c6d2d17ee353babf3bdd8ad1c6473505fe893421074bb04a9391c")
