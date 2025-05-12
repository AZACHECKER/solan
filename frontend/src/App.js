import { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Link, useNavigate } from "react-router-dom";
import axios from "axios";
import { Buffer } from "buffer";
import AIChat from "./AIChat";

// Make Buffer available globally (needed for crypto operations)
window.Buffer = Buffer;

// API endpoint
const API = process.env.REACT_APP_API_URL || "http://localhost:5000";

// Language translations
const languages = {
  en: {
    // Common
    loading: "Loading...",
    error: "Error",
    success: "Success",
    cancel: "Cancel",
    save: "Save",
    edit: "Edit",
    delete: "Delete",
    confirm: "Confirm",
    back: "Back",
    next: "Next",
    
    // Navigation
    dashboard: "Dashboard",
    wallets: "Wallets",
    transactions: "Transactions",
    settings: "Settings",
    
    // Wallet management
    createWallet: "Create Wallet",
    importWallet: "Import Wallet",
    walletName: "Wallet Name",
    walletAddress: "Wallet Address",
    walletBalance: "Balance",
    walletType: "Wallet Type",
    selectChain: "Select Chain",
    enterWalletName: "Enter wallet name",
    
    // Transaction related
    send: "Send",
    receive: "Receive",
    amount: "Amount",
    recipient: "Recipient",
    sender: "Sender",
    fee: "Fee",
    total: "Total",
    memo: "Memo",
    status: "Status",
    date: "Date",
    
    // AI Chat
    aiChat: "AI Assistant",
    selectWallet: "Select Wallet",
    generalChat: "General Chat",
    chatPlaceholder: "Ask me anything about crypto...",
    sendBtn: "Send",
    welcomeToAI: "Welcome to Crypto Terminal AI",
    askAnything: "Ask me anything about crypto, wallets, or transactions",
    exampleQuestions: "Example questions:",
    exampleQuestion1: "How do I create a new wallet?",
    exampleQuestion2: "What's my current balance?",
    exampleQuestion3: "How do I send tokens?",
    noWalletsAvailable: "No wallets available",
    aiWalletAssistant: "AI Wallet Assistant",
    
    // Errors
    walletExists: "Wallet with this name already exists",
    invalidAddress: "Invalid wallet address",
    insufficientFunds: "Insufficient funds",
    networkError: "Network error. Please try again",
    
    // Success messages
    walletCreated: "Wallet created successfully",
    walletImported: "Wallet imported successfully",
    transactionSent: "Transaction sent successfully",
    
    // Wallet types
    ethereum: "Ethereum",
    solana: "Solana",
    tron: "Tron",
    
    // Additional fields
    address: "Address",
    balance: "Balance",
    tokens: "Tokens",
    sponsorAddress: "Sponsor",
  },
  es: {
    // Common
    loading: "Cargando...",
    error: "Error",
    success: "Éxito",
    cancel: "Cancelar",
    save: "Guardar",
    edit: "Editar",
    delete: "Eliminar",
    confirm: "Confirmar",
    back: "Atrás",
    next: "Siguiente",
    
    // Navigation
    dashboard: "Panel",
    wallets: "Billeteras",
    transactions: "Transacciones",
    settings: "Ajustes",
    
    // Wallet management
    createWallet: "Crear Billetera",
    importWallet: "Importar Billetera",
    walletName: "Nombre de Billetera",
    walletAddress: "Dirección de Billetera",
    walletBalance: "Saldo",
    walletType: "Tipo de Billetera",
    selectChain: "Seleccionar Cadena",
    enterWalletName: "Ingrese nombre de billetera",
    
    // Transaction related
    send: "Enviar",
    receive: "Recibir",
    amount: "Cantidad",
    recipient: "Destinatario",
    sender: "Remitente",
    fee: "Comisión",
    total: "Total",
    memo: "Nota",
    status: "Estado",
    date: "Fecha",
    
    // AI Chat
    aiChat: "Asistente IA",
    selectWallet: "Seleccionar Billetera",
    generalChat: "Chat General",
    chatPlaceholder: "Pregúntame cualquier cosa sobre crypto...",
    sendBtn: "Enviar",
    welcomeToAI: "Bienvenido a Crypto Terminal IA",
    askAnything: "Pregúntame cualquier cosa sobre crypto, billeteras o transacciones",
    exampleQuestions: "Preguntas de ejemplo:",
    exampleQuestion1: "¿Cómo creo una nueva billetera?",
    exampleQuestion2: "¿Cuál es mi saldo actual?",
    exampleQuestion3: "¿Cómo envío tokens?",
    noWalletsAvailable: "No hay billeteras disponibles",
    aiWalletAssistant: "Asistente de Billetera IA",
    
    // Errors
    walletExists: "Ya existe una billetera con este nombre",
    invalidAddress: "Dirección de billetera inválida",
    insufficientFunds: "Fondos insuficientes",
    networkError: "Error de red. Por favor intente de nuevo",
    
    // Success messages
    walletCreated: "Billetera creada exitosamente",
    walletImported: "Billetera importada exitosamente",
    transactionSent: "Transacción enviada exitosamente",
    
    // Wallet types
    ethereum: "Ethereum",
    solana: "Solana",
    tron: "Tron",
    
    // Additional fields
    address: "Dirección",
    balance: "Saldo",
    tokens: "Tokens",
    sponsorAddress: "Patrocinador",
  }
};

// Export languages for use in other components
export { languages, API };

// App Component
const App = () => {
  const [language, setLanguage] = useState("en");
  
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-900 text-gray-100">
        <Routes>
          <Route path="/" element={<AIChat language={language} />} />
          <Route path="/wallets" element={<div>Wallets page (TODO)</div>} />
          <Route path="/wallet/:id" element={<div>Wallet details page (TODO)</div>} />
        </Routes>
      </div>
    </BrowserRouter>
  );
};

export default App;