import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.models.account import Account
from src.models.credit_card import CreditCard
from src.models.category import Category
from src.models.transaction import Transaction
from src.routes.user import user_bp
from src.routes.accounts import accounts_bp
from src.routes.credit_cards import credit_cards_bp
from src.routes.categories import categories_bp
from src.routes.transactions import transactions_bp
from src.routes.dashboard import dashboard_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Configurar CORS para permitir comunicação com frontend
CORS(app)

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(accounts_bp, url_prefix='/api')
app.register_blueprint(credit_cards_bp, url_prefix='/api')
app.register_blueprint(categories_bp, url_prefix='/api')
app.register_blueprint(transactions_bp, url_prefix='/api')
app.register_blueprint(dashboard_bp, url_prefix='/api')

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Criar tabelas e dados iniciais
with app.app_context():
    db.create_all()
    
    # Verificar se já existe o usuário admin
    from src.models.user import User
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        # Criar usuário admin
        admin_user = User(username='admin', password='142066')
        db.session.add(admin_user)
        db.session.commit()
        
        # Criar categorias padrão de receita
        income_categories = [
            'Salário', 'Adiantamento', 'PPR', '13º Salário', 'Restituição de IR', 'Outros'
        ]
        for cat_name in income_categories:
            category = Category(user_id=admin_user.id, name=cat_name, type='income', is_default=True)
            db.session.add(category)
        
        # Criar categorias padrão de despesa
        expense_categories = ['Alimentação', 'Combustível']
        for cat_name in expense_categories:
            category = Category(user_id=admin_user.id, name=cat_name, type='expense', is_default=True)
            db.session.add(category)
        
        # Criar conta bancária padrão
        account = Account(user_id=admin_user.id, name='Conta Corrente', balance=0.00)
        db.session.add(account)
        
        # Criar cartões de crédito padrão
        nubank = CreditCard(user_id=admin_user.id, name='Nubank', closing_day=15)
        itau = CreditCard(user_id=admin_user.id, name='Itaú', closing_day=10)
        db.session.add(nubank)
        db.session.add(itau)
        
        db.session.commit()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
