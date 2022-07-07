class Wallet:
    def __init__(self, address: int) -> None:
        self.address = address
        self.transactions = []
        self.eth_amount = 0

    def add_transaction(self, transaction) -> None:
        self.transactions.append(transaction)

class Transaction:
    def __init__(self, api_result) -> None:
        api_result['value'] = float(api_result['value']) / (10 ** int(api_result['tokenDecimal']))
        api_result['from_'] = api_result.pop('from')
        self.__dict__.update(api_result)

    def formatted(self):
        return [self.hash, self.timeStamp, self.from_, self.to, self.tokenSymbol, self.value]