"""
Rotas de Pedidos de Compra
Endpoints: Gerenciamento de pedidos de compra (entrada de estoque)
"""

from flask import Blueprint, request, jsonify
from dao_mysql.pedido_compra_dao import PedidoCompraDAO
from dao_mysql.item_pedido_compra_dao import ItemPedidoCompraDAO
from dao_mysql.fornecedor_dao import FornecedorDAO
from dao_mysql.funcionario_dao import FuncionarioDAO
from dao_mysql.produto_dao import ProdutoDAO
from service.pedido_compra_service import PedidoCompraService
from service.auth_service import token_required, funcionario_required

pedido_compra_bp = Blueprint('pedido_compra', __name__, url_prefix='/api/pedidos-compra')

# Instanciar DAOs e Service
pedido_compra_dao = PedidoCompraDAO()
item_pedido_compra_dao = ItemPedidoCompraDAO()
fornecedor_dao = FornecedorDAO()
funcionario_dao = FuncionarioDAO()
produto_dao = ProdutoDAO()

pedido_compra_service = PedidoCompraService(
    pedido_compra_dao,
    item_pedido_compra_dao,
    fornecedor_dao,
    produto_dao
)


@pedido_compra_bp.route('/', methods=['POST'])
@token_required
@funcionario_required
def criar_pedido_compra(usuario_atual):
    """
    Cria um novo pedido de compra.
    Requer autenticação e nível funcionario ou superior.
    
    Request body:
    {
        "id_fornecedor": 1,
        "itens": [
            {
                "id_produto": 1,
                "quantidade": 10,
                "preco_custo_unitario": 50.00
            },
            {
                "id_produto": 2,
                "quantidade": 5,
                "preco_custo_unitario": 30.00
            }
        ]
    }
    
    Response:
    {
        "success": true,
        "message": "Pedido de compra criado com sucesso",
        "pedido": {...}
    }
    """
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({'success': False, 'message': 'Dados não fornecidos'}), 400
        
        # Validar campos obrigatórios
        if 'id_fornecedor' not in dados:
            return jsonify({
                'success': False,
                'message': 'Campo "id_fornecedor" é obrigatório'
            }), 400
        
        # Buscar funcionário pelo id_usuario
        funcionario = funcionario_dao.buscar_por_usuario(usuario_atual['id_usuario'])
        if not funcionario:
            return jsonify({
                'success': False,
                'message': 'Usuário não é um funcionário'
            }), 403
        
        id_funcionario = funcionario['id_funcionario']
        
        # Criar pedido com itens
        resultado = pedido_compra_service.criar_pedido_compra(
            id_fornecedor=dados['id_fornecedor'],
            id_funcionario=id_funcionario,
            itens=dados.get('itens')
        )
        
        if resultado['success']:
            return jsonify(resultado), 201
        else:
            return jsonify(resultado), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao criar pedido de compra: {str(e)}'
        }), 500


@pedido_compra_bp.route('/', methods=['GET'])
@token_required
@funcionario_required
def listar_pedidos_compra(usuario_atual):
    """
    Lista pedidos de compra.
    Requer autenticação e nível funcionario ou superior.
    
    Query params (opcionais):
    - status: filtra por status (Pendente, Aprovado, Enviado, Recebido, Cancelado)
    
    Exemplo: /api/pedidos-compra?status=Pendente
    
    Response:
    {
        "success": true,
        "pedidos": [...]
    }
    """
    try:
        status = request.args.get('status')
        
        pedidos = pedido_compra_service.listar_pedidos(status)
        
        return jsonify({
            'success': True,
            'pedidos': pedidos,
            'total': len(pedidos)
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar pedidos de compra: {str(e)}'
        }), 500


@pedido_compra_bp.route('/<int:id_pedido>', methods=['GET'])
@token_required
@funcionario_required
def buscar_pedido_compra(usuario_atual, id_pedido):
    """
    Busca um pedido de compra por ID com seus itens.
    Requer autenticação e nível funcionario ou superior.
    
    Response:
    {
        "success": true,
        "pedido": {
            "id_pedido_compra": 1,
            "status": "Pendente",
            "valor_total": 650.00,
            "itens": [...]
        }
    }
    """
    try:
        pedido = pedido_compra_service.buscar_pedido(id_pedido)
        
        if pedido:
            return jsonify({
                'success': True,
                'pedido': pedido
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Pedido de compra não encontrado'
            }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar pedido de compra: {str(e)}'
        }), 500


@pedido_compra_bp.route('/<int:id_pedido>/itens', methods=['POST'])
@token_required
@funcionario_required
def adicionar_itens(usuario_atual, id_pedido):
    """
    Adiciona itens a um pedido de compra.
    Requer autenticação e nível funcionario ou superior.
    
    Request body:
    {
        "itens": [
            {
                "id_produto": 3,
                "quantidade": 15,
                "preco_custo_unitario": 25.00
            }
        ]
    }
    
    Response:
    {
        "success": true,
        "message": "1 item(ns) adicionado(s) com sucesso"
    }
    """
    try:
        dados = request.get_json()
        
        if not dados or 'itens' not in dados:
            return jsonify({
                'success': False,
                'message': 'Campo "itens" é obrigatório'
            }), 400
        
        resultado = pedido_compra_service.adicionar_itens(id_pedido, dados['itens'])
        
        if resultado['success']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao adicionar itens: {str(e)}'
        }), 500


@pedido_compra_bp.route('/<int:id_pedido>/status', methods=['PUT'])
@token_required
@funcionario_required
def atualizar_status(usuario_atual, id_pedido):
    """
    Atualiza o status de um pedido de compra.
    Requer autenticação e nível funcionario ou superior.
    
    Status válidos: Pendente, Aprovado, Enviado, Recebido, Cancelado
    
    Request body:
    {
        "status": "Aprovado"
    }
    
    Response:
    {
        "success": true,
        "message": "Status atualizado para Aprovado"
    }
    """
    try:
        dados = request.get_json()
        
        if not dados or 'status' not in dados:
            return jsonify({
                'success': False,
                'message': 'Campo "status" é obrigatório'
            }), 400
        
        resultado = pedido_compra_service.atualizar_status(id_pedido, dados['status'])
        
        if resultado['success']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar status: {str(e)}'
        }), 500


@pedido_compra_bp.route('/<int:id_pedido>/receber', methods=['POST'])
@token_required
@funcionario_required
def receber_pedido(usuario_atual, id_pedido):
    """
    Marca o pedido como recebido e atualiza o estoque.
    Requer autenticação e nível funcionario ou superior.
    
    Ação: Incrementa estoque dos produtos e atualiza preço de custo médio.
    
    Response:
    {
        "success": true,
        "message": "Pedido recebido com sucesso. Estoque atualizado."
    }
    """
    try:
        resultado = pedido_compra_service.receber_pedido(id_pedido)
        
        if resultado['success']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao receber pedido: {str(e)}'
        }), 500


@pedido_compra_bp.route('/<int:id_pedido>/cancelar', methods=['POST'])
@token_required
@funcionario_required
def cancelar_pedido(usuario_atual, id_pedido):
    """
    Cancela um pedido de compra.
    Requer autenticação e nível funcionario ou superior.
    
    Response:
    {
        "success": true,
        "message": "Pedido cancelado com sucesso"
    }
    """
    try:
        resultado = pedido_compra_service.cancelar_pedido(id_pedido)
        
        if resultado['success']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao cancelar pedido: {str(e)}'
        }), 500


@pedido_compra_bp.route('/relatorio', methods=['GET'])
@token_required
@funcionario_required
def obter_relatorio_compras(usuario_atual):
    """
    Obtém relatório de compras.
    Requer autenticação e nível funcionario ou superior.
    
    Query params (opcionais):
    - data_inicio: data inicial (YYYY-MM-DD)
    - data_fim: data final (YYYY-MM-DD)
    
    Exemplo: /api/pedidos-compra/relatorio?data_inicio=2025-01-01&data_fim=2025-12-31
    
    Response:
    {
        "success": true,
        "relatorio": [...]
    }
    """
    try:
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        relatorio = pedido_compra_service.obter_relatorio_compras(data_inicio, data_fim)
        
        return jsonify({
            'success': True,
            'relatorio': relatorio,
            'total_registros': len(relatorio)
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao obter relatório: {str(e)}'
        }), 500
