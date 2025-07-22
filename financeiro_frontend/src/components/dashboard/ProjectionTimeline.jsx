import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, TrendingDown } from 'lucide-react';

export const ProjectionTimeline = () => {
  const [projections, setProjections] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProjections();
  }, []);

  const loadProjections = async () => {
    try {
      const response = await fetch('/api/projections?months=6');
      if (response.ok) {
        const data = await response.json();
        setProjections(data.projections);
      }
    } catch (error) {
      console.error('Erro ao carregar projeções:', error);
    } finally {
      setLoading(false);
    }
  };

  const getMonthName = (month) => {
    const months = [
      'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
      'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'
    ];
    return months[month - 1];
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Projeção Mensal</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-4">
            <p>Carregando projeções...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Projeção Mensal</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {projections.map((projection, index) => {
            const isPositive = projection.projected_balance >= 0;
            const hasExpenses = projection.credit_card_expenses > 0;
            
            return (
              <div key={index} className="text-center space-y-2">
                <div className="text-sm font-medium">
                  {getMonthName(projection.month)}/{projection.year}
                </div>
                
                <div className={`text-lg font-bold ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                  {isPositive ? (
                    <TrendingUp className="h-4 w-4 inline mr-1" />
                  ) : (
                    <TrendingDown className="h-4 w-4 inline mr-1" />
                  )}
                  R$ {Math.abs(projection.projected_balance).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                </div>
                
                {hasExpenses && (
                  <Badge variant="secondary" className="text-xs">
                    Cartão: R$ {projection.credit_card_expenses.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                  </Badge>
                )}
                
                {projection.installments && projection.installments.length > 0 && (
                  <div className="text-xs text-muted-foreground">
                    {projection.installments.length} parcela{projection.installments.length > 1 ? 's' : ''}
                  </div>
                )}
              </div>
            );
          })}
        </div>
        
        {projections.length === 0 && (
          <div className="text-center py-4 text-muted-foreground">
            <p>Nenhuma projeção disponível</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

