import { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from './AuthContext';

const AppContext = createContext();

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp deve ser usado dentro de um AppProvider');
  }
  return context;
};

export const AppProvider = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const [accounts, setAccounts] = useState([]);
  const [creditCards, setCreditCards] = useState([]);
  const [categories, setCategories] = useState({ income: [], expense: [] });
  const [transactions, setTransactions] = useState([]);
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(false);

  // Carregar dados quando o usuário estiver autenticado
  useEffect(() => {
    if (isAuthenticated) {
      loadInitialData();
    } else {
      // Limpar dados quando não autenticado
      setAccounts([]);
      setCreditCards([]);
      setCategories({ income: [], expense: [] });
      setTransactions([]);
      setDashboardData(null);
    }
  }, [isAuthenticated]);

  const loadInitialData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        loadAccounts(),
        loadCreditCards(),
        loadCategories(),
        loadDashboard(),
      ]);
    } catch (error) {
      console.error('Erro ao carregar dados iniciais:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadAccounts = async () => {
    try {
      const response = await fetch('/api/accounts');
      if (response.ok) {
        const data = await response.json();
        setAccounts(data.accounts);
      }
    } catch (error) {
      console.error('Erro ao carregar contas:', error);
    }
  };

  const loadCreditCards = async () => {
    try {
      const response = await fetch('/api/credit-cards');
      if (response.ok) {
        const data = await response.json();
        setCreditCards(data.credit_cards);
      }
    } catch (error) {
      console.error('Erro ao carregar cartões:', error);
    }
  };

  const loadCategories = async () => {
    try {
      const response = await fetch('/api/categories');
      if (response.ok) {
        const data = await response.json();
        setCategories({
          income: data.income_categories,
          expense: data.expense_categories,
        });
      }
    } catch (error) {
      console.error('Erro ao carregar categorias:', error);
    }
  };

  const loadTransactions = async (filters = {}) => {
    try {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });

      const response = await fetch(`/api/transactions?${params}`);
      if (response.ok) {
        const data = await response.json();
        setTransactions(data.transactions);
        return data;
      }
    } catch (error) {
      console.error('Erro ao carregar transações:', error);
    }
  };

  const loadDashboard = async (filters = {}) => {
    try {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });

      const response = await fetch(`/api/dashboard?${params}`);
      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
        return data;
      }
    } catch (error) {
      console.error('Erro ao carregar dashboard:', error);
    }
  };

  const createTransaction = async (transactionData) => {
    try {
      const response = await fetch('/api/transactions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(transactionData),
      });

      const data = await response.json();

      if (data.success) {
        // Recarregar dados após criar transação
        await Promise.all([
          loadAccounts(),
          loadCreditCards(),
          loadDashboard(),
        ]);
        return { success: true, data: data.transaction };
      } else {
        return { success: false, message: data.error };
      }
    } catch (error) {
      console.error('Erro ao criar transação:', error);
      return { success: false, message: 'Erro de conexão' };
    }
  };

  const deleteTransaction = async (transactionId) => {
    try {
      const response = await fetch(`/api/transactions/${transactionId}`, {
        method: 'DELETE',
      });

      const data = await response.json();

      if (data.success) {
        // Recarregar dados após excluir transação
        await Promise.all([
          loadAccounts(),
          loadCreditCards(),
          loadDashboard(),
        ]);
        return { success: true };
      } else {
        return { success: false, message: data.error };
      }
    } catch (error) {
      console.error('Erro ao excluir transação:', error);
      return { success: false, message: 'Erro de conexão' };
    }
  };

  const updateAccount = async (accountId, accountData) => {
    try {
      const response = await fetch(`/api/accounts/${accountId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(accountData),
      });

      const data = await response.json();

      if (data.success) {
        await loadAccounts();
        await loadDashboard();
        return { success: true, data: data.account };
      } else {
        return { success: false, message: data.error };
      }
    } catch (error) {
      console.error('Erro ao atualizar conta:', error);
      return { success: false, message: 'Erro de conexão' };
    }
  };

  const createCreditCard = async (cardData) => {
    try {
      const response = await fetch('/api/credit-cards', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(cardData),
      });

      const data = await response.json();

      if (data.success) {
        await loadCreditCards();
        return { success: true, data: data.credit_card };
      } else {
        return { success: false, message: data.error };
      }
    } catch (error) {
      console.error('Erro ao criar cartão:', error);
      return { success: false, message: 'Erro de conexão' };
    }
  };

  const createCategory = async (categoryData) => {
    try {
      const response = await fetch('/api/categories', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(categoryData),
      });

      const data = await response.json();

      if (data.success) {
        await loadCategories();
        return { success: true, data: data.category };
      } else {
        return { success: false, message: data.error };
      }
    } catch (error) {
      console.error('Erro ao criar categoria:', error);
      return { success: false, message: 'Erro de conexão' };
    }
  };

  const value = {
    accounts,
    creditCards,
    categories,
    transactions,
    dashboardData,
    loading,
    loadTransactions,
    loadDashboard,
    createTransaction,
    deleteTransaction,
    updateAccount,
    createCreditCard,
    createCategory,
    refreshData: loadInitialData,
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
};

