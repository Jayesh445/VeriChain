import pandas as pd
import hashlib
from web3 import Web3
from datetime import datetime
from solcx import compile_source, install_solc, set_solc_version

# ----------------------------
# Configuration (Amoy Testnet)
# ----------------------------
INFURA_URL = "https://polygon-amoy.infura.io/v3/1307fe2d730d4f98982eb391c1f9afb3"
ACCOUNT = "0x9ABd635A15f9aFA256b83bD06CC59FeFC15e1Af1"  # your wallet
PRIVATE_KEY = "0xd9ea795152216526ae1d27be0ab3157a07f5e813ba684b21327a4deb5c0b4bbe"  # ⚠️ keep safe!

# ----------------------------
# Web3 setup
# ----------------------------
w3 = Web3(Web3.HTTPProvider(INFURA_URL))
if not w3.is_connected():
    raise Exception("Web3 connection failed")
print("Connected to Polygon Amoy Testnet:", w3.is_connected())

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

    function getReport(uint256 id) public view returns (Report memory) {
        require(id < reports.length, "Report ID out of bounds");
        return reports[id];
    }

    function getReportCount() public view returns (uint256) {
        return reports.length;
    }
}
'''

# ----------------------------
# Compile and deploy contract
# ----------------------------
install_solc("0.8.19")
set_solc_version("0.8.19")

compiled_sol = compile_source(contract_source_code, output_values=['abi', 'bin'])
contract_id, contract_interface = compiled_sol.popitem()

contract_abi = contract_interface['abi']
contract_bytecode = contract_interface['bin']

# Deploy contract
contract = w3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)
nonce = w3.eth.get_transaction_count(ACCOUNT)
tx = contract.constructor().build_transaction({
    'from': ACCOUNT,
    'nonce': nonce,
    'gas': 2000000,  # deployment gas
    'gasPrice': w3.to_wei('35', 'gwei')  # updated to 35 gwei for faster confirmation
})
signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
print("Deploying contract... Tx hash:", w3.to_hex(tx_hash))
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
contract_address = tx_receipt.contractAddress
print("Contract deployed at:", contract_address)

contract_instance = w3.eth.contract(address=contract_address, abi=contract_abi)

# ----------------------------
# Generate mock AI finance data
# ----------------------------
data = [
    {"vendor": "Vendor A", "sales": 10000, "purchase": 7000, "currency": "USD"},
    {"vendor": "Vendor B", "sales": 20000, "purchase": 15000, "currency": "USD"},
]
df = pd.DataFrame(data)
df["profit"] = df["sales"] - df["purchase"]
df["margin"] = df["profit"] / df["sales"] * 100

pivot_table = pd.pivot_table(df, index="vendor", values=["sales", "purchase", "profit", "margin"])

# ----------------------------
# Export report
# ----------------------------
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
report_name = f"finance_report_{timestamp}.xlsx"
pivot_table.to_excel(report_name)

# ----------------------------
# Hash report
# ----------------------------
with open(report_name, "rb") as f:
    file_hash = hashlib.sha256(f.read()).hexdigest()
print("Report SHA256 Hash:", file_hash)

# ----------------------------
# Metadata
# ----------------------------
period = "Q3 2025"
auditor = "CA Firm XYZ"

# ----------------------------
# Store report on blockchain
# ----------------------------
nonce = w3.eth.get_transaction_count(ACCOUNT)
tx = contract_instance.functions.storeReport(
    report_name,
    period,
    auditor,
    file_hash
).build_transaction({
    'from': ACCOUNT,
    'nonce': nonce,
    'gas': 150000,  # sufficient for storeReport
    'gasPrice': w3.to_wei('35', 'gwei')  # updated to 35 gwei
})
signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
print("Report stored! Tx hash:", w3.to_hex(tx_hash))

# ----------------------------
# Query latest report
# ----------------------------
report_count = contract_instance.functions.getReportCount().call()
print("Total reports stored:", report_count)

if report_count > 0:
    latest_report = contract_instance.functions.getReport(report_count - 1).call()
    print("Latest report on blockchain:", latest_report)
