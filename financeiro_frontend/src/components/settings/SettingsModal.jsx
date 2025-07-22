import React, { useState, useEffect } from 'react';
import { X, Settings, Save, Plus, Trash2 } from 'lucide-react';

const SettingsModal = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState('accounts');
  const [accounts, setAccounts] = useState([]);
  const [creditCards, setCreditCards] = useState([]);
  const [categories, setCategories] = useState({ income: [], expense: [] });
  const [loading, setLoading] = useState(false);
  const [newCategory, setNewCategory] = useState({ name: '', type: 'expense' });

  useEffect(() => {
    if (isOpen) {
      loadData();
    }
  }, [isOpen]);

  const loadData = async () => {
    setLoading(true);
    try {
      // Carregar contas
      const accountsRes = await fetch('/api/accounts');
      if (accountsRes.ok) {
        const accountsData = await accountsRes.json();
        setAccounts(accountsData.accounts || []);
      }

      // Carregar cartões
      const cardsRes = await fetch('/api/credit-cards');
      if (cardsRes.ok) {
        const cardsData = await cardsRes.json();
        setCreditCards(cardsData.credit_cards || []);
      }

      // Carregar categorias
      const categoriesRes = await fetch('/api/categories');
      if (categoriesRes.ok) {
        const categoriesData = await categoriesRes.json();
        const income = categoriesData.categories?.filter(c => c.type === 'income') || [];
        const expense = categoriesData.categories?.filter(c => c.type === 'expense') || [];
        setCategories({ income, expense });
      }
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateAccountBalance = async (accountId, newBalance) => {
    try {
      const response = await fetch(`/api/accounts/${accountId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ balance: parseFloat(newBalance) })
      });

      if (response.ok) {
        loadData();
      } else {
        alert('Erro ao atualizar saldo da conta');
      }
    } catch (error) {
      console.error('Erro ao atualizar conta:', error);
      alert('Erro ao atualizar saldo da conta');
    }
  };

  const updateCreditCardClosingDay = async (cardId, closingDay) => {
    try {
      const response = await fetch(`/api/credit-cards/${cardId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ closing_day: parseInt(closingDay) })
      });

      if (response.ok) {
        loadData();
      } else {
        alert('Erro ao atualizar data de fechamento');
      }
    } catch (error) {
      console.error('Erro ao atualizar cartão:', error);
      alert('Erro ao atualizar data de fechamento');
    }
  };

  const addCategory = async () => {
    if (!newCategory.name.trim()) {
      alert('Nome da categoria é obrigatório');
      return;
    }

    try {
      const response = await fetch('/api/categories', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newCategory.name.trim(),
          type: newCategory.type
        })
      });

      if (response.ok) {
        setNewCategory({ name: '', type: 'expense' });
        loadData();
      } else {
        alert('Erro ao criar categoria');
      }
    } catch (error) {
      console.error('Erro ao criar categoria:', error);
      alert('Erro ao criar categoria');
    }
  };

  const deleteCategory = async (categoryId) => {
    if (!confirm('Tem certeza que deseja excluir esta categoria?')) {
      return;
    }

    try {
      const response = await fetch(`/api/categories/${categoryId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        loadData();
      } else {
        alert('Erro ao excluir categoria');
      }
    } catch (error) {
      console.error('Erro ao excluir categoria:', error);
      alert('Erro ao excluir categoria');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <Settings className="w-6 h-6 text-blue-400" />
            <h2 className="text-xl font-semibold text-white">Configurações</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex space-x-1 mb-6 bg-gray-700 rounded-lg p-1">
          <button
            onClick={() => setActiveTab('accounts')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'accounts'
                ? 'bg-blue-600 text-white'
                : 'text-gray-300 hover:text-white'
            }`}
          >
            Contas e Cartões
          </button>
          <button
            onClick={() => setActiveTab('categories')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'categories'
                ? 'bg-blue-600 text-white'
                : 'text-gray-300 hover:text-white'
            }`}
          >
            Categorias
          </button>
        </div>

        {loading ? (
          <div className="text-center py-8">
            <div className="text-gray-400">Carregando...</div>
          </div>
        ) : (
          <>
            {/* Tab: Contas e Cartões */}
            {activeTab === 'accounts' && (
              <div className="space-y-6">
                {/* Contas */}
                <div>
                  <h3 className="text-lg font-medium text-white mb-4">Contas Bancárias</h3>
                  <div className="space-y-3">
                    {accounts.map(account => (
                      <div key={account.id} className="bg-gray-700 rounded-lg p-4">
                        <div className="flex items-center justify-between">
                          <span className="text-white font-medium">{account.name}</span>
                          <div className="flex items-center gap-2">
                            <span className="text-gray-400">Saldo:</span>
                            <input
                              type="number"
                              step="0.01"
                              defaultValue={account.balance}
                              className="bg-gray-600 text-white px-3 py-1 rounded w-32 text-right"
                              onBlur={(e) => {
                                if (e.target.value !== account.balance.toString()) {
                                  updateAccountBalance(account.id, e.target.value);
                                }
                              }}
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Cartões de Crédito */}
                <div>
                  <h3 className="text-lg font-medium text-white mb-4">Cartões de Crédito</h3>
                  <div className="space-y-3">
                    {creditCards.map(card => (
                      <div key={card.id} className="bg-gray-700 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-white font-medium">{card.name}</span>
                          <span className="text-gray-400">
                            Saldo: R$ {card.current_balance?.toFixed(2) || '0,00'}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-gray-400">Dia do fechamento:</span>
                          <input
                            type="number"
                            min="1"
                            max="31"
                            defaultValue={card.closing_day}
                            className="bg-gray-600 text-white px-3 py-1 rounded w-20 text-center"
                            onBlur={(e) => {
                              if (e.target.value !== card.closing_day.toString()) {
                                updateCreditCardClosingDay(card.id, e.target.value);
                              }
                            }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Tab: Categorias */}
            {activeTab === 'categories' && (
              <div className="space-y-6">
                {/* Adicionar Nova Categoria */}
                <div className="bg-gray-700 rounded-lg p-4">
                  <h3 className="text-lg font-medium text-white mb-4">Adicionar Nova Categoria</h3>
                  <div className="flex gap-3">
                    <input
                      type="text"
                      placeholder="Nome da categoria"
                      value={newCategory.name}
                      onChange={(e) => setNewCategory({ ...newCategory, name: e.target.value })}
                      className="flex-1 bg-gray-600 text-white px-3 py-2 rounded"
                    />
                    <select
                      value={newCategory.type}
                      onChange={(e) => setNewCategory({ ...newCategory, type: e.target.value })}
                      className="bg-gray-600 text-white px-3 py-2 rounded"
                    >
                      <option value="expense">Despesa</option>
                      <option value="income">Receita</option>
                    </select>
                    <button
                      onClick={addCategory}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded flex items-center gap-2"
                    >
                      <Plus className="w-4 h-4" />
                      Adicionar
                    </button>
                  </div>
                </div>

                {/* Categorias de Receita */}
                <div>
                  <h3 className="text-lg font-medium text-white mb-4">Categorias de Receita</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {categories.income.map(category => (
                      <div key={category.id} className="bg-gray-700 rounded-lg p-3 flex items-center justify-between">
                        <span className="text-white">{category.name}</span>
                        {!category.is_default && (
                          <button
                            onClick={() => deleteCategory(category.id)}
                            className="text-red-400 hover:text-red-300 transition-colors"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Categorias de Despesa */}
                <div>
                  <h3 className="text-lg font-medium text-white mb-4">Categorias de Despesa</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {categories.expense.map(category => (
                      <div key={category.id} className="bg-gray-700 rounded-lg p-3 flex items-center justify-between">
                        <span className="text-white">{category.name}</span>
                        {!category.is_default && (
                          <button
                            onClick={() => deleteCategory(category.id)}
                            className="text-red-400 hover:text-red-300 transition-colors"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default SettingsModal;

