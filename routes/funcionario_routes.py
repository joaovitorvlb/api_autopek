"""
Rotas de Funcionários
Endpoints CRUD para funcionários com autenticação
"""

from flask import Blueprint, request, jsonify
from dao_mysql.funcionario_dao import FuncionarioDAO
from dao_mysql.usuario_dao import UsuarioDAO
from dao_mysql.nivel_acesso_dao import NivelAcessoDAO
from service.funcionario_service import FuncionarioService
from service.auth_service import token_required, admin_required, funcionario_required

funcionario_bp = Blueprint('funcionarios', __name__, url_prefix='/api/funcionarios')

# Instanciar DAOs e Service
funcionario_dao = FuncionarioDAO()
usuario_dao = UsuarioDAO()
nivel_acesso_dao = NivelAcessoDAO()
funcionario_service = FuncionarioService(funcionario_dao, usuario_dao, nivel_acesso_dao)


@funcionario_bp.route('/', methods=['POST'])
@token_required
@admin_required
def criar_funcionario(usuario_atual):
    """
    Cria novo funcionário.
    Requer autenticação de admin.
    
    Request body:
    {
        "nome": "Maria Santos",
        "email": "maria@autopeck.com",
        "senha": "senha123",
        "cargo": "Vendedor",
        "salario": 3500.00,
        "data_contratacao": "2024-01-15",
        "telefone": "11988887777",
        "nivel_acesso": "funcionario"
    }
    """
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({'success': False, 'message': 'Dados não fornecidos'}), 400
        
        # Extrair dados
        nome = dados.get('nome')
        email = dados.get('email')
        senha = dados.get('senha')
        cargo = dados.get('cargo')
        salario = dados.get('salario')
        data_contratacao = dados.get('data_contratacao')
        telefone = dados.get('telefone')
        nivel_acesso = dados.get('nivel_acesso', 'funcionario')
        
        # Validar campos obrigatórios
        if not all([nome, email, senha, cargo, salario]):
            return jsonify({
                'success': False,
                'message': 'Campos obrigatórios: nome, email, senha, cargo, salario'
            }), 400
        
        # Criar funcionário
        resultado = funcionario_service.criar_funcionario_completo(
            nome=nome,
            email=email,
            senha=senha,
            cargo=cargo,
            salario=salario,
            data_contratacao=data_contratacao,
            telefone=telefone,
            nivel_acesso=nivel_acesso
        )
        
        if resultado['success']:
            return jsonify(resultado), 201
        else:
            return jsonify(resultado), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao criar funcionário: {str(e)}'
        }), 500


@funcionario_bp.route('/', methods=['GET'])
@token_required
@funcionario_required
def listar_funcionarios(usuario_atual):
    """
    Lista todos os funcionários.
    Requer autenticação de funcionário ou admin.
    
    Query params:
        apenas_ativos: true/false (padrão: true)
    """
    try:
        apenas_ativos = request.args.get('apenas_ativos', 'true').lower() == 'true'
        
        funcionarios = funcionario_service.listar_funcionarios(apenas_ativos)
        
        return jsonify({
            'success': True,
            'funcionarios': funcionarios
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar funcionários: {str(e)}'
        }), 500


@funcionario_bp.route('/<int:id_funcionario>', methods=['GET'])
@token_required
@funcionario_required
def buscar_funcionario(usuario_atual, id_funcionario):
    """
    Busca funcionário por ID.
    Requer autenticação de funcionário ou admin.
    """
    try:
        funcionario = funcionario_service.buscar_funcionario(id_funcionario)
        
        if not funcionario:
            return jsonify({'success': False, 'message': 'Funcionário não encontrado'}), 404
        
        return jsonify({
            'success': True,
            'funcionario': funcionario
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar funcionário: {str(e)}'
        }), 500


@funcionario_bp.route('/cargo/<cargo>', methods=['GET'])
@token_required
@funcionario_required
def listar_por_cargo(usuario_atual, cargo):
    """
    Lista funcionários por cargo.
    Requer autenticação de funcionário ou admin.
    """
    try:
        funcionarios = funcionario_service.listar_por_cargo(cargo)
        
        return jsonify({
            'success': True,
            'funcionarios': funcionarios
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar funcionários: {str(e)}'
        }), 500


@funcionario_bp.route('/<int:id_funcionario>', methods=['PUT'])
@token_required
@admin_required
def atualizar_funcionario(usuario_atual, id_funcionario):
    """
    Atualiza dados do funcionário.
    Requer autenticação de admin.
    
    Request body (todos opcionais):
    {
        "nome": "Maria Santos Silva",
        "email": "maria.santos@autopeck.com",
        "telefone": "11977776666",
        "cargo": "Gerente de Vendas",
        "salario": 5000.00,
        "data_contratacao": "2024-01-15"
    }
    """
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({'success': False, 'message': 'Dados não fornecidos'}), 400
        
        # Atualizar funcionário
        resultado = funcionario_service.atualizar_funcionario(
            id_funcionario=id_funcionario,
            cargo=dados.get('cargo'),
            salario=dados.get('salario'),
            data_contratacao=dados.get('data_contratacao'),
            nome=dados.get('nome'),
            email=dados.get('email'),
            telefone=dados.get('telefone')
        )
        
        return jsonify(resultado), 200 if resultado['success'] else 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar funcionário: {str(e)}'
        }), 500


@funcionario_bp.route('/<int:id_funcionario>/promover', methods=['PUT'])
@token_required
@admin_required
def promover_funcionario(usuario_atual, id_funcionario):
    """
    Promove funcionário (atualiza cargo e salário).
    Requer autenticação de admin.
    
    Request body:
    {
        "novo_cargo": "Gerente",
        "novo_salario": 6000.00
    }
    """
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({'success': False, 'message': 'Dados não fornecidos'}), 400
        
        novo_cargo = dados.get('novo_cargo')
        novo_salario = dados.get('novo_salario')
        
        if not novo_cargo or not novo_salario:
            return jsonify({
                'success': False,
                'message': 'Campos obrigatórios: novo_cargo, novo_salario'
            }), 400
        
        # Promover funcionário
        resultado = funcionario_service.promover_funcionario(
            id_funcionario=id_funcionario,
            novo_cargo=novo_cargo,
            novo_salario=novo_salario
        )
        
        return jsonify(resultado), 200 if resultado['success'] else 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao promover funcionário: {str(e)}'
        }), 500


@funcionario_bp.route('/<int:id_funcionario>/aumento', methods=['PUT'])
@token_required
@admin_required
def dar_aumento(usuario_atual, id_funcionario):
    """
    Dá aumento percentual ao funcionário.
    Requer autenticação de admin.
    
    Request body:
    {
        "percentual": 10.0
    }
    """
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({'success': False, 'message': 'Dados não fornecidos'}), 400
        
        percentual = dados.get('percentual')
        
        if not percentual:
            return jsonify({'success': False, 'message': 'Campo obrigatório: percentual'}), 400
        
        # Dar aumento
        resultado = funcionario_service.dar_aumento(
            id_funcionario=id_funcionario,
            percentual=percentual
        )
        
        return jsonify(resultado), 200 if resultado['success'] else 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao dar aumento: {str(e)}'
        }), 500


@funcionario_bp.route('/<int:id_funcionario>/nivel-acesso', methods=['PUT'])
@token_required
@admin_required
def alterar_nivel_acesso(usuario_atual, id_funcionario):
    """
    Altera nível de acesso do funcionário (promover a admin ou rebaixar).
    Requer autenticação de admin.
    
    Request body:
    {
        "novo_nivel": "admin"
    }
    """
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({'success': False, 'message': 'Dados não fornecidos'}), 400
        
        novo_nivel = dados.get('novo_nivel')
        
        if not novo_nivel:
            return jsonify({'success': False, 'message': 'Campo obrigatório: novo_nivel'}), 400
        
        # Alterar nível
        resultado = funcionario_service.alterar_nivel_acesso(
            id_funcionario=id_funcionario,
            novo_nivel=novo_nivel
        )
        
        return jsonify(resultado), 200 if resultado['success'] else 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao alterar nível de acesso: {str(e)}'
        }), 500


@funcionario_bp.route('/<int:id_funcionario>/senha', methods=['PUT'])
@token_required
def alterar_senha_funcionario(usuario_atual, id_funcionario):
    """
    Altera senha do funcionário.
    Funcionário pode alterar apenas sua própria senha.
    Admin pode alterar senha de qualquer funcionário.
    
    Request body:
    {
        "senha_atual": "senha123",
        "senha_nova": "novaSenha456"
    }
    """
    try:
        # Buscar funcionário
        funcionario = funcionario_service.buscar_funcionario(id_funcionario)
        
        if not funcionario:
            return jsonify({'success': False, 'message': 'Funcionário não encontrado'}), 404
        
        # Verificar permissão
        nivel = usuario_atual.get('nivel_acesso')
        if nivel != 'admin':
            # Funcionário só pode alterar sua própria senha
            if funcionario['id_usuario'] != usuario_atual['id_usuario']:
                return jsonify({'success': False, 'message': 'Permissão negada'}), 403
        
        dados = request.get_json()
        
        if not dados:
            return jsonify({'success': False, 'message': 'Dados não fornecidos'}), 400
        
        senha_atual = dados.get('senha_atual')
        senha_nova = dados.get('senha_nova')
        
        if not senha_atual or not senha_nova:
            return jsonify({
                'success': False,
                'message': 'Campos obrigatórios: senha_atual, senha_nova'
            }), 400
        
        # Alterar senha
        resultado = funcionario_service.alterar_senha_funcionario(
            id_funcionario=id_funcionario,
            senha_atual=senha_atual,
            senha_nova=senha_nova
        )
        
        return jsonify(resultado), 200 if resultado['success'] else 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao alterar senha: {str(e)}'
        }), 500


@funcionario_bp.route('/<int:id_funcionario>/desativar', methods=['PUT'])
@token_required
@admin_required
def desativar_funcionario(usuario_atual, id_funcionario):
    """
    Desativa funcionário (soft delete).
    Requer autenticação de admin.
    """
    try:
        resultado = funcionario_service.desativar_funcionario(id_funcionario)
        
        return jsonify(resultado), 200 if resultado['success'] else 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao desativar funcionário: {str(e)}'
        }), 500


@funcionario_bp.route('/<int:id_funcionario>/ativar', methods=['PUT'])
@token_required
@admin_required
def ativar_funcionario(usuario_atual, id_funcionario):
    """
    Ativa funcionário.
    Requer autenticação de admin.
    """
    try:
        resultado = funcionario_service.ativar_funcionario(id_funcionario)
        
        return jsonify(resultado), 200 if resultado['success'] else 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao ativar funcionário: {str(e)}'
        }), 500
