import requests
import json
import pprint
from collections import defaultdict

input_address = '0xEcA19B1a87442b0c25801B809bf567A6ca87B1da'.lower()
coin_address = '0x38e26c68bdef7c6e7f1aea94b7ceb8d95b11bd69'

API_KEY = '1W8UKCDBQM3TA6CHCHPCMMFUY6W2V59G86'
base_url = f'https://api-ropsten.etherscan.io/api'
payload = {
    'module': 'account',
    'action': 'tokentx',
    'contractaddress': coin_address,
    'address': input_address,
    'sort': 'asc',
    'apikey': API_KEY
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

res = requests.get(base_url, params=payload, headers=headers)

# with open('out.json', 'w') as f:
#     f.write(json.dumps(res.json(), indent=2))
tx_dump = open('transactions.txt', 'w')
balance_dump = open('balance.txt', 'w')

queue = []
balance = defaultdict(lambda: 0)
txns = json.loads(res.text)['result']
for tx in txns:
    tx_hash = tx['hash']
    from_acc = tx['from']
    to_acc = tx['to']
    amount = tx['value']
    if from_acc == input_address:
        queue.append((tx_hash, from_acc, to_acc, int(amount)))
    else:
        balance[to_acc] += int(amount)


finished_hash = []
while len(queue) > 0:
    tx_hash, from_acc, to_acc, amount = queue.pop(0)
    if tx_hash in finished_hash:
        continue
    finished_hash.append(tx_hash)
    balance[to_acc] += amount
    balance[from_acc] -= amount
    print(f'from: {from_acc[:5]} to {to_acc[:5]} amount {amount}')
    tx_dump.writelines(
        f'hash: {tx_hash}, from: {from_acc}, to: {to_acc}, amount: {amount}\n')
    payload['address'] = to_acc
    res = requests.get(base_url, params=payload, headers=headers)
    txns = json.loads(res.text)['result']
    for tx_ in txns:
        tx_hash_ = tx_['hash']
        from_acc_ = tx_['from']
        to_acc_ = tx_['to']
        amount_ = tx_['value']
        if from_acc_ == to_acc:
            queue.append((tx_hash_, from_acc_, to_acc_, int(amount_)))
        else:
            balance[to_acc_] += int(amount_)

for addr, val in balance.items():
    balance_dump.writelines(f'{addr}: {val}\n')
# while len(queue) > 0:
#     print(queue.pop(0)[2])

# cnt = 0
# visited = []
# while len(queue) > 0:
#     top = queue.pop(0)
#     tx_hash, from_acc, to_acc, amount = top
#     if to_acc in visited:
#         continue

#     file.write(f'{tx_hash} {from_acc} {to_acc} {amount}')
#     print(f'{cnt}: {to_acc} {amount}')

#     payload['address'] = to_acc
#     res = requests.get(base_url, params=payload, headers=headers)
#     txns = json.loads(res.text)['result']
#     for tx in txns:
#         tx_hash = tx['hash']
#         from_acc = tx['from']
#         to_acc = tx['to']
#         amount = tx['value']
#         queue.append((tx_hash, from_acc, to_acc, amount))
#     cnt += 1
#     visited.append(to_acc)


tx_dump.close()
balance_dump.close()
