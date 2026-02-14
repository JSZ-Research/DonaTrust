import json
import random
import sys
import time
from web3 import Web3
import solcx

SOLIDITY_VERSION = '0.8.0'
RPC_URL = "http://127.0.0.1:8545"


INSTITUTIONAL_DONORS = [
    "Global Hope Foundation",
    "Apex Capital Charity",
    "Future Education Trust"
]

INDIVIDUAL_DONORS = [
    "Liam Johnson",
    "Emma Williams",
    "Noah Brown",
    "Olivia Jones",
    "Sophia Garcia"
]

RECIPIENTS = [
    "Student: Lucas Miller",
    "Student: Ava Davis",
    "Project: Clean Water Initiative",
    "Project: Rural Coding Camp",
    "Family: The Wilson Family",
    "Scholarship: STEM for Girls"
]

def compile_contract():
    print(f"Installing solc v{SOLIDITY_VERSION}...")
    try:
        solcx.install_solc(SOLIDITY_VERSION)
    except Exception as e:
        print(f"Note: Auto-install of solc failed or already installed. Proceeding... ({e})")

    print("Compiling CharityPlatform.sol...")
    with open("contracts/CharityPlatform.sol", "r") as f:
        source = f.read()

    compiled_sol = solcx.compile_source(
        source,
        output_values=["abi", "bin"],
        solc_version=SOLIDITY_VERSION
    )
    
    contract_id = '<stdin>:CharityPlatform'
    contract_interface = compiled_sol[contract_id]
    return contract_interface['abi'], contract_interface['bin']

def main():
    print(f"Connecting to {RPC_URL}...")
    w3 = Web3(Web3.HTTPProvider(RPC_URL))

    if not w3.is_connected():
        print("Could not connect to existing local blockchain.")
        print("Attempting to start Anvil automatically...")
        
        import subprocess
        import shutil
        import os
        
        
        anvil_path = shutil.which("anvil")
        if not anvil_path:
           
            home = os.path.expanduser("~")
            potential_path = os.path.join(home, ".foundry/bin/anvil")
            if os.path.exists(potential_path):
                anvil_path = potential_path
        
        if not anvil_path:
            print("Error: 'anvil' not found. Please install Foundry or start a local node manually.")
            sys.exit(1)
            
        print(f"Starting Anvil from: {anvil_path}")
        try:
            anvil_process = subprocess.Popen(
                [anvil_path, "-a", "20"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("Waiting for Anvil to initialize...")
            time.sleep(3) 
            
            
            if not w3.is_connected():
                print("Error: Started Anvil but still cannot connect. Check ports.")
                anvil_process.terminate()
                sys.exit(1)
            else:
                print("Successfully started and connected to Anvil.")
                
                import atexit
                def cleanup():
                    print("\nStopping local blockchain...")
                    anvil_process.terminate()
                atexit.register(cleanup)
                
                
                should_keep_alive = True
        except Exception as e:
            print(f"Failed to start Anvil: {e}")
            sys.exit(1)
    else:
        should_keep_alive = False

    accounts = w3.eth.accounts
    if len(accounts) < 14:
        print(f"Warning: Need at least 14 accounts, but found {len(accounts)}. Rerun Anvil with '-a 20'.")
    
    
    abi, bytecode = compile_contract()
    
    CharityPlatform = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    print("Deploying contract...")
    deployer = accounts[0]
    tx_hash = CharityPlatform.constructor().transact({'from': deployer})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    contract_address = tx_receipt.contractAddress
    print(f"CharityPlatform deployed to: {contract_address}")
    
    charity = w3.eth.contract(address=contract_address, abi=abi)

   
    
    donor_accounts = [] 
    recipient_objs = [] 

    print("\n--- Registering Users ---")

    
    for i, name in enumerate(INSTITUTIONAL_DONORS):
        account = accounts[i]
        print(f"Registering Institutional Donor: {name} ({account})")
        charity.functions.registerDonor(name).transact({'from': account})
        donor_accounts.append({'name': name, 'address': account, 'type': 'institution'})

    
    for i, name in enumerate(INDIVIDUAL_DONORS):
        account = accounts[i + 3] 
        print(f"Registering Individual Donor: {name} ({account})")
        charity.functions.registerDonor(name).transact({'from': account})
        donor_accounts.append({'name': name, 'address': account, 'type': 'individual'})

   
    for i, name in enumerate(RECIPIENTS):
        account = accounts[i + 8] 
        print(f"Registering Recipient: {name} ({account})")
        charity.functions.registerRecipient(name).transact({'from': account})
        recipient_objs.append({'name': name, 'address': account})

    
    print("\n--- Generating 30 Random Donations ---")
    
    recipient_donors = {r['name']: set() for r in recipient_objs}
    
    for i in range(30):
       
        needy = [r for r in recipient_objs if len(recipient_donors[r['name']]) < 2]
        
        if needy:
            recipient = random.choice(needy)
            
            possible_donors = [d for d in donor_accounts if d['name'] not in recipient_donors[recipient['name']]]
            if not possible_donors:
                possible_donors = donor_accounts
            donor = random.choice(possible_donors)
        else:
            recipient = random.choice(recipient_objs)
            donor = random.choice(donor_accounts)
            
        
        if donor['type'] == 'institution':
            amount_eth = random.uniform(5.0, 10.0)
        else:
            amount_eth = random.uniform(0.1, 1.0)
            
        amount_wei = w3.to_wei(amount_eth, 'ether')
        
        
        try:
            tx_hash = charity.functions.donate(recipient['address']).transact({
                'from': donor['address'],
                'value': amount_wei
            })

            recipient_donors[recipient['name']].add(donor['name'])
            
            print(f"[{i+1}/30] [Transferred] {donor['name']} -> {recipient['name']} ({amount_eth:.4f} ETH)")
        except Exception as e:
            print(f"Error donating: {e}")

    
    export_data = {
        "network": "localhost",
        "contract_address": contract_address,
        "abi": abi,
        "donors": donor_accounts,
        "recipients": recipient_objs,
        "donations": []}
    
    
    print("\nSaving deployment data to 'deployment.json'...")
    with open("deployment.json", "w") as f:
        json.dump(export_data, f, indent=2)
    print("Data saved successfully.")

    print("\nSeeding Complete!")
    print(f"Contract Address: {contract_address}")

    if should_keep_alive:
        print("\n" + "="*50)
        print("  LOCAL BLOCKCHAIN IS RUNNING  ")
        print("="*50)
        print("Anvil is running in the background of this script.")
        print(f"RPC URL: {RPC_URL}")
        print(f"Contract Address: {contract_address}")
        print("Deployment data saved to: deployment.json")
        print("Do NOT close this terminal if you want to keep the chain data.")
        print("Press Ctrl+C to stop the blockchain and exit.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nExiting...")

if __name__ == "__main__":
    main()
