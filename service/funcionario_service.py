"""
FuncionarioService - Serviço de Funcionários
Lógica de negócio para operações com funcionários.
"""

from datetime import date
from .usuario_service import UsuarioService


class FuncionarioService:
    """Serviço de lógica de negócio para funcionários"""
    
    def __init__(self, funcionario_dao, usuario_dao, nivel_acesso_dao):
        """
        Inicializa o serviço.
        
        Args:
            funcionario_dao: Instância de FuncionarioDAO
            usuario_dao: Instância de UsuarioDAO
            nivel_acesso_dao: Instância de NivelAcessoDAO
        """
        self.funcionario_dao = funcionario_dao
        self.usuario_dao = usuario_dao
        self.nivel_acesso_dao = nivel_acesso_dao
        self.usuario_service = UsuarioService(usuario_dao, nivel_acesso_dao)
    
    def listar_funcionarios(self, apenas_ativos=True):
        """
        Lista todos os funcionários.
        
        Args:
            apenas_ativos (bool): Se True, lista apenas funcionários ativos
        
        Returns:
            list: Lista de funcionários com dados completos
        """
        return self.funcionario_dao.listar_todos(apenas_ativos)
    
    def buscar_funcionario(self, id_funcionario):
        """
        Busca funcionário por ID.
        
        Args:
            id_funcionario (int): ID do funcionário
        
        Returns:
            dict: Dados completos do funcionário ou None
        """
        return self.funcionario_dao.buscar_por_id(id_funcionario)
    
    def buscar_funcionario_por_email(self, email):
        """
        Busca funcionário por email.
        
        Args:
            email (str): Email do funcionário
        
        Returns:
            dict: Dados completos do funcionário ou None
        """
        return self.funcionario_dao.buscar_por_email(email)
    
    def listar_por_cargo(self, cargo):
        """
        Lista funcionários por cargo.
        
        Args:
            cargo (str): Cargo a filtrar
        
        Returns:
            list: Lista de funcionários do cargo especificado
        """
        return self.funcionario_dao.listar_por_cargo(cargo)
    
    def criar_funcionario_completo(self, nome, email, senha, cargo, salario, 
                                   data_contratacao=None, telefone=None, 
                                   nivel_acesso='funcionario'):
        """
        Cria funcionário completo (usuario + funcionario).
        
        Args:
            nome (str): Nome do funcionário
            email (str): Email do funcionário
            senha (str): Senha em texto plano
            cargo (str): Cargo do funcionário
            salario (float): Salário do funcionário
            data_contratacao (str): Data de contratação (YYYY-MM-DD) - padrão hoje
            telefone (str): Telefone (opcional)
            nivel_acesso (str): 'admin' ou 'funcionario' - padrão 'funcionario'
        
        Returns:
            dict: {'success': bool, 'id_funcionario': int, 'id_usuario': int, 'message': str}
        """
        # Validar cargo
        if not cargo or len(cargo.strip()) < 3:
            return {'success': False, 'message': 'Cargo deve ter no mínimo 3 caracteres'}
        
        # Validar salário
        try:
            salario_float = float(salario)
            if salario_float <= 0:
                return {'success': False, 'message': 'Salário deve ser maior que zero'}
        except (ValueError, TypeError):
            return {'success': False, 'message': 'Salário inválido'}
        
        # Validar data de contratação
        if data_contratacao:
            try:
                # Verificar formato YYYY-MM-DD
                date.fromisoformat(data_contratacao)
            except ValueError:
                return {'success': False, 'message': 'Data de contratação inválida (use YYYY-MM-DD)'}
        else:
            # Se não fornecida, usar data atual
            data_contratacao = date.today().isoformat()
        
        # Validar nível de acesso
        if nivel_acesso not in ['admin', 'funcionario']:
            return {'success': False, 'message': 'Nível de acesso deve ser "admin" ou "funcionario"'}
        
        # Buscar nível de acesso
        nivel = self.nivel_acesso_dao.buscar_nivel_acesso_por_nome(nivel_acesso)
        if not nivel:
            return {'success': False, 'message': f'Nível de acesso "{nivel_acesso}" não encontrado'}
        
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
        
        # Criar funcionário
        try:
            id_funcionario = self.funcionario_dao.inserir(
                id_usuario=id_usuario,
                cargo=cargo.strip(),
                salario=salario_float,
                data_contratacao=data_contratacao
            )
            
            return {
                'success': True,
                'id_funcionario': id_funcionario,
                'id_usuario': id_usuario,
                'message': 'Funcionário criado com sucesso'
            }
        except Exception as e:
            # Se falhar, tentar desativar usuário criado
            try:
                self.usuario_dao.ativar_desativar(id_usuario, False)
            except:
                pass
            
            return {'success': False, 'message': f'Erro ao criar funcionário: {str(e)}'}
    
    def atualizar_funcionario(self, id_funcionario, cargo=None, salario=None, 
                             data_contratacao=None, nome=None, email=None, telefone=None):
        """
        Atualiza dados do funcionário.
        Atualiza tanto dados do funcionário quanto do usuário associado.
        
        Args:
            id_funcionario (int): ID do funcionário
            cargo (str): Cargo (opcional)
            salario (float): Salário (opcional)
            data_contratacao (str): Data de contratação (opcional)
            nome (str): Nome (opcional) - atualiza no usuario
            email (str): Email (opcional) - atualiza no usuario
            telefone (str): Telefone (opcional) - atualiza no usuario
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        # Verificar se funcionário existe
        funcionario = self.funcionario_dao.buscar_por_id(id_funcionario)
        if not funcionario:
            return {'success': False, 'message': 'Funcionário não encontrado'}
        
        id_usuario = funcionario['id_usuario']
        
        # Atualizar dados do funcionário
        if cargo is not None or salario is not None or data_contratacao is not None:
            # Validar cargo se fornecido
            if cargo is not None and len(cargo.strip()) < 3:
                return {'success': False, 'message': 'Cargo deve ter no mínimo 3 caracteres'}
            
            # Validar salário se fornecido
            if salario is not None:
                try:
                    salario_float = float(salario)
                    if salario_float <= 0:
                        return {'success': False, 'message': 'Salário deve ser maior que zero'}
                except (ValueError, TypeError):
                    return {'success': False, 'message': 'Salário inválido'}
            else:
                salario_float = None
            
            # Validar data se fornecida
            if data_contratacao is not None:
                try:
                    date.fromisoformat(data_contratacao)
                except ValueError:
                    return {'success': False, 'message': 'Data de contratação inválida (use YYYY-MM-DD)'}
            
            try:
                self.funcionario_dao.atualizar(
                    id_funcionario=id_funcionario,
                    cargo=cargo.strip() if cargo else None,
                    salario=salario_float,
                    data_contratacao=data_contratacao
                )
            except Exception as e:
                return {'success': False, 'message': f'Erro ao atualizar funcionário: {str(e)}'}
        
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
        
        return {'success': True, 'message': 'Funcionário atualizado com sucesso'}
    
    def promover_funcionario(self, id_funcionario, novo_cargo, novo_salario):
        """
        Promove funcionário (atualiza cargo e salário).
        
        Args:
            id_funcionario (int): ID do funcionário
            novo_cargo (str): Novo cargo
            novo_salario (float): Novo salário
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        return self.atualizar_funcionario(
            id_funcionario=id_funcionario,
            cargo=novo_cargo,
            salario=novo_salario
        )
    
    def dar_aumento(self, id_funcionario, percentual):
        """
        Dá aumento percentual ao funcionário.
        
        Args:
            id_funcionario (int): ID do funcionário
            percentual (float): Percentual de aumento (ex: 10 para 10%)
        
        Returns:
            dict: {'success': bool, 'salario_anterior': float, 'salario_novo': float, 'message': str}
        """
        funcionario = self.funcionario_dao.buscar_por_id(id_funcionario)
        if not funcionario:
            return {'success': False, 'message': 'Funcionário não encontrado'}
        
        try:
            percentual_float = float(percentual)
            if percentual_float <= 0:
                return {'success': False, 'message': 'Percentual deve ser maior que zero'}
        except (ValueError, TypeError):
            return {'success': False, 'message': 'Percentual inválido'}
        
        salario_anterior = float(funcionario['salario'])
        salario_novo = salario_anterior * (1 + percentual_float / 100)
        
        resultado = self.atualizar_funcionario(
            id_funcionario=id_funcionario,
            salario=salario_novo
        )
        
        if resultado['success']:
            return {
                'success': True,
                'salario_anterior': salario_anterior,
                'salario_novo': salario_novo,
                'message': f'Aumento de {percentual}% aplicado com sucesso'
            }
        
        return resultado
    
    def alterar_nivel_acesso(self, id_funcionario, novo_nivel):
        """
        Altera nível de acesso do funcionário (promover a admin ou rebaixar).
        
        Args:
            id_funcionario (int): ID do funcionário
            novo_nivel (str): 'admin' ou 'funcionario'
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        if novo_nivel not in ['admin', 'funcionario']:
            return {'success': False, 'message': 'Nível deve ser "admin" ou "funcionario"'}
        
        funcionario = self.funcionario_dao.buscar_por_id(id_funcionario)
        if not funcionario:
            return {'success': False, 'message': 'Funcionário não encontrado'}
        
        nivel = self.nivel_acesso_dao.buscar_nivel_acesso_por_nome(novo_nivel)
        if not nivel:
            return {'success': False, 'message': f'Nível de acesso "{novo_nivel}" não encontrado'}
        
        return self.usuario_service.atualizar_usuario(
            id_usuario=funcionario['id_usuario'],
            id_nivel_acesso=nivel['id_nivel_acesso']
        )
    
    def desativar_funcionario(self, id_funcionario):
        """
        Desativa funcionário (desativa o usuário associado).
        
        Args:
            id_funcionario (int): ID do funcionário
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        funcionario = self.funcionario_dao.buscar_por_id(id_funcionario)
        if not funcionario:
            return {'success': False, 'message': 'Funcionário não encontrado'}
        
        return self.usuario_service.desativar_usuario(funcionario['id_usuario'])
    
    def ativar_funcionario(self, id_funcionario):
        """
        Ativa funcionário.
        
        Args:
            id_funcionario (int): ID do funcionário
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        funcionario = self.funcionario_dao.buscar_por_id(id_funcionario)
        if not funcionario:
            return {'success': False, 'message': 'Funcionário não encontrado'}
        
        return self.usuario_service.ativar_usuario(funcionario['id_usuario'])
    
    def alterar_senha_funcionario(self, id_funcionario, senha_atual, senha_nova):
        """
        Altera senha do funcionário.
        
        Args:
            id_funcionario (int): ID do funcionário
            senha_atual (str): Senha atual
            senha_nova (str): Nova senha
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        funcionario = self.funcionario_dao.buscar_por_id(id_funcionario)
        if not funcionario:
            return {'success': False, 'message': 'Funcionário não encontrado'}
        
        return self.usuario_service.alterar_senha(
            funcionario['id_usuario'],
            senha_atual,
            senha_nova
        )
