"""
Rotas de Produtos
Endpoints: CRUD de produtos + upload de imagens
"""

from flask import Blueprint, request, jsonify, current_app
from dao_sqlite.produto_dao import ProdutoDAO
from service.produto_service import ProdutoService
from service.auth_service import token_required, admin_required, funcionario_required

produto_bp = Blueprint('produto', __name__, url_prefix='/api/produtos')

# Instanciar DAO
produto_dao = ProdutoDAO()


@produto_bp.route('/', methods=['POST'])
@token_required
@funcionario_required
def criar_produto(usuario_atual):
    """
    Cria um novo produto com imagem.
    Requer autenticação e nível funcionario ou superior.
    
    Request (multipart/form-data):
    - nome: string (obrigatório)
    - descricao: string (opcional)
    - preco: float (obrigatório)
    - estoque: int (obrigatório)
    - imagem: file (opcional) - PNG, JPG ou JPEG
    
    Response:
    {
        "success": true,
        "message": "Produto criado com sucesso",
        "produto": {
            "id_produto": 1,
            "nome": "Nome do Produto",
            "descricao": "Descrição opcional",
            "preco_venda": 99.90,
            "estoque_atual": 10,
            "imagens": {
                "thumbnail": "http://localhost:5000/static/images/produtos/Produto_1_abc123_thumbnail.png",
                "medium": "http://localhost:5000/static/images/produtos/Produto_1_abc123_medium.png",
                "large": "http://localhost:5000/static/images/produtos/Produto_1_abc123_large.png"
            }
        }
    }
    """
    try:
        # Verificar se é JSON (sem imagem) ou form-data (com imagem)
        if request.is_json:
            # Modo JSON (compatibilidade retroativa)
            dados = request.get_json()
            imagem = None
        else:
            # Modo form-data (com imagem)
            dados = request.form.to_dict()
            imagem = request.files.get('imagem')
        
        if not dados:
            return jsonify({'success': False, 'message': 'Dados não fornecidos'}), 400
        
        # Validar campos obrigatórios
        campos_obrigatorios = ['nome', 'preco', 'estoque']
        for campo in campos_obrigatorios:
            if campo not in dados:
                return jsonify({
                    'success': False,
                    'message': f"Campo '{campo}' é obrigatório"
                }), 400
        
        # Converter tipos (form-data vem como string)
        try:
            preco = float(dados['preco'])
            estoque = int(dados['estoque'])
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Preço deve ser número e estoque deve ser inteiro'
            }), 400
        
        # Criar produto
        resultado = ProdutoService.criar_produto(
            produto_dao,
            nome=dados['nome'],
            preco=preco,
            estoque=estoque,
            descricao=dados.get('descricao'),
            imagem=imagem,
            request_host=request.host_url.rstrip('/')
        )
        
        if resultado['success']:
            return jsonify(resultado), 201
        else:
            return jsonify(resultado), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao criar produto: {str(e)}'
        }), 500


@produto_bp.route('/', methods=['GET'])
def listar_produtos():
    """
    Lista todos os produtos.
    Rota pública (não requer autenticação).
    
    Response:
    {
        "success": true,
        "produtos": [
            {
                "id_produto": 1,
                "nome": "Produto 1",
                "preco": 99.90,
                "estoque": 10,
                "imagens": {...}
            }
        ]
    }
    """
    try:
        produtos = produto_dao.listar_todos()
        
        # Obter host da requisição
        request_host = request.host_url.rstrip('/')
        
        # Processar imagens de cada produto com URLs completas
        produtos_processados = [
            ProdutoService.process_product_images(p, request_host) for p in produtos
        ]
        
        return jsonify({
            'success': True,
            'produtos': produtos_processados
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar produtos: {str(e)}'
        }), 500


@produto_bp.route('/<int:id_produto>', methods=['GET'])
def buscar_produto(id_produto):
    """
    Busca um produto por ID.
    Rota pública (não requer autenticação).
    
    Response:
    {
        "success": true,
        "produto": {
            "id_produto": 1,
            "nome": "Produto 1",
            "descricao": "Descrição",
            "preco": 99.90,
            "estoque": 10,
            "imagens": {...}
        }
    }
    """
    try:
        produto = produto_dao.buscar_por_id(id_produto)
        
        if not produto:
            return jsonify({
                'success': False,
                'message': 'Produto não encontrado'
            }), 404
        
        # Obter host da requisição
        request_host = request.host_url.rstrip('/')
        
        # Processar imagens com URLs completas
        produto_processado = ProdutoService.process_product_images(produto, request_host)
        
        return jsonify({
            'success': True,
            'produto': produto_processado
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar produto: {str(e)}'
        }), 500


@produto_bp.route('/<int:id_produto>', methods=['PUT'])
@token_required
@funcionario_required
def atualizar_produto(usuario_atual, id_produto):
    """
    Atualiza um produto existente.
    Requer autenticação e nível funcionario ou superior.
    
    Request body (todos os campos são opcionais):
    {
        "nome": "Novo Nome",
        "descricao": "Nova Descrição",
        "preco": 149.90,
        "estoque": 20
    }
    
    Response:
    {
        "success": true,
        "message": "Produto atualizado com sucesso",
        "produto": {...}
    }
    """
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({'success': False, 'message': 'Dados não fornecidos'}), 400
        
        # Atualizar produto
        resultado = ProdutoService.atualizar_produto(
            produto_dao,
            id_produto,
            request_host=request.host_url.rstrip('/'),
            **dados
        )
        
        if resultado['success']:
            return jsonify(resultado), 200
        else:
            status_code = 404 if 'não encontrado' in resultado['message'] else 400
            return jsonify(resultado), status_code
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar produto: {str(e)}'
        }), 500


@produto_bp.route('/<int:id_produto>', methods=['DELETE'])
@token_required
@admin_required
def deletar_produto(usuario_atual, id_produto):
    """
    Deleta um produto.
    Requer autenticação e nível admin.
    
    Response:
    {
        "success": true,
        "message": "Produto deletado com sucesso"
    }
    """
    try:
        # Verificar se produto existe
        produto = produto_dao.buscar_por_id(id_produto)
        if not produto:
            return jsonify({
                'success': False,
                'message': 'Produto não encontrado'
            }), 404
        
        # Deletar produto
        sucesso = produto_dao.deletar(id_produto)
        
        if sucesso:
            return jsonify({
                'success': True,
                'message': 'Produto deletado com sucesso'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Erro ao deletar produto'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao deletar produto: {str(e)}'
        }), 500


@produto_bp.route('/<int:id_produto>/imagem', methods=['POST'])
@token_required
@funcionario_required
def upload_imagem(usuario_atual, id_produto):
    """
    Faz upload de imagem para um produto.
    Requer autenticação e nível funcionario ou superior.
    
    A imagem é automaticamente processada em múltiplas resoluções:
    - thumbnail: 150x150
    - medium: 400x400
    - large: 800x800
    
    Request:
    - Content-Type: multipart/form-data
    - Campo: "imagem" (arquivo)
    
    Response:
    {
        "success": true,
        "message": "Imagem enviada com sucesso",
        "imagens": {
            "thumbnail": "produto_1_thumbnail.jpg",
            "medium": "produto_1_medium.jpg",
            "large": "produto_1_large.jpg"
        }
    }
    """
    try:
        # Verificar se produto existe
        produto = produto_dao.buscar_por_id(id_produto)
        if not produto:
            return jsonify({
                'success': False,
                'message': 'Produto não encontrado'
            }), 404
        
        # Verificar se arquivo foi enviado
        if 'imagem' not in request.files:
            return jsonify({
                'success': False,
                'message': 'Nenhum arquivo enviado. Use o campo "imagem"'
            }), 400
        
        file = request.files['imagem']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'Nenhum arquivo selecionado'
            }), 400
        
        # Obter pasta de upload da configuração
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/images/produtos')
        
        # Salvar e processar imagem
        resultado = ProdutoService.salvar_imagem_produto(file, id_produto, upload_folder)
        
        if resultado['success']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao fazer upload de imagem: {str(e)}'
        }), 500


@produto_bp.route('/buscar', methods=['GET'])
def buscar_produtos_por_nome():
    """
    Busca produtos por nome (case-insensitive, busca parcial).
    Rota pública (não requer autenticação).
    
    Query params:
    - nome: termo de busca
    
    Exemplo: /api/produtos/buscar?nome=camiseta
    
    Response:
    {
        "success": true,
        "produtos": [...]
    }
    """
    try:
        nome = request.args.get('nome', '').strip()
        
        if not nome:
            return jsonify({
                'success': False,
                'message': 'Parâmetro "nome" é obrigatório'
            }), 400
        
        produtos = produto_dao.buscar_por_nome(nome)
        
        # Obter host da requisição
        request_host = request.host_url.rstrip('/')
        
        # Processar imagens com URLs completas
        produtos_processados = [
            ProdutoService.process_product_images(p, request_host) for p in produtos
        ]
        
        return jsonify({
            'success': True,
            'produtos': produtos_processados,
            'total': len(produtos_processados)
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar produtos: {str(e)}'
        }), 500
