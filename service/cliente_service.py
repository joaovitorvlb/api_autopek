"""
ClienteService - Serviço de Clientes
Lógica de negócio para operações com clientes.
"""

import re
from .usuario_service import UsuarioService


class ClienteService:
    """Serviço de lógica de negócio para clientes"""
    
    def __init__(self, cliente_dao, usuario_dao, nivel_acesso_dao):
        """
        Inicializa o serviço.
        
        Args:
            cliente_dao: Instância de ClienteDAO
            usuario_dao: Instância de UsuarioDAO
            nivel_acesso_dao: Instância de NivelAcessoDAO
        """
        self.cliente_dao = cliente_dao
        self.usuario_dao = usuario_dao
        self.nivel_acesso_dao = nivel_acesso_dao
        self.usuario_service = UsuarioService(usuario_dao, nivel_acesso_dao)
    
    @staticmethod
    def validar_cpf(cpf):
        """
        Valida CPF brasileiro.
        
        Args:
            cpf (str): CPF a ser validado
        
        Returns:
            dict: {'valido': bool, 'mensagem': str}
        """
        if not cpf:
            return {'valido': False, 'mensagem': 'CPF não pode ser vazio'}
        
        # Remove caracteres não numéricos
        cpf_numeros = re.sub(r'\D', '', cpf)
        
        # Verifica se tem 11 dígitos
        if len(cpf_numeros) != 11:
            return {'valido': False, 'mensagem': 'CPF deve ter 11 dígitos'}
        
        # Verifica se não são todos números iguais
        if cpf_numeros == cpf_numeros[0] * 11:
            return {'valido': False, 'mensagem': 'CPF inválido'}
        
        # Valida primeiro dígito verificador
        soma = sum(int(cpf_numeros[i]) * (10 - i) for i in range(9))
        digito1 = 11 - (soma % 11)
        digito1 = digito1 if digito1 < 10 else 0
        
        if int(cpf_numeros[9]) != digito1:
            return {'valido': False, 'mensagem': 'CPF inválido'}
        
        # Valida segundo dígito verificador
        soma = sum(int(cpf_numeros[i]) * (11 - i) for i in range(10))
        digito2 = 11 - (soma % 11)
        digito2 = digito2 if digito2 < 10 else 0
        
        if int(cpf_numeros[10]) != digito2:
            return {'valido': False, 'mensagem': 'CPF inválido'}
        
        return {'valido': True, 'mensagem': 'CPF válido'}
    
    @staticmethod
    def formatar_cpf(cpf):
        """
        Formata CPF para padrão xxx.xxx.xxx-xx
        
        Args:
            cpf (str): CPF em qualquer formato
        
        Returns:
            str: CPF formatado
        """
        cpf_numeros = re.sub(r'\D', '', cpf)
        if len(cpf_numeros) == 11:
            return f"{cpf_numeros[:3]}.{cpf_numeros[3:6]}.{cpf_numeros[6:9]}-{cpf_numeros[9:]}"
        return cpf
    
    def listar_clientes(self, apenas_ativos=True):
        """
        Lista todos os clientes.
        
        Args:
            apenas_ativos (bool): Se True, lista apenas clientes ativos
        
        Returns:
            list: Lista de clientes com dados completos
        """
        if apenas_ativos:
            return self.cliente_dao.listar_clientes_ativos()
        return self.cliente_dao.listar_todos()
    
    def buscar_cliente(self, id_cliente):
        """
        Busca cliente por ID.
        
        Args:
            id_cliente (int): ID do cliente
        
        Returns:
            dict: Dados completos do cliente ou None
        """
        return self.cliente_dao.buscar_por_id(id_cliente)
    
    def buscar_cliente_por_cpf(self, cpf):
        """
        Busca cliente por CPF.
        
        Args:
            cpf (str): CPF do cliente (com ou sem formatação)
        
        Returns:
            dict: Dados completos do cliente ou None
        """
        # Formatar CPF antes de buscar (banco armazena formatado)
        cpf_formatado = self.formatar_cpf(cpf)
        return self.cliente_dao.buscar_por_cpf(cpf_formatado)
    
    def buscar_cliente_por_email(self, email):
        """
        Busca cliente por email.
        
        Args:
            email (str): Email do cliente
        
        Returns:
            dict: Dados completos do cliente ou None
        """
        return self.cliente_dao.buscar_por_email(email)
    
    def criar_cliente_completo(self, nome, email, senha, cpf, telefone=None,
                              cep=None, logradouro=None, numero=None, bairro=None,
                              cidade=None, estado=None, data_nascimento=None,
                              origem_cadastro='site'):
        """
        Cria cliente completo (usuario + cliente).
        
        Args:
            nome (str): Nome do cliente
            email (str): Email do cliente
            senha (str): Senha em texto plano
            cpf (str): CPF do cliente
            telefone (str): Telefone (opcional)
            cep (str): CEP (opcional)
            logradouro (str): Logradouro (opcional)
            numero (str): Número (opcional)
            bairro (str): Bairro (opcional)
            cidade (str): Cidade (opcional)
            estado (str): Estado (opcional)
            data_nascimento (str): Data de nascimento no formato YYYY-MM-DD (opcional)
            origem_cadastro (str): Origem do cadastro (site, app_mobile, loja_fisica)
        
        Returns:
            dict: {'success': bool, 'id_cliente': int, 'id_usuario': int, 'message': str}
        """
        # Validar CPF
        validacao_cpf = self.validar_cpf(cpf)
        if not validacao_cpf['valido']:
            return {'success': False, 'message': validacao_cpf['mensagem']}
        
        # Formatar CPF
        cpf_formatado = self.formatar_cpf(cpf)
        
        # Verificar se CPF já existe
        if self.usuario_dao.verificar_cpf_existe(cpf_formatado):
            return {'success': False, 'message': 'CPF já cadastrado'}
        
        # Buscar nível de acesso 'cliente'
        nivel = self.nivel_acesso_dao.buscar_nivel_acesso_por_nome('cliente')
        if not nivel:
            return {'success': False, 'message': 'Nível de acesso "cliente" não encontrado'}
        
        # Criar usuário com todos os campos
        resultado_usuario = self.usuario_service.criar_usuario(
            nome=nome,
            email=email,
            senha=senha,
            id_nivel_acesso=nivel['id_nivel_acesso'],
            telefone=telefone,
            cpf=cpf_formatado,
            cep=cep,
            logradouro=logradouro,
            numero=numero,
            bairro=bairro,
            cidade=cidade,
            estado=estado,
            data_nascimento=data_nascimento
        )
        
        if not resultado_usuario['success']:
            return resultado_usuario
        
        id_usuario = resultado_usuario['id_usuario']
        
        # Criar cliente
        try:
            id_cliente = self.cliente_dao.inserir(
                id_usuario=id_usuario,
                origem_cadastro=origem_cadastro
            )
            
            return {
                'success': True,
                'id_cliente': id_cliente,
                'id_usuario': id_usuario,
                'message': 'Cliente cadastrado com sucesso'
            }
        except Exception as e:
            # Se falhar, tentar desativar usuário criado
            try:
                self.usuario_dao.ativar_desativar(id_usuario, False)
            except:
                pass
            
            return {'success': False, 'message': f'Erro ao criar cliente: {str(e)}'}
    
    def atualizar_cliente(self, id_cliente, nome=None, email=None, cpf=None, 
                         telefone=None, cep=None, logradouro=None, numero=None,
                         bairro=None, cidade=None, estado=None, data_nascimento=None):
        """
        Atualiza dados do cliente.
        Atualiza tanto dados do cliente quanto do usuário associado.
        
        Args:
            id_cliente (int): ID do cliente
            nome (str): Nome (opcional)
            email (str): Email (opcional)
            cpf (str): CPF (opcional)
            telefone (str): Telefone (opcional)
            cep (str): CEP (opcional)
            logradouro (str): Logradouro (opcional)
            numero (str): Número (opcional)
            bairro (str): Bairro (opcional)
            cidade (str): Cidade (opcional)
            estado (str): Estado (opcional)
            data_nascimento (str): Data de nascimento formato YYYY-MM-DD (opcional)
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        # Verificar se cliente existe
        cliente = self.cliente_dao.buscar_por_id(id_cliente)
        if not cliente:
            return {'success': False, 'message': 'Cliente não encontrado'}
        
        id_usuario = cliente['id_usuario']
        
        # Validar e formatar CPF se fornecido
        cpf_formatado = None
        if cpf is not None:
            validacao_cpf = self.validar_cpf(cpf)
            if not validacao_cpf['valido']:
                return {'success': False, 'message': validacao_cpf['mensagem']}
            
            cpf_formatado = self.formatar_cpf(cpf)
            
            # Verificar se CPF já existe (excluindo o próprio usuário)
            if self.usuario_dao.verificar_cpf_existe(cpf_formatado, id_usuario):
                return {'success': False, 'message': 'CPF já cadastrado'}
        
        # Atualizar dados do usuário
        try:
            resultado = self.usuario_service.atualizar_usuario(
                id_usuario=id_usuario,
                nome=nome,
                email=email,
                cpf=cpf_formatado,
                telefone=telefone,
                cep=cep,
                logradouro=logradouro,
                numero=numero,
                bairro=bairro,
                cidade=cidade,
                estado=estado,
                data_nascimento=data_nascimento
            )
            
            if not resultado['success']:
                return resultado
                
        except Exception as e:
            return {'success': False, 'message': f'Erro ao atualizar dados: {str(e)}'}
        
        return {'success': True, 'message': 'Cliente atualizado com sucesso'}
    
    def desativar_cliente(self, id_cliente):
        """
        Desativa cliente (desativa o usuário associado).
        
        Args:
            id_cliente (int): ID do cliente
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        cliente = self.cliente_dao.buscar_por_id(id_cliente)
        if not cliente:
            return {'success': False, 'message': 'Cliente não encontrado'}
        
        return self.usuario_service.desativar_usuario(cliente['id_usuario'])
    
    def ativar_cliente(self, id_cliente):
        """
        Ativa cliente.
        
        Args:
            id_cliente (int): ID do cliente
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        cliente = self.cliente_dao.buscar_por_id(id_cliente)
        if not cliente:
            return {'success': False, 'message': 'Cliente não encontrado'}
        
        return self.usuario_service.ativar_usuario(cliente['id_usuario'])
    
    def alterar_senha_cliente(self, id_cliente, senha_atual, senha_nova):
        """
        Altera senha do cliente.
        
        Args:
            id_cliente (int): ID do cliente
            senha_atual (str): Senha atual
            senha_nova (str): Nova senha
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        cliente = self.cliente_dao.buscar_por_id(id_cliente)
        if not cliente:
            return {'success': False, 'message': 'Cliente não encontrado'}
        
        return self.usuario_service.alterar_senha(
            cliente['id_usuario'],
            senha_atual,
            senha_nova
        )
