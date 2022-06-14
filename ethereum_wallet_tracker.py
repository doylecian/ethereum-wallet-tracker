import requests
import json
from textwrap import wrap

with open('cfg.json') as config:
    cfg = json.load(config)

api_url = cfg['api_url']
api_key = cfg['api_key']
startblock = cfg['startblock']
endblock = cfg['endblock']

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
    '0x7ff36ab5': 'swapExactETHForTokens',
    '0x18cbafe5': 'swapExactTokensForETH',
    '0x38ed1739': 'swapExactTokensForTokens',
    '0x414bf389': 'exactInputSingle', # todo 0x60c22434deab8cbc3fddcbc1cc85a7f5a21a854f7856454428eeb159ccf9e4a2
    '0x3805550f': 'exit', # todo 0xcfd8a65b4355b05c36c0d72a04640f16c0f456a630b882a41a78219357999d81
    '0xa9059cbb': 'transfer(address _to, uint256 _value)' # todo 0x3951c492fd124ca0635b277848200460fcd4effd8a42392e958ca0013a0ed7fb
}

token_contract_decimals = {
    'SYN': 18,
    'DEFAULT': 18
}

def list_token_txns(wallet_address, token_symbol=0, ascending=False, query_limit=0):

    if not token_symbol:
        token_symbol = "DEFAULT"

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

    print("\nIncoming token transactions for " + wallet_address + "\n")
    token_balance = 0
    eth_balance = 0
    for txn in txns['result']:
        if query_count < query_limit or query_limit == 0:
            if txn['tokenSymbol'] == token_symbol or token_symbol == 'DEFAULT': # If it's a transaction we care about

                transaction_hash = txn['hash']
                print(transaction_hash)
                transaction_info = get_transaction_info(transaction_hash)
                transaction_input = transaction_info['input']
                input_method = transaction_input[0:10] # Extract first 10 bytes for method hash
                stripped_input = transaction_input[10:] # Remove method hash
                input_method_params = split_hash(stripped_input) # Get passed parameters
                transaction_outgoing = 0

                if eth_function_hashes[input_method] == 'swapExactTokensForETH': # selling tokens for eth
                    value_wei = hex_to_decimal(strip_zeros(input_method_params[1]))
                    address_to = input_method_params[3]
                    amount = hex_to_value(hex_to_decimal(input_method_params[0]), token_symbol)
                    transaction_outgoing = 1
                elif eth_function_hashes[input_method] == 'swapExactETHForTokens': # buying tokens for eth
                    value_wei = hex_to_decimal(strip_zeros(transaction_info['value']))
                    address_to = input_method_params[2]
                    amount = hex_to_value(hex_to_decimal(input_method_params[0]), token_symbol)
                elif eth_function_hashes[input_method] == 'swapExactTokensForTokens': # bUYING TOKEN -- TODO: GET RECEIPT HERE
                    address_to = input_method_params[3]
                    if transaction_info['value'] == '0x0': # Buying our tokens with other tokens (USDC, WETH, ETC)
                        value_wei = hex_to_decimal(strip_zeros(input_method_params[0]))
                        amount = hex_to_value(hex_to_decimal(input_method_params[1]), token_symbol)
                    else: # Selling our tokens for other tokens
                        value_wei = hex_to_decimal(strip_zeros(input_method_params[1]))
                        amount = hex_to_value(hex_to_decimal(input_method_params[0]), token_symbol)
                        transaction_outgoing = 1

                value_eth = wei_to_eth(value_wei)
                char_limit = 12
                if transaction_outgoing:
                    print("[" + eth_function_hashes[input_method] +  "] " + amount[:char_limit] + " " + token_symbol + " -> " + value_eth[:char_limit] + " ETH")
                    eth_balance += float(value_eth)
                    token_balance -= float(amount)
                else:
                    print("[" + eth_function_hashes[input_method] +  "] " + value_eth[:char_limit] + " " + "ETH -> " + amount[:char_limit] + " " + token_symbol)
                    eth_balance -= float(value_eth)
                    token_balance += float(amount)

                query_count += 1

            #print("Net outcome -> " + token_symbol + ": " + str(token_balance) + " | " + str(eth_balance) + " ETH")

def list_transaction_events(txhash):
    tx_receipt = get_transaction_receipt(txhash)
    print("Transaction events: \n")

    for log in tx_receipt['logs']:
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
    return r.json()['result']

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

list_token_txns('0x1beb5cc62a71683bE44681814a8a6fedC9e484B8', query_limit=4, ascending=True)
#list_token_txns('0x0da634aaae01eb2cc3a90dac6734c45bb9180e9e', 'SYN', query_limit=4, ascending=True)
#list_token_txns('0xf76219cecc4329707d2188934f3fec3edb306e2c', 'SYN', query_limit=3)
#list_transaction_events("0x1c5df1fd206c6d2d17ee353babf3bdd8ad1c6473505fe893421074bb04a9391c")
#TODO 0xfc87736145f79e4dc2c69bdcd335ae3fb471d5cec9c1fa312f2621ff76e17b30 - get exact amnt received from swap function with to argument as wallet_address
