"""
Rotas de Pedidos de Venda
Endpoints: Gerenciamento de pedidos de venda (saída de estoque)
"""

from flask import Blueprint, request, jsonify
from dao_sqlite.pedido_venda_dao import PedidoVendaDAO
from dao_sqlite.item_pedido_venda_dao import ItemPedidoVendaDAO
from dao_sqlite.cliente_dao import ClienteDAO
from dao_sqlite.produto_dao import ProdutoDAO
from service.pedido_venda_service import PedidoVendaService
from service.auth_service import token_required, funcionario_required

pedido_venda_bp = Blueprint('pedido_venda', __name__, url_prefix='/api/pedidos-venda')

# Instanciar DAOs e Service
pedido_venda_dao = PedidoVendaDAO()
item_pedido_venda_dao = ItemPedidoVendaDAO()
cliente_dao = ClienteDAO()
produto_dao = ProdutoDAO()

pedido_venda_service = PedidoVendaService(
    pedido_venda_dao,
    item_pedido_venda_dao,
    cliente_dao,
    produto_dao
)


@pedido_venda_bp.route('/', methods=['POST'])
@token_required
@funcionario_required
def criar_pedido_venda(usuario_atual):
    """
    Cria um novo pedido de venda.
    Requer autenticação e nível funcionario ou superior.
    
    Request body:
    {
        "id_cliente": 1,
        "itens": [
            {
                "id_produto": 1,
                "quantidade": 2,
                "preco_venda_unitario": 99.90
            },
            {
                "id_produto": 2,
                "quantidade": 1,
                "preco_venda_unitario": 149.90
            }
        ]
    }
    
    Response:
    {
        "success": true,
        "message": "Pedido de venda criado com sucesso",
        "pedido": {...}
    }
    """
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({'success': False, 'message': 'Dados não fornecidos'}), 400
        
        # Validar campos obrigatórios
        if 'id_cliente' not in dados:
            return jsonify({
                'success': False,
                'message': 'Campo "id_cliente" é obrigatório'
            }), 400
        
        # ID do funcionário é o usuário autenticado
        id_funcionario = usuario_atual['id_usuario']
        
        # Criar pedido com itens
        resultado = pedido_venda_service.criar_pedido_venda(
            id_cliente=dados['id_cliente'],
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
            'message': f'Erro ao criar pedido de venda: {str(e)}'
        }), 500


@pedido_venda_bp.route('/', methods=['GET'])
@token_required
@funcionario_required
def listar_pedidos_venda(usuario_atual):
    """
    Lista pedidos de venda.
    Requer autenticação e nível funcionario ou superior.
    
    Query params (opcionais):
    - status: filtra por status (Pendente, Confirmado, Preparando, Enviado, Entregue, Cancelado)
    
    Exemplo: /api/pedidos-venda?status=Confirmado
    
    Response:
    {
        "success": true,
        "pedidos": [...]
    }
    """
    try:
        status = request.args.get('status')
        
        pedidos = pedido_venda_service.listar_pedidos(status)
        
        return jsonify({
            'success': True,
            'pedidos': pedidos,
            'total': len(pedidos)
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar pedidos de venda: {str(e)}'
        }), 500


@pedido_venda_bp.route('/<int:id_pedido>', methods=['GET'])
@token_required
@funcionario_required
def buscar_pedido_venda(usuario_atual, id_pedido):
    """
    Busca um pedido de venda por ID com seus itens.
    Requer autenticação e nível funcionario ou superior.
    
    Response:
    {
        "success": true,
        "pedido": {
            "id_pedido_venda": 1,
            "status": "Confirmado",
            "valor_total": 349.70,
            "itens": [...]
        }
    }
    """
    try:
        pedido = pedido_venda_service.buscar_pedido(id_pedido)
        
        if pedido:
            return jsonify({
                'success': True,
                'pedido': pedido
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Pedido de venda não encontrado'
            }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar pedido de venda: {str(e)}'
        }), 500


@pedido_venda_bp.route('/<int:id_pedido>/itens', methods=['POST'])
@token_required
@funcionario_required
def adicionar_itens(usuario_atual, id_pedido):
    """
    Adiciona itens a um pedido de venda.
    Verifica disponibilidade em estoque.
    Requer autenticação e nível funcionario ou superior.
    
    Request body:
    {
        "itens": [
            {
                "id_produto": 3,
                "quantidade": 1,
                "preco_venda_unitario": 79.90
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
        
        resultado = pedido_venda_service.adicionar_itens(id_pedido, dados['itens'])
        
        if resultado['success']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao adicionar itens: {str(e)}'
        }), 500


@pedido_venda_bp.route('/<int:id_pedido>/status', methods=['PUT'])
@token_required
@funcionario_required
def atualizar_status(usuario_atual, id_pedido):
    """
    Atualiza o status de um pedido de venda.
    Requer autenticação e nível funcionario ou superior.
    
    Status válidos: Pendente, Confirmado, Preparando, Enviado, Entregue, Cancelado
    
    Request body:
    {
        "status": "Preparando"
    }
    
    Response:
    {
        "success": true,
        "message": "Status atualizado para Preparando"
    }
    """
    try:
        dados = request.get_json()
        
        if not dados or 'status' not in dados:
            return jsonify({
                'success': False,
                'message': 'Campo "status" é obrigatório'
            }), 400
        
        resultado = pedido_venda_service.atualizar_status(id_pedido, dados['status'])
        
        if resultado['success']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar status: {str(e)}'
        }), 500


@pedido_venda_bp.route('/<int:id_pedido>/confirmar', methods=['POST'])
@token_required
@funcionario_required
def confirmar_pedido(usuario_atual, id_pedido):
    """
    Confirma o pedido e deduz o estoque.
    Requer autenticação e nível funcionario ou superior.
    
    Ação: Decrementa estoque dos produtos.
    
    Response:
    {
        "success": true,
        "message": "Pedido confirmado com sucesso. Estoque atualizado."
    }
    """
    try:
        resultado = pedido_venda_service.confirmar_pedido(id_pedido)
        
        if resultado['success']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao confirmar pedido: {str(e)}'
        }), 500


@pedido_venda_bp.route('/<int:id_pedido>/cancelar', methods=['POST'])
@token_required
@funcionario_required
def cancelar_pedido(usuario_atual, id_pedido):
    """
    Cancela um pedido de venda.
    Requer autenticação e nível funcionario ou superior.
    
    Query params (opcionais):
    - devolver_estoque: true/false (padrão: true) - Devolve produtos ao estoque se pedido confirmado
    
    Exemplo: /api/pedidos-venda/1/cancelar?devolver_estoque=true
    
    Response:
    {
        "success": true,
        "message": "Pedido cancelado com sucesso. Estoque devolvido."
    }
    """
    try:
        devolver_estoque = request.args.get('devolver_estoque', 'true').lower() == 'true'
        
        resultado = pedido_venda_service.cancelar_pedido(id_pedido, devolver_estoque)
        
        if resultado['success']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao cancelar pedido: {str(e)}'
        }), 500


@pedido_venda_bp.route('/<int:id_pedido>/lucro', methods=['GET'])
@token_required
@funcionario_required
def calcular_lucro(usuario_atual, id_pedido):
    """
    Calcula o lucro de um pedido de venda.
    Requer autenticação e nível funcionario ou superior.
    
    Response:
    {
        "success": true,
        "lucro": {
            "valor_venda": 349.70,
            "custo_total": 200.00,
            "lucro_bruto": 149.70,
            "margem_percentual": 42.8
        }
    }
    """
    try:
        resultado = pedido_venda_service.calcular_lucro(id_pedido)
        
        if resultado['success']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao calcular lucro: {str(e)}'
        }), 500


@pedido_venda_bp.route('/relatorio', methods=['GET'])
@token_required
@funcionario_required
def obter_relatorio_vendas(usuario_atual):
    """
    Obtém relatório de vendas com lucro.
    Requer autenticação e nível funcionario ou superior.
    
    Query params (opcionais):
    - data_inicio: data inicial (YYYY-MM-DD)
    - data_fim: data final (YYYY-MM-DD)
    
    Exemplo: /api/pedidos-venda/relatorio?data_inicio=2025-01-01&data_fim=2025-12-31
    
    Response:
    {
        "success": true,
        "relatorio": [...]
    }
    """
    try:
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        relatorio = pedido_venda_service.obter_relatorio_vendas(data_inicio, data_fim)
        
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


@pedido_venda_bp.route('/produtos-mais-vendidos', methods=['GET'])
@token_required
@funcionario_required
def obter_produtos_mais_vendidos(usuario_atual):
    """
    Obtém os produtos mais vendidos.
    Requer autenticação e nível funcionario ou superior.
    
    Query params (opcionais):
    - limite: número de produtos (padrão: 10)
    
    Exemplo: /api/pedidos-venda/produtos-mais-vendidos?limite=5
    
    Response:
    {
        "success": true,
        "produtos": [...]
    }
    """
    try:
        limite = request.args.get('limite', 10, type=int)
        
        produtos = pedido_venda_service.obter_produtos_mais_vendidos(limite)
        
        return jsonify({
            'success': True,
            'produtos': produtos,
            'total': len(produtos)
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao obter produtos mais vendidos: {str(e)}'
        }), 500
