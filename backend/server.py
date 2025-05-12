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
from hdwallet import HDWallet
from hdwallet.symbols import ETH, SOL
import base58
from mnemonic import Mnemonic
import secrets

# For Solana
from solana.rpc.api import Client as SolanaClient
try:
    from solana.publickey import PublicKey
except ImportError:
    # Fallback if the import fails
    class PublicKey:
        def __init__(self, value):
            if isinstance(value, bytes):
                self.value = value
            elif isinstance(value, str):
                self.value = base58.b58decode(value)
            else:
                raise ValueError("Unsupported value type")
        
        def __str__(self):
            return base58.b58encode(self.value).decode('utf-8')

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
    chain_type: str  # "ETH" or "SOL"

class WalletCreate(BaseModel):
    name: str
    chain_type: str
    mnemonic: Optional[str] = None  # If provided, will import existing wallet

class WalletImport(BaseModel):
    name: str
    chain_type: str
    mnemonic: str

class Wallet(WalletBase):
    address: str
    public_key: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    encrypted_mnemonic: Optional[str] = None  # In production, encrypt this

class Balance(BaseModel):
    wallet_id: str
    address: str
    balance: str  # String to handle large numbers precisely
    token_symbol: str  # ETH, SOL, etc.
    usd_value: Optional[float] = None

class Transaction(BaseModel):
    tx_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    wallet_id: str
    from_address: str
    to_address: str
    amount: str
    token_symbol: str
    tx_hash: Optional[str] = None
    status: str = "pending"  # pending, confirmed, failed
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class TransactionCreate(BaseModel):
    wallet_id: str
    to_address: str
    amount: str
    token_symbol: str

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
    
    # Create HD wallet
    hdwallet = HDWallet(symbol=ETH)
    hdwallet.from_mnemonic(mnemonic=mnemonic)
    hdwallet.from_path("m/44'/60'/0'/0/0")
    
    # Get wallet details
    private_key = hdwallet.private_key()
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
    
    # Create HD wallet
    hdwallet = HDWallet(symbol=SOL)
    hdwallet.from_mnemonic(mnemonic=mnemonic)
    hdwallet.from_path("m/44'/501'/0'/0'")
    
    # Get wallet details
    keypair_bytes = hdwallet.seed()[0:32]
    public_key = PublicKey(keypair_bytes)
    address = str(public_key)
    
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
        balance = solana_client.get_balance(PublicKey(address))
        return float(balance['result']['value']) / 1_000_000_000  # Convert lamports to SOL
    except Exception as e:
        logging.error(f"Error getting SOL balance: {e}")
        return 0.0

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
                
                wallet_context = f"Current wallet: {wallet['name']} ({chain_type}) - Address: {address} - Balance: {balance_str}"
        
        # Create system message with context
        system_message = f"""You are a helpful blockchain wallet assistant. 
You can help users manage their Ethereum and Solana wallets.
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
    if wallet_data.chain_type not in ["ETH", "SOL"]:
        raise HTTPException(status_code=400, detail="Chain type must be either ETH or SOL")
    
    try:
        if wallet_data.chain_type == "ETH":
            wallet = await create_ethereum_wallet(wallet_data.name, wallet_data.mnemonic)
        else:  # SOL
            wallet = await create_solana_wallet(wallet_data.name, wallet_data.mnemonic)
        
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
    
    return Balance(
        wallet_id=wallet_id,
        address=address,
        balance=str(balance),
        token_symbol=token_symbol
    )

@api_router.post("/transactions", response_model=Transaction)
async def create_transaction(tx_data: TransactionCreate):
    """Create a new transaction (in this demo, we simulate the transaction)"""
    wallet = await db.wallets.find_one({"wallet_id": tx_data.wallet_id})
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    # In a real app, we would use the wallet's private key to sign and send the transaction
    # For this demo, we'll just create a transaction record
    
    tx = Transaction(
        wallet_id=tx_data.wallet_id,
        from_address=wallet["address"],
        to_address=tx_data.to_address,
        amount=tx_data.amount,
        token_symbol=tx_data.token_symbol,
        tx_hash=f"demo_tx_{uuid.uuid4().hex}",  # This would be the actual transaction hash in production
        status="confirmed"  # For demo purposes, we mark it as confirmed immediately
    )
    
    await db.transactions.insert_one(tx.dict())
    
    return tx

@api_router.get("/transactions/{wallet_id}", response_model=List[Transaction])
async def get_wallet_transactions(wallet_id: str):
    """Get all transactions for a wallet"""
    transactions = await db.transactions.find({"wallet_id": wallet_id}).to_list(1000)
    return [Transaction(**tx) for tx in transactions]

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
