import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ArrowUpRight, ArrowDownRight, CreditCard, Banknote } from 'lucide-react';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

export const RecentTransactions = ({ transactions }) => {
  const formatDate = (dateString) => {
    try {
      return format(new Date(dateString), 'dd/MM', { locale: ptBR });
    } catch {
      return dateString;
    }
  };

  const getPaymentIcon = (paymentType) => {
    switch (paymentType) {
      case 'credit_card':
        return <CreditCard className="h-3 w-3" />;
      case 'pix':
      case 'debit':
        return <Banknote className="h-3 w-3" />;
      default:
        return null;
    }
  };

  const getPaymentLabel = (paymentType) => {
    switch (paymentType) {
      case 'credit_card':
        return 'Cartão';
      case 'pix':
        return 'PIX';
      case 'debit':
        return 'Débito';
      default:
        return paymentType;
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Transações Recentes</CardTitle>
      </CardHeader>
      <CardContent>
        {transactions.length === 0 ? (
          <div className="text-center py-4 text-muted-foreground">
            <p>Nenhuma transação encontrada</p>
          </div>
        ) : (
          <div className="space-y-3">
            {transactions.map((transaction) => {
              const isIncome = transaction.type === 'income';
              
              return (
                <div key={transaction.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-full ${isIncome ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}`}>
                      {isIncome ? (
                        <ArrowUpRight className="h-4 w-4" />
                      ) : (
                        <ArrowDownRight className="h-4 w-4" />
                      )}
                    </div>
                    
                    <div>
                      <p className="font-medium">{transaction.description}</p>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <span>{formatDate(transaction.date)}</span>
                        <Badge variant="outline" className="text-xs">
                          {getPaymentIcon(transaction.payment_type)}
                          <span className="ml-1">{getPaymentLabel(transaction.payment_type)}</span>
                        </Badge>
                        {transaction.installment_info && (
                          <Badge variant="secondary" className="text-xs">
                            {transaction.installment_info}
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className={`text-right font-medium ${isIncome ? 'text-green-600' : 'text-red-600'}`}>
                    {isIncome ? '+' : '-'}R$ {transaction.amount.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

