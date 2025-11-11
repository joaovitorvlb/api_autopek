"""
Módulo de Rotas
Contém blueprints para organizar endpoints da API
"""

from .auth_routes import auth_bp
from .cliente_routes import cliente_bp
from .funcionario_routes import funcionario_bp
from .produto_routes import produto_bp
from .fornecedor_routes import fornecedor_bp
from .pedido_compra_routes import pedido_compra_bp
from .pedido_venda_routes import pedido_venda_bp

__all__ = [
    'auth_bp',
    'cliente_bp',
    'funcionario_bp',
    'produto_bp',
    'fornecedor_bp',
    'pedido_compra_bp',
    'pedido_venda_bp'
]
