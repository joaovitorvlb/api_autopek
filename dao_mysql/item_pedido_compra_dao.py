"""
DAO para manipulação da tabela Item_Pedido_Compra no MySQL
"""

from typing import List, Optional
from .db_pythonanywhere import get_cursor


class ItemPedidoCompraDAO:
    """
    Data Access Object para Item de Pedido de Compra
    """

    def criar(self, id_pedido_compra: int, id_produto: int, 
              quantidade: int, preco_custo_unitario: float) -> Optional[int]:
        """
        Cria um novo item de pedido de compra
        
        Args:
            id_pedido_compra: ID do pedido de compra
            id_produto: ID do produto
            quantidade: Quantidade do produto
            preco_custo_unitario: Preço de custo unitário
        
        Returns:
            ID do item criado ou None se houver erro
        """
        try:
            with get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Item_Pedido_Compra (id_pedido_compra, id_produto, quantidade, preco_custo_unitario)
                    VALUES (%s, %s, %s, %s)
                """, (id_pedido_compra, id_produto, quantidade, preco_custo_unitario))
                
                return cursor.lastrowid
        except Exception as e:
            return None

    def buscar_por_id(self, id_item_pedido_compra: int) -> Optional[dict]:
        """
        Busca item de pedido de compra por ID
        
        Args:
            id_item_pedido_compra: ID do item
        
        Returns:
            Dicionário com dados do item ou None se não encontrado
        """
        try:
            with get_cursor(commit=False) as cursor:
                cursor.execute("""
                    SELECT 
                        ipc.id_item_compra as id_item_pedido_compra,
                        ipc.id_pedido_compra,
                        ipc.id_produto,
                        ipc.quantidade,
                        ipc.preco_custo_unitario,
                        p.nome as produto_nome,
                        p.sku as produto_sku,
                        (ipc.quantidade * ipc.preco_custo_unitario) as subtotal
                    FROM Item_Pedido_Compra ipc
                    JOIN Produto p ON ipc.id_produto = p.id_produto
                    WHERE ipc.id_item_compra = %s
                """, (id_item_pedido_compra,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            return None

    def listar_por_pedido(self, id_pedido_compra: int) -> List[dict]:
        """
        Lista todos os itens de um pedido de compra
        
        Args:
            id_pedido_compra: ID do pedido
        
        Returns:
            Lista de dicionários com dados dos itens
        """
        try:
            with get_cursor(commit=False) as cursor:
                cursor.execute("""
                    SELECT 
                        ipc.id_item_compra as id_item_pedido_compra,
                        ipc.id_pedido_compra,
                        ipc.id_produto,
                        ipc.quantidade,
                        ipc.preco_custo_unitario,
                        p.nome as produto_nome,
                        p.sku as produto_sku,
                        p.estoque_atual as produto_estoque,
                        (ipc.quantidade * ipc.preco_custo_unitario) as subtotal
                    FROM Item_Pedido_Compra ipc
                    JOIN Produto p ON ipc.id_produto = p.id_produto
                    WHERE ipc.id_pedido_compra = %s
                    ORDER BY p.nome
                """, (id_pedido_compra,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            return []

    def listar_por_produto(self, id_produto: int) -> List[dict]:
        """
        Lista todos os itens de pedido que contêm um produto específico
        
        Args:
            id_produto: ID do produto
        
        Returns:
            Lista de dicionários com dados dos itens
        """
        try:
            with get_cursor(commit=False) as cursor:
                cursor.execute("""
                    SELECT 
                        ipc.id_item_compra as id_item_pedido_compra,
                        ipc.id_pedido_compra,
                        ipc.id_produto,
                        ipc.quantidade,
                        ipc.preco_custo_unitario,
                        pc.data_pedido,
                        pc.status as pedido_status,
                        f.nome_fantasia as fornecedor_nome,
                        (ipc.quantidade * ipc.preco_custo_unitario) as subtotal
                    FROM Item_Pedido_Compra ipc
                    JOIN Pedido_Compra pc ON ipc.id_pedido_compra = pc.id_pedido_compra
                    JOIN Fornecedor f ON pc.id_fornecedor = f.id_fornecedor
                    WHERE ipc.id_produto = %s
                    ORDER BY pc.data_pedido DESC
                """, (id_produto,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            return []

    def atualizar(self, id_item_pedido_compra: int, quantidade: int = None,
                  preco_custo_unitario: float = None) -> bool:
        """
        Atualiza dados de um item de pedido de compra
        
        Args:
            id_item_pedido_compra: ID do item
            quantidade: Nova quantidade (opcional)
            preco_custo_unitario: Novo preço (opcional)
        
        Returns:
            True se atualizado com sucesso, False caso contrário
        """
        try:
            campos = []
            valores = []
            
            if quantidade is not None:
                campos.append("quantidade = %s")
                valores.append(quantidade)
            
            if preco_custo_unitario is not None:
                campos.append("preco_custo_unitario = %s")
                valores.append(preco_custo_unitario)
            
            if not campos:
                return False
            
            valores.append(id_item_pedido_compra)
            
            with get_cursor() as cursor:
                query = f"""
                    UPDATE Item_Pedido_Compra
                    SET {', '.join(campos)}
                    WHERE id_item_compra = %s
                """
                cursor.execute(query, valores)
                
                return cursor.rowcount > 0
        except Exception as e:
            return False

    def deletar(self, id_item_pedido_compra: int) -> bool:
        """
        Deleta um item de pedido de compra
        
        Args:
            id_item_pedido_compra: ID do item
        
        Returns:
            True se deletado com sucesso, False caso contrário
        """
        try:
            with get_cursor() as cursor:
                cursor.execute("""
                    DELETE FROM Item_Pedido_Compra
                    WHERE id_item_compra = %s
                """, (id_item_pedido_compra,))
                
                return cursor.rowcount > 0
        except Exception as e:
            return False

    def deletar_por_pedido(self, id_pedido_compra: int) -> bool:
        """
        Deleta todos os itens de um pedido de compra
        
        Args:
            id_pedido_compra: ID do pedido
        
        Returns:
            True se deletado com sucesso, False caso contrário
        """
        try:
            with get_cursor() as cursor:
                cursor.execute("""
                    DELETE FROM Item_Pedido_Compra
                    WHERE id_pedido_compra = %s
                """, (id_pedido_compra,))
                
                return True
        except Exception as e:
            return False

    def calcular_total_pedido(self, id_pedido_compra: int) -> float:
        """
        Calcula o total de um pedido de compra
        
        Args:
            id_pedido_compra: ID do pedido
        
        Returns:
            Valor total do pedido
        """
        try:
            with get_cursor(commit=False) as cursor:
                cursor.execute("""
                    SELECT COALESCE(SUM(quantidade * preco_custo_unitario), 0) as total
                    FROM Item_Pedido_Compra
                    WHERE id_pedido_compra = %s
                """, (id_pedido_compra,))
                
                row = cursor.fetchone()
                return float(row['total']) if row else 0.0
        except Exception as e:
            return 0.0

    def contar_itens_pedido(self, id_pedido_compra: int) -> int:
        """
        Conta quantos itens um pedido possui
        
        Args:
            id_pedido_compra: ID do pedido
        
        Returns:
            Número de itens
        """
        try:
            with get_cursor(commit=False) as cursor:
                cursor.execute("""
                    SELECT COUNT(*) as total
                    FROM Item_Pedido_Compra
                    WHERE id_pedido_compra = %s
                """, (id_pedido_compra,))
                
                row = cursor.fetchone()
                return row['total'] if row else 0
        except Exception as e:
            return 0

    def verificar_produto_em_pedido(self, id_pedido_compra: int, id_produto: int) -> bool:
        """
        Verifica se um produto já está no pedido
        
        Args:
            id_pedido_compra: ID do pedido
            id_produto: ID do produto
        
        Returns:
            True se o produto já está no pedido, False caso contrário
        """
        try:
            with get_cursor(commit=False) as cursor:
                cursor.execute("""
                    SELECT COUNT(*) as total
                    FROM Item_Pedido_Compra
                    WHERE id_pedido_compra = %s AND id_produto = %s
                """, (id_pedido_compra, id_produto))
                
                row = cursor.fetchone()
                return row['total'] > 0 if row else False
        except Exception as e:
            return False

    def buscar_por_pedido_e_produto(self, id_pedido_compra: int, id_produto: int) -> Optional[dict]:
        """
        Busca item específico por pedido e produto
        
        Args:
            id_pedido_compra: ID do pedido
            id_produto: ID do produto
        
        Returns:
            Dicionário com dados do item ou None se não encontrado
        """
        try:
            with get_cursor(commit=False) as cursor:
                cursor.execute("""
                    SELECT 
                        ipc.id_item_compra as id_item_pedido_compra,
                        ipc.id_pedido_compra,
                        ipc.id_produto,
                        ipc.quantidade,
                        ipc.preco_custo_unitario,
                        p.nome as produto_nome
                    FROM Item_Pedido_Compra ipc
                    JOIN Produto p ON ipc.id_produto = p.id_produto
                    WHERE ipc.id_pedido_compra = %s AND ipc.id_produto = %s
                """, (id_pedido_compra, id_produto))
                
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            return None

    def obter_historico_compras_produto(self, id_produto: int, limite: int = 10) -> List[dict]:
        """
        Obtém histórico de compras de um produto
        
        Args:
            id_produto: ID do produto
            limite: Número máximo de registros (padrão: 10)
        
        Returns:
            Lista com histórico de compras
        """
        try:
            with get_cursor(commit=False) as cursor:
                cursor.execute("""
                    SELECT 
                        pc.data_pedido,
                        f.nome_fantasia as fornecedor,
                        ipc.quantidade,
                        ipc.preco_custo_unitario,
                        (ipc.quantidade * ipc.preco_custo_unitario) as subtotal,
                        pc.status
                    FROM Item_Pedido_Compra ipc
                    JOIN Pedido_Compra pc ON ipc.id_pedido_compra = pc.id_pedido_compra
                    JOIN Fornecedor f ON pc.id_fornecedor = f.id_fornecedor
                    WHERE ipc.id_produto = %s AND pc.status = 'Recebido'
                    ORDER BY pc.data_pedido DESC
                    LIMIT %s
                """, (id_produto, limite))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            return []
