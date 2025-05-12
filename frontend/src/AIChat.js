// AI Chat Page
const AIChat = ({ language }) => {
  const t = languages[language];
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [chatId, setChatId] = useState(null);
  const [selectedWallet, setSelectedWallet] = useState(null);
  const [selectedWalletData, setSelectedWalletData] = useState(null);
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
  
  // Fetch selected wallet data when wallet changes
  useEffect(() => {
    if (selectedWallet) {
      fetchWalletDetails(selectedWallet);
    } else {
      setSelectedWalletData(null);
    }
  }, [selectedWallet]);
  
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
  
  const fetchWalletDetails = async (walletId) => {
    try {
      const walletResponse = await axios.get(`${API}/wallets/${walletId}`);
      const balanceResponse = await axios.get(`${API}/wallets/${walletId}/balance`);
      
      let tokens = [];
      try {
        const tokensResponse = await axios.get(`${API}/wallets/${walletId}/tokens`);
        tokens = tokensResponse.data;
      } catch (err) {
        console.error("Error fetching tokens:", err);
      }
      
      setSelectedWalletData({
        ...walletResponse.data,
        balance: balanceResponse.data.balance,
        token_symbol: balanceResponse.data.token_symbol,
        tokens
      });
    } catch (err) {
      console.error("Error fetching wallet details:", err);
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
    
    // Example action handling
    if (action.type === "CREATE_WALLET") {
      // Redirect to wallet creation page
      window.location.href = "/wallets";
    } else if (action.type === "CHECK_BALANCE" && action.wallet_id) {
      // Refresh wallet data
      fetchWalletDetails(action.wallet_id);
    } else if (action.type === "SEND_TRANSACTION" && action.wallet_id) {
      // Redirect to wallet details page for transaction
      window.location.href = `/wallet/${action.wallet_id}`;
    } else if (action.type === "UPDATE_OWNER" && action.wallet_id) {
      // Redirect to wallet details page for owner update
      window.location.href = `/wallet/${action.wallet_id}`;
    } else if (action.type === "SET_SPONSOR" && action.wallet_id) {
      // Redirect to wallet details page for sponsor setting
      window.location.href = `/wallet/${action.wallet_id}`;
    } else if (action.type === "BUNDLE_TRANSACTION" && action.wallet_id) {
      // Redirect to wallet details page for bundle creation
      window.location.href = `/wallet/${action.wallet_id}`;
    }
  };
  
  // Get chain color styling
  const getChainColor = (chainType) => {
    if (chainType === "ETH") return "var(--console-eth)";
    if (chainType === "SOL") return "var(--console-sol)";
    if (chainType === "TRON") return "var(--console-tron)";
    return "var(--console-text)";
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="console-window">
        <div className="console-window-title">
          <span>[root@crypto-terminal] ~$ ./ai-assistant.sh</span>
        </div>
        <div className="console-window-content p-4">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            {/* Sidebar with wallet selection */}
            <div className="lg:col-span-1">
              <div className="console-card h-full">
                <div className="console-card-title">{t.selectWallet}</div>
                <div className="console-card-content">
                  {walletsLoading ? (
                    <div className="flex justify-center py-4">
                      <div className="console-loader"></div>
                    </div>
                  ) : wallets.length === 0 ? (
                    <div className="py-2">
                      <p className="mb-2">{t.noWalletsAvailable}</p>
                      <Link to="/wallets" className="console-btn console-btn-sm console-btn-primary">{t.createWallet}</Link>
                    </div>
                  ) : (
                    <div className="flex flex-col gap-2 mt-2">
                      <div className="console-radio">
                        <label className="console-label cursor-pointer">
                          <input 
                            type="radio" 
                            name="wallet" 
                            className="console-radio-input" 
                            checked={selectedWallet === null}
                            onChange={() => setSelectedWallet(null)}
                          />
                          <span className="ml-2">{t.generalChat}</span>
                        </label>
                      </div>
                      
                      {wallets.map((wallet) => (
                        <div key={wallet.wallet_id} className="console-radio">
                          <label className="console-label cursor-pointer">
                            <input 
                              type="radio" 
                              name="wallet" 
                              className="console-radio-input" 
                              checked={selectedWallet === wallet.wallet_id}
                              onChange={() => setSelectedWallet(wallet.wallet_id)}
                            />
                            <span className="ml-2">
                              {wallet.name} <span className="console-badge" style={{
                                backgroundColor: getChainColor(wallet.chain_type),
                                padding: '0 4px',
                                fontSize: '0.7rem'
                              }}>{wallet.chain_type}</span>
                            </span>
                          </label>
                        </div>
                      ))}
                    </div>
                  )}
                  
                  {/* Selected wallet info */}
                  {selectedWalletData && (
                    <div className="mt-6 p-2 border border-[#297fb8] rounded bg-[#0c3b59]">
                      <h4 className="text-[#36f9f6] text-sm font-bold mb-2">{selectedWalletData.name}</h4>
                      <p className="text-sm mb-1 truncate"><span className="text-[#4ba3c3]">{t.address}:</span> {selectedWalletData.address}</p>
                      <p className="text-sm mb-1"><span className="text-[#4ba3c3]">{t.balance}:</span> {selectedWalletData.balance} {selectedWalletData.token_symbol}</p>
                      
                      {selectedWalletData.tokens && selectedWalletData.tokens.length > 0 && (
                        <div className="mt-2">
                          <p className="text-sm text-[#4ba3c3] mb-1">{t.tokens}:</p>
                          <div className="console-inset p-1 max-h-[100px] overflow-y-auto">
                            {selectedWalletData.tokens.map((token, idx) => (
                              <div key={idx} className="flex justify-between text-xs p-1">
                                <span>{token.symbol}</span>
                                <span>{token.balance}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {selectedWalletData.sponsor_address && (
                        <p className="text-sm mt-2">
                          <span className="text-[#feca57]">{t.sponsorAddress}:</span> 
                          <span className="ml-1 truncate">{selectedWalletData.sponsor_address}</span>
                        </p>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
            
            {/* Chat interface */}
            <div className="lg:col-span-3">
              <div className="console-card h-full">
                <div className="console-card-title">{t.aiChat}</div>
                <div className="console-card-content">
                  <div className="console-inset h-96 overflow-y-auto mb-4 p-4 bg-[#0a1929]">
                    {messages.length === 0 ? (
                      <div className="text-center py-12">
                        <h3 className="text-xl font-semibold mb-2 text-[#36f9f6]">{t.welcomeToAI}</h3>
                        <p className="mb-4 text-[#7df9ff]">{t.askAnything}</p>
                        <p className="text-sm text-[#4ba3c3]">{t.exampleQuestions}</p>
                        <ul className="text-sm list-disc list-inside text-[#7df9ff]">
                          <li className="cursor-pointer hover:text-[#36f9f6]" onClick={() => setInput(t.exampleQuestion1)}>
                            {t.exampleQuestion1}
                          </li>
                          <li className="cursor-pointer hover:text-[#36f9f6]" onClick={() => setInput(t.exampleQuestion2)}>
                            {t.exampleQuestion2}
                          </li>
                          <li className="cursor-pointer hover:text-[#36f9f6]" onClick={() => setInput(t.exampleQuestion3)}>
                            {t.exampleQuestion3}
                          </li>
                        </ul>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {messages.map((msg, index) => (
                          <div 
                            key={index} 
                            className={`console-message ${msg.role === "user" ? "console-message-user" : "console-message-assistant"}`}
                          >
                            <div className="console-message-content">
                              {msg.content}
                            </div>
                          </div>
                        ))}
                        
                        {loading && (
                          <div className="console-message console-message-assistant">
                            <div className="console-message-content">
                              <div className="console-loader console-loader-sm"></div>
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  
                  <form onSubmit={sendMessage} className="flex gap-2">
                    <input 
                      type="text" 
                      className="console-input flex-1" 
                      placeholder={t.chatPlaceholder}
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      disabled={loading}
                    />
                    <button 
                      type="submit" 
                      className="console-btn console-btn-primary"
                      disabled={loading}
                    >
                      {loading ? <div className="console-loader console-loader-sm"></div> : t.sendBtn}
                    </button>
                  </form>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIChat;