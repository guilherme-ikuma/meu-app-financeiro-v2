# Aplicativo Financeiro - Controle de Gastos e Ganhos

## Descrição

Este é um aplicativo web completo para controle financeiro pessoal, desenvolvido com React (frontend) e Flask (backend). O sistema permite gerenciar contas bancárias, cartões de crédito, lançamentos de receitas e despesas, com projeções futuras e relatórios detalhados.

## Funcionalidades Principais

### 🔐 Sistema de Login
- Usuário:
- Senha:
- Controle de acesso seguro

### 💰 Gestão de Contas
- Visualização do saldo atual da conta bancária
- Possibilidade de atualizar o saldo manualmente
- Controle de múltiplas contas

### 💳 Cartões de Crédito
- Gestão dos cartões Nubank e Itaú (pré-configurados)
- Possibilidade de adicionar novos cartões
- Controle de data de fechamento da fatura
- Cálculo automático do saldo atual

### 📊 Lançamentos Financeiros
- **Receitas**: Salário, Adiantamento, PPR, 13º Salário, Restituição de IR, Outros
- **Despesas**: Alimentação, Combustível (com possibilidade de adicionar novas categorias)
- Formas de pagamento: Débito, PIX, Cartão de Crédito
- Compras parceladas com cálculo automático das parcelas

### 📈 Projeções Futuras
- Timeline de 6 meses com projeções de gastos
- Cálculo automático de parcelas futuras
- Visualização de gastos projetados por cartão de crédito
- Saldo projetado considerando receitas e despesas

### 📋 Dashboard e Relatórios
- Resumo mensal de receitas e despesas
- Saldo líquido do período
- Transações recentes com filtros
- Filtros por período específico
- Tabelas separadas para receitas e despesas

### 🎨 Interface
- Tema escuro moderno
- Design responsivo para desktop e mobile
- Interface intuitiva e fácil de usar

## Estrutura do Projeto

```
aplicativo-financeiro/
├── financeiro_backend/          # Backend Flask
│   ├── src/
│   │   ├── models/             # Modelos de dados
│   │   ├── routes/             # APIs REST
│   │   ├── database/           # Banco de dados SQLite
│   │   └── main.py            # Aplicação principal
│   ├── venv/                  # Ambiente virtual Python
│   └── requirements.txt       # Dependências Python
│
├── financeiro_frontend/        # Frontend React
│   ├── src/
│   │   ├── components/        # Componentes React
│   │   ├── contexts/          # Contextos de estado
│   │   └── assets/           # Recursos estáticos
│   ├── public/               # Arquivos públicos
│   └── package.json          # Dependências Node.js
│
└── documentacao/             # Documentação do projeto
    ├── planejamento_app_financeiro.md
    ├── database_schema.md
    ├── api_schema.md
    └── wireframes.md
```

## Como Executar

### Pré-requisitos
- Python 3.11+
- Node.js 20+
- pnpm

### Backend (Flask)
```bash
cd financeiro_backend
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```
O backend estará disponível em: `http://localhost:5000`

### Frontend (React)
```bash
cd financeiro_frontend
pnpm install
pnpm run dev
```
O frontend estará disponível em: `http://localhost:5173`

## Uso do Sistema

### 1. Login
- Acesse a aplicação no navegador
- Use as credenciais: `admin` / `142066`

### 2. Dashboard
- Visualize o resumo financeiro atual
- Veja os saldos das contas e cartões
- Acompanhe as projeções mensais

### 3. Nova Transação
- Clique em "Nova Transação"
- Escolha entre Receita ou Despesa
- Preencha os dados:
  - Descrição
  - Valor
  - Data
  - Categoria
  - Forma de pagamento
  - Para cartão: número de parcelas

### 4. Gestão de Contas
- Clique no ícone de edição no card de saldo
- Atualize o saldo atual da conta

### 5. Filtros e Relatórios
- Use os filtros de data no topo do dashboard
- Visualize as transações recentes
- Acompanhe as projeções na timeline

## Tecnologias Utilizadas

### Backend
- **Flask**: Framework web Python
- **SQLAlchemy**: ORM para banco de dados
- **SQLite**: Banco de dados
- **Flask-CORS**: Suporte a CORS
- **Werkzeug**: Utilitários web

### Frontend
- **React**: Biblioteca JavaScript
- **Vite**: Build tool
- **Tailwind CSS**: Framework CSS
- **shadcn/ui**: Componentes UI
- **Lucide React**: Ícones
- **date-fns**: Manipulação de datas

## Funcionalidades Avançadas

### Cálculo de Projeções
- O sistema calcula automaticamente as projeções futuras baseadas em:
  - Parcelas de compras no cartão de crédito
  - Data de fechamento das faturas
  - Receitas recorrentes
  - Despesas programadas

### Gestão de Parcelas
- Compras parceladas são automaticamente distribuídas nos meses futuros
- Considera a data de fechamento do cartão para determinar o mês de cobrança
- Atualiza as projeções automaticamente

### Categorização Inteligente
- Categorias pré-definidas para receitas e despesas
- Possibilidade de criar novas categorias
- Relatórios por categoria

## Segurança
- Autenticação baseada em sessão
- Validação de dados no frontend e backend
- Proteção contra CORS
- Sanitização de inputs

## Suporte
Para dúvidas ou problemas, consulte a documentação técnica nos arquivos de planejamento incluídos no projeto.

---

**Desenvolvido com ❤️ para controle financeiro pessoal**

