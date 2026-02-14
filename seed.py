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

