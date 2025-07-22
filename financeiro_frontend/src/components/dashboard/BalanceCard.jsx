import { useState } from 'react';
import { useApp } from '../../contexts/AppContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Edit, Wallet } from 'lucide-react';

export const BalanceCard = ({ balance, accountName }) => {
  const { accounts, updateAccount } = useApp();
  const [isEditing, setIsEditing] = useState(false);
  const [newBalance, setNewBalance] = useState(balance);
  const [loading, setLoading] = useState(false);

  const handleUpdateBalance = async () => {
    if (accounts.length === 0) return;
    
    setLoading(true);
    const account = accounts[0]; // Assumindo primeira conta como principal
    
    const result = await updateAccount(account.id, {
      balance: parseFloat(newBalance)
    });

    if (result.success) {
      setIsEditing(false);
    }
    
    setLoading(false);
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">
          {accountName}
        </CardTitle>
        <Wallet className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          <div>
            <div className="text-2xl font-bold">
              R$ {balance.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
            </div>
            <p className="text-xs text-muted-foreground">
              Saldo atual
            </p>
          </div>
          
          <Dialog open={isEditing} onOpenChange={setIsEditing}>
            <DialogTrigger asChild>
              <Button variant="outline" size="sm">
                <Edit className="h-4 w-4" />
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Atualizar Saldo</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="balance">Novo Saldo</Label>
                  <Input
                    id="balance"
                    type="number"
                    step="0.01"
                    value={newBalance}
                    onChange={(e) => setNewBalance(e.target.value)}
                    placeholder="0,00"
                  />
                </div>
                <div className="flex justify-end gap-2">
                  <Button
                    variant="outline"
                    onClick={() => setIsEditing(false)}
                    disabled={loading}
                  >
                    Cancelar
                  </Button>
                  <Button
                    onClick={handleUpdateBalance}
                    disabled={loading}
                  >
                    {loading ? 'Salvando...' : 'Salvar'}
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </CardContent>
    </Card>
  );
};

