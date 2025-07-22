import { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { BalanceCard } from './BalanceCard';
import { CreditCardCard } from './CreditCardCard';
import { ProjectionTimeline } from './ProjectionTimeline';
import { RecentTransactions } from './RecentTransactions';
import MonthlyChart from './MonthlyChart';
import SettingsModal from '../settings/SettingsModal';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { CalendarIcon, Plus, RefreshCw, Settings } from 'lucide-react';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

export const Dashboard = ({ onNewTransaction }) => {
  const { dashboardData, loading, loadDashboard } = useApp();
  const [showSettings, setShowSettings] = useState(false);
  const [dateFilter, setDateFilter] = useState({
    start_date: format(new Date(new Date().getFullYear(), new Date().getMonth(), 1), 'yyyy-MM-dd'),
    end_date: format(new Date(new Date().getFullYear(), new Date().getMonth() + 1, 0), 'yyyy-MM-dd')
  });
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    if (!loading) {
      loadDashboard(dateFilter);
    }
  }, [dateFilter]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadDashboard(dateFilter);
    setRefreshing(false);
  };

  const handleDateFilterChange = (field, value) => {
    setDateFilter(prev => ({
      ...prev,
      [field]: value
    }));
  };

  if (loading && !dashboardData) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-2" />
          <p>Carregando dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header com filtros */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">
            Visão geral das suas finanças
          </p>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-2">
          <div className="flex gap-2">
            <div>
              <Label htmlFor="start-date" className="text-xs">De</Label>
              <Input
                id="start-date"
                type="date"
                value={dateFilter.start_date}
                onChange={(e) => handleDateFilterChange('start_date', e.target.value)}
                className="w-auto"
              />
            </div>
            <div>
              <Label htmlFor="end-date" className="text-xs">Até</Label>
              <Input
                id="end-date"
                type="date"
                value={dateFilter.end_date}
                onChange={(e) => handleDateFilterChange('end_date', e.target.value)}
                className="w-auto"
              />
            </div>
          </div>
          
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              disabled={refreshing}
            >
              <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowSettings(true)}
            >
              <Settings className="h-4 w-4" />
            </Button>
            <Button
              size="sm"
              onClick={onNewTransaction}
            >
              <Plus className="h-4 w-4 mr-2" />
              Nova Transação
            </Button>
          </div>
        </div>
      </div>

      {/* Cards de saldo */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <BalanceCard 
          balance={dashboardData?.current_balance || 0}
          accountName="Saldo Total"
        />
        
        {dashboardData?.credit_cards?.map((card, index) => (
          <CreditCardCard
            key={index}
            creditCard={card}
          />
        ))}
      </div>

      {/* Resumo mensal */}
      {dashboardData?.monthly_summary && (
        <Card>
          <CardHeader>
            <CardTitle>Resumo do Período</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <p className="text-sm text-muted-foreground">Receitas</p>
                <p className="text-2xl font-bold text-green-600">
                  R$ {dashboardData.monthly_summary.total_income.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                </p>
              </div>
              <div className="text-center">
                <p className="text-sm text-muted-foreground">Despesas</p>
                <p className="text-2xl font-bold text-red-600">
                  R$ {dashboardData.monthly_summary.total_expenses.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                </p>
              </div>
              <div className="text-center">
                <p className="text-sm text-muted-foreground">Saldo Líquido</p>
                <p className={`text-2xl font-bold ${dashboardData.monthly_summary.net_balance >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  R$ {dashboardData.monthly_summary.net_balance.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Gráfico Mensal */}
      <MonthlyChart />

      {/* Timeline de projeções */}
      <ProjectionTimeline />

      {/* Transações recentes */}
      <RecentTransactions 
        transactions={dashboardData?.recent_transactions || []}
      />

      {/* Modal de Configurações */}
      <SettingsModal
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
      />
    </div>
  );
};

