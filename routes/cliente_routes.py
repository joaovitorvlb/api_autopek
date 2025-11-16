"""
Rotas de Clientes
Endpoints CRUD para clientes com autenticação
"""

from flask import Blueprint, request, jsonify
from dao_mysql.cliente_dao import ClienteDAO
from dao_mysql.usuario_dao import UsuarioDAO
from dao_mysql.nivel_acesso_dao import NivelAcessoDAO
from service.cliente_service import ClienteService
from service.auth_service import token_required, admin_required, funcionario_required

cliente_bp = Blueprint('clientes', __name__, url_prefix='/api/clientes')

# Instanciar DAOs e Service
cliente_dao = ClienteDAO()
usuario_dao = UsuarioDAO()
nivel_acesso_dao = NivelAcessoDAO()
cliente_service = ClienteService(cliente_dao, usuario_dao, nivel_acesso_dao)


@cliente_bp.route('/register', methods=['POST'])
def registrar_cliente():
    """
    Registra novo cliente (auto-registro público).
    Não requer autenticação.
    
    Request body:
    {
        "nome": "João Silva",
        "email": "joao.silva@email.com",
        "senha": "senha123",
        "cpf": "123.456.789-00",
        "telefone": "11999999999",
        "cep": "01310-100",
        "logradouro": "Av. Paulista",
        "numero": "1578",
        "bairro": "Bela Vista",
        "cidade": "São Paulo",
        "estado": "SP",
        "data_nascimento": "1990-05-15",
        "origem_cadastro": "site"
    }
    """
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({'success': False, 'message': 'Dados não fornecidos'}), 400
        
        # Extrair dados obrigatórios
        nome = dados.get('nome')
        email = dados.get('email')
        senha = dados.get('senha')
        cpf = dados.get('cpf')
        
        # Validar campos obrigatórios
        if not all([nome, email, senha, cpf]):
            return jsonify({
                'success': False,
                'message': 'Campos obrigatórios: nome, email, senha, cpf'
            }), 400
        
        # Extrair dados opcionais
        telefone = dados.get('telefone')
        cep = dados.get('cep')
        logradouro = dados.get('logradouro')
        numero = dados.get('numero')
        bairro = dados.get('bairro')
        cidade = dados.get('cidade')
        estado = dados.get('estado')
        data_nascimento = dados.get('data_nascimento')
        origem_cadastro = dados.get('origem_cadastro', 'site')  # Default: 'site'
        
        # Criar cliente
        resultado = cliente_service.criar_cliente_completo(
            nome=nome,
            email=email,
            senha=senha,
            cpf=cpf,
            telefone=telefone,
            cep=cep,
            logradouro=logradouro,
            numero=numero,
            bairro=bairro,
            cidade=cidade,
            estado=estado,
            data_nascimento=data_nascimento,
            origem_cadastro=origem_cadastro
        )
        
        if resultado['success']:
            return jsonify(resultado), 201
        else:
            return jsonify(resultado), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao registrar cliente: {str(e)}'
        }), 500


@cliente_bp.route('/', methods=['GET'])
@token_required
@funcionario_required
def listar_clientes(usuario_atual):
    """
    Lista todos os clientes.
    Requer autenticação de funcionário ou admin.
    
    Query params:
        apenas_ativos: true/false (padrão: true)
    """
    try:
        apenas_ativos = request.args.get('apenas_ativos', 'true').lower() == 'true'
        
        clientes = cliente_service.listar_clientes(apenas_ativos)
        
        return jsonify({
            'success': True,
            'clientes': clientes
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar clientes: {str(e)}'
        }), 500


@cliente_bp.route('/<int:id_cliente>', methods=['GET'])
@token_required
def buscar_cliente(usuario_atual, id_cliente):
    """
    Busca cliente por ID.
    Cliente pode ver apenas seus próprios dados.
    Funcionário/Admin podem ver qualquer cliente.
    """
    try:
        cliente = cliente_service.buscar_cliente(id_cliente)
        
        if not cliente:
            return jsonify({'success': False, 'message': 'Cliente não encontrado'}), 404
        
        # Verificar permissão
        nivel = usuario_atual.get('nivel_acesso')
        if nivel == 'cliente':
            # Cliente só pode ver seus próprios dados
            if cliente['id_usuario'] != usuario_atual['id_usuario']:
                return jsonify({'success': False, 'message': 'Permissão negada'}), 403
        
        return jsonify({
            'success': True,
            'cliente': cliente
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar cliente: {str(e)}'
        }), 500


@cliente_bp.route('/cpf/<cpf>', methods=['GET'])
@token_required
@funcionario_required
def buscar_cliente_por_cpf(usuario_atual, cpf):
    """
    Busca cliente por CPF.
    Requer autenticação de funcionário ou admin.
    """
    try:
        cliente = cliente_service.buscar_cliente_por_cpf(cpf)
        
        if not cliente:
            return jsonify({'success': False, 'message': 'Cliente não encontrado'}), 404
        
        return jsonify({
            'success': True,
            'cliente': cliente
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar cliente: {str(e)}'
        }), 500


@cliente_bp.route('/<int:id_cliente>', methods=['PUT'])
@token_required
def atualizar_cliente(usuario_atual, id_cliente):
    """
    Atualiza dados do cliente.
    Cliente pode atualizar apenas seus próprios dados.
    Funcionário/Admin podem atualizar qualquer cliente.
    
    Request body (todos opcionais):
    {
        "nome": "João Silva Santos",
        "email": "joao.novo@email.com",
        "telefone": "11988887777",
        "cpf": "987.654.321-00",
        "cep": "01310-100",
        "logradouro": "Av. Paulista",
        "numero": "2000",
        "bairro": "Bela Vista",
        "cidade": "São Paulo",
        "estado": "SP",
        "data_nascimento": "1995-03-20"
    }
    """
    try:
        # Buscar cliente
        cliente = cliente_service.buscar_cliente(id_cliente)
        
        if not cliente:
            return jsonify({'success': False, 'message': 'Cliente não encontrado'}), 404
        
        # Verificar permissão
        nivel = usuario_atual.get('nivel_acesso')
        if nivel == 'cliente':
            # Cliente só pode atualizar seus próprios dados
            if cliente['id_usuario'] != usuario_atual['id_usuario']:
                return jsonify({'success': False, 'message': 'Permissão negada'}), 403
        
        dados = request.get_json()
        
        if not dados:
            return jsonify({'success': False, 'message': 'Dados não fornecidos'}), 400
        
        # Atualizar cliente
        resultado = cliente_service.atualizar_cliente(
            id_cliente=id_cliente,
            nome=dados.get('nome'),
            email=dados.get('email'),
            cpf=dados.get('cpf'),
            telefone=dados.get('telefone'),
            cep=dados.get('cep'),
            logradouro=dados.get('logradouro'),
            numero=dados.get('numero'),
            bairro=dados.get('bairro'),
            cidade=dados.get('cidade'),
            estado=dados.get('estado'),
            data_nascimento=dados.get('data_nascimento')
        )
        
        return jsonify(resultado), 200 if resultado['success'] else 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar cliente: {str(e)}'
        }), 500


@cliente_bp.route('/<int:id_cliente>/senha', methods=['PUT'])
@token_required
def alterar_senha_cliente(usuario_atual, id_cliente):
    """
    Altera senha do cliente.
    Cliente pode alterar apenas sua própria senha.
    
    Request body:
    {
        "senha_atual": "senha123",
        "senha_nova": "novaSenha456"
    }
    """
    try:
        # Buscar cliente
        cliente = cliente_service.buscar_cliente(id_cliente)
        
        if not cliente:
            return jsonify({'success': False, 'message': 'Cliente não encontrado'}), 404
        
        # Verificar permissão (apenas o próprio cliente)
        if cliente['id_usuario'] != usuario_atual['id_usuario']:
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
        resultado = cliente_service.alterar_senha_cliente(
            id_cliente=id_cliente,
            senha_atual=senha_atual,
            senha_nova=senha_nova
        )
        
        return jsonify(resultado), 200 if resultado['success'] else 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao alterar senha: {str(e)}'
        }), 500


@cliente_bp.route('/<int:id_cliente>/desativar', methods=['PUT'])
@token_required
@funcionario_required
def desativar_cliente(usuario_atual, id_cliente):
    """
    Desativa cliente (soft delete).
    Requer autenticação de funcionário ou admin.
    """
    try:
        resultado = cliente_service.desativar_cliente(id_cliente)
        
        return jsonify(resultado), 200 if resultado['success'] else 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao desativar cliente: {str(e)}'
        }), 500


@cliente_bp.route('/<int:id_cliente>/ativar', methods=['PUT'])
@token_required
@funcionario_required
def ativar_cliente(usuario_atual, id_cliente):
    """
    Ativa cliente.
    Requer autenticação de funcionário ou admin.
    """
    try:
        resultado = cliente_service.ativar_cliente(id_cliente)
        
        return jsonify(resultado), 200 if resultado['success'] else 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao ativar cliente: {str(e)}'
        }), 500
