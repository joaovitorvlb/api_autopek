"""
AuthService - Serviço de Autenticação
Responsável por login, logout, geração de tokens JWT e verificação de permissões.
Usa flask-jwt-extended para gerenciamento de tokens JWT.
"""

import hashlib
from functools import wraps
from flask import jsonify
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    get_jwt,
    verify_jwt_in_request,
    jwt_required
)
from datetime import timedelta

# Configuração de expiração do token (pode ser sobrescrito no app.py)
TOKEN_EXPIRATION_HOURS = 24

# Blacklist de tokens (em produção, usar Redis)
# Com flask-jwt-extended, usamos o jti (JWT ID) para invalidar tokens
token_blacklist = set()


class AuthService:
    """Serviço de autenticação e autorização"""
    
    @staticmethod
    def hash_senha(senha):
        """
        Gera hash SHA-256 da senha.
        Em produção, usar bcrypt ou argon2.
        
        Args:
            senha (str): Senha em texto plano
        
        Returns:
            str: Hash da senha
        """
        return hashlib.sha256(senha.encode()).hexdigest()
    
    @staticmethod
    def verificar_senha(senha, senha_hash):
        """
        Verifica se a senha corresponde ao hash.
        
        Args:
            senha (str): Senha em texto plano
            senha_hash (str): Hash armazenado
        
        Returns:
            bool: True se a senha é válida
        """
        return AuthService.hash_senha(senha) == senha_hash
    
    @staticmethod
    def gerar_token(id_usuario, email, nivel_acesso):
        """
        Gera token JWT com dados do usuário usando flask-jwt-extended.
        
        Args:
            id_usuario (int): ID do usuário
            email (str): Email do usuário
            nivel_acesso (str): Nome do nível de acesso ('admin', 'funcionario', 'cliente')
        
        Returns:
            str: Token JWT
        """
        # Claims adicionais que serão incluídos no token
        additional_claims = {
            'email': email,
            'nivel_acesso': nivel_acesso
        }
        
        # create_access_token usa o primeiro argumento como "identity" (subject do JWT)
        # IMPORTANTE: identity deve ser string
        # A duração pode ser configurada no app com JWT_ACCESS_TOKEN_EXPIRES
        token = create_access_token(
            identity=str(id_usuario),  # Converter para string
            additional_claims=additional_claims,
            expires_delta=timedelta(hours=TOKEN_EXPIRATION_HOURS)
        )
        
        return token
    
    @staticmethod
    def invalidar_token(jti):
        """
        Adiciona JTI (JWT ID) à blacklist (logout).
        Com flask-jwt-extended, cada token tem um 'jti' único.
        
        Args:
            jti (str): JWT ID do token a ser invalidado
        """
        token_blacklist.add(jti)
    
    @staticmethod
    def token_esta_na_blacklist(jti):
        """
        Verifica se o token está na blacklist.
        
        Args:
            jti (str): JWT ID do token
        
        Returns:
            bool: True se está na blacklist
        """
        return jti in token_blacklist
    
    @staticmethod
    def login(usuario_dao, email, senha):
        """
        Realiza login do usuário.
        
        Args:
            usuario_dao: Instância de UsuarioDAO
            email (str): Email do usuário
            senha (str): Senha em texto plano
        
        Returns:
            dict: {'success': True, 'token': str, 'usuario': dict} ou {'success': False, 'message': str}
        """
        # Buscar usuário com senha
        usuario = usuario_dao.buscar_por_email_com_senha(email)
        
        if not usuario:
            return {'success': False, 'message': 'Email ou senha inválidos'}
        
        # Verificar se usuário está ativo
        if not usuario.get('ativo', True):
            return {'success': False, 'message': 'Conta desativada'}
        
        # Verificar senha
        if not AuthService.verificar_senha(senha, usuario['senha_hash']):
            return {'success': False, 'message': 'Email ou senha inválidos'}
        
        # Gerar token
        token = AuthService.gerar_token(
            usuario['id_usuario'],
            usuario['email'],
            usuario['nivel_acesso_nome']
        )
        
        # Remover senha_hash antes de retornar
        usuario_sem_senha = {k: v for k, v in usuario.items() if k != 'senha_hash'}
        
        return {
            'success': True,
            'token': token,
            'usuario': usuario_sem_senha
        }
    
    @staticmethod
    def logout():
        """
        Realiza logout do usuário (adiciona JTI do token à blacklist).
        Deve ser chamado dentro de uma rota protegida com @jwt_required().
        
        Returns:
            dict: {'success': True, 'message': str}
        """
        # get_jwt() retorna o payload completo do token atual
        jti = get_jwt()['jti']
        AuthService.invalidar_token(jti)
        return {'success': True, 'message': 'Logout realizado com sucesso'}
    
    @staticmethod
    def obter_usuario_atual():
        """
        Obtém dados do usuário autenticado atual.
        Deve ser chamado dentro de uma rota protegida com @jwt_required().
        
        Returns:
            dict: Dados do usuário extraídos do token JWT
        """
        # get_jwt_identity() retorna o 'identity' do token (id_usuario como string)
        id_usuario_str = get_jwt_identity()
        
        # get_jwt() retorna todos os claims do token
        claims = get_jwt()
        
        return {
            'id_usuario': int(id_usuario_str),  # Converter de volta para int
            'email': claims.get('email'),
            'nivel_acesso': claims.get('nivel_acesso')
        }
    
    @staticmethod
    def verificar_permissao(nivel_acesso_usuario, nivel_requerido):
        """
        Verifica se o usuário tem permissão para acessar recurso.
        
        Hierarquia: admin > funcionario > cliente
        
        Args:
            nivel_acesso_usuario (str): Nível de acesso do usuário
            nivel_requerido (str): Nível mínimo requerido
        
        Returns:
            bool: True se tem permissão, False caso contrário
        """
        niveis = {
            'admin': 3,
            'funcionario': 2,
            'cliente': 1
        }
        
        nivel_usuario = niveis.get(nivel_acesso_usuario, 0)
        nivel_req = niveis.get(nivel_requerido, 0)
        
        return nivel_usuario >= nivel_req


# Decoradores para proteger rotas
def token_required(f):
    """
    Decorador para rotas que requerem autenticação.
    Usa flask-jwt-extended internamente.
    Adiciona 'usuario_atual' aos kwargs da função.
    
    Uso:
        @app.route('/protected')
        @token_required
        def protected_route(usuario_atual):
            return jsonify(usuario_atual)
    """
    @wraps(f)
    @jwt_required()  # Usa o decorador nativo do flask-jwt-extended
    def decorated(*args, **kwargs):
        try:
            # Verifica se o token está na blacklist
            jti = get_jwt()['jti']
            if AuthService.token_esta_na_blacklist(jti):
                return jsonify({'message': 'Token foi invalidado (logout)'}), 401
            
            # Obtém dados do usuário
            usuario_atual = AuthService.obter_usuario_atual()
            
            # Adiciona aos kwargs
            kwargs['usuario_atual'] = usuario_atual
            
            return f(*args, **kwargs)
        
        except Exception as e:
            return jsonify({'message': f'Token inválido: {str(e)}'}), 401
    
    return decorated


def nivel_required(nivel_minimo):
    """
    Decorador para rotas que requerem nível de acesso específico.
    Usar em conjunto com @token_required.
    
    Args:
        nivel_minimo (str): Nível mínimo requerido ('admin', 'funcionario', 'cliente')
    
    Exemplo:
        @app.route('/admin/dashboard')
        @token_required
        @nivel_required('admin')
        def admin_dashboard(usuario_atual):
            return jsonify({'message': 'Dashboard admin'})
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            usuario_atual = kwargs.get('usuario_atual')
            
            if not usuario_atual:
                return jsonify({'message': 'Usuário não autenticado'}), 401
            
            nivel_usuario = usuario_atual.get('nivel_acesso')
            
            if not AuthService.verificar_permissao(nivel_usuario, nivel_minimo):
                return jsonify({'message': 'Permissão negada'}), 403
            
            return f(*args, **kwargs)
        
        return decorated
    
    return decorator


def admin_required(f):
    """Atalho para @nivel_required('admin')"""
    return nivel_required('admin')(f)


def funcionario_required(f):
    """Atalho para @nivel_required('funcionario')"""
    return nivel_required('funcionario')(f)
