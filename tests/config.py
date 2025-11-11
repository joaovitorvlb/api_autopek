"""
Configuração compartilhada para todos os testes
"""

# URL base da API
API_BASE_URL = "http://localhost:5000"

# Credenciais padrão
ADMIN_EMAIL = "admin@autopeck.com"
ADMIN_SENHA = "admin123"

# Endpoints
ENDPOINTS = {
    'auth': {
        'login': f"{API_BASE_URL}/api/auth/login",
        'logout': f"{API_BASE_URL}/api/auth/logout",
        'verify': f"{API_BASE_URL}/api/auth/verify",
        'me': f"{API_BASE_URL}/api/auth/me"
    },
    'produtos': {
        'base': f"{API_BASE_URL}/api/produtos",
        'buscar': f"{API_BASE_URL}/api/produtos/buscar"
    },
    'clientes': {
        'base': f"{API_BASE_URL}/api/clientes",
        'register': f"{API_BASE_URL}/api/clientes/register"
    },
    'funcionarios': {
        'base': f"{API_BASE_URL}/api/funcionarios"
    },
    'fornecedores': {
        'base': f"{API_BASE_URL}/api/fornecedores",
        'buscar': f"{API_BASE_URL}/api/fornecedores/buscar",
        'estatisticas': f"{API_BASE_URL}/api/fornecedores/estatisticas"
    },
    'pedidos_compra': {
        'base': f"{API_BASE_URL}/api/pedidos-compra",
        'relatorio': f"{API_BASE_URL}/api/pedidos-compra/relatorio"
    },
    'pedidos_venda': {
        'base': f"{API_BASE_URL}/api/pedidos-venda",
        'relatorio': f"{API_BASE_URL}/api/pedidos-venda/relatorio",
        'produtos_mais_vendidos': f"{API_BASE_URL}/api/pedidos-venda/produtos-mais-vendidos"
    }
}

# Token global (será preenchido após login)
TOKEN = None


def set_token(token):
    """Define o token global"""
    global TOKEN
    TOKEN = token


def get_token():
    """Retorna o token global"""
    return TOKEN


def get_headers():
    """Retorna headers com token de autenticação"""
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
