from fastapi import FastAPI, APIRouter, HTTPException, Depends, Body
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
import uuid
from datetime import datetime
import json

# Blockchain related imports
from web3 import Web3
from eth_account import Account
import base58
from mnemonic import Mnemonic
import secrets
import hashlib

# For Solana
from solana.rpc.api import Client as SolanaClient

# AI related imports
import openai

# Setup basic app configuration
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'wallet_agent_db')]

# Initialize blockchain connections
# Ethereum - Use Infura for mainnet, or public testnet endpoints
eth_rpc_url = os.environ.get('ETH_RPC_URL', 'https://mainnet.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161')  # Default to public endpoint
web3 = Web3(Web3.HTTPProvider(eth_rpc_url))

# Solana - Use public RPC endpoints
sol_rpc_url = os.environ.get('SOL_RPC_URL', 'https://api.mainnet-beta.solana.com')  # Default to mainnet
solana_client = SolanaClient(sol_rpc_url)

# TRON - Use public RPC endpoints
tron_rpc_url = os.environ.get('TRON_RPC_URL', 'https://api.trongrid.io')  # Default to mainnet

# OpenAI configuration (if provided)
openai_api_key = os.environ.get('OPENAI_API_KEY')
if openai_api_key:
    openai.api_key = openai_api_key

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class WalletBase(BaseModel):
    wallet_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    chain_type: str  # "ETH", "SOL", or "TRON"

class WalletCreate(BaseModel):
    name: str
    chain_type: str
    mnemonic: Optional[str] = None  # If provided, will import existing wallet

class WalletImport(BaseModel):
    name: str
    chain_type: str
    mnemonic: str

class WalletOwnerUpdate(BaseModel):
    wallet_id: str
    new_owner_address: str
    new_owner_type: str = "external"  # "external" or "wallet" (another wallet in the system)

class TokenInfo(BaseModel):
    token_address: str
    symbol: str
    decimals: int
    balance: str
    name: Optional[str] = None
    logo_url: Optional[str] = None

class WalletSponsor(BaseModel):
    wallet_id: str
    sponsor_address: str
    gas_limit: Optional[float] = None
    active: bool = True

class TransactionSimulation(BaseModel):
    wallet_id: str
    to_address: str
    amount: str
    token_address: Optional[str] = None  # If None, native token
    data: Optional[str] = None  # For contract interactions

class TransactionBundle(BaseModel):
    wallet_id: str
    transactions: List[Dict[str, Any]]
    name: Optional[str] = None
    description: Optional[str] = None

class Wallet(WalletBase):
    address: str
    public_key: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    encrypted_mnemonic: Optional[str] = None  # In production, encrypt this
    tokens: List[TokenInfo] = []
    sponsor_address: Optional[str] = None

class Balance(BaseModel):
    wallet_id: str
    address: str
    balance: str  # String to handle large numbers precisely
    token_symbol: str  # ETH, SOL, TRX, etc.
    usd_value: Optional[float] = None

class Transaction(BaseModel):
    tx_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    wallet_id: str
    from_address: str
    to_address: str
    amount: str
    token_symbol: str
    token_address: Optional[str] = None
    tx_hash: Optional[str] = None
    status: str = "pending"  # pending, confirmed, failed, simulated
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    gas_used: Optional[float] = None
    gas_price: Optional[str] = None
    is_sponsored: bool = False
    sponsor_address: Optional[str] = None
    bundle_id: Optional[str] = None
    data: Optional[str] = None

class TransactionCreate(BaseModel):
    wallet_id: str
    to_address: str
    amount: str
    token_symbol: str
    token_address: Optional[str] = None
    use_sponsor: bool = False
    data: Optional[str] = None

class AIChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str

class AIChat(BaseModel):
    chat_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    messages: List[AIChatMessage] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AIChatRequest(BaseModel):
    message: str
    wallet_id: Optional[str] = None
    chat_id: Optional[str] = None

class AIChatResponse(BaseModel):
    chat_id: str
    response: str
    action: Optional[Dict[str, Any]] = None  # Optional action to perform

# Wallet management functions
async def create_ethereum_wallet(name: str, mnemonic: Optional[str] = None) -> Wallet:
    """Create a new Ethereum wallet or import from mnemonic"""
    mnemo = Mnemonic("english")
    
    if not mnemonic:
        # Generate a new mnemonic
        mnemonic = mnemo.generate(strength=128)
    
    # Create a seed from the mnemonic
    seed = hashlib.pbkdf2_hmac("sha512", mnemonic.encode("utf-8"), b"mnemonic", 2048)
    
    # Use the first 32 bytes as private key (simplified for demo)
    private_key = "0x" + seed[:32].hex()
    
    # Create account from private key
    account = Account.from_key(private_key)
    
    wallet = Wallet(
        name=name,
        chain_type="ETH",
        address=account.address,
        public_key=account.address,  # For ETH, address is the public key
        encrypted_mnemonic=mnemonic  # Not encrypted in this demo, but would be in production
    )
    
    # Save to database
    await db.wallets.insert_one(wallet.dict())
    
    return wallet

async def create_solana_wallet(name: str, mnemonic: Optional[str] = None) -> Wallet:
    """Create a new Solana wallet or import from mnemonic"""
    mnemo = Mnemonic("english")
    
    if not mnemonic:
        # Generate a new mnemonic
        mnemonic = mnemo.generate(strength=128)
    
    # Create a seed from the mnemonic (simplified for demo)
    seed = hashlib.pbkdf2_hmac("sha512", mnemonic.encode("utf-8"), b"mnemonic", 2048)
    
    # Use first 32 bytes for keypair
    keypair_bytes = seed[:32]
    
    # Create a basic base58 encoding for the address
    address = base58.b58encode(keypair_bytes).decode('utf-8')
    
    wallet = Wallet(
        name=name,
        chain_type="SOL",
        address=address,
        public_key=address,  # For Solana, the address is derived from the public key
        encrypted_mnemonic=mnemonic  # Not encrypted in this demo, but would be in production
    )
    
    # Save to database
    await db.wallets.insert_one(wallet.dict())
    
    return wallet

async def create_tron_wallet(name: str, mnemonic: Optional[str] = None) -> Wallet:
    """Create a new TRON wallet or import from mnemonic"""
    mnemo = Mnemonic("english")
    
    if not mnemonic:
        # Generate a new mnemonic
        mnemonic = mnemo.generate(strength=128)
    
    # Create a seed from the mnemonic (simplified for demo)
    seed = hashlib.pbkdf2_hmac("sha512", mnemonic.encode("utf-8"), b"mnemonic", 2048)
    
    # Use first 32 bytes for keypair (simplified)
    private_key = "0x" + seed[:32].hex()
    
    # Create a demo address (in real implementation, we'd derive from private key)
    address = "T" + secrets.token_hex(20)  # Just a placeholder
    
    wallet = Wallet(
        name=name,
        chain_type="TRON",
        address=address,
        public_key=address,
        encrypted_mnemonic=mnemonic
    )
    
    # Add default TRX token
    wallet.tokens.append(
        TokenInfo(
            token_address="native",
            symbol="TRX",
            decimals=6,
            balance="0",
            name="TRON",
            logo_url="https://cryptologos.cc/logos/tron-trx-logo.png?v=022"
        )
    )
    
    # Save to database
    await db.wallets.insert_one(wallet.dict())
    
    return wallet

async def get_ethereum_balance(address: str) -> float:
    """Get the balance of an Ethereum address in ETH"""
    try:
        balance_wei = web3.eth.get_balance(address)
        balance_eth = web3.from_wei(balance_wei, 'ether')
        return float(balance_eth)
    except Exception as e:
        logging.error(f"Error getting ETH balance: {e}")
        return 0.0

async def get_solana_balance(address: str) -> float:
    """Get the balance of a Solana address in SOL"""
    try:
        response = solana_client.get_balance(address)
        # Depending on how the response is structured
        if isinstance(response, dict) and 'result' in response:
            value = response['result']['value']
        else:
            value = response.value
        return float(value) / 1_000_000_000  # Convert lamports to SOL
    except Exception as e:
        logging.error(f"Error getting SOL balance: {e}")
        return 0.0

async def get_tron_balance(address: str) -> float:
    """Get the balance of a TRON address in TRX"""
    # In a real app, we would call TRON API
    # For this demo, we'll return a fake balance
    try:
        # Simulate a random balance based on address
        # In a real app, we would call TRON API
        random_seed = int(address[1:5], 16) if len(address) > 5 else 0
        balance = (random_seed % 100) + (random_seed % 10) / 10
        return balance
    except Exception as e:
        logging.error(f"Error getting TRON balance: {e}")
        return 0.0

async def get_token_balances(wallet_id: str) -> List[TokenInfo]:
    """Get token balances for a wallet"""
    wallet = await db.wallets.find_one({"wallet_id": wallet_id})
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    # In a real app, we would query the blockchain for token balances
    # For this demo, we'll return the stored tokens or create some dummy ones
    
    if "tokens" in wallet and wallet["tokens"]:
        return wallet["tokens"]
    
    # Create some dummy tokens based on chain type
    tokens = []
    if wallet["chain_type"] == "ETH":
        tokens = [
            TokenInfo(
                token_address="0xdac17f958d2ee523a2206206994597c13d831ec7",
                symbol="USDT",
                decimals=6,
                balance="100.5",
                name="Tether",
                logo_url="https://cryptologos.cc/logos/tether-usdt-logo.png?v=022"
            ),
            TokenInfo(
                token_address="0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
                symbol="USDC",
                decimals=6,
                balance="250.75",
                name="USD Coin",
                logo_url="https://cryptologos.cc/logos/usd-coin-usdc-logo.png?v=022"
            )
        ]
    elif wallet["chain_type"] == "SOL":
        tokens = [
            TokenInfo(
                token_address="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                symbol="USDC",
                decimals=6,
                balance="175.25",
                name="USD Coin",
                logo_url="https://cryptologos.cc/logos/usd-coin-usdc-logo.png?v=022"
            ),
            TokenInfo(
                token_address="Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
                symbol="USDT",
                decimals=6,
                balance="130.0",
                name="Tether",
                logo_url="https://cryptologos.cc/logos/tether-usdt-logo.png?v=022"
            )
        ]
    elif wallet["chain_type"] == "TRON":
        tokens = [
            TokenInfo(
                token_address="TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
                symbol="USDT",
                decimals=6,
                balance="200.0",
                name="Tether",
                logo_url="https://cryptologos.cc/logos/tether-usdt-logo.png?v=022"
            ),
            TokenInfo(
                token_address="TEkxiTehnzSmSe2XqrBj4w32RUN966rdz8",
                symbol="USDC",
                decimals=6,
                balance="150.0",
                name="USD Coin",
                logo_url="https://cryptologos.cc/logos/usd-coin-usdc-logo.png?v=022"
            )
        ]
    
    # Update wallet with tokens
    await db.wallets.update_one(
        {"wallet_id": wallet_id},
        {"$set": {"tokens": [token.dict() for token in tokens]}}
    )
    
    return tokens

# AI Assistant functions
async def process_ai_message(message: str, wallet_id: Optional[str] = None) -> Dict[str, Any]:
    """Process a message with AI and return a response with optional actions"""
    
    # If no OpenAI API key, just return a basic response
    if not openai_api_key:
        return {
            "response": "I'm a wallet assistant, but I need an OpenAI API key to provide intelligent responses. I can still help with basic wallet operations though!",
            "action": None
        }
    
    try:
        # Get wallet context if wallet_id is provided
        wallet_context = ""
        if wallet_id:
            wallet = await db.wallets.find_one({"wallet_id": wallet_id})
            if wallet:
                chain_type = wallet["chain_type"]
                address = wallet["address"]
                balance = 0
                
                if chain_type == "ETH":
                    balance = await get_ethereum_balance(address)
                    balance_str = f"{balance} ETH"
                elif chain_type == "SOL":
                    balance = await get_solana_balance(address)
                    balance_str = f"{balance} SOL"
                elif chain_type == "TRON":
                    balance = await get_tron_balance(address)
                    balance_str = f"{balance} TRX"
                
                wallet_context = f"Current wallet: {wallet['name']} ({chain_type}) - Address: {address} - Balance: {balance_str}"
                
                # Add token information if available
                if "tokens" in wallet and wallet["tokens"]:
                    tokens_str = ", ".join([f"{token['balance']} {token['symbol']}" for token in wallet["tokens"]])
                    wallet_context += f"\nTokens: {tokens_str}"
                
                # Add sponsor information if available
                if "sponsor_address" in wallet and wallet["sponsor_address"]:
                    wallet_context += f"\nSponsor: {wallet['sponsor_address']}"
        
        # Create system message with context
        system_message = f"""You are a helpful blockchain wallet assistant. 
You can help users manage their Ethereum, Solana, and TRON wallets.
Current date: {datetime.now().strftime('%Y-%m-%d')}
{wallet_context}

If the user wants to perform actions like checking balance, creating a wallet, or sending transactions, 
you should return a structured action in your response."""
        
        # Call OpenAI API
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
        )
        
        response_text = completion.choices[0].message.content
        
        # Parse for potential actions (in a real app, we'd use a more robust approach)
        action = None
        if "CREATE_WALLET" in response_text or "create wallet" in response_text.lower():
            action = {"type": "CREATE_WALLET"}
        elif "CHECK_BALANCE" in response_text or "check balance" in response_text.lower():
            action = {"type": "CHECK_BALANCE", "wallet_id": wallet_id}
        elif "SEND_TRANSACTION" in response_text or "send transaction" in response_text.lower() or "send tokens" in response_text.lower():
            action = {"type": "SEND_TRANSACTION", "wallet_id": wallet_id}
        elif "UPDATE_OWNER" in response_text or "change owner" in response_text.lower():
            action = {"type": "UPDATE_OWNER", "wallet_id": wallet_id}
        elif "SET_SPONSOR" in response_text or "add sponsor" in response_text.lower():
            action = {"type": "SET_SPONSOR", "wallet_id": wallet_id}
        elif "BUNDLE_TRANSACTION" in response_text or "create bundle" in response_text.lower():
            action = {"type": "BUNDLE_TRANSACTION", "wallet_id": wallet_id}
        
        return {
            "response": response_text,
            "action": action
        }
    except Exception as e:
        logging.error(f"Error in AI processing: {e}")
        return {
            "response": f"I encountered an error while processing your request: {str(e)}",
            "action": None
        }

# API Routes
@api_router.post("/wallets", response_model=Wallet)
async def create_wallet(wallet_data: WalletCreate):
    """Create a new wallet or import from mnemonic"""
    if wallet_data.chain_type not in ["ETH", "SOL", "TRON"]:
        raise HTTPException(status_code=400, detail="Chain type must be ETH, SOL, or TRON")
    
    try:
        if wallet_data.chain_type == "ETH":
            wallet = await create_ethereum_wallet(wallet_data.name, wallet_data.mnemonic)
        elif wallet_data.chain_type == "SOL":
            wallet = await create_solana_wallet(wallet_data.name, wallet_data.mnemonic)
        elif wallet_data.chain_type == "TRON":
            wallet = await create_tron_wallet(wallet_data.name, wallet_data.mnemonic)
        
        return wallet
    except Exception as e:
        logging.error(f"Error creating wallet: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating wallet: {str(e)}")

@api_router.get("/wallets", response_model=List[Wallet])
async def get_wallets():
    """Get all wallets"""
    wallets = await db.wallets.find().to_list(1000)
    return [Wallet(**wallet) for wallet in wallets]

@api_router.get("/wallets/{wallet_id}", response_model=Wallet)
async def get_wallet(wallet_id: str):
    """Get a wallet by ID"""
    wallet = await db.wallets.find_one({"wallet_id": wallet_id})
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    return Wallet(**wallet)

@api_router.get("/wallets/{wallet_id}/balance", response_model=Balance)
async def get_wallet_balance(wallet_id: str):
    """Get the balance of a wallet"""
    wallet = await db.wallets.find_one({"wallet_id": wallet_id})
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    address = wallet["address"]
    chain_type = wallet["chain_type"]
    
    balance = 0
    token_symbol = ""
    
    if chain_type == "ETH":
        balance = await get_ethereum_balance(address)
        token_symbol = "ETH"
    elif chain_type == "SOL":
        balance = await get_solana_balance(address)
        token_symbol = "SOL"
    elif chain_type == "TRON":
        balance = await get_tron_balance(address)
        token_symbol = "TRX"
    
    return Balance(
        wallet_id=wallet_id,
        address=address,
        balance=str(balance),
        token_symbol=token_symbol
    )

@api_router.get("/wallets/{wallet_id}/tokens", response_model=List[TokenInfo])
async def get_wallet_tokens(wallet_id: str):
    """Get tokens for a wallet"""
    tokens = await get_token_balances(wallet_id)
    return tokens

@api_router.post("/transactions", response_model=Transaction)
async def create_transaction(tx_data: TransactionCreate):
    """Create a new transaction (in this demo, we simulate the transaction)"""
    wallet = await db.wallets.find_one({"wallet_id": tx_data.wallet_id})
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    # Get sponsor address if requested
    sponsor_address = None
    if tx_data.use_sponsor and "sponsor_address" in wallet and wallet["sponsor_address"]:
        sponsor_address = wallet["sponsor_address"]
    
    # In a real app, we would use the wallet's private key to sign and send the transaction
    # For this demo, we'll just create a transaction record
    
    tx = Transaction(
        wallet_id=tx_data.wallet_id,
        from_address=wallet["address"],
        to_address=tx_data.to_address,
        amount=tx_data.amount,
        token_symbol=tx_data.token_symbol,
        token_address=tx_data.token_address,
        tx_hash=f"demo_tx_{uuid.uuid4().hex}",  # This would be the actual transaction hash in production
        status="confirmed",  # For demo purposes, we mark it as confirmed immediately
        is_sponsored=tx_data.use_sponsor,
        sponsor_address=sponsor_address,
        data=tx_data.data
    )
    
    await db.transactions.insert_one(tx.dict())
    
    return tx

@api_router.get("/transactions/{wallet_id}", response_model=List[Transaction])
async def get_wallet_transactions(wallet_id: str):
    """Get all transactions for a wallet"""
    transactions = await db.transactions.find({"wallet_id": wallet_id}).to_list(1000)
    return [Transaction(**tx) for tx in transactions]

@api_router.post("/wallets/{wallet_id}/owner", response_model=Wallet)
async def update_wallet_owner(wallet_id: str, owner_data: WalletOwnerUpdate):
    """Update the owner of a wallet"""
    wallet = await db.wallets.find_one({"wallet_id": wallet_id})
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    # In a real app, we would verify ownership through a signature or other means
    # For this demo, we'll just update the address
    
    # Check if new owner is another wallet in the system
    if owner_data.new_owner_type == "wallet":
        owner_wallet = await db.wallets.find_one({"wallet_id": owner_data.new_owner_address})
        if not owner_wallet:
            raise HTTPException(status_code=404, detail="Owner wallet not found")
        new_address = owner_wallet["address"]
    else:
        new_address = owner_data.new_owner_address
    
    # In a real app, we would handle the transfer of ownership on-chain
    # For this demo, we'll just update our record
    
    # Create an ownership transfer record
    transfer = {
        "transfer_id": str(uuid.uuid4()),
        "wallet_id": wallet_id,
        "old_owner": wallet["address"],
        "new_owner": new_address,
        "timestamp": datetime.utcnow()
    }
    await db.ownership_transfers.insert_one(transfer)
    
    # Update wallet address
    await db.wallets.update_one(
        {"wallet_id": wallet_id},
        {"$set": {"address": new_address}}
    )
    
    # Return updated wallet
    updated_wallet = await db.wallets.find_one({"wallet_id": wallet_id})
    return Wallet(**updated_wallet)

@api_router.post("/wallets/{wallet_id}/sponsor", response_model=Wallet)
async def set_wallet_sponsor(wallet_id: str, sponsor_data: WalletSponsor):
    """Set a sponsor address for wallet transactions"""
    wallet = await db.wallets.find_one({"wallet_id": wallet_id})
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    # In a real app, we would verify the sponsor's consent
    # For this demo, we'll just update the wallet
    
    if sponsor_data.active:
        await db.wallets.update_one(
            {"wallet_id": wallet_id},
            {"$set": {"sponsor_address": sponsor_data.sponsor_address}}
        )
    else:
        await db.wallets.update_one(
            {"wallet_id": wallet_id},
            {"$unset": {"sponsor_address": ""}}
        )
    
    # Return updated wallet
    updated_wallet = await db.wallets.find_one({"wallet_id": wallet_id})
    return Wallet(**updated_wallet)

@api_router.post("/transactions/simulate", response_model=Transaction)
async def simulate_transaction(sim_data: TransactionSimulation):
    """Simulate a transaction and return expected result without sending it"""
    wallet = await db.wallets.find_one({"wallet_id": sim_data.wallet_id})
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    # In a real app, we would perform an actual simulation on the blockchain
    # For this demo, we'll create a simulated transaction record
    
    # Set token information
    token_symbol = wallet["chain_type"]  # Default to native token
    if sim_data.token_address:
        # Look up token symbol (simplified for demo)
        tokens = await get_token_balances(sim_data.wallet_id)
        for token in tokens:
            if token.token_address == sim_data.token_address:
                token_symbol = token.symbol
                break
    
    # Create simulated transaction
    tx = Transaction(
        wallet_id=sim_data.wallet_id,
        from_address=wallet["address"],
        to_address=sim_data.to_address,
        amount=sim_data.amount,
        token_symbol=token_symbol,
        token_address=sim_data.token_address,
        status="simulated",
        gas_used=0.000142 if wallet["chain_type"] != "SOL" else 0.000005,
        gas_price="20 Gwei" if wallet["chain_type"] == "ETH" else "0.01 TRX" if wallet["chain_type"] == "TRON" else "5 lamports",
        data=sim_data.data
    )
    
    await db.transactions.insert_one(tx.dict())
    
    return tx

@api_router.post("/transactions/bundle", response_model=List[Transaction])
async def create_transaction_bundle(bundle_data: TransactionBundle):
    """Create and execute a bundle of transactions"""
    wallet = await db.wallets.find_one({"wallet_id": bundle_data.wallet_id})
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    # Generate a bundle ID
    bundle_id = str(uuid.uuid4())
    
    # Process each transaction in the bundle
    transactions = []
    for tx_data in bundle_data.transactions:
        # Extract transaction data
        to_address = tx_data.get("to_address")
        amount = tx_data.get("amount")
        token_symbol = tx_data.get("token_symbol", wallet["chain_type"])
        token_address = tx_data.get("token_address")
        data = tx_data.get("data")
        
        # In a real app, we would batch and send these transactions
        # For this demo, we'll create individual transaction records
        tx = Transaction(
            wallet_id=bundle_data.wallet_id,
            from_address=wallet["address"],
            to_address=to_address,
            amount=amount,
            token_symbol=token_symbol,
            token_address=token_address,
            tx_hash=f"bundle_tx_{uuid.uuid4().hex}",
            status="confirmed",  # For demo purposes
            bundle_id=bundle_id,
            data=data
        )
        
        await db.transactions.insert_one(tx.dict())
        transactions.append(tx)
    
    # Store bundle metadata
    bundle_meta = {
        "bundle_id": bundle_id,
        "wallet_id": bundle_data.wallet_id,
        "name": bundle_data.name,
        "description": bundle_data.description,
        "transaction_count": len(transactions),
        "timestamp": datetime.utcnow()
    }
    await db.transaction_bundles.insert_one(bundle_meta)
    
    return transactions

@api_router.post("/ai/chat", response_model=AIChatResponse)
async def ai_chat(request: AIChatRequest):
    """Chat with the AI assistant"""
    chat_id = request.chat_id
    
    # If no chat_id, create a new chat
    if not chat_id:
        chat = AIChat()
        chat_id = chat.chat_id
        chat.messages.append(AIChatMessage(role="user", content=request.message))
        await db.ai_chats.insert_one(chat.dict())
    else:
        # Add message to existing chat
        chat = await db.ai_chats.find_one({"chat_id": chat_id})
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        # Update the chat with the new message
        chat["messages"].append({"role": "user", "content": request.message})
        await db.ai_chats.update_one({"chat_id": chat_id}, {"$set": {"messages": chat["messages"]}})
    
    # Process the message with AI
    ai_response = await process_ai_message(request.message, request.wallet_id)
    
    # Add AI response to the chat
    await db.ai_chats.update_one(
        {"chat_id": chat_id}, 
        {"$push": {"messages": {"role": "assistant", "content": ai_response["response"]}}}
    )
    
    return AIChatResponse(
        chat_id=chat_id,
        response=ai_response["response"],
        action=ai_response["action"]
    )

@api_router.get("/ai/chat/{chat_id}", response_model=AIChat)
async def get_chat(chat_id: str):
    """Get a chat by ID"""
    chat = await db.ai_chats.find_one({"chat_id": chat_id})
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    return AIChat(**chat)

# Root API endpoint
@api_router.get("/")
async def root():
    return {"message": "Welcome to the Blockchain Wallet AI Agent API"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
