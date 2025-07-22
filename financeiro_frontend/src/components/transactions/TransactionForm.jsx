import { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2 } from 'lucide-react';

export const TransactionForm = ({ isOpen, onClose, onSuccess }) => {
  const { accounts, creditCards, categories, createTransaction } = useApp();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [formData, setFormData] = useState({
    type: 'expense',
    description: '',
    amount: '',
    transaction_date: new Date().toISOString().split('T')[0],
    category_id: '',
    payment_type: 'debit',
    account_id: '',
    credit_card_id: '',
    installments: 1
  });

  // Reset form when dialog opens
  useEffect(() => {
    if (isOpen) {
      setFormData({
        type: 'expense',
        description: '',
        amount: '',
        transaction_date: new Date().toISOString().split('T')[0],
        category_id: '',
        payment_type: 'debit',
        account_id: accounts[0]?.id || '',
        credit_card_id: creditCards[0]?.id || '',
        installments: 1
      });
      setError('');
    }
  }, [isOpen, accounts, creditCards]);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear category when type changes
    if (field === 'type') {
      setFormData(prev => ({
        ...prev,
        category_id: ''
      }));
    }
    
    // Reset installments when payment type changes
    if (field === 'payment_type' && value !== 'credit_card') {
      setFormData(prev => ({
        ...prev,
        installments: 1
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Validation
    if (!formData.description.trim()) {
      setError('Descrição é obrigatória');
      setLoading(false);
      return;
    }

    if (!formData.amount || parseFloat(formData.amount) <= 0) {
      setError('Valor deve ser maior que zero');
      setLoading(false);
      return;
    }

    if (!formData.category_id) {
      setError('Categoria é obrigatória');
      setLoading(false);
      return;
    }

    if (formData.payment_type === 'credit_card' && !formData.credit_card_id) {
      setError('Cartão de crédito é obrigatório');
      setLoading(false);
      return;
    }

    if ((formData.payment_type === 'debit' || formData.payment_type === 'pix') && !formData.account_id) {
      setError('Conta é obrigatória para débito/PIX');
      setLoading(false);
      return;
    }

    // Prepare data for API
    const transactionData = {
      description: formData.description.trim(),
      amount: parseFloat(formData.amount),
      transaction_date: formData.transaction_date,
      category_id: parseInt(formData.category_id),
      payment_type: formData.payment_type,
      installments: parseInt(formData.installments)
    };

    if (formData.payment_type === 'credit_card') {
      transactionData.credit_card_id = parseInt(formData.credit_card_id);
    } else {
      transactionData.account_id = parseInt(formData.account_id);
    }

    const result = await createTransaction(transactionData);

    if (result.success) {
      onSuccess?.();
      onClose();
    } else {
      setError(result.message || 'Erro ao criar transação');
    }

    setLoading(false);
  };

  const currentCategories = formData.type === 'income' ? categories.income : categories.expense;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Nova Transação</DialogTitle>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Tipo */}
          <div>
            <Label>Tipo</Label>
            <RadioGroup
              value={formData.type}
              onValueChange={(value) => handleInputChange('type', value)}
              className="flex gap-4 mt-2"
            >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="income" id="income" />
                <Label htmlFor="income">Receita</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="expense" id="expense" />
                <Label htmlFor="expense">Despesa</Label>
              </div>
            </RadioGroup>
          </div>

          {/* Descrição */}
          <div>
            <Label htmlFor="description">Descrição</Label>
            <Input
              id="description"
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              placeholder="Ex: Compra no supermercado"
              required
            />
          </div>

          {/* Valor */}
          <div>
            <Label htmlFor="amount">Valor (R$)</Label>
            <Input
              id="amount"
              type="number"
              step="0.01"
              min="0.01"
              value={formData.amount}
              onChange={(e) => handleInputChange('amount', e.target.value)}
              placeholder="0,00"
              required
            />
          </div>

          {/* Data */}
          <div>
            <Label htmlFor="date">Data</Label>
            <Input
              id="date"
              type="date"
              value={formData.transaction_date}
              onChange={(e) => handleInputChange('transaction_date', e.target.value)}
              required
            />
          </div>

          {/* Categoria */}
          <div>
            <Label>Categoria</Label>
            <Select
              value={formData.category_id}
              onValueChange={(value) => handleInputChange('category_id', value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Selecione uma categoria" />
              </SelectTrigger>
              <SelectContent>
                {currentCategories.map((category) => (
                  <SelectItem key={category.id} value={category.id.toString()}>
                    {category.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Forma de Pagamento */}
          <div>
            <Label>Forma de Pagamento</Label>
            <RadioGroup
              value={formData.payment_type}
              onValueChange={(value) => handleInputChange('payment_type', value)}
              className="flex gap-4 mt-2"
            >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="debit" id="debit" />
                <Label htmlFor="debit">Débito</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="pix" id="pix" />
                <Label htmlFor="pix">PIX</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="credit_card" id="credit_card" />
                <Label htmlFor="credit_card">Cartão</Label>
              </div>
            </RadioGroup>
          </div>

          {/* Conta (para débito/PIX) */}
          {(formData.payment_type === 'debit' || formData.payment_type === 'pix') && (
            <div>
              <Label>Conta</Label>
              <Select
                value={formData.account_id}
                onValueChange={(value) => handleInputChange('account_id', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Selecione uma conta" />
                </SelectTrigger>
                <SelectContent>
                  {accounts.map((account) => (
                    <SelectItem key={account.id} value={account.id.toString()}>
                      {account.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}

          {/* Cartão (para cartão de crédito) */}
          {formData.payment_type === 'credit_card' && (
            <>
              <div>
                <Label>Cartão</Label>
                <Select
                  value={formData.credit_card_id}
                  onValueChange={(value) => handleInputChange('credit_card_id', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione um cartão" />
                  </SelectTrigger>
                  <SelectContent>
                    {creditCards.map((card) => (
                      <SelectItem key={card.id} value={card.id.toString()}>
                        {card.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Parcelas */}
              <div>
                <Label htmlFor="installments">Parcelas</Label>
                <Select
                  value={formData.installments.toString()}
                  onValueChange={(value) => handleInputChange('installments', parseInt(value))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {Array.from({ length: 24 }, (_, i) => i + 1).map((num) => (
                      <SelectItem key={num} value={num.toString()}>
                        {num}x {formData.amount ? `de R$ ${(parseFloat(formData.amount) / num).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}` : ''}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </>
          )}

          {/* Buttons */}
          <div className="flex justify-end gap-2 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={loading}
            >
              Cancelar
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Salvando...
                </>
              ) : (
                'Salvar'
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

