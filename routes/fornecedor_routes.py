"""
Rotas de Fornecedores
Endpoints: CRUD de fornecedores
"""

from flask import Blueprint, request, jsonify
from dao_mysql.fornecedor_dao import FornecedorDAO
from service.fornecedor_service import FornecedorService
from service.auth_service import token_required, funcionario_required, admin_required

fornecedor_bp = Blueprint('fornecedor', __name__, url_prefix='/api/fornecedores')

# Instanciar DAO e Service
fornecedor_dao = FornecedorDAO()
fornecedor_service = FornecedorService(fornecedor_dao)


@fornecedor_bp.route('/', methods=['POST'])
@token_required
@funcionario_required
def criar_fornecedor(usuario_atual):
    """
    Cria um novo fornecedor.
    Requer autenticação e nível funcionario ou superior.
    
    Request body:
    {
        "razao_social": "Fornecedor XYZ Ltda",
        "nome_fantasia": "Fornecedor XYZ",
        "cnpj": "12.345.678/0001-90",
        "email": "contato@fornecedor.com",
        "telefone": "(11) 98765-4321",
        "endereco": "Rua das Peças, 123 - São Paulo, SP"
    }
    
    Response:
    {
        "success": true,
        "message": "Fornecedor criado com sucesso",
        "fornecedor": {...}
    }
    """
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({'success': False, 'message': 'Dados não fornecidos'}), 400
        
        # Campos obrigatórios
        campos_obrigatorios = ['razao_social', 'nome_fantasia', 'cnpj']
        for campo in campos_obrigatorios:
            if campo not in dados:
                return jsonify({
                    'success': False,
                    'message': f"Campo '{campo}' é obrigatório"
                }), 400
        
        # Criar fornecedor
        resultado = fornecedor_service.criar_fornecedor(
            razao_social=dados['razao_social'],
            nome_fantasia=dados['nome_fantasia'],
            cnpj=dados['cnpj'],
            email=dados.get('email'),
            telefone=dados.get('telefone'),
            endereco=dados.get('endereco')
        )
        
        if resultado['success']:
            return jsonify(resultado), 201
        else:
            return jsonify(resultado), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao criar fornecedor: {str(e)}'
        }), 500


@fornecedor_bp.route('/', methods=['GET'])
@token_required
@funcionario_required
def listar_fornecedores(usuario_atual):
    """
    Lista todos os fornecedores.
    Requer autenticação e nível funcionario ou superior.
    
    Response:
    {
        "success": true,
        "fornecedores": [...]
    }
    """
    try:
        fornecedores = fornecedor_service.listar_fornecedores()
        
        return jsonify({
            'success': True,
            'fornecedores': fornecedores,
            'total': len(fornecedores)
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar fornecedores: {str(e)}'
        }), 500


@fornecedor_bp.route('/<int:id_fornecedor>', methods=['GET'])
@token_required
@funcionario_required
def buscar_fornecedor(usuario_atual, id_fornecedor):
    """
    Busca um fornecedor por ID.
    Requer autenticação e nível funcionario ou superior.
    
    Response:
    {
        "success": true,
        "fornecedor": {...}
    }
    """
    try:
        resultado = fornecedor_service.buscar_fornecedor(id_fornecedor)
        
        if resultado['success']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar fornecedor: {str(e)}'
        }), 500


@fornecedor_bp.route('/buscar', methods=['GET'])
@token_required
@funcionario_required
def buscar_fornecedores_por_nome(usuario_atual):
    """
    Busca fornecedores por nome (razão social ou nome fantasia).
    Requer autenticação e nível funcionario ou superior.
    
    Query params:
    - nome: termo de busca
    - apenas_ativos: true/false (padrão: true)
    
    Exemplo: /api/fornecedores/buscar?nome=distribuidora&apenas_ativos=true
    
    Response:
    {
        "success": true,
        "fornecedores": [...]
    }
    """
    try:
        nome = request.args.get('nome', '').strip()
        apenas_ativos = request.args.get('apenas_ativos', 'true').lower() == 'true'
        
        if not nome:
            return jsonify({
                'success': False,
                'message': 'Parâmetro "nome" é obrigatório'
            }), 400
        
        fornecedores = fornecedor_service.buscar_por_nome(nome, apenas_ativos)
        
        return jsonify({
            'success': True,
            'fornecedores': fornecedores,
            'total': len(fornecedores)
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar fornecedores: {str(e)}'
        }), 500


@fornecedor_bp.route('/<int:id_fornecedor>', methods=['PUT'])
@token_required
@funcionario_required
def atualizar_fornecedor(usuario_atual, id_fornecedor):
    """
    Atualiza um fornecedor existente.
    Requer autenticação e nível funcionario ou superior.
    
    Request body (todos os campos são opcionais):
    {
        "razao_social": "Nova Razão Social",
        "nome_fantasia": "Novo Nome Fantasia",
        "cnpj": "98.765.432/0001-10",
        "email": "novo@email.com",
        "telefone": "(11) 11111-1111",
        "endereco": "Novo Endereço"
    }
    
    Response:
    {
        "success": true,
        "message": "Fornecedor atualizado com sucesso",
        "fornecedor": {...}
    }
    """
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({'success': False, 'message': 'Dados não fornecidos'}), 400
        
        # Atualizar fornecedor
        resultado = fornecedor_service.atualizar_fornecedor(id_fornecedor, **dados)
        
        if resultado['success']:
            return jsonify(resultado), 200
        else:
            status_code = 404 if 'não encontrado' in resultado['message'] else 400
            return jsonify(resultado), status_code
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar fornecedor: {str(e)}'
        }), 500


@fornecedor_bp.route('/<int:id_fornecedor>', methods=['DELETE'])
@token_required
@admin_required
def deletar_fornecedor(usuario_atual, id_fornecedor):
    """
    Deleta um fornecedor permanentemente.
    Requer autenticação e nível admin.
    Não permite deletar se houver pedidos de compra vinculados.
    
    Response:
    {
        "success": true,
        "message": "Fornecedor deletado com sucesso"
    }
    """
    try:
        resultado = fornecedor_service.deletar_fornecedor(id_fornecedor)
        
        if resultado['success']:
            return jsonify(resultado), 200
        else:
            status_code = 404 if 'não encontrado' in resultado['message'] else 400
            return jsonify(resultado), status_code
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao deletar fornecedor: {str(e)}'
        }), 500


@fornecedor_bp.route('/<int:id_fornecedor>/desativar', methods=['PATCH'])
@token_required
@funcionario_required
def desativar_fornecedor(usuario_atual, id_fornecedor):
    """
    Desativa um fornecedor (soft delete).
    Requer autenticação e nível funcionario ou superior.
    
    Response:
    {
        "success": true,
        "message": "Fornecedor desativado com sucesso"
    }
    """
    try:
        resultado = fornecedor_service.desativar_fornecedor(id_fornecedor)
        
        if resultado['success']:
            return jsonify(resultado), 200
        else:
            status_code = 404 if 'não encontrado' in resultado['message'] else 400
            return jsonify(resultado), status_code
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao desativar fornecedor: {str(e)}'
        }), 500


@fornecedor_bp.route('/<int:id_fornecedor>/ativar', methods=['PATCH'])
@token_required
@funcionario_required
def ativar_fornecedor(usuario_atual, id_fornecedor):
    """
    Ativa um fornecedor.
    Requer autenticação e nível funcionario ou superior.
    
    Response:
    {
        "success": true,
        "message": "Fornecedor ativado com sucesso"
    }
    """
    try:
        resultado = fornecedor_service.ativar_fornecedor(id_fornecedor)
        
        if resultado['success']:
            return jsonify(resultado), 200
        else:
            status_code = 404 if 'não encontrado' in resultado['message'] else 400
            return jsonify(resultado), status_code
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao ativar fornecedor: {str(e)}'
        }), 500


@fornecedor_bp.route('/estatisticas', methods=['GET'])
@token_required
@funcionario_required
def obter_estatisticas(usuario_atual):
    """
    Obtém estatísticas dos fornecedores.
    Requer autenticação e nível funcionario ou superior.
    
    Response:
    {
        "success": true,
        "estatisticas": {
            "total_fornecedores": 10,
            "fornecedores_com_pedidos": 7
        }
    }
    """
    try:
        estatisticas = fornecedor_service.obter_estatisticas()
        
        return jsonify({
            'success': True,
            'estatisticas': estatisticas
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao obter estatísticas: {str(e)}'
        }), 500
