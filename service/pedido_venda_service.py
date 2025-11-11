"""
PedidoVendaService - Serviço de Pedidos de Venda
Lógica de negócio para operações com pedidos de venda (saída de estoque).
"""


class PedidoVendaService:
    """Serviço de lógica de negócio para pedidos de venda"""
    
    def __init__(self, pedido_venda_dao, item_pedido_venda_dao, cliente_dao, produto_dao):
        """
        Inicializa o serviço.
        
        Args:
            pedido_venda_dao: Instância de PedidoVendaDAO
            item_pedido_venda_dao: Instância de ItemPedidoVendaDAO
            cliente_dao: Instância de ClienteDAO
            produto_dao: Instância de ProdutoDAO
        """
        self.pedido_dao = pedido_venda_dao
        self.item_dao = item_pedido_venda_dao
        self.cliente_dao = cliente_dao
        self.produto_dao = produto_dao
    
    def criar_pedido_venda(self, id_cliente, id_funcionario, itens=None):
        """
        Cria um novo pedido de venda com itens.
        
        Args:
            id_cliente (int): ID do cliente
            id_funcionario (int): ID do funcionário responsável
            itens (list, optional): Lista de itens [{id_produto, quantidade, preco_venda_unitario}]
        
        Returns:
            dict: {'success': bool, 'message': str, 'pedido': dict}
        """
        try:
            # Verificar se cliente existe
            cliente = self.cliente_dao.buscar_por_id(id_cliente)
            if not cliente:
                return {
                    'success': False,
                    'message': 'Cliente não encontrado'
                }
            
            # Criar pedido
            id_pedido = self.pedido_dao.criar(
                id_cliente=id_cliente,
                id_funcionario=id_funcionario,
                status='Pendente'
            )
            
            if not id_pedido:
                return {
                    'success': False,
                    'message': 'Erro ao criar pedido de venda'
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
                'message': 'Pedido de venda criado com sucesso',
                'pedido': pedido
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao criar pedido de venda: {str(e)}'
            }
    
    def adicionar_itens(self, id_pedido_venda, itens):
        """
        Adiciona múltiplos itens a um pedido de venda.
        Valida disponibilidade em estoque.
        
        Args:
            id_pedido_venda (int): ID do pedido
            itens (list): Lista de dicts com {id_produto, quantidade, preco_venda_unitario}
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            # Verificar se pedido existe
            pedido = self.pedido_dao.buscar_por_id(id_pedido_venda)
            if not pedido:
                return {
                    'success': False,
                    'message': 'Pedido de venda não encontrado'
                }
            
            # Verificar se pedido pode ser modificado
            if pedido['status'] in ['Confirmado', 'Entregue', 'Cancelado']:
                return {
                    'success': False,
                    'message': f'Não é possível adicionar itens a um pedido {pedido["status"]}'
                }
            
            # Validar estoque de todos os itens antes de adicionar
            for item in itens:
                id_produto = item.get('id_produto')
                quantidade = item.get('quantidade')
                
                produto = self.produto_dao.buscar_por_id(id_produto)
                if not produto:
                    return {
                        'success': False,
                        'message': f'Produto com ID {id_produto} não encontrado'
                    }
                
                if quantidade > produto['estoque_atual']:
                    return {
                        'success': False,
                        'message': f'Estoque insuficiente para {produto["nome"]}. Disponível: {produto["estoque_atual"]}, Solicitado: {quantidade}'
                    }
            
            # Adicionar cada item
            for item in itens:
                id_produto = item.get('id_produto')
                quantidade = item.get('quantidade')
                preco_venda = item.get('preco_venda_unitario')
                
                # Validações
                if not id_produto or not quantidade or not preco_venda:
                    return {
                        'success': False,
                        'message': 'Campos obrigatórios: id_produto, quantidade, preco_venda_unitario'
                    }
                
                if quantidade <= 0:
                    return {
                        'success': False,
                        'message': 'Quantidade deve ser maior que zero'
                    }
                
                if preco_venda <= 0:
                    return {
                        'success': False,
                        'message': 'Preço deve ser maior que zero'
                    }
                
                # Buscar produto
                produto = self.produto_dao.buscar_por_id(id_produto)
                
                # Verificar se produto já está no pedido
                item_existente = self.item_dao.buscar_por_pedido_e_produto(id_pedido_venda, id_produto)
                
                if item_existente:
                    # Somar quantidade ao item existente
                    nova_quantidade = item_existente['quantidade'] + quantidade
                    sucesso = self.item_dao.atualizar(
                        id_item_pedido_venda=item_existente['id_item_pedido_venda'],
                        quantidade=nova_quantidade
                    )
                    
                    if not sucesso:
                        return {
                            'success': False,
                            'message': f'Erro ao atualizar quantidade do produto {produto["nome"]}'
                        }
                else:
                    # Criar novo item
                    id_item = self.item_dao.criar(
                        id_pedido_venda=id_pedido_venda,
                        id_produto=id_produto,
                        quantidade=quantidade,
                        preco_unitario_venda=preco_venda  # Parâmetro correto do DAO
                    )
                    
                    if not id_item:
                        return {
                            'success': False,
                            'message': f'Erro ao adicionar produto {produto["nome"]}'
                        }
            
            # Atualizar total do pedido
            self.pedido_dao.atualizar_total(id_pedido_venda)
            
            return {
                'success': True,
                'message': f'{len(itens)} item(ns) adicionado(s) com sucesso'
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao adicionar itens: {str(e)}'
            }
    
    def atualizar_status(self, id_pedido_venda, novo_status):
        """
        Atualiza o status de um pedido de venda.
        
        Args:
            id_pedido_venda (int): ID do pedido
            novo_status (str): Novo status
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            # Validar status
            status_validos = ['Pendente', 'Confirmado', 'Preparando', 'Enviado', 'Entregue', 'Cancelado']
            if novo_status not in status_validos:
                return {
                    'success': False,
                    'message': f'Status inválido. Use: {", ".join(status_validos)}'
                }
            
            # Verificar se pedido existe
            pedido = self.pedido_dao.buscar_por_id(id_pedido_venda)
            if not pedido:
                return {
                    'success': False,
                    'message': 'Pedido de venda não encontrado'
                }
            
            # Regras de transição de status
            status_atual = pedido['status']
            
            if status_atual == 'Entregue':
                return {
                    'success': False,
                    'message': 'Pedido já foi entregue e não pode ter o status alterado'
                }
            
            if status_atual == 'Cancelado':
                return {
                    'success': False,
                    'message': 'Pedido cancelado não pode ter o status alterado'
                }
            
            # Atualizar status
            sucesso = self.pedido_dao.atualizar_status(id_pedido_venda, novo_status)
            
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
    
    def confirmar_pedido(self, id_pedido_venda):
        """
        Confirma pedido e deduz estoque.
        
        Args:
            id_pedido_venda (int): ID do pedido
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            # Verificar se pedido existe
            pedido = self.pedido_dao.buscar_por_id(id_pedido_venda)
            if not pedido:
                return {
                    'success': False,
                    'message': 'Pedido de venda não encontrado'
                }
            
            # Verificar status
            if pedido['status'] == 'Confirmado':
                return {
                    'success': False,
                    'message': 'Pedido já foi confirmado'
                }
            
            if pedido['status'] == 'Cancelado':
                return {
                    'success': False,
                    'message': 'Não é possível confirmar um pedido cancelado'
                }
            
            # Verificar se tem itens
            itens = self.item_dao.listar_por_pedido(id_pedido_venda)
            if not itens:
                return {
                    'success': False,
                    'message': 'Pedido não possui itens'
                }
            
            # Verificar estoque novamente antes de confirmar
            for item in itens:
                produto = self.produto_dao.buscar_por_id(item['id_produto'])
                if item['quantidade'] > produto['estoque_atual']:
                    return {
                        'success': False,
                        'message': f'Estoque insuficiente para {produto["nome"]}. Disponível: {produto["estoque_atual"]}, Necessário: {item["quantidade"]}'
                    }
            
            # Confirmar pedido (deduz estoque automaticamente)
            sucesso = self.pedido_dao.confirmar_pedido(id_pedido_venda)
            
            if sucesso:
                return {
                    'success': True,
                    'message': 'Pedido confirmado com sucesso. Estoque atualizado.'
                }
            else:
                return {
                    'success': False,
                    'message': 'Erro ao confirmar pedido'
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao confirmar pedido: {str(e)}'
            }
    
    def cancelar_pedido(self, id_pedido_venda, devolver_estoque=True):
        """
        Cancela um pedido de venda.
        
        Args:
            id_pedido_venda (int): ID do pedido
            devolver_estoque (bool): Se deve devolver produtos ao estoque (para pedidos confirmados)
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            # Verificar se pedido existe
            pedido = self.pedido_dao.buscar_por_id(id_pedido_venda)
            if not pedido:
                return {
                    'success': False,
                    'message': 'Pedido de venda não encontrado'
                }
            
            # Verificar se já está cancelado
            if pedido['status'] == 'Cancelado':
                return {
                    'success': False,
                    'message': 'Pedido já está cancelado'
                }
            
            # Não pode cancelar se já entregue
            if pedido['status'] == 'Entregue':
                return {
                    'success': False,
                    'message': 'Não é possível cancelar um pedido já entregue'
                }
            
            # Se pedido foi confirmado e deve devolver estoque
            if pedido['status'] in ['Confirmado', 'Preparando', 'Enviado'] and devolver_estoque:
                itens = self.item_dao.listar_por_pedido(id_pedido_venda)
                for item in itens:
                    # Devolver ao estoque
                    produto = self.produto_dao.buscar_por_id(item['id_produto'])
                    nova_quantidade = produto['estoque_atual'] + item['quantidade']
                    self.produto_dao.atualizar(
                        id_produto=item['id_produto'],
                        estoque=nova_quantidade
                    )
            
            # Cancelar pedido
            sucesso = self.pedido_dao.cancelar_pedido(id_pedido_venda)
            
            if sucesso:
                mensagem = 'Pedido cancelado com sucesso'
                if devolver_estoque and pedido['status'] in ['Confirmado', 'Preparando', 'Enviado']:
                    mensagem += '. Estoque devolvido.'
                
                return {
                    'success': True,
                    'message': mensagem
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
    
    def calcular_lucro(self, id_pedido_venda):
        """
        Calcula o lucro de um pedido de venda.
        
        Args:
            id_pedido_venda (int): ID do pedido
        
        Returns:
            dict: {'success': bool, 'message': str, 'lucro': dict}
        """
        try:
            lucro = self.pedido_dao.calcular_lucro_pedido(id_pedido_venda)
            
            if lucro:
                return {
                    'success': True,
                    'lucro': lucro
                }
            else:
                return {
                    'success': False,
                    'message': 'Pedido não encontrado ou sem itens'
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao calcular lucro: {str(e)}'
            }
    
    def listar_pedidos(self, status=None):
        """
        Lista pedidos de venda.
        
        Args:
            status (str, optional): Filtrar por status
        
        Returns:
            list: Lista de pedidos
        """
        return self.pedido_dao.listar_todos(status)
    
    def buscar_pedido(self, id_pedido_venda):
        """
        Busca pedido por ID com seus itens.
        
        Args:
            id_pedido_venda (int): ID do pedido
        
        Returns:
            dict: Pedido com lista de itens
        """
        pedido = self.pedido_dao.buscar_por_id(id_pedido_venda)
        if pedido:
            pedido['itens'] = self.item_dao.listar_por_pedido(id_pedido_venda)
        return pedido
    
    def obter_relatorio_vendas(self, data_inicio=None, data_fim=None):
        """
        Obtém relatório de vendas com lucro.
        
        Args:
            data_inicio (str, optional): Data inicial (YYYY-MM-DD)
            data_fim (str, optional): Data final (YYYY-MM-DD)
        
        Returns:
            list: Relatório de vendas
        """
        return self.pedido_dao.obter_relatorio_vendas(data_inicio, data_fim)
    
    def obter_produtos_mais_vendidos(self, limite=10):
        """
        Obtém produtos mais vendidos.
        
        Args:
            limite (int): Número de produtos
        
        Returns:
            list: Produtos mais vendidos
        """
        return self.item_dao.obter_produtos_mais_vendidos(limite)
