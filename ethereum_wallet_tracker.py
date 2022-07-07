import requests
import json
from eth_classes import Wallet, Transaction
from textwrap import wrap
from eth_contracts import eth_function_hashes, token_contract_decimals
from tabulate import tabulate

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
    api_res = r.json()

    query_count = 0

    print("\nIncoming token transactions for " + wallet_address + "\n")
    
    wallet = Wallet(wallet_address)
    for transaction_dict in api_res['result']:
        if query_count < query_limit or query_limit == 0:
            if transaction_dict['tokenSymbol'] == token_symbol or token_symbol == 'DEFAULT': # If it's a transaction we care about
                wallet.add_transaction(Transaction(transaction_dict).formatted())
    
    headers = ['Transaction hash', 'Date', 'From', 'To', 'Token', 'Amount']
    print(tabulate(wallet.transactions, headers, tablefmt="grid"))

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
