from web3 import Web3
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes

# Connect to the Ethereum node
node_url = 'http://node.masnet.ai:8545'
web3 = Web3(Web3.HTTPProvider(node_url))

# Check if connected to the node
if not web3.is_connected():
    raise Exception("Failed to connect to the Ethereum node")

# List of mnemonic phrases
mnemonic_phrases = [
    "your first twelve word mnemonic phrase here",
    "your second twelve word mnemonic phrase here",
    "your third twelve word mnemonic phrase here",
    # Add more phrases as needed
]

# Define the receiver address
receiver_address = '0x64669F88Fd2cE75A2448C7F41B78e0bb6b79ce19'

# Define the amount to send (in wei)
amount_to_send = web3.to_wei(0.499979, 'ether')

# Define gas and gas price
gas_limit = 21000
gas_price = web3.to_wei('1', 'gwei')
chainid = 220315

with open('mas_tes.txt', 'r') as file:
    mnemonic_phrases = [line.strip() for line in file]

for mnemonic_phrase in mnemonic_phrases:
    # Generate seed from mnemonic phrase
    seed_bytes = Bip39SeedGenerator(mnemonic_phrase).Generate()

    # Generate the BIP44 master key for Ethereum
    bip44_mst = Bip44.FromSeed(seed_bytes, Bip44Coins.ETHEREUM)

    # Derive the private key from the master key
    bip44_acc = bip44_mst.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
    private_key = bip44_acc.PrivateKey().Raw().ToHex()
    sender_address = bip44_acc.PublicKey().ToAddress()

    # Get the nonce (transaction count for the sender address)
    nonce = web3.eth.get_transaction_count(sender_address)

    # Define the transaction
    tx = {
        'nonce': nonce,
        'to': receiver_address,
        'value': amount_to_send,  # Amount to send (in wei)
        'gas': gas_limit,
        'gasPrice': gas_price,
        'chainId': chainid,
    }

    # Sign the transaction
    signed_tx = web3.eth.account.sign_transaction(tx, private_key)

    # Send the transaction
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

    # Get the transaction hash
    print(f"Transaction from {sender_address} sent with hash: {tx_hash.hex()}")
