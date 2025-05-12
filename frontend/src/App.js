import { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Link, useNavigate } from "react-router-dom";
import axios from "axios";
import { Buffer } from "buffer";

// Make Buffer available globally (needed for crypto operations)
window.Buffer = Buffer;

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Language options
const languages = {
  en: {
    // Header
    wallets: "Wallets",
    aiChat: "AI Chat",
    
    // Hero
    heroTitle: "Manage Your Crypto with AI",
    heroSubtitle: "The smartest way to manage your Solana and Ethereum wallets. Let our AI assistant help you navigate the crypto world.",
    createWallet: "Create Wallet",
    chatWithAI: "Chat with AI",
    
    // Features
    smartWalletManagement: "Smart Wallet Management",
    secureWallets: "Secure Wallets",
    secureWalletsDesc: "Create and manage both Solana and Ethereum wallets with ease and security.",
    simpleTransactions: "Simple Transactions",
    simpleTransactionsDesc: "Send and receive crypto with just a few clicks or a simple voice command.",
    aiAssistant: "AI Assistant",
    aiAssistantDesc: "Get help, information, and advice from our intelligent AI assistant.",
    
    // Wallets
    yourWallets: "Your Wallets",
    createNewWallet: "Create New Wallet",
    cancel: "Cancel",
    importExistingWallet: "Import Existing Wallet",
    walletName: "Wallet Name",
    blockchain: "Blockchain",
    ethereum: "Ethereum",
    solana: "Solana",
    importWallet: "Import existing wallet",
    recoveryPhrase: "Recovery Phrase (12 or 24 words)",
    recoveryPlaceholder: "Enter recovery phrase (12 or 24 words separated by spaces)",
    importWalletBtn: "Import Wallet",
    noWallets: "You don't have any wallets yet.",
    createFirstWallet: "Create Your First Wallet",
    viewDetails: "View Details",
    useWithAI: "Use with AI",
    
    // Wallet Details
    back: "Back to Wallets",
    send: "Send",
    balance: "Balance",
    recipient: "Recipient Address",
    amount: "Amount",
    amountPlaceholder: "Amount in",
    sendTransaction: "Send Transaction",
    transactionHistory: "Transaction History",
    noTransactions: "No transactions found.",
    date: "Date",
    from: "From",
    to: "To",
    status: "Status",
    privateKeyHeading: "Private Key (Keep Secret!)",
    
    // AI Chat
    aiWalletAssistant: "AI Wallet Assistant",
    selectWallet: "Select Wallet",
    noWalletsAvailable: "No wallets available.",
    generalChat: "No wallet (general chat)",
    welcomeToAI: "Welcome to the AI Wallet Assistant!",
    askAnything: "Ask me anything about your wallets, crypto, or blockchain.",
    exampleQuestions: "Example questions:",
    exampleQuestion1: "How do I create a new Solana wallet?",
    exampleQuestion2: "What's the current balance of my wallet?",
    exampleQuestion3: "How do I send ETH to another address?",
    chatPlaceholder: "Ask anything about your wallets or crypto...",
    sendBtn: "Send",
    
    // Footer
    disclaimer: "Disclaimer: This is a demo app. Do not use for real funds.",
    copyright: "© 2025 WalletAI - Crypto Wallet Management with AI"
  },
  ru: {
    // Header
    wallets: "Кошельки",
    aiChat: "ИИ Чат",
    
    // Hero
    heroTitle: "Управляйте криптовалютой с помощью ИИ",
    heroSubtitle: "Самый умный способ управления кошельками Solana и Ethereum. Позвольте нашему ИИ-ассистенту помочь вам ориентироваться в мире криптовалют.",
    createWallet: "Создать кошелек",
    chatWithAI: "Чат с ИИ",
    
    // Features
    smartWalletManagement: "Умное управление кошельком",
    secureWallets: "Безопасные кошельки",
    secureWalletsDesc: "Создавайте и управляйте кошельками Solana и Ethereum с легкостью и безопасностью.",
    simpleTransactions: "Простые транзакции",
    simpleTransactionsDesc: "Отправляйте и получайте криптовалюту всего в несколько кликов или с помощью голосовой команды.",
    aiAssistant: "ИИ-ассистент",
    aiAssistantDesc: "Получайте помощь, информацию и советы от нашего интеллектуального ИИ-ассистента.",
    
    // Wallets
    yourWallets: "Ваши кошельки",
    createNewWallet: "Создать новый кошелек",
    cancel: "Отмена",
    importExistingWallet: "Импортировать существующий кошелек",
    walletName: "Название кошелька",
    blockchain: "Блокчейн",
    ethereum: "Ethereum",
    solana: "Solana",
    importWallet: "Импортировать существующий кошелек",
    recoveryPhrase: "Фраза восстановления (12 или 24 слова)",
    recoveryPlaceholder: "Введите фразу восстановления (12 или 24 слова, разделенные пробелами)",
    importWalletBtn: "Импортировать кошелек",
    noWallets: "У вас пока нет кошельков.",
    createFirstWallet: "Создайте свой первый кошелек",
    viewDetails: "Подробности",
    useWithAI: "Использовать с ИИ",
    
    // Wallet Details
    back: "Назад к кошелькам",
    send: "Отправить",
    balance: "Баланс",
    recipient: "Адрес получателя",
    amount: "Сумма",
    amountPlaceholder: "Сумма в",
    sendTransaction: "Отправить транзакцию",
    transactionHistory: "История транзакций",
    noTransactions: "Транзакции не найдены.",
    date: "Дата",
    from: "От",
    to: "Кому",
    status: "Статус",
    privateKeyHeading: "Приватный ключ (Держите в тайне!)",
    
    // AI Chat
    aiWalletAssistant: "ИИ-ассистент кошелька",
    selectWallet: "Выберите кошелек",
    noWalletsAvailable: "Нет доступных кошельков.",
    generalChat: "Без кошелька (общий чат)",
    welcomeToAI: "Добро пожаловать в ИИ-ассистент кошелька!",
    askAnything: "Спросите меня о чем угодно, касающемся ваших кошельков, криптовалют или блокчейна.",
    exampleQuestions: "Примеры вопросов:",
    exampleQuestion1: "Как создать новый кошелек Solana?",
    exampleQuestion2: "Какой текущий баланс моего кошелька?",
    exampleQuestion3: "Как отправить ETH на другой адрес?",
    chatPlaceholder: "Спросите что-нибудь о ваших кошельках или криптовалюте...",
    sendBtn: "Отправить",
    
    // Footer
    disclaimer: "Отказ от ответственности: Это демо-приложение. Не используйте его для реальных средств.",
    copyright: "© 2025 WalletAI - Управление криптокошельками с ИИ"
  }
};

// Header Component
const Header = ({ darkMode, toggleDarkMode, language, setLanguage }) => {
  const t = languages[language];
  
  return (
    <header className="win98-header shadow-md">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <Link to="/" className="text-2xl font-bold win98-title">WalletAI</Link>
        <nav className="flex items-center gap-4">
          <Link to="/wallets" className="win98-btn">{t.wallets}</Link>
          <Link to="/chat" className="win98-btn">{t.aiChat}</Link>
          <button 
            onClick={toggleDarkMode}
            className="win98-btn px-3"
          >
            {darkMode ? "🌙" : "☀️"}
          </button>
          <select 
            className="win98-select"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
          >
            <option value="en">English</option>
            <option value="ru">Русский</option>
          </select>
        </nav>
      </div>
    </header>
  );
};

// Hero Section for Home Page
const Hero = () => {
  return (
    <section className="py-20 bg-gradient-to-b from-primary to-primary-dark text-white">
      <div className="container mx-auto px-4 text-center">
        <h1 className="text-5xl font-bold mb-6">Manage Your Crypto with AI</h1>
        <p className="text-xl mb-10 max-w-2xl mx-auto">
          The smartest way to manage your Solana and Ethereum wallets. Let our AI assistant help you navigate the crypto world.
        </p>
        <div className="flex gap-4 justify-center">
          <Link to="/wallets" className="btn btn-secondary btn-lg">Create Wallet</Link>
          <Link to="/chat" className="btn btn-outline btn-lg">Chat with AI</Link>
        </div>
      </div>
    </section>
  );
};

// Features Section
const Features = () => {
  return (
    <section className="py-16 bg-base-100">
      <div className="container mx-auto px-4">
        <h2 className="text-3xl font-bold text-center mb-12">Smart Wallet Management</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="card bg-base-200 shadow-xl">
            <div className="card-body">
              <div className="text-4xl text-primary mb-4">🔐</div>
              <h3 className="card-title text-xl mb-2">Secure Wallets</h3>
              <p>Create and manage both Solana and Ethereum wallets with ease and security.</p>
            </div>
          </div>
          <div className="card bg-base-200 shadow-xl">
            <div className="card-body">
              <div className="text-4xl text-primary mb-4">💸</div>
              <h3 className="card-title text-xl mb-2">Simple Transactions</h3>
              <p>Send and receive crypto with just a few clicks or a simple voice command.</p>
            </div>
          </div>
          <div className="card bg-base-200 shadow-xl">
            <div className="card-body">
              <div className="text-4xl text-primary mb-4">🤖</div>
              <h3 className="card-title text-xl mb-2">AI Assistant</h3>
              <p>Get help, information, and advice from our intelligent AI assistant.</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

// Home Page
const Home = () => {
  return (
    <div>
      <Hero />
      <Features />
    </div>
  );
};

// Wallets Page
const Wallets = () => {
  const [wallets, setWallets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newWalletName, setNewWalletName] = useState("");
  const [newWalletChain, setNewWalletChain] = useState("ETH");
  const [importMode, setImportMode] = useState(false);
  const [mnemonic, setMnemonic] = useState("");
  
  useEffect(() => {
    fetchWallets();
  }, []);
  
  const fetchWallets = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/wallets`);
      setWallets(response.data);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching wallets:", err);
      setLoading(false);
    }
  };
  
  const createWallet = async (e) => {
    e.preventDefault();
    
    try {
      const walletData = {
        name: newWalletName,
        chain_type: newWalletChain,
      };
      
      if (importMode && mnemonic) {
        walletData.mnemonic = mnemonic;
      }
      
      const response = await axios.post(`${API}/wallets`, walletData);
      
      // Add new wallet to list
      setWallets([...wallets, response.data]);
      
      // Reset form
      setNewWalletName("");
      setMnemonic("");
      setShowCreateForm(false);
    } catch (err) {
      console.error("Error creating wallet:", err);
      alert("Failed to create wallet. Please try again.");
    }
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Your Wallets</h1>
        <button 
          className="btn btn-primary"
          onClick={() => setShowCreateForm(!showCreateForm)}
        >
          {showCreateForm ? "Cancel" : "Create New Wallet"}
        </button>
      </div>
      
      {showCreateForm && (
        <div className="card bg-base-200 shadow-xl mb-8">
          <div className="card-body">
            <h2 className="card-title">{importMode ? "Import Existing Wallet" : "Create New Wallet"}</h2>
            <form onSubmit={createWallet}>
              <div className="form-control mb-4">
                <label className="label">
                  <span className="label-text">Wallet Name</span>
                </label>
                <input 
                  type="text" 
                  value={newWalletName}
                  onChange={(e) => setNewWalletName(e.target.value)}
                  className="input input-bordered" 
                  placeholder="My Wallet"
                  required
                />
              </div>
              
              <div className="form-control mb-4">
                <label className="label">
                  <span className="label-text">Blockchain</span>
                </label>
                <select 
                  className="select select-bordered w-full"
                  value={newWalletChain}
                  onChange={(e) => setNewWalletChain(e.target.value)}
                >
                  <option value="ETH">Ethereum</option>
                  <option value="SOL">Solana</option>
                </select>
              </div>
              
              <div className="form-control mb-6">
                <label className="label cursor-pointer">
                  <span className="label-text">Import existing wallet</span>
                  <input 
                    type="checkbox" 
                    className="toggle"
                    checked={importMode}
                    onChange={() => setImportMode(!importMode)}
                  />
                </label>
              </div>
              
              {importMode && (
                <div className="form-control mb-4">
                  <label className="label">
                    <span className="label-text">Recovery Phrase (12 or 24 words)</span>
                  </label>
                  <textarea 
                    className="textarea textarea-bordered h-24"
                    value={mnemonic}
                    onChange={(e) => setMnemonic(e.target.value)}
                    placeholder="Enter recovery phrase (12 or 24 words separated by spaces)"
                    required
                  ></textarea>
                </div>
              )}
              
              <div className="card-actions justify-end">
                <button type="submit" className="btn btn-primary">
                  {importMode ? "Import Wallet" : "Create Wallet"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      
      {loading ? (
        <div className="flex justify-center py-12">
          <span className="loading loading-spinner loading-lg"></span>
        </div>
      ) : wallets.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-lg mb-4">You don't have any wallets yet.</p>
          <button className="btn btn-primary" onClick={() => setShowCreateForm(true)}>
            Create Your First Wallet
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {wallets.map((wallet) => (
            <WalletCard key={wallet.wallet_id} wallet={wallet} />
          ))}
        </div>
      )}
    </div>
  );
};

// Wallet Card Component
const WalletCard = ({ wallet }) => {
  const [balance, setBalance] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  
  useEffect(() => {
    fetchBalance();
  }, []);
  
  const fetchBalance = async () => {
    try {
      const response = await axios.get(`${API}/wallets/${wallet.wallet_id}/balance`);
      setBalance(response.data);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching balance:", err);
      setLoading(false);
    }
  };
  
  return (
    <div className="card bg-base-200 shadow-xl">
      <div className="card-body">
        <h2 className="card-title">
          {wallet.name}
          <div className="badge badge-secondary">{wallet.chain_type}</div>
        </h2>
        
        <p className="text-sm font-mono overflow-hidden text-ellipsis">
          {truncateAddress(wallet.address)}
        </p>
        
        <div className="mt-4">
          <h3 className="text-sm font-semibold mb-1">Balance:</h3>
          {loading ? (
            <span className="loading loading-spinner loading-sm"></span>
          ) : (
            <p className="text-xl font-bold">{balance?.balance} {balance?.token_symbol}</p>
          )}
        </div>
        
        <div className="card-actions justify-end mt-4">
          <button 
            className="btn btn-sm btn-outline"
            onClick={() => navigate(`/wallet/${wallet.wallet_id}`)}
          >
            View Details
          </button>
          <button 
            className="btn btn-sm btn-primary"
            onClick={() => navigate(`/chat?wallet=${wallet.wallet_id}`)}
          >
            Use with AI
          </button>
        </div>
      </div>
    </div>
  );
};

// Wallet Detail Page
const WalletDetail = () => {
  const navigate = useNavigate();
  const [wallet, setWallet] = useState(null);
  const [balance, setBalance] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showSendForm, setShowSendForm] = useState(false);
  const [recipient, setRecipient] = useState("");
  const [amount, setAmount] = useState("");
  
  // Get wallet ID from URL
  const walletId = window.location.pathname.split('/').pop();
  
  useEffect(() => {
    fetchWalletData();
  }, [walletId]);
  
  const fetchWalletData = async () => {
    try {
      setLoading(true);
      
      // Fetch wallet details
      const walletResponse = await axios.get(`${API}/wallets/${walletId}`);
      setWallet(walletResponse.data);
      
      // Fetch balance
      const balanceResponse = await axios.get(`${API}/wallets/${walletId}/balance`);
      setBalance(balanceResponse.data);
      
      // Fetch transactions
      const txResponse = await axios.get(`${API}/transactions/${walletId}`);
      setTransactions(txResponse.data);
      
      setLoading(false);
    } catch (err) {
      console.error("Error fetching wallet data:", err);
      setLoading(false);
      // Redirect back to wallets page if wallet not found
      if (err.response?.status === 404) {
        navigate('/wallets');
      }
    }
  };
  
  const sendTransaction = async (e) => {
    e.preventDefault();
    
    try {
      const txData = {
        wallet_id: walletId,
        to_address: recipient,
        amount: amount,
        token_symbol: wallet.chain_type === "ETH" ? "ETH" : "SOL"
      };
      
      await axios.post(`${API}/transactions`, txData);
      
      // Refresh data
      fetchWalletData();
      setShowSendForm(false);
      setRecipient("");
      setAmount("");
    } catch (err) {
      console.error("Error sending transaction:", err);
      alert("Failed to send transaction. Please try again.");
    }
  };
  
  if (loading && !wallet) {
    return (
      <div className="container mx-auto px-4 py-12 flex justify-center">
        <span className="loading loading-spinner loading-lg"></span>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <button onClick={() => navigate('/wallets')} className="btn btn-ghost mb-4">
          ← Back to Wallets
        </button>
        
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">
              {wallet?.name}
              <span className="ml-2 badge badge-secondary">{wallet?.chain_type}</span>
            </h1>
            <p className="font-mono text-sm mt-2">{wallet?.address}</p>
          </div>
          
          <button 
            className="btn btn-primary"
            onClick={() => setShowSendForm(!showSendForm)}
          >
            Send {wallet?.chain_type === "ETH" ? "ETH" : "SOL"}
          </button>
        </div>
      </div>
      
      {/* Balance Card */}
      <div className="card bg-base-200 shadow-xl mb-8">
        <div className="card-body">
          <h2 className="card-title">Balance</h2>
          {balance ? (
            <p className="text-3xl font-bold">{balance.balance} {balance.token_symbol}</p>
          ) : (
            <span className="loading loading-spinner loading-md"></span>
          )}
        </div>
      </div>
      
      {/* Send Form */}
      {showSendForm && (
        <div className="card bg-base-200 shadow-xl mb-8">
          <div className="card-body">
            <h2 className="card-title">Send {wallet?.chain_type === "ETH" ? "ETH" : "SOL"}</h2>
            <form onSubmit={sendTransaction}>
              <div className="form-control mb-4">
                <label className="label">
                  <span className="label-text">Recipient Address</span>
                </label>
                <input 
                  type="text" 
                  value={recipient}
                  onChange={(e) => setRecipient(e.target.value)}
                  className="input input-bordered" 
                  placeholder={wallet?.chain_type === "ETH" ? "0x..." : "..."}
                  required
                />
              </div>
              
              <div className="form-control mb-4">
                <label className="label">
                  <span className="label-text">Amount</span>
                </label>
                <input 
                  type="number" 
                  step="0.000001"
                  min="0"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="input input-bordered" 
                  placeholder={`Amount in ${wallet?.chain_type === "ETH" ? "ETH" : "SOL"}`}
                  required
                />
              </div>
              
              <div className="card-actions justify-end">
                <button type="button" onClick={() => setShowSendForm(false)} className="btn btn-ghost">
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Send Transaction
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      
      {/* Transactions */}
      <div className="card bg-base-200 shadow-xl">
        <div className="card-body">
          <h2 className="card-title mb-4">Transaction History</h2>
          
          {loading ? (
            <div className="flex justify-center py-4">
              <span className="loading loading-spinner loading-md"></span>
            </div>
          ) : transactions.length === 0 ? (
            <p className="text-center py-4">No transactions found.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="table table-zebra">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>From</th>
                    <th>To</th>
                    <th>Amount</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.map((tx) => (
                    <tr key={tx.tx_id}>
                      <td>{new Date(tx.timestamp).toLocaleString()}</td>
                      <td className="font-mono">{truncateAddress(tx.from_address)}</td>
                      <td className="font-mono">{truncateAddress(tx.to_address)}</td>
                      <td>{tx.amount} {tx.token_symbol}</td>
                      <td>
                        <span className={`badge ${
                          tx.status === "confirmed" ? "badge-success" : 
                          tx.status === "pending" ? "badge-warning" : "badge-error"
                        }`}>
                          {tx.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// AI Chat Page
const AIChat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [chatId, setChatId] = useState(null);
  const [selectedWallet, setSelectedWallet] = useState(null);
  const [wallets, setWallets] = useState([]);
  const [walletsLoading, setWalletsLoading] = useState(true);
  
  // Get wallet ID from URL if present
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const walletId = params.get('wallet');
    if (walletId) {
      setSelectedWallet(walletId);
    }
    
    fetchWallets();
  }, []);
  
  const fetchWallets = async () => {
    try {
      setWalletsLoading(true);
      const response = await axios.get(`${API}/wallets`);
      setWallets(response.data);
      setWalletsLoading(false);
    } catch (err) {
      console.error("Error fetching wallets:", err);
      setWalletsLoading(false);
    }
  };
  
  const sendMessage = async (e) => {
    e.preventDefault();
    
    if (!input.trim()) return;
    
    // Add user message to chat
    const userMessage = {
      role: "user",
      content: input,
    };
    
    setMessages([...messages, userMessage]);
    setInput("");
    setLoading(true);
    
    try {
      const response = await axios.post(`${API}/ai/chat`, {
        message: input,
        chat_id: chatId,
        wallet_id: selectedWallet
      });
      
      // Save chat ID if new
      if (!chatId) {
        setChatId(response.data.chat_id);
      }
      
      // Add AI response to chat
      const aiMessage = {
        role: "assistant",
        content: response.data.response,
      };
      
      setMessages([...messages, userMessage, aiMessage]);
      
      // Handle action if present
      if (response.data.action) {
        handleAction(response.data.action);
      }
    } catch (err) {
      console.error("Error sending message:", err);
      
      // Add error message
      const errorMessage = {
        role: "assistant",
        content: "Sorry, there was an error processing your request. Please try again.",
      };
      
      setMessages([...messages, userMessage, errorMessage]);
    }
    
    setLoading(false);
  };
  
  const handleAction = (action) => {
    // In a real app, we would implement handling of actions here
    console.log("AI suggested action:", action);
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">AI Wallet Assistant</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Sidebar with wallet selection */}
        <div className="lg:col-span-1">
          <div className="card bg-base-200 shadow-xl">
            <div className="card-body">
              <h2 className="card-title">Select Wallet</h2>
              
              {walletsLoading ? (
                <div className="flex justify-center py-4">
                  <span className="loading loading-spinner loading-md"></span>
                </div>
              ) : wallets.length === 0 ? (
                <div className="py-2">
                  <p className="mb-2">No wallets available.</p>
                  <Link to="/wallets" className="btn btn-sm btn-primary">Create Wallet</Link>
                </div>
              ) : (
                <div className="flex flex-col gap-2 mt-2">
                  <div className="form-control">
                    <label className="label cursor-pointer">
                      <span className="label-text">No wallet (general chat)</span>
                      <input 
                        type="radio" 
                        name="wallet" 
                        className="radio" 
                        checked={selectedWallet === null}
                        onChange={() => setSelectedWallet(null)}
                      />
                    </label>
                  </div>
                  
                  {wallets.map((wallet) => (
                    <div key={wallet.wallet_id} className="form-control">
                      <label className="label cursor-pointer">
                        <span className="label-text">
                          {wallet.name} ({wallet.chain_type})
                        </span>
                        <input 
                          type="radio" 
                          name="wallet" 
                          className="radio" 
                          checked={selectedWallet === wallet.wallet_id}
                          onChange={() => setSelectedWallet(wallet.wallet_id)}
                        />
                      </label>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
        
        {/* Chat interface */}
        <div className="lg:col-span-3">
          <div className="card bg-base-200 shadow-xl">
            <div className="card-body">
              <div className="chat-container h-96 overflow-y-auto mb-4 p-4 bg-base-300 rounded-lg">
                {messages.length === 0 ? (
                  <div className="text-center py-12">
                    <h3 className="text-xl font-semibold mb-2">Welcome to the AI Wallet Assistant!</h3>
                    <p className="mb-4">Ask me anything about your wallets, crypto, or blockchain.</p>
                    <p className="text-sm">Example questions:</p>
                    <ul className="text-sm list-disc list-inside">
                      <li className="cursor-pointer hover:text-primary" onClick={() => setInput("How do I create a new Solana wallet?")}>
                        How do I create a new Solana wallet?
                      </li>
                      <li className="cursor-pointer hover:text-primary" onClick={() => setInput("What's the current balance of my wallet?")}>
                        What's the current balance of my wallet?
                      </li>
                      <li className="cursor-pointer hover:text-primary" onClick={() => setInput("How do I send ETH to another address?")}>
                        How do I send ETH to another address?
                      </li>
                    </ul>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {messages.map((msg, index) => (
                      <div 
                        key={index} 
                        className={`chat ${msg.role === "user" ? "chat-end" : "chat-start"}`}
                      >
                        <div className={`chat-bubble ${msg.role === "user" ? "chat-bubble-primary" : "chat-bubble-secondary"}`}>
                          {msg.content}
                        </div>
                      </div>
                    ))}
                    
                    {loading && (
                      <div className="chat chat-start">
                        <div className="chat-bubble chat-bubble-secondary">
                          <span className="loading loading-dots loading-sm"></span>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
              
              <form onSubmit={sendMessage} className="flex gap-2">
                <input 
                  type="text" 
                  className="input input-bordered flex-1" 
                  placeholder="Ask anything about your wallets or crypto..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  disabled={loading}
                />
                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={loading}
                >
                  {loading ? <span className="loading loading-spinner loading-sm"></span> : "Send"}
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Footer Component
const Footer = () => {
  return (
    <footer className="bg-base-300 py-8">
      <div className="container mx-auto px-4 text-center">
        <p className="mb-2">© 2025 WalletAI - Crypto Wallet Management with AI</p>
        <p className="text-sm">
          Disclaimer: This is a demo app. Do not use for real funds.
        </p>
      </div>
    </footer>
  );
};

// Main App Component
function App() {
  const [darkMode, setDarkMode] = useState(true);
  
  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  useEffect(() => {
    // Apply theme to html element
    document.documentElement.setAttribute("data-theme", darkMode ? "dark" : "light");
  }, [darkMode]);

  return (
    <div className={`App min-h-screen flex flex-col`}>
      <BrowserRouter>
        <Header darkMode={darkMode} toggleDarkMode={toggleDarkMode} />
        <main className="flex-grow">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/wallets" element={<Wallets />} />
            <Route path="/wallet/:id" element={<WalletDetail />} />
            <Route path="/chat" element={<AIChat />} />
          </Routes>
        </main>
        <Footer />
      </BrowserRouter>
    </div>
  );
}

export default App;
