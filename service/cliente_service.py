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
        return self.cliente_dao.listar_todos(apenas_ativos)
    
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
            cpf (str): CPF do cliente
        
        Returns:
            dict: Dados completos do cliente ou None
        """
        return self.cliente_dao.buscar_por_cpf(cpf)
    
    def buscar_cliente_por_email(self, email):
        """
        Busca cliente por email.
        
        Args:
            email (str): Email do cliente
        
        Returns:
            dict: Dados completos do cliente ou None
        """
        return self.cliente_dao.buscar_por_email(email)
    
    def criar_cliente_completo(self, nome, email, senha, cpf, endereco, telefone=None):
        """
        Cria cliente completo (usuario + cliente).
        
        Args:
            nome (str): Nome do cliente
            email (str): Email do cliente
            senha (str): Senha em texto plano
            cpf (str): CPF do cliente
            endereco (str): Endereço do cliente
            telefone (str): Telefone (opcional)
        
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
        if self.cliente_dao.verificar_cpf_existe(cpf_formatado):
            return {'success': False, 'message': 'CPF já cadastrado'}
        
        # Validar endereço
        if not endereco or len(endereco.strip()) < 10:
            return {'success': False, 'message': 'Endereço deve ter no mínimo 10 caracteres'}
        
        # Buscar nível de acesso 'cliente'
        nivel = self.nivel_acesso_dao.buscar_nivel_acesso_por_nome('cliente')
        if not nivel:
            return {'success': False, 'message': 'Nível de acesso "cliente" não encontrado'}
        
        # Criar usuário
        resultado_usuario = self.usuario_service.criar_usuario(
            nome=nome,
            email=email,
            senha=senha,
            id_nivel_acesso=nivel['id_nivel_acesso'],
            telefone=telefone
        )
        
        if not resultado_usuario['success']:
            return resultado_usuario
        
        id_usuario = resultado_usuario['id_usuario']
        
        # Criar cliente
        try:
            id_cliente = self.cliente_dao.inserir(
                id_usuario=id_usuario,
                cpf=cpf_formatado,
                endereco=endereco.strip()
            )
            
            return {
                'success': True,
                'id_cliente': id_cliente,
                'id_usuario': id_usuario,
                'message': 'Cliente criado com sucesso'
            }
        except Exception as e:
            # Se falhar, tentar desativar usuário criado
            try:
                self.usuario_dao.ativar_desativar(id_usuario, False)
            except:
                pass
            
            return {'success': False, 'message': f'Erro ao criar cliente: {str(e)}'}
    
    def atualizar_cliente(self, id_cliente, cpf=None, endereco=None, 
                         nome=None, email=None, telefone=None):
        """
        Atualiza dados do cliente.
        Atualiza tanto dados do cliente quanto do usuário associado.
        
        Args:
            id_cliente (int): ID do cliente
            cpf (str): CPF (opcional)
            endereco (str): Endereço (opcional)
            nome (str): Nome (opcional) - atualiza no usuario
            email (str): Email (opcional) - atualiza no usuario
            telefone (str): Telefone (opcional) - atualiza no usuario
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        # Verificar se cliente existe
        cliente = self.cliente_dao.buscar_por_id(id_cliente)
        if not cliente:
            return {'success': False, 'message': 'Cliente não encontrado'}
        
        id_usuario = cliente['id_usuario']
        
        # Atualizar dados do cliente
        if cpf is not None or endereco is not None:
            # Validar CPF se fornecido
            if cpf is not None:
                validacao_cpf = self.validar_cpf(cpf)
                if not validacao_cpf['valido']:
                    return {'success': False, 'message': validacao_cpf['mensagem']}
                
                cpf_formatado = self.formatar_cpf(cpf)
                
                # Verificar se CPF já existe (excluindo o próprio cliente)
                if self.cliente_dao.verificar_cpf_existe(cpf_formatado, id_cliente):
                    return {'success': False, 'message': 'CPF já cadastrado'}
            else:
                cpf_formatado = None
            
            # Validar endereço se fornecido
            if endereco is not None and len(endereco.strip()) < 10:
                return {'success': False, 'message': 'Endereço deve ter no mínimo 10 caracteres'}
            
            try:
                self.cliente_dao.atualizar(
                    id_cliente=id_cliente,
                    cpf=cpf_formatado,
                    endereco=endereco.strip() if endereco else None
                )
            except Exception as e:
                return {'success': False, 'message': f'Erro ao atualizar cliente: {str(e)}'}
        
        # Atualizar dados do usuário
        if nome is not None or email is not None or telefone is not None:
            resultado = self.usuario_service.atualizar_usuario(
                id_usuario=id_usuario,
                nome=nome,
                email=email,
                telefone=telefone
            )
            
            if not resultado['success']:
                return resultado
        
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
