"""
DAO para manipulação da tabela Item_Pedido_Venda no SQLite
"""

from typing import List, Optional
from decimal import Decimal
from dao_sqlite.db import get_cursor


class ItemPedidoVendaDAO:
    """
    Data Access Object para Item de Pedido de Venda
    """

    def criar(self, id_pedido_venda: int, id_produto: int,
              quantidade: int, preco_unitario_venda: float) -> Optional[int]:
        """
        Cria um novo item de pedido de venda
        
        Args:
            id_pedido_venda: ID do pedido de venda
            id_produto: ID do produto
            quantidade: Quantidade do produto
            preco_unitario_venda: Preço de venda unitário (snapshot do momento)
        
        Returns:
            ID do item criado ou None se houver erro
        """
        try:
            with get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Item_Pedido_Venda (id_pedido_venda, id_produto, quantidade, preco_unitario_venda)
                    VALUES (?, ?, ?, ?)
                """, (id_pedido_venda, id_produto, quantidade, preco_unitario_venda))
                
                return cursor.lastrowid
        except Exception as e:
            return None

    def buscar_por_id(self, id_item_pedido_venda: int) -> Optional[dict]:
        """
        Busca item de pedido de venda por ID
        
        Args:
            id_item_pedido_venda: ID do item
        
        Returns:
            Dicionário com dados do item ou None se não encontrado
        """
        try:
            with get_cursor(commit=False) as cursor:
                cursor.execute("""
                    SELECT 
                        ipv.id_item_venda as id_item_pedido_venda,
                        ipv.id_pedido_venda,
                        ipv.id_produto,
                        ipv.quantidade,
                        ipv.preco_unitario_venda,
                        p.nome as produto_nome,
                        p.sku as produto_sku,
                        p.estoque_atual as produto_estoque,
                        (ipv.quantidade * ipv.preco_unitario_venda) as subtotal
                    FROM Item_Pedido_Venda ipv
                    JOIN Produto p ON ipv.id_produto = p.id_produto
                    WHERE ipv.id_item_venda = ?
                """, (id_item_pedido_venda,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            return None

    def listar_por_pedido(self, id_pedido_venda: int) -> List[dict]:
        """
        Lista todos os itens de um pedido de venda
        
        Args:
            id_pedido_venda: ID do pedido
        
        Returns:
            Lista de dicionários com dados dos itens
        """
        try:
            with get_cursor(commit=False) as cursor:
                cursor.execute("""
                    SELECT 
                        ipv.id_item_venda as id_item_pedido_venda,
                        ipv.id_pedido_venda,
                        ipv.id_produto,
                        ipv.quantidade,
                        ipv.preco_unitario_venda,
                        p.nome as produto_nome,
                        p.sku as produto_sku,
                        p.descricao as produto_descricao,
                        p.estoque_atual as produto_estoque,
                        p.preco_custo_medio as produto_custo,
                        (ipv.quantidade * ipv.preco_unitario_venda) as subtotal,
                        (ipv.quantidade * p.preco_custo_medio) as custo_total,
                        ((ipv.quantidade * ipv.preco_unitario_venda) - (ipv.quantidade * p.preco_custo_medio)) as lucro
                    FROM Item_Pedido_Venda ipv
                    JOIN Produto p ON ipv.id_produto = p.id_produto
                    WHERE ipv.id_pedido_venda = ?
                    ORDER BY p.nome
                """, (id_pedido_venda,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            return None

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
                        ipv.id_item_venda as id_item_pedido_venda,
                        ipv.id_pedido_venda,
                        ipv.id_produto,
                        ipv.quantidade,
                        ipv.preco_unitario_venda,
                        pv.data_pedido,
                        pv.status as pedido_status,
                        u.nome as cliente_nome,
                        (ipv.quantidade * ipv.preco_unitario_venda) as subtotal
                    FROM Item_Pedido_Venda ipv
                    JOIN Pedido_Venda pv ON ipv.id_pedido_venda = pv.id_pedido_venda
                    JOIN Cliente c ON pv.id_cliente = c.id_cliente
                    JOIN Usuario u ON c.id_usuario = u.id_usuario
                    WHERE ipv.id_produto = ?
                    ORDER BY pv.data_pedido DESC
                """, (id_produto,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            return None

    def atualizar(self, id_item_pedido_venda: int, quantidade: int = None,
                  preco_unitario_venda: float = None) -> bool:
        """
        Atualiza dados de um item de pedido de venda
        
        Args:
            id_item_pedido_venda: ID do item
            quantidade: Nova quantidade (opcional)
            preco_unitario_venda: Novo preço (opcional)
        
        Returns:
            True se atualizado com sucesso, False caso contrário
        """
        try:
            campos = []
            valores = []
            
            if quantidade is not None:
                campos.append("quantidade = ?")
                valores.append(quantidade)
            
            if preco_unitario_venda is not None:
                campos.append("preco_unitario_venda = ?")
                valores.append(preco_unitario_venda)
            
            if not campos:
                return False
            
            valores.append(id_item_pedido_venda)
            
            with get_cursor() as cursor:
                query = f"""
                    UPDATE Item_Pedido_Venda
                    SET {', '.join(campos)}
                    WHERE id_item_venda = ?
                """
                cursor.execute(query, valores)
                
                return cursor.rowcount > 0
        except Exception as e:
            return False

    def deletar(self, id_item_pedido_venda: int) -> bool:
        """
        Deleta um item de pedido de venda
        
        Args:
            id_item_pedido_venda: ID do item
        
        Returns:
            True se deletado com sucesso, False caso contrário
        """
        try:
            with get_cursor() as cursor:
                cursor.execute("""
                    DELETE FROM Item_Pedido_Venda
                    WHERE id_item_venda = ?
                """, (id_item_pedido_venda,))
                
                return cursor.rowcount > 0
        except Exception as e:
            return False

    def deletar_por_pedido(self, id_pedido_venda: int) -> bool:
        """
        Deleta todos os itens de um pedido de venda
        
        Args:
            id_pedido_venda: ID do pedido
        
        Returns:
            True se deletado com sucesso, False caso contrário
        """
        try:
            with get_cursor() as cursor:
                cursor.execute("""
                    DELETE FROM Item_Pedido_Venda
                    WHERE id_pedido_venda = ?
                """, (id_pedido_venda,))
                
                return True
        except Exception as e:
            return False

    def calcular_total_pedido(self, id_pedido_venda: int) -> float:
        """
        Calcula o total de um pedido de venda
        
        Args:
            id_pedido_venda: ID do pedido
        
        Returns:
            Valor total do pedido
        """
        try:
            with get_cursor(commit=False) as cursor:
                cursor.execute("""
                    SELECT COALESCE(SUM(quantidade * preco_unitario_venda), 0) as total
                    FROM Item_Pedido_Venda
                    WHERE id_pedido_venda = ?
                """, (id_pedido_venda,))
                
                row = cursor.fetchone()
                return float(row['total']) if row else 0.0
        except Exception as e:
            return 0.0

    def contar_itens_pedido(self, id_pedido_venda: int) -> int:
        """
        Conta quantos itens um pedido possui
        
        Args:
            id_pedido_venda: ID do pedido
        
        Returns:
            Número de itens
        """
        try:
            with get_cursor(commit=False) as cursor:
                cursor.execute("""
                    SELECT COUNT(*) as total
                    FROM Item_Pedido_Venda
                    WHERE id_pedido_venda = ?
                """, (id_pedido_venda,))
                
                row = cursor.fetchone()
                return row['total'] if row else 0
        except Exception as e:
            return 0

    def verificar_produto_em_pedido(self, id_pedido_venda: int, id_produto: int) -> bool:
        """
        Verifica se um produto já está no pedido
        
        Args:
            id_pedido_venda: ID do pedido
            id_produto: ID do produto
        
        Returns:
            True se o produto já está no pedido, False caso contrário
        """
        try:
            with get_cursor(commit=False) as cursor:
                cursor.execute("""
                    SELECT COUNT(*) as total
                    FROM Item_Pedido_Venda
                    WHERE id_pedido_venda = ? AND id_produto = ?
                """, (id_pedido_venda, id_produto))
                
                row = cursor.fetchone()
                return row['total'] > 0 if row else False
        except Exception as e:
            return False

    def buscar_por_pedido_e_produto(self, id_pedido_venda: int, id_produto: int) -> Optional[dict]:
        """
        Busca item específico por pedido e produto
        
        Args:
            id_pedido_venda: ID do pedido
            id_produto: ID do produto
        
        Returns:
            Dicionário com dados do item ou None se não encontrado
        """
        try:
            with get_cursor(commit=False) as cursor:
                cursor.execute("""
                    SELECT 
                        ipv.id_item_venda as id_item_pedido_venda,
                        ipv.id_pedido_venda,
                        ipv.id_produto,
                        ipv.quantidade,
                        ipv.preco_unitario_venda,
                        p.nome as produto_nome
                    FROM Item_Pedido_Venda ipv
                    JOIN Produto p ON ipv.id_produto = p.id_produto
                    WHERE ipv.id_pedido_venda = ? AND ipv.id_produto = ?
                """, (id_pedido_venda, id_produto))
                
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            return None

    def verificar_disponibilidade_estoque(self, id_pedido_venda: int) -> List[dict]:
        """
        Verifica se há estoque suficiente para todos os itens do pedido
        
        Args:
            id_pedido_venda: ID do pedido
        
        Returns:
            Lista de produtos sem estoque suficiente (vazia se todos estão OK)
        """
        try:
            with get_cursor(commit=False) as cursor:
                cursor.execute("""
                    SELECT 
                        p.id_produto,
                        p.nome as produto_nome,
                        p.estoque_atual,
                        ipv.quantidade as quantidade_pedido,
                        (ipv.quantidade - p.estoque_atual) as falta
                    FROM Item_Pedido_Venda ipv
                    JOIN Produto p ON ipv.id_produto = p.id_produto
                    WHERE ipv.id_pedido_venda = ? AND p.estoque_atual < ipv.quantidade
                """, (id_pedido_venda,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            return None

    def obter_produtos_mais_vendidos(self, limite: int = 10, data_inicio: str = None, 
                                      data_fim: str = None) -> List[dict]:
        """
        Obtém os produtos mais vendidos
        
        Args:
            limite: Número máximo de produtos (padrão: 10)
            data_inicio: Data inicial (formato: YYYY-MM-DD)
            data_fim: Data final (formato: YYYY-MM-DD)
        
        Returns:
            Lista com os produtos mais vendidos
        """
        try:
            with get_cursor(commit=False) as cursor:
                query = """
                    SELECT 
                        p.id_produto,
                        p.nome as produto_nome,
                        p.sku,
                        SUM(ipv.quantidade) as total_vendido,
                        SUM(ipv.quantidade * ipv.preco_unitario_venda) as receita_total,
                        AVG(ipv.preco_unitario_venda) as preco_medio
                    FROM Item_Pedido_Venda ipv
                    JOIN Produto p ON ipv.id_produto = p.id_produto
                    JOIN Pedido_Venda pv ON ipv.id_pedido_venda = pv.id_pedido_venda
                    WHERE pv.status IN ('Confirmado', 'Separado', 'Enviado', 'Entregue')
                """
                params = []
                
                if data_inicio:
                    query += " AND DATE(pv.data_pedido) >= ?"
                    params.append(data_inicio)
                
                if data_fim:
                    query += " AND DATE(pv.data_pedido) <= ?"
                    params.append(data_fim)
                
                query += """
                    GROUP BY p.id_produto, p.nome, p.sku
                    ORDER BY total_vendido DESC
                    LIMIT ?
                """
                params.append(limite)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            return None

    def obter_historico_vendas_produto(self, id_produto: int, limite: int = 10) -> List[dict]:
        """
        Obtém histórico de vendas de um produto
        
        Args:
            id_produto: ID do produto
            limite: Número máximo de registros (padrão: 10)
        
        Returns:
            Lista com histórico de vendas
        """
        try:
            with get_cursor(commit=False) as cursor:
                cursor.execute("""
                    SELECT 
                        pv.data_pedido,
                        u.nome as cliente,
                        ipv.quantidade,
                        ipv.preco_unitario_venda,
                        (ipv.quantidade * ipv.preco_unitario_venda) as subtotal,
                        pv.status
                    FROM Item_Pedido_Venda ipv
                    JOIN Pedido_Venda pv ON ipv.id_pedido_venda = pv.id_pedido_venda
                    JOIN Cliente c ON pv.id_cliente = c.id_cliente
                    JOIN Usuario u ON c.id_usuario = u.id_usuario
                    WHERE ipv.id_produto = ? 
                        AND pv.status IN ('Confirmado', 'Separado', 'Enviado', 'Entregue')
                    ORDER BY pv.data_pedido DESC
                    LIMIT ?
                """, (id_produto, limite))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            return []
