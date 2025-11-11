"""
FornecedorService - Serviço de Fornecedores
Lógica de negócio para operações com fornecedores.
"""

import re


class FornecedorService:
    """Serviço de lógica de negócio para fornecedores"""
    
    def __init__(self, fornecedor_dao):
        """
        Inicializa o serviço.
        
        Args:
            fornecedor_dao: Instância de FornecedorDAO
        """
        self.fornecedor_dao = fornecedor_dao
    
    @staticmethod
    def validar_cnpj(cnpj):
        """
        Valida CNPJ brasileiro.
        
        Args:
            cnpj (str): CNPJ a ser validado
        
        Returns:
            dict: {'valido': bool, 'mensagem': str}
        """
        if not cnpj:
            return {'valido': False, 'mensagem': 'CNPJ não pode ser vazio'}
        
        # Remove caracteres não numéricos
        cnpj_numeros = re.sub(r'\D', '', cnpj)
        
        # Verifica se tem 14 dígitos
        if len(cnpj_numeros) != 14:
            return {'valido': False, 'mensagem': 'CNPJ deve ter 14 dígitos'}
        
        # Verifica se não são todos números iguais
        if cnpj_numeros == cnpj_numeros[0] * 14:
            return {'valido': False, 'mensagem': 'CNPJ inválido'}
        
        # Validação dos dígitos verificadores
        def calcular_digito(cnpj_base, pesos):
            soma = sum(int(cnpj_base[i]) * pesos[i] for i in range(len(pesos)))
            resto = soma % 11
            return 0 if resto < 2 else 11 - resto
        
        # Primeiro dígito
        pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        digito1 = calcular_digito(cnpj_numeros[:12], pesos1)
        
        if int(cnpj_numeros[12]) != digito1:
            return {'valido': False, 'mensagem': 'CNPJ inválido'}
        
        # Segundo dígito
        pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        digito2 = calcular_digito(cnpj_numeros[:13], pesos2)
        
        if int(cnpj_numeros[13]) != digito2:
            return {'valido': False, 'mensagem': 'CNPJ inválido'}
        
        return {'valido': True, 'mensagem': 'CNPJ válido'}
    
    def criar_fornecedor(self, razao_social, nome_fantasia, cnpj, 
                         email=None, telefone=None, endereco=None):
        """
        Cria um novo fornecedor com validações.
        
        Args:
            razao_social (str): Razão social do fornecedor (obrigatório)
            nome_fantasia (str): Nome fantasia do fornecedor (obrigatório)
            cnpj (str): CNPJ do fornecedor
            email (str, optional): Email do fornecedor
            telefone (str, optional): Telefone do fornecedor
            endereco (str, optional): Endereço do fornecedor
        
        Returns:
            dict: {'success': bool, 'message': str, 'fornecedor': dict}
        """
        try:
            # Validar campos obrigatórios
            if not razao_social or not razao_social.strip():
                return {'success': False, 'message': 'Razão social é obrigatória'}
            
            if not nome_fantasia or not nome_fantasia.strip():
                return {'success': False, 'message': 'Nome fantasia é obrigatório'}
            
            # Validar CNPJ
            validacao = self.validar_cnpj(cnpj)
            if not validacao['valido']:
                return {'success': False, 'message': validacao['mensagem']}
            
            # Verificar se CNPJ já existe
            fornecedor_existente = self.fornecedor_dao.buscar_por_cnpj(cnpj)
            if fornecedor_existente:
                return {
                    'success': False,
                    'message': 'CNPJ já cadastrado'
                }
            
            # Criar fornecedor
            id_fornecedor = self.fornecedor_dao.criar(
                razao_social=razao_social,
                nome_fantasia=nome_fantasia,
                cnpj=cnpj,
                email=email,
                telefone=telefone,
                endereco=endereco
            )
            
            if id_fornecedor:
                fornecedor = self.fornecedor_dao.buscar_por_id(id_fornecedor)
                return {
                    'success': True,
                    'message': 'Fornecedor criado com sucesso',
                    'fornecedor': fornecedor
                }
            else:
                return {
                    'success': False,
                    'message': 'Erro ao criar fornecedor'
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao criar fornecedor: {str(e)}'
            }
    
    def buscar_fornecedor(self, id_fornecedor):
        """
        Busca fornecedor por ID.
        
        Args:
            id_fornecedor (int): ID do fornecedor
        
        Returns:
            dict: {'success': bool, 'fornecedor': dict, 'message': str}
        """
        try:
            fornecedor = self.fornecedor_dao.buscar_por_id(id_fornecedor)
            
            if fornecedor:
                return {
                    'success': True,
                    'fornecedor': fornecedor
                }
            else:
                return {
                    'success': False,
                    'message': 'Fornecedor não encontrado'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao buscar fornecedor: {str(e)}'
            }
    
    def listar_fornecedores(self, apenas_ativos=True):
        """
        Lista todos os fornecedores.
        
        Args:
            apenas_ativos (bool): Se True, lista apenas fornecedores ativos
        
        Returns:
            list: Lista de fornecedores
        """
        return self.fornecedor_dao.listar_todos(apenas_ativos)
    
    def buscar_por_nome(self, nome, apenas_ativos=True):
        """
        Busca fornecedores por nome (razão social ou nome fantasia).
        
        Args:
            nome (str): Nome ou parte do nome
            apenas_ativos (bool): Se True, busca apenas fornecedores ativos
        
        Returns:
            list: Lista de fornecedores encontrados
        """
        return self.fornecedor_dao.buscar_por_nome(nome, apenas_ativos)
    
    def atualizar_fornecedor(self, id_fornecedor, **dados):
        """
        Atualiza dados do fornecedor.
        
        Args:
            id_fornecedor (int): ID do fornecedor
            **dados: Campos a atualizar (razao_social, nome_fantasia, cnpj, email, telefone, endereco)
        
        Returns:
            dict: {'success': bool, 'message': str, 'fornecedor': dict}
        """
        try:
            # Verificar se fornecedor existe
            fornecedor = self.fornecedor_dao.buscar_por_id(id_fornecedor)
            if not fornecedor:
                return {
                    'success': False,
                    'message': 'Fornecedor não encontrado'
                }
            
            # Validar CNPJ se estiver sendo atualizado
            if 'cnpj' in dados and dados['cnpj']:
                validacao = self.validar_cnpj(dados['cnpj'])
                if not validacao['valido']:
                    return {'success': False, 'message': validacao['mensagem']}
                
                # Verificar se novo CNPJ já existe em outro fornecedor
                fornecedor_existente = self.fornecedor_dao.buscar_por_cnpj(dados['cnpj'])
                if fornecedor_existente and fornecedor_existente['id_fornecedor'] != id_fornecedor:
                    return {
                        'success': False,
                        'message': 'CNPJ já cadastrado em outro fornecedor'
                    }
            
            # Preparar dados para atualização
            dados_dao = {}
            campos_permitidos = ['razao_social', 'nome_fantasia', 'cnpj', 'email', 'telefone', 'endereco']
            
            for campo in campos_permitidos:
                if campo in dados:
                    dados_dao[campo] = dados[campo]
            
            if not dados_dao:
                return {
                    'success': False,
                    'message': 'Nenhum campo válido para atualizar'
                }
            
            # Atualizar fornecedor
            sucesso = self.fornecedor_dao.atualizar(id_fornecedor, **dados_dao)
            
            if sucesso:
                fornecedor_atualizado = self.fornecedor_dao.buscar_por_id(id_fornecedor)
                return {
                    'success': True,
                    'message': 'Fornecedor atualizado com sucesso',
                    'fornecedor': fornecedor_atualizado
                }
            else:
                return {
                    'success': False,
                    'message': 'Erro ao atualizar fornecedor'
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao atualizar fornecedor: {str(e)}'
            }
    
    def deletar_fornecedor(self, id_fornecedor):
        """
        Deleta um fornecedor.
        
        Args:
            id_fornecedor (int): ID do fornecedor
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            # Verificar se fornecedor existe
            fornecedor = self.fornecedor_dao.buscar_por_id(id_fornecedor)
            if not fornecedor:
                return {
                    'success': False,
                    'message': 'Fornecedor não encontrado'
                }
            
            # Verificar se tem pedidos de compra
            total_pedidos = self.fornecedor_dao.contar_pedidos_compra(id_fornecedor)
            if total_pedidos > 0:
                return {
                    'success': False,
                    'message': f'Não é possível deletar fornecedor com {total_pedidos} pedido(s) de compra'
                }
            
            # Deletar fornecedor
            sucesso = self.fornecedor_dao.deletar(id_fornecedor)
            
            if sucesso:
                return {
                    'success': True,
                    'message': 'Fornecedor deletado com sucesso'
                }
            else:
                return {
                    'success': False,
                    'message': 'Erro ao deletar fornecedor'
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao deletar fornecedor: {str(e)}'
            }
    
    def desativar_fornecedor(self, id_fornecedor):
        """
        Desativa um fornecedor (soft delete).
        
        Args:
            id_fornecedor (int): ID do fornecedor
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            # Verificar se fornecedor existe
            fornecedor = self.fornecedor_dao.buscar_por_id(id_fornecedor)
            if not fornecedor:
                return {
                    'success': False,
                    'message': 'Fornecedor não encontrado'
                }
            
            # Desativar fornecedor
            sucesso = self.fornecedor_dao.desativar(id_fornecedor)
            
            if sucesso:
                return {
                    'success': True,
                    'message': 'Fornecedor desativado com sucesso'
                }
            else:
                return {
                    'success': False,
                    'message': 'Erro ao desativar fornecedor'
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao desativar fornecedor: {str(e)}'
            }
    
    def ativar_fornecedor(self, id_fornecedor):
        """
        Ativa um fornecedor.
        
        Args:
            id_fornecedor (int): ID do fornecedor
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            # Verificar se fornecedor existe
            fornecedor = self.fornecedor_dao.buscar_por_id(id_fornecedor)
            if not fornecedor:
                return {
                    'success': False,
                    'message': 'Fornecedor não encontrado'
                }
            
            # Ativar fornecedor
            sucesso = self.fornecedor_dao.ativar(id_fornecedor)
            
            if sucesso:
                return {
                    'success': True,
                    'message': 'Fornecedor ativado com sucesso'
                }
            else:
                return {
                    'success': False,
                    'message': 'Erro ao ativar fornecedor'
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao ativar fornecedor: {str(e)}'
            }
    
    def obter_estatisticas(self):
        """
        Obtém estatísticas gerais de fornecedores.
        
        Returns:
            dict: Estatísticas gerais
        """
        try:
            total_fornecedores = len(self.fornecedor_dao.listar_todos(apenas_ativos=False))
            fornecedores_ativos = len(self.fornecedor_dao.listar_todos(apenas_ativos=True))
            
            return {
                'total_fornecedores': total_fornecedores,
                'fornecedores_ativos': fornecedores_ativos
            }
        except Exception as e:
            return {
                'total_fornecedores': 0,
                'fornecedores_ativos': 0,
                'erro': str(e)
            }
    
    def obter_estatisticas_fornecedor(self, id_fornecedor):
        """
        Obtém estatísticas de compras de um fornecedor específico.
        
        Args:
            id_fornecedor (int): ID do fornecedor
        
        Returns:
            dict: Estatísticas ou None
        """
        return self.fornecedor_dao.obter_estatisticas(id_fornecedor)
