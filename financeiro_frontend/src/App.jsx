import { useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { AppProvider } from './contexts/AppContext';
import { LoginForm } from './components/auth/LoginForm';
import { Dashboard } from './components/dashboard/Dashboard';
import { TransactionForm } from './components/transactions/TransactionForm';
import { Button } from '@/components/ui/button';
import { LogOut, User } from 'lucide-react';
import './App.css';

const AppContent = () => {
  const { user, isAuthenticated, loading, logout } = useAuth();
  const [showTransactionForm, setShowTransactionForm] = useState(false);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p>Carregando...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginForm />;
  }

  return (
    <AppProvider>
      <div className="min-h-screen bg-background">
        {/* Header */}
        <header className="border-b bg-card">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-xl font-bold">Controle Financeiro</h1>
              </div>
              
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2 text-sm">
                  <User className="h-4 w-4" />
                  <span>{user?.username}</span>
                </div>
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={logout}
                >
                  <LogOut className="h-4 w-4 mr-2" />
                  Sair
                </Button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="container mx-auto px-4 py-6">
          <Dashboard onNewTransaction={() => setShowTransactionForm(true)} />
        </main>

        {/* Transaction Form Modal */}
        <TransactionForm
          isOpen={showTransactionForm}
          onClose={() => setShowTransactionForm(false)}
          onSuccess={() => {
            // Form will close automatically on success
            console.log('Transação criada com sucesso!');
          }}
        />
      </div>
    </AppProvider>
  );
};

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
