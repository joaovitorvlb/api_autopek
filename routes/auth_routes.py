"""
Rotas de Autenticação
Endpoints: login, logout, verificação de token
"""

from flask import Blueprint, request, jsonify
from dao_mysql.usuario_dao import UsuarioDAO
from service.auth_service import AuthService, token_required

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Instanciar DAOs
usuario_dao = UsuarioDAO()


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Realiza login do usuário.
    
    Request body:
    {
        "email": "usuario@email.com",
        "senha": "senha123"
    }
    
    Response:
    {
        "success": true,
        "token": "eyJ...",
        "usuario": {
            "id_usuario": 1,
            "nome": "João Silva",
            "email": "usuario@email.com",
            "nivel_acesso_nome": "cliente",
            "ativo": true
        }
    }
    """
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({'success': False, 'message': 'Dados não fornecidos'}), 400
        
        email = dados.get('email')
        senha = dados.get('senha')
        
        if not email or not senha:
            return jsonify({'success': False, 'message': 'Email e senha são obrigatórios'}), 400
        
        # Realizar login
        resultado = AuthService.login(usuario_dao, email, senha)
        
        if resultado['success']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 401
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao realizar login: {str(e)}'
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(usuario_atual):
    """
    Realiza logout do usuário (invalida token).
    
    Headers:
        Authorization: Bearer <token>
    
    Response:
    {
        "success": true,
        "message": "Logout realizado com sucesso"
    }
    """
    try:
        # Realizar logout (o decorador @token_required já validou o token)
        resultado = AuthService.logout()
        
        return jsonify(resultado), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao realizar logout: {str(e)}'
        }), 500


@auth_bp.route('/verify', methods=['GET'])
@token_required
def verify_token(usuario_atual):
    """
    Verifica se token é válido e retorna dados do usuário.
    
    Headers:
        Authorization: Bearer <token>
    
    Response:
    {
        "success": true,
        "usuario": {
            "id_usuario": 1,
            "email": "usuario@email.com",
            "nivel_acesso": "cliente"
        }
    }
    """
    try:
        # O decorador @token_required já validou o token e forneceu usuario_atual
        return jsonify({
            'success': True,
            'usuario': usuario_atual
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao verificar token: {str(e)}'
        }), 500


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(usuario_atual):
    """
    Retorna dados completos do usuário autenticado.
    
    Headers:
        Authorization: Bearer <token>
    
    Response:
    {
        "success": true,
        "usuario": {
            "id_usuario": 1,
            "nome": "João Silva",
            "email": "usuario@email.com",
            "nivel_acesso_nome": "cliente",
            "telefone": "11999999999",
            "ativo": true,
            "data_criacao": "2024-01-01 10:00:00"
        }
    }
    """
    try:
        # Buscar dados completos do usuário no banco
        id_usuario = usuario_atual['id_usuario']
        usuario = usuario_dao.buscar_por_id(id_usuario)
        
        if not usuario:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404
        
        return jsonify({
            'success': True,
            'usuario': usuario
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar usuário: {str(e)}'
        }), 500
