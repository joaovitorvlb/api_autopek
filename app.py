"""
API AutoPek
Sistema de gestão para loja de peças automotivas

Credenciais padrão para primeiro acesso:
- Email: admin@autopeck.com
- Senha: admin123
⚠️  IMPORTANTE: Altere a senha após o primeiro login!
"""

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta

# Importar blueprints
from routes import (
    auth_bp, 
    cliente_bp, 
    funcionario_bp, 
    produto_bp,
    fornecedor_bp,
    pedido_compra_bp,
    pedido_venda_bp
)

# Importar inicialização do banco
from dao_sqlite.db import init_db, close_db_connection


# Configuração das resoluções de imagem
IMAGE_RESOLUTIONS = {
    'thumbnail': (150, 150),   # Para listas/miniaturas
    'medium': (400, 400),      # Para detalhes/cards
    'large': (800, 800)        # Para visualização ampliada
}


def create_app():
    """
    Factory function para criar e configurar a aplicação Flask
    """
    app = Flask(__name__)
    
    # Configurações
    app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'  # TODO: Mover para variável de ambiente
    app.config['JSON_SORT_KEYS'] = False
    
    # Configurações JWT
    app.config['JWT_SECRET_KEY'] = 'jwt-secret-key-autopek-2025'  # TODO: Mover para variável de ambiente
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['JWT_ALGORITHM'] = 'HS256'
    
    # Inicializar JWT Manager
    jwt = JWTManager(app)
    
    # Callback para verificar se token está na blacklist (logout)
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        from service.auth_service import AuthService
        jti = jwt_payload['jti']
        return AuthService.token_esta_na_blacklist(jti)
    
    # Handlers de erro JWT
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {'message': 'Token inválido', 'error': str(error)}, 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {'message': 'Token não fornecido', 'error': str(error)}, 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {'message': 'Token expirado'}, 401
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return {'message': 'Token foi revogado (logout realizado)'}, 401
    
    # Inicializar banco de dados SQLite
    init_db()
    
    # Registrar teardown para fechar conexão ao fim da requisição
    app.teardown_appcontext(close_db_connection)
    
    # Habilitar CORS
    CORS(app)
    
    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(cliente_bp)
    app.register_blueprint(funcionario_bp)
    app.register_blueprint(produto_bp)
    app.register_blueprint(fornecedor_bp)
    app.register_blueprint(pedido_compra_bp)
    app.register_blueprint(pedido_venda_bp)
    
    # Rota raiz
    @app.route('/')
    def index():
        return {
            'message': 'API AutoPek',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth',
                'clientes': '/api/clientes',
                'funcionarios': '/api/funcionarios',
                'produtos': '/api/produtos',
                'fornecedores': '/api/fornecedores',
                'pedidos_compra': '/api/pedidos-compra',
                'pedidos_venda': '/api/pedidos-venda'
            }
        }
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
