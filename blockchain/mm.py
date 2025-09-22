import pandas as pd
import hashlib
from web3 import Web3
from datetime import datetime
from solcx import compile_source, install_solc, set_solc_version

# ----------------------------
# Configuration (Ganache Local Blockchain)
# ----------------------------
INFURA_URL = "http://127.0.0.1:8545"  # Ganache RPC URL

# Private key from Ganache (pre-funded account)
# Use pre-funded Ganache account
ACCOUNT = Web3.to_checksum_address("0x6A83bF8C0C1bCDDDEAB33B0D75Dd45Dfd6745cd0")
PRIVATE_KEY = "0xe69aea6c94b69d8740d93ef46a77e6ea064c7874dab2849aa5d9501fce41f591"

# ----------------------------
# Web3 setup
# ----------------------------
w3 = Web3(Web3.HTTPProvider(INFURA_URL))
if not w3.is_connected():
    raise Exception("Web3 connection failed")
print("Connected to Ganache Local Blockchain:", w3.is_connected())
print("Using account:", ACCOUNT)

# ----------------------------
# Solidity Smart Contract
# ----------------------------
contract_source_code = '''
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract ReportStorage {
    struct Report {
        string reportName;
        string period;
        string auditor;
        string hash;
        uint256 timestamp;
    }

    Report[] public reports;

    event ReportStored(uint256 indexed id, string reportName, string period, string auditor, string hash, uint256 timestamp);

    function storeReport(string memory reportName, string memory period, string memory auditor, string memory hash) public {
        reports.push(Report(reportName, period, auditor, hash, block.timestamp));
        emit ReportStored(reports.length - 1, reportName, period, auditor, hash, block.timestamp);
    }

    function getReportCount() public view returns (uint256) {
        return reports.length;
    }

    function getReport(uint256 id) public view returns (string memory, string memory, string memory, string memory, uint256) {
        Report storage r = reports[id];
        return (r.reportName, r.period, r.auditor, r.hash, r.timestamp);
    }
}
'''

# ----------------------------
# Compile contract
# ----------------------------
install_solc("0.8.19")
set_solc_version("0.8.19")
compiled_sol = compile_source(contract_source_code, output_values=['abi', 'bin'])
contract_id, contract_interface = compiled_sol.popitem()
contract_abi = contract_interface['abi']
contract_bytecode = contract_interface['bin']

# ----------------------------
# Deploy contract
# ----------------------------
contract = w3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)
nonce = w3.eth.get_transaction_count(ACCOUNT)
tx = contract.constructor().build_transaction({
    'from': ACCOUNT,
    'nonce': nonce,
    'gas': 3000000,
    'gasPrice': w3.to_wei('1', 'gwei')
})
signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
print("Deploying contract... Tx hash:", w3.to_hex(tx_hash))
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
contract_address = tx_receipt.contractAddress
print("Contract deployed at:", contract_address)

contract_instance = w3.eth.contract(address=contract_address, abi=contract_abi)

# ----------------------------
# Function to generate & store report
# ----------------------------
def generate_finance_report(vendor_data, period="Q3 2025", auditor="CA Firm XYZ"):
    print("\n=== Processing Report ===")
    
    df = pd.DataFrame(vendor_data)
    df["profit"] = df["sales"] - df["purchase"]
    df["margin"] = df["profit"] / df["sales"] * 100
    
    # Select best vendor
    best_vendor = df.loc[df["profit"].idxmax()]
    print(f"Best Vendor Selected: {best_vendor['vendor']} with Profit: {best_vendor['profit']}")
    
    pivot_table = pd.pivot_table(df, index="vendor", values=["sales", "purchase", "profit", "margin"])
    
    # Export report
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    report_name = f"finance_report_{timestamp}.xlsx"
    pivot_table.to_excel(report_name)
    
    # Hash report
    with open(report_name, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    print("Report SHA256 Hash:", file_hash)
    
    # Store report on blockchain
    nonce = w3.eth.get_transaction_count(ACCOUNT)
    tx = contract_instance.functions.storeReport(
        report_name, period, auditor, file_hash
    ).build_transaction({
        'from': ACCOUNT,
        'nonce': nonce,
        'gas': 200000,
        'gasPrice': w3.to_wei('1', 'gwei')
    })
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print("Report stored! Tx hash:", w3.to_hex(tx_hash))
    
    # Wait for mining
    w3.eth.wait_for_transaction_receipt(tx_hash)
    
    # Query latest report
    report_count = contract_instance.functions.getReportCount().call()
    latest_index = int(report_count - 1)
    report_data = contract_instance.functions.getReport(latest_index).call()
    
    print("Total reports stored:", report_count)
    print("Latest report on blockchain:")
    print("Report Name:", report_data[0])
    print("Period:", report_data[1])
    print("Auditor:", report_data[2])
    print("Hash:", report_data[3])
    print("Timestamp:", report_data[4])

# ----------------------------
# Demo multiple reports
# ----------------------------
vendor_reports = [
    [
        {"vendor": "Vendor A", "sales": 10000, "purchase": 7000, "currency": "USD"},
        {"vendor": "Vendor B", "sales": 20000, "purchase": 15000, "currency": "USD"},
    ],
    [
        {"vendor": "Vendor C", "sales": 15000, "purchase": 5000, "currency": "USD"},
        {"vendor": "Vendor D", "sales": 12000, "purchase": 6000, "currency": "USD"},
    ]
]

for report_data in vendor_reports:
    generate_finance_report(report_data)
