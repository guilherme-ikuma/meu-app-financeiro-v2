#!/bin/bash

echo "=== Aplicativo Financeiro ==="
echo "Iniciando backend e frontend..."
echo ""

# Verificar se os diretórios existem
if [ ! -d "financeiro_backend" ]; then
    echo "❌ Erro: Diretório financeiro_backend não encontrado!"
    exit 1
fi

if [ ! -d "financeiro_frontend" ]; then
    echo "❌ Erro: Diretório financeiro_frontend não encontrado!"
    exit 1
fi

# Função para limpar processos ao sair
cleanup() {
    echo ""
    echo "🛑 Parando aplicativo..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Aplicativo parado com sucesso!"
    exit 0
}

# Capturar Ctrl+C
trap cleanup SIGINT

# Iniciar backend
echo "🚀 Iniciando backend Flask..."
cd financeiro_backend
source venv/bin/activate
python src/main.py &
BACKEND_PID=$!
cd ..

# Aguardar backend inicializar
sleep 3

# Iniciar frontend
echo "🚀 Iniciando frontend React..."
cd financeiro_frontend
pnpm run dev --host &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Aplicativo iniciado com sucesso!"
echo ""
echo "📱 Frontend: http://localhost:5173"
echo "🔧 Backend:  http://localhost:5000"
echo ""
echo "👤 Login:"
echo "   Usuário: admin"
echo "   Senha:   142066"
echo ""
echo "💡 Pressione Ctrl+C para parar o aplicativo"
echo ""

# Aguardar indefinidamente
wait

