"""
DAO para manipulação da tabela Pedido_Compra no MySQL
"""

from typing import List, Optional
from datetime import datetime
from dao_mysql.db_pythonanywhere import get_cursor


class PedidoCompraDAO:
    """
    Data Access Object para Pedido de Compra
    """

    def criar(self, id_fornecedor: int, id_funcionario: int, 
              status: str = 'Pendente') -> Optional[int]:
        """
        Cria um novo pedido de compra
        
        Args:
            id_fornecedor: ID do fornecedor
            id_funcionario: ID do funcionário responsável
            status: Status inicial (padrão: 'Pendente')
        
        Returns:
            ID do pedido criado ou None se houver erro
        """
        try:
            with get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Pedido_Compra (id_fornecedor, id_funcionario, data_pedido, status, total)
                    VALUES (%s, %s, %s, %s, 0.00)
                """, (id_fornecedor, id_funcionario, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), status))
                
                return cursor.lastrowid
        except Exception as e:
            return None

    def buscar_por_id(self, id_pedido_compra: int) -> Optional[dict]:
        """
        Busca pedido de compra por ID com informações do fornecedor e funcionário
        
        Args:
            id_pedido_compra: ID do pedido
        
        Returns:
            Dicionário com dados do pedido ou None se não encontrado
        """
        try:
            with get_cursor(commit=False) as cursor:
                cursor.execute("""
                    SELECT 
                        pc.id_pedido_compra,
                        pc.id_fornecedor,
                        pc.id_funcionario,
                        pc.data_pedido,
                        pc.status,
                        pc.total,
                        f.nome_fantasia as fornecedor_nome,
                        f.cnpj as fornecedor_cnpj,
                        u.nome as funcionario_nome
                    FROM Pedido_Compra pc
                    JOIN Fornecedor f ON pc.id_fornecedor = f.id_fornecedor
                    JOIN Funcionario func ON pc.id_funcionario = func.id_funcionario
                    JOIN Usuario u ON func.id_usuario = u.id_usuario
                    WHERE pc.id_pedido_compra = %s
                """, (id_pedido_compra,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            return None

    def listar_todos(self, status: str = None) -> List[dict]:
        """
        Lista todos os pedidos de compra
        
        Args:
            status: Filtrar por status específico (opcional)
        
        Returns:
            Lista de dicionários com dados dos pedidos
        """
        try:
            with get_cursor(commit=False) as cursor:
                if status:
                    cursor.execute("""
                        SELECT 
                            pc.id_pedido_compra,
                            pc.id_fornecedor,
                            pc.id_funcionario,
                            pc.data_pedido,
                            pc.status,
                            pc.total,
                            f.nome_fantasia as fornecedor_nome,
                            u.nome as funcionario_nome
                        FROM Pedido_Compra pc
                        JOIN Fornecedor f ON pc.id_fornecedor = f.id_fornecedor
                        JOIN Funcionario func ON pc.id_funcionario = func.id_funcionario
                        JOIN Usuario u ON func.id_usuario = u.id_usuario
                        WHERE pc.status = %s
                        ORDER BY pc.data_pedido DESC
                    """, (status,))
                else:
                    cursor.execute("""
                        SELECT 
                            pc.id_pedido_compra,
                            pc.id_fornecedor,
                            pc.id_funcionario,
                            pc.data_pedido,
                            pc.status,
                            pc.total,
                            f.nome_fantasia as fornecedor_nome,
                            u.nome as funcionario_nome
                        FROM Pedido_Compra pc
                        JOIN Fornecedor f ON pc.id_fornecedor = f.id_fornecedor
                        JOIN Funcionario func ON pc.id_funcionario = func.id_funcionario
                        JOIN Usuario u ON func.id_usuario = u.id_usuario
                        ORDER BY pc.data_pedido DESC
                    """)
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            return []

    def listar_por_fornecedor(self, id_fornecedor: int) -> List[dict]:
        """
        Lista pedidos de compra de um fornecedor específico
        
        Args:
            id_fornecedor: ID do fornecedor
        
        Returns:
            Lista de dicionários com dados dos pedidos
        """
        try:
            with get_cursor(commit=False) as cursor:
                cursor.execute("""
                    SELECT 
                        pc.id_pedido_compra,
                        pc.id_fornecedor,
                        pc.id_funcionario,
                        pc.data_pedido,
                        pc.status,
                        pc.total,
                        f.nome_fantasia as fornecedor_nome,
                        u.nome as funcionario_nome
                    FROM Pedido_Compra pc
                    JOIN Fornecedor f ON pc.id_fornecedor = f.id_fornecedor
                    JOIN Funcionario func ON pc.id_funcionario = func.id_funcionario
                    JOIN Usuario u ON func.id_usuario = u.id_usuario
                    WHERE pc.id_fornecedor = %s
                    ORDER BY pc.data_pedido DESC
                """, (id_fornecedor,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            return []

    def listar_por_funcionario(self, id_funcionario: int) -> List[dict]:
        """
        Lista pedidos de compra realizados por um funcionário
        
        Args:
            id_funcionario: ID do funcionário
        
        Returns:
            Lista de dicionários com dados dos pedidos
        """
        try:
            with get_cursor(commit=False) as cursor:
                cursor.execute("""
                    SELECT 
                        pc.id_pedido_compra,
                        pc.id_fornecedor,
                        pc.id_funcionario,
                        pc.data_pedido,
                        pc.status,
                        pc.total,
                        f.nome_fantasia as fornecedor_nome,
                        u.nome as funcionario_nome
                    FROM Pedido_Compra pc
                    JOIN Fornecedor f ON pc.id_fornecedor = f.id_fornecedor
                    JOIN Funcionario func ON pc.id_funcionario = func.id_funcionario
                    JOIN Usuario u ON func.id_usuario = u.id_usuario
                    WHERE pc.id_funcionario = %s
                    ORDER BY pc.data_pedido DESC
                """, (id_funcionario,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            return []

    def atualizar_status(self, id_pedido_compra: int, novo_status: str) -> bool:
        """
        Atualiza o status de um pedido de compra
        
        Args:
            id_pedido_compra: ID do pedido
            novo_status: Novo status (Pendente, Aprovado, Enviado, Recebido, Cancelado)
        
        Returns:
            True se atualizado com sucesso, False caso contrário
        """
        try:
            with get_cursor() as cursor:
                cursor.execute("""
                    UPDATE Pedido_Compra
                    SET status = %s
                    WHERE id_pedido_compra = %s
                """, (novo_status, id_pedido_compra))
                
                return cursor.rowcount > 0
        except Exception as e:
            return False

    def atualizar_total(self, id_pedido_compra: int) -> bool:
        """
        Recalcula e atualiza o total do pedido baseado nos itens
        
        Args:
            id_pedido_compra: ID do pedido
        
        Returns:
            True se atualizado com sucesso, False caso contrário
        """
        try:
            with get_cursor() as cursor:
                cursor.execute("""
                    UPDATE Pedido_Compra
                    SET total = (
                        SELECT COALESCE(SUM(quantidade * preco_custo_unitario), 0)
                        FROM Item_Pedido_Compra
                        WHERE id_pedido_compra = %s
                    )
                    WHERE id_pedido_compra = %s
                """, (id_pedido_compra, id_pedido_compra))
                
                return cursor.rowcount > 0
        except Exception as e:
            return False

    def receber_pedido(self, id_pedido_compra: int) -> bool:
        """
        Marca o pedido como recebido e atualiza o estoque dos produtos
        
        Args:
            id_pedido_compra: ID do pedido
        
        Returns:
            True se recebido com sucesso, False caso contrário
        """
        try:
            with get_cursor() as cursor:
                # Buscar itens do pedido
                cursor.execute("""
                    SELECT id_produto, quantidade, preco_custo_unitario
                    FROM Item_Pedido_Compra
                    WHERE id_pedido_compra = %s
                """, (id_pedido_compra,))
                
                itens = cursor.fetchall()
                
                # Atualizar estoque de cada produto
                for item in itens:
                    id_produto = item['id_produto']
                    quantidade = item['quantidade']
                    preco_custo = item['preco_custo_unitario']
                    
                    # Buscar dados atuais do produto
                    cursor.execute("""
                        SELECT estoque_atual, preco_custo_medio
                        FROM Produto
                        WHERE id_produto = %s
                    """, (id_produto,))
                    
                    produto = cursor.fetchone()
                    if produto:
                        estoque_atual = produto['estoque_atual']
                        custo_medio_atual = produto['preco_custo_medio']
                        
                        # Calcular novo estoque
                        novo_estoque = estoque_atual + quantidade
                        
                        # Calcular novo custo médio ponderado
                        if estoque_atual > 0:
                            novo_custo_medio = (
                                (estoque_atual * custo_medio_atual) + (quantidade * preco_custo)
                            ) / novo_estoque
                        else:
                            novo_custo_medio = preco_custo
                        
                        # Atualizar produto
                        cursor.execute("""
                            UPDATE Produto
                            SET estoque_atual = %s,
                                preco_custo_medio = %s
                            WHERE id_produto = %s
                        """, (novo_estoque, novo_custo_medio, id_produto))
                
                # Atualizar status do pedido
                cursor.execute("""
                    UPDATE Pedido_Compra
                    SET status = 'Recebido'
                    WHERE id_pedido_compra = %s
                """, (id_pedido_compra,))
                
                return True
        except Exception as e:
            return False

    def cancelar_pedido(self, id_pedido_compra: int) -> bool:
        """
        Cancela um pedido de compra
        ATENÇÃO: Se o pedido já foi recebido, não deve ser cancelado
        
        Args:
            id_pedido_compra: ID do pedido
        
        Returns:
            True se cancelado com sucesso, False caso contrário
        """
        try:
            with get_cursor() as cursor:
                # Verificar se pedido já foi recebido
                cursor.execute("""
                    SELECT status
                    FROM Pedido_Compra
                    WHERE id_pedido_compra = %s
                """, (id_pedido_compra,))
                
                row = cursor.fetchone()
                if row and row['status'] == 'Recebido':
                    return False
                
                cursor.execute("""
                    UPDATE Pedido_Compra
                    SET status = 'Cancelado'
                    WHERE id_pedido_compra = %s
                """, (id_pedido_compra,))
                
                return cursor.rowcount > 0
        except Exception as e:
            return False

    def deletar(self, id_pedido_compra: int) -> bool:
        """
        Deleta um pedido de compra permanentemente
        ATENÇÃO: Só deve ser usado se o pedido não tiver itens ou não foi recebido
        
        Args:
            id_pedido_compra: ID do pedido
        
        Returns:
            True se deletado com sucesso, False caso contrário
        """
        try:
            with get_cursor() as cursor:
                cursor.execute("""
                    DELETE FROM Pedido_Compra
                    WHERE id_pedido_compra = %s
                """, (id_pedido_compra,))
                
                return cursor.rowcount > 0
        except Exception as e:
            return False

    def obter_relatorio_compras(self, data_inicio: str = None, data_fim: str = None) -> List[dict]:
        """
        Obtém relatório de compras em um período
        
        Args:
            data_inicio: Data inicial (formato: YYYY-MM-DD)
            data_fim: Data final (formato: YYYY-MM-DD)
        
        Returns:
            Lista com dados do relatório
        """
        try:
            with get_cursor(commit=False) as cursor:
                query = """
                    SELECT 
                        f.nome_fantasia as fornecedor,
                        COUNT(pc.id_pedido_compra) as total_pedidos,
                        SUM(pc.total) as valor_total,
                        AVG(pc.total) as valor_medio
                    FROM Pedido_Compra pc
                    JOIN Fornecedor f ON pc.id_fornecedor = f.id_fornecedor
                    WHERE pc.status = 'Recebido'
                """
                params = []
                
                if data_inicio:
                    query += " AND DATE(pc.data_pedido) >= %s"
                    params.append(data_inicio)
                
                if data_fim:
                    query += " AND DATE(pc.data_pedido) <= %s"
                    params.append(data_fim)
                
                query += " GROUP BY f.id_fornecedor, f.nome_fantasia ORDER BY valor_total DESC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            return []
