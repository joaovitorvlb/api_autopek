"""
PedidoCompraService - Serviço de Pedidos de Compra
Lógica de negócio para operações com pedidos de compra (entrada de estoque).
"""


class PedidoCompraService:
    """Serviço de lógica de negócio para pedidos de compra"""
    
    def __init__(self, pedido_compra_dao, item_pedido_compra_dao, fornecedor_dao, produto_dao):
        """
        Inicializa o serviço.
        
        Args:
            pedido_compra_dao: Instância de PedidoCompraDAO
            item_pedido_compra_dao: Instância de ItemPedidoCompraDAO
            fornecedor_dao: Instância de FornecedorDAO
            produto_dao: Instância de ProdutoDAO
        """
        self.pedido_dao = pedido_compra_dao
        self.item_dao = item_pedido_compra_dao
        self.fornecedor_dao = fornecedor_dao
        self.produto_dao = produto_dao
    
    def criar_pedido_compra(self, id_fornecedor, id_funcionario, itens=None):
        """
        Cria um novo pedido de compra com itens.
        
        Args:
            id_fornecedor (int): ID do fornecedor
            id_funcionario (int): ID do funcionário responsável
            itens (list, optional): Lista de itens [{id_produto, quantidade, preco_custo_unitario}]
        
        Returns:
            dict: {'success': bool, 'message': str, 'pedido': dict}
        """
        try:
            # Verificar se fornecedor existe
            fornecedor = self.fornecedor_dao.buscar_por_id(id_fornecedor)
            if not fornecedor:
                return {
                    'success': False,
                    'message': 'Fornecedor não encontrado'
                }
            
            # Criar pedido
            id_pedido = self.pedido_dao.criar(
                id_fornecedor=id_fornecedor,
                id_funcionario=id_funcionario,
                status='Pendente'
            )
            
            if not id_pedido:
                return {
                    'success': False,
                    'message': 'Erro ao criar pedido de compra'
                }
            
            # Adicionar itens se fornecidos
            if itens:
                resultado_itens = self.adicionar_itens(id_pedido, itens)
                if not resultado_itens['success']:
                    # Se falhar ao adicionar itens, deletar pedido
                    self.pedido_dao.deletar(id_pedido)
                    return resultado_itens
            
            # Atualizar total
            self.pedido_dao.atualizar_total(id_pedido)
            
            # Buscar pedido completo
            pedido = self.pedido_dao.buscar_por_id(id_pedido)
            
            return {
                'success': True,
                'message': 'Pedido de compra criado com sucesso',
                'pedido': pedido
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao criar pedido de compra: {str(e)}'
            }
    
    def adicionar_itens(self, id_pedido_compra, itens):
        """
        Adiciona múltiplos itens a um pedido de compra.
        
        Args:
            id_pedido_compra (int): ID do pedido
            itens (list): Lista de dicts com {id_produto, quantidade, preco_custo_unitario}
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            # Verificar se pedido existe
            pedido = self.pedido_dao.buscar_por_id(id_pedido_compra)
            if not pedido:
                return {
                    'success': False,
                    'message': 'Pedido de compra não encontrado'
                }
            
            # Verificar se pedido pode ser modificado
            if pedido['status'] in ['Recebido', 'Cancelado']:
                return {
                    'success': False,
                    'message': f'Não é possível adicionar itens a um pedido {pedido["status"]}'
                }
            
            # Adicionar cada item
            for item in itens:
                id_produto = item.get('id_produto')
                quantidade = item.get('quantidade')
                preco_custo = item.get('preco_custo_unitario')
                
                # Validações
                if not id_produto or not quantidade or not preco_custo:
                    return {
                        'success': False,
                        'message': 'Campos obrigatórios: id_produto, quantidade, preco_custo_unitario'
                    }
                
                if quantidade <= 0:
                    return {
                        'success': False,
                        'message': 'Quantidade deve ser maior que zero'
                    }
                
                if preco_custo <= 0:
                    return {
                        'success': False,
                        'message': 'Preço deve ser maior que zero'
                    }
                
                # Verificar se produto existe
                produto = self.produto_dao.buscar_por_id(id_produto)
                if not produto:
                    return {
                        'success': False,
                        'message': f'Produto com ID {id_produto} não encontrado'
                    }
                
                # Verificar se produto já está no pedido
                item_existente = self.item_dao.buscar_por_pedido_e_produto(id_pedido_compra, id_produto)
                
                if item_existente:
                    # Se já existe, somar a quantidade
                    nova_quantidade = item_existente['quantidade'] + quantidade
                    sucesso = self.item_dao.atualizar(
                        id_item_pedido_compra=item_existente['id_item_pedido_compra'],
                        quantidade=nova_quantidade
                    )
                    
                    if not sucesso:
                        return {
                            'success': False,
                            'message': f'Erro ao atualizar quantidade do produto {produto["nome"]}'
                        }
                else:
                    # Se não existe, adicionar novo item
                    id_item = self.item_dao.criar(
                        id_pedido_compra=id_pedido_compra,
                        id_produto=id_produto,
                        quantidade=quantidade,
                        preco_custo_unitario=preco_custo
                    )
                    
                    if not id_item:
                        return {
                            'success': False,
                            'message': f'Erro ao adicionar produto {produto["nome"]}'
                        }
            
            # Atualizar total do pedido
            self.pedido_dao.atualizar_total(id_pedido_compra)
            
            return {
                'success': True,
                'message': f'{len(itens)} item(ns) adicionado(s) com sucesso'
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao adicionar itens: {str(e)}'
            }
    
    def atualizar_status(self, id_pedido_compra, novo_status):
        """
        Atualiza o status de um pedido de compra.
        
        Args:
            id_pedido_compra (int): ID do pedido
            novo_status (str): Novo status
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            # Validar status
            status_validos = ['Pendente', 'Aprovado', 'Enviado', 'Recebido', 'Cancelado']
            if novo_status not in status_validos:
                return {
                    'success': False,
                    'message': f'Status inválido. Use: {", ".join(status_validos)}'
                }
            
            # Verificar se pedido existe
            pedido = self.pedido_dao.buscar_por_id(id_pedido_compra)
            if not pedido:
                return {
                    'success': False,
                    'message': 'Pedido de compra não encontrado'
                }
            
            # Regras de transição de status
            status_atual = pedido['status']
            
            if status_atual == 'Recebido':
                return {
                    'success': False,
                    'message': 'Pedido já foi recebido e não pode ter o status alterado'
                }
            
            if status_atual == 'Cancelado':
                return {
                    'success': False,
                    'message': 'Pedido cancelado não pode ter o status alterado'
                }
            
            # Atualizar status
            sucesso = self.pedido_dao.atualizar_status(id_pedido_compra, novo_status)
            
            if sucesso:
                return {
                    'success': True,
                    'message': f'Status atualizado para {novo_status}'
                }
            else:
                return {
                    'success': False,
                    'message': 'Erro ao atualizar status'
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao atualizar status: {str(e)}'
            }
    
    def receber_pedido(self, id_pedido_compra):
        """
        Marca pedido como recebido e atualiza estoque.
        
        Args:
            id_pedido_compra (int): ID do pedido
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            # Verificar se pedido existe
            pedido = self.pedido_dao.buscar_por_id(id_pedido_compra)
            if not pedido:
                return {
                    'success': False,
                    'message': 'Pedido de compra não encontrado'
                }
            
            # Verificar status
            if pedido['status'] == 'Recebido':
                return {
                    'success': False,
                    'message': 'Pedido já foi recebido'
                }
            
            if pedido['status'] == 'Cancelado':
                return {
                    'success': False,
                    'message': 'Não é possível receber um pedido cancelado'
                }
            
            # Verificar se tem itens
            itens = self.item_dao.listar_por_pedido(id_pedido_compra)
            if not itens:
                return {
                    'success': False,
                    'message': 'Pedido não possui itens'
                }
            
            # Receber pedido (atualiza estoque automaticamente)
            sucesso = self.pedido_dao.receber_pedido(id_pedido_compra)
            
            if sucesso:
                return {
                    'success': True,
                    'message': 'Pedido recebido com sucesso. Estoque atualizado.'
                }
            else:
                return {
                    'success': False,
                    'message': 'Erro ao receber pedido'
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao receber pedido: {str(e)}'
            }
    
    def cancelar_pedido(self, id_pedido_compra):
        """
        Cancela um pedido de compra.
        
        Args:
            id_pedido_compra (int): ID do pedido
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            # Cancelar através do DAO (já tem validações)
            sucesso = self.pedido_dao.cancelar_pedido(id_pedido_compra)
            
            if sucesso:
                return {
                    'success': True,
                    'message': 'Pedido cancelado com sucesso'
                }
            else:
                return {
                    'success': False,
                    'message': 'Erro ao cancelar pedido'
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao cancelar pedido: {str(e)}'
            }
    
    def listar_pedidos(self, status=None):
        """
        Lista pedidos de compra.
        
        Args:
            status (str, optional): Filtrar por status
        
        Returns:
            list: Lista de pedidos
        """
        return self.pedido_dao.listar_todos(status)
    
    def buscar_pedido(self, id_pedido_compra):
        """
        Busca pedido por ID com seus itens.
        
        Args:
            id_pedido_compra (int): ID do pedido
        
        Returns:
            dict: Pedido com lista de itens
        """
        pedido = self.pedido_dao.buscar_por_id(id_pedido_compra)
        if pedido:
            pedido['itens'] = self.item_dao.listar_por_pedido(id_pedido_compra)
        return pedido
    
    def obter_relatorio_compras(self, data_inicio=None, data_fim=None):
        """
        Obtém relatório de compras.
        
        Args:
            data_inicio (str, optional): Data inicial (YYYY-MM-DD)
            data_fim (str, optional): Data final (YYYY-MM-DD)
        
        Returns:
            list: Relatório de compras
        """
        return self.pedido_dao.obter_relatorio_compras(data_inicio, data_fim)
