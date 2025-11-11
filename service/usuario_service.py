"""
UsuarioService - Serviço de Usuários
Lógica de negócio para operações com usuários.
"""

import re
from .auth_service import AuthService


class UsuarioService:
    """Serviço de lógica de negócio para usuários"""
    
    def __init__(self, usuario_dao, nivel_acesso_dao):
        """
        Inicializa o serviço.
        
        Args:
            usuario_dao: Instância de UsuarioDAO
            nivel_acesso_dao: Instância de NivelAcessoDAO
        """
        self.usuario_dao = usuario_dao
        self.nivel_acesso_dao = nivel_acesso_dao
    
    @staticmethod
    def validar_email(email):
        """
        Valida formato de email.
        
        Args:
            email (str): Email a ser validado
        
        Returns:
            bool: True se válido, False caso contrário
        """
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validar_senha(senha):
        """
        Valida força da senha.
        Mínimo 6 caracteres.
        
        Args:
            senha (str): Senha a ser validada
        
        Returns:
            dict: {'valido': bool, 'mensagem': str}
        """
        if not senha:
            return {'valido': False, 'mensagem': 'Senha não pode ser vazia'}
        
        if len(senha) < 6:
            return {'valido': False, 'mensagem': 'Senha deve ter no mínimo 6 caracteres'}
        
        # Regras adicionais podem ser adicionadas aqui
        # Ex: letra maiúscula, número, caractere especial
        
        return {'valido': True, 'mensagem': 'Senha válida'}
    
    @staticmethod
    def validar_telefone(telefone):
        """
        Valida formato de telefone brasileiro.
        Aceita: (11) 99999-9999, 11999999999, etc.
        
        Args:
            telefone (str): Telefone a ser validado
        
        Returns:
            bool: True se válido, False caso contrário
        """
        if not telefone:
            return True  # Telefone é opcional
        
        # Remove caracteres não numéricos
        numeros = re.sub(r'\D', '', telefone)
        
        # Deve ter 10 ou 11 dígitos (com ou sem 9 no celular)
        return len(numeros) in [10, 11]
    
    def listar_usuarios(self, apenas_ativos=True):
        """
        Lista todos os usuários.
        
        Args:
            apenas_ativos (bool): Se True, lista apenas usuários ativos
        
        Returns:
            list: Lista de usuários (sem senha_hash)
        """
        return self.usuario_dao.listar_todos(apenas_ativos)
    
    def buscar_usuario(self, id_usuario):
        """
        Busca usuário por ID.
        
        Args:
            id_usuario (int): ID do usuário
        
        Returns:
            dict: Dados do usuário ou None
        """
        return self.usuario_dao.buscar_por_id(id_usuario)
    
    def buscar_usuario_por_email(self, email):
        """
        Busca usuário por email.
        
        Args:
            email (str): Email do usuário
        
        Returns:
            dict: Dados do usuário ou None
        """
        return self.usuario_dao.buscar_por_email(email)
    
    def criar_usuario(self, nome, email, senha, id_nivel_acesso, telefone=None):
        """
        Cria novo usuário com validações.
        
        Args:
            nome (str): Nome do usuário
            email (str): Email do usuário
            senha (str): Senha em texto plano
            id_nivel_acesso (int): ID do nível de acesso
            telefone (str): Telefone (opcional)
        
        Returns:
            dict: {'success': bool, 'id_usuario': int, 'message': str}
        """
        # Validar nome
        if not nome or len(nome.strip()) < 3:
            return {'success': False, 'message': 'Nome deve ter no mínimo 3 caracteres'}
        
        # Validar email
        if not self.validar_email(email):
            return {'success': False, 'message': 'Email inválido'}
        
        # Verificar se email já existe
        if self.usuario_dao.verificar_email_existe(email):
            return {'success': False, 'message': 'Email já cadastrado'}
        
        # Validar senha
        validacao_senha = self.validar_senha(senha)
        if not validacao_senha['valido']:
            return {'success': False, 'message': validacao_senha['mensagem']}
        
        # Validar telefone
        if telefone and not self.validar_telefone(telefone):
            return {'success': False, 'message': 'Telefone inválido'}
        
        # Verificar se nível de acesso existe
        nivel = self.nivel_acesso_dao.buscar_nivel_acesso(id_nivel_acesso)
        if not nivel:
            return {'success': False, 'message': 'Nível de acesso inválido'}
        
        # Hash da senha
        senha_hash = AuthService.hash_senha(senha)
        
        # Inserir no banco
        try:
            id_usuario = self.usuario_dao.inserir(
                nome=nome.strip(),
                email=email.lower().strip(),
                senha_hash=senha_hash,
                id_nivel_acesso=id_nivel_acesso,
                telefone=telefone,
                ativo=True
            )
            
            return {
                'success': True,
                'id_usuario': id_usuario,
                'message': 'Usuário criado com sucesso'
            }
        except Exception as e:
            return {'success': False, 'message': f'Erro ao criar usuário: {str(e)}'}
    
    def atualizar_usuario(self, id_usuario, nome=None, email=None, telefone=None, 
                         id_nivel_acesso=None, ativo=None):
        """
        Atualiza dados do usuário.
        
        Args:
            id_usuario (int): ID do usuário
            nome (str): Nome (opcional)
            email (str): Email (opcional)
            telefone (str): Telefone (opcional)
            id_nivel_acesso (int): ID do nível de acesso (opcional)
            ativo (bool): Status ativo (opcional)
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        # Verificar se usuário existe
        usuario = self.usuario_dao.buscar_por_id(id_usuario)
        if not usuario:
            return {'success': False, 'message': 'Usuário não encontrado'}
        
        # Validar nome se fornecido
        if nome is not None and len(nome.strip()) < 3:
            return {'success': False, 'message': 'Nome deve ter no mínimo 3 caracteres'}
        
        # Validar email se fornecido
        if email is not None:
            if not self.validar_email(email):
                return {'success': False, 'message': 'Email inválido'}
            
            # Verificar se email já existe (excluindo o próprio usuário)
            if self.usuario_dao.verificar_email_existe(email, id_usuario):
                return {'success': False, 'message': 'Email já cadastrado'}
        
        # Validar telefone se fornecido
        if telefone is not None and not self.validar_telefone(telefone):
            return {'success': False, 'message': 'Telefone inválido'}
        
        # Validar nível de acesso se fornecido
        if id_nivel_acesso is not None:
            nivel = self.nivel_acesso_dao.buscar_nivel_acesso(id_nivel_acesso)
            if not nivel:
                return {'success': False, 'message': 'Nível de acesso inválido'}
        
        # Atualizar
        try:
            self.usuario_dao.atualizar(
                id_usuario=id_usuario,
                nome=nome.strip() if nome else None,
                email=email.lower().strip() if email else None,
                telefone=telefone,
                id_nivel_acesso=id_nivel_acesso,
                ativo=ativo
            )
            
            return {'success': True, 'message': 'Usuário atualizado com sucesso'}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao atualizar usuário: {str(e)}'}
    
    def alterar_senha(self, id_usuario, senha_atual, senha_nova):
        """
        Altera senha do usuário.
        
        Args:
            id_usuario (int): ID do usuário
            senha_atual (str): Senha atual
            senha_nova (str): Nova senha
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        # Buscar usuário com senha
        usuario = self.usuario_dao.buscar_por_id_com_senha(id_usuario)
        if not usuario:
            return {'success': False, 'message': 'Usuário não encontrado'}
        
        # Verificar senha atual
        if not AuthService.verificar_senha(senha_atual, usuario['senha_hash']):
            return {'success': False, 'message': 'Senha atual incorreta'}
        
        # Validar nova senha
        validacao = self.validar_senha(senha_nova)
        if not validacao['valido']:
            return {'success': False, 'message': validacao['mensagem']}
        
        # Atualizar senha
        try:
            senha_hash = AuthService.hash_senha(senha_nova)
            self.usuario_dao.atualizar_senha(id_usuario, senha_hash)
            
            return {'success': True, 'message': 'Senha alterada com sucesso'}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao alterar senha: {str(e)}'}
    
    def desativar_usuario(self, id_usuario):
        """
        Desativa usuário (soft delete).
        
        Args:
            id_usuario (int): ID do usuário
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            self.usuario_dao.ativar_desativar(id_usuario, False)
            return {'success': True, 'message': 'Usuário desativado com sucesso'}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao desativar usuário: {str(e)}'}
    
    def ativar_usuario(self, id_usuario):
        """
        Ativa usuário.
        
        Args:
            id_usuario (int): ID do usuário
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            self.usuario_dao.ativar_desativar(id_usuario, True)
            return {'success': True, 'message': 'Usuário ativado com sucesso'}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao ativar usuário: {str(e)}'}
    
    def listar_por_nivel(self, nivel_nome, apenas_ativos=True):
        """
        Lista usuários por nível de acesso.
        
        Args:
            nivel_nome (str): Nome do nível ('admin', 'funcionario', 'cliente')
            apenas_ativos (bool): Se True, lista apenas ativos
        
        Returns:
            list: Lista de usuários ou None se nível não existe
        """
        nivel = self.nivel_acesso_dao.buscar_nivel_acesso_por_nome(nivel_nome)
        if not nivel:
            return None
        
        return self.usuario_dao.buscar_usuarios_por_nivel(nivel['id_nivel_acesso'], apenas_ativos)
