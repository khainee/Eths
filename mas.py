from web3 import Web3
from mnemonic import Mnemonic
from eth_account import Account
import json

# Connect to the Ethereum node
node_url = 'http://node.masnet.ai:8545'
web3 = Web3(Web3.HTTPProvider(node_url))

Account.enable_unaudited_hdwallet_features()

# Check if connected to the node
if not web3.is_connected():
    raise Exception("Failed to connect to the Ethereum node")

print("Connected to Ethereum node")

# Define the receiver address
receiver_address = '0x64669F88Fd2cE75A2448C7F41B78e0bb6b79ce19'

# Define gas and gas price
gas_limit = 21000
gas_price = web3.to_wei('1', 'gwei')
chain_id = 220315  # Use the appropriate chain ID for your network

# Initialize total transferred amount
total_transferred = 0
done_acc = 0

# Initialize Mnemonic instance
mnemo = Mnemonic("english")

# Read mnemonic phrases from file
with open('mas_tes.txt', 'r') as file:
    mnemonic_phrases = [line.strip() for line in file]

for mnemonic_phrase in mnemonic_phrases:
    try:
        # Validate mnemonic phrase
        if not mnemo.check(mnemonic_phrase):
            print(f"Invalid mnemonic phrase: {mnemonic_phrase}")
            continue

        # Generate seed from mnemonic phrase
        seed_bytes = mnemo.to_seed(mnemonic_phrase)

        # Generate the account from the seed
        acct = Account.from_mnemonic(mnemonic_phrase)
        sender_address = acct.address
        private_key = acct.key

        #print(f"Derived sender address: {sender_address}")

        # Get the balance of the sender address
        balance = web3.eth.get_balance(sender_address)

        #print(f"Balance for {sender_address}: {web3.from_wei(balance, 'ether')} ETH")

        # Calculate the total transaction cost
        transaction_fee = gas_limit * gas_price

        # Check if balance is sufficient
        if balance <= transaction_fee:
            print(f"Insufficient funds for address {sender_address}. Balance: {web3.from_wei(balance, 'ether')} ETH")
            continue

        # Calculate the amount to send (available balance - transaction fee)
        amount_to_send = balance - transaction_fee

        # Get the nonce (transaction count for the sender address)
        nonce = web3.eth.get_transaction_count(sender_address)

        # Define the transaction
        tx = {
            'nonce': nonce,
            'to': receiver_address,
            'value': amount_to_send,  # Amount to send (in wei)
            'gas': gas_limit,
            'gasPrice': gas_price,
            'chainId': chain_id,  # Include chain ID
        }

        # Sign the transaction
        signed_tx = Account.sign_transaction(tx, private_key)

        # Send the transaction
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

        # Update total transferred amount
        total_transferred += amount_to_send
        done_acc += 1

        # Get the transaction hash
        #print(f"Transaction from {sender_address} sent with hash: {tx_hash.hex()}")

    except Exception as e:
        print(f"Error processing mnemonic phrase: {mnemonic_phrase}. Error: {e}")

# Print the total transferred amount after processing all transactions
print(f"Total amount transferred: {web3.from_wei(total_transferred, 'ether')} ETH, doneacc: = {done_acc}")
