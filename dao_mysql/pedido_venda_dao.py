"""
DAO para manipulação da tabela Pedido_Venda no MySQL
"""

from typing import List, Optional
from datetime import datetime
from .db_pythonanywhere import get_cursor


class PedidoVendaDAO:
    """
    Data Access Object para Pedido de Venda
    """

    def criar(self, id_cliente: int, id_funcionario: int = None,
              status: str = 'Pendente') -> Optional[int]:
        """
        Cria um novo pedido de venda
        
        Args:
            id_cliente: ID do cliente
            id_funcionario: ID do funcionário vendedor (opcional para vendas online)
            status: Status inicial (padrão: 'Pendente')
        
        Returns:
            ID do pedido criado ou None se houver erro
        """
        try:
            with get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Pedido_Venda (id_cliente, id_funcionario, data_pedido, status, total)
                    VALUES (%s, %s, %s, %s, 0.00)
                """, (id_cliente, id_funcionario, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), status))
                
                return cursor.lastrowid
        except Exception as e:
            return None

    def buscar_por_id(self, id_pedido_venda: int) -> Optional[dict]:
        """
        Busca pedido de venda por ID com informações do cliente e funcionário
        
        Args:
            id_pedido_venda: ID do pedido
        
        Returns:
            Dicionário com dados do pedido ou None se não encontrado
        """
        try:
            with get_cursor(commit=False) as cursor:
                cursor.execute("""
                    SELECT 
                        pv.id_pedido_venda,
                        pv.id_cliente,
                        pv.id_funcionario,
                        pv.data_pedido,
                        pv.status,
                        pv.total,
                        u_cliente.nome as cliente_nome,
                        u_cliente.email as cliente_email,
                        u_cliente.cpf as cliente_cpf,
                        u_func.nome as funcionario_nome
                    FROM Pedido_Venda pv
                    JOIN Cliente c ON pv.id_cliente = c.id_cliente
                    JOIN usuario u_cliente ON c.id_usuario = u_cliente.id_usuario
                    LEFT JOIN Funcionario f ON pv.id_funcionario = f.id_funcionario
                    LEFT JOIN usuario u_func ON f.id_usuario = u_func.id_usuario
                    WHERE pv.id_pedido_venda = %s
                """, (id_pedido_venda,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            return None

    def listar_todos(self, status: str = None) -> List[dict]:
        """
        Lista todos os pedidos de venda
        
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
                            pv.id_pedido_venda,
                            pv.id_cliente,
                            pv.id_funcionario,
                            pv.data_pedido,
                            pv.status,
                            pv.total,
                            u_cliente.nome as cliente_nome,
                            u_func.nome as funcionario_nome
                        FROM Pedido_Venda pv
                        JOIN Cliente c ON pv.id_cliente = c.id_cliente
                        JOIN usuario u_cliente ON c.id_usuario = u_cliente.id_usuario
                        LEFT JOIN Funcionario f ON pv.id_funcionario = f.id_funcionario
                        LEFT JOIN usuario u_func ON f.id_usuario = u_func.id_usuario
                        WHERE pv.status = %s
                        ORDER BY pv.data_pedido DESC
                    """, (status,))
                else:
                    cursor.execute("""
                        SELECT 
                            pv.id_pedido_venda,
                            pv.id_cliente,
                            pv.id_funcionario,
                            pv.data_pedido,
                            pv.status,
                            pv.total,
                            u_cliente.nome as cliente_nome,
                            u_func.nome as funcionario_nome
                        FROM Pedido_Venda pv
                        JOIN Cliente c ON pv.id_cliente = c.id_cliente
                        JOIN usuario u_cliente ON c.id_usuario = u_cliente.id_usuario
                        LEFT JOIN Funcionario f ON pv.id_funcionario = f.id_funcionario
                        LEFT JOIN usuario u_func ON f.id_usuario = u_func.id_usuario
                        ORDER BY pv.data_pedido DESC
                    """)
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            return []

    def listar_por_cliente(self, id_cliente: int) -> List[dict]:
        """
        Lista pedidos de venda de um cliente específico
        
        Args:
            id_cliente: ID do cliente
        
        Returns:
            Lista de dicionários com dados dos pedidos
        """
        try:
            with get_cursor(commit=False) as cursor:
                cursor.execute("""
                    SELECT 
                        pv.id_pedido_venda,
                        pv.id_cliente,
                        pv.id_funcionario,
                        pv.data_pedido,
                        pv.status,
                        pv.total,
                        u_cliente.nome as cliente_nome,
                        u_func.nome as funcionario_nome
                    FROM Pedido_Venda pv
                    JOIN Cliente c ON pv.id_cliente = c.id_cliente
                    JOIN usuario u_cliente ON c.id_usuario = u_cliente.id_usuario
                    LEFT JOIN Funcionario f ON pv.id_funcionario = f.id_funcionario
                    LEFT JOIN usuario u_func ON f.id_usuario = u_func.id_usuario
                    WHERE pv.id_cliente = %s
                    ORDER BY pv.data_pedido DESC
                """, (id_cliente,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            return []

    def listar_por_funcionario(self, id_funcionario: int) -> List[dict]:
        """
        Lista pedidos de venda realizados por um funcionário
        
        Args:
            id_funcionario: ID do funcionário
        
        Returns:
            Lista de dicionários com dados dos pedidos
        """
        try:
            with get_cursor(commit=False) as cursor:
                cursor.execute("""
                    SELECT 
                        pv.id_pedido_venda,
                        pv.id_cliente,
                        pv.id_funcionario,
                        pv.data_pedido,
                        pv.status,
                        pv.total,
                        u_cliente.nome as cliente_nome,
                        u_func.nome as funcionario_nome
                    FROM Pedido_Venda pv
                    JOIN Cliente c ON pv.id_cliente = c.id_cliente
                    JOIN usuario u_cliente ON c.id_usuario = u_cliente.id_usuario
                    LEFT JOIN Funcionario f ON pv.id_funcionario = f.id_funcionario
                    LEFT JOIN usuario u_func ON f.id_usuario = u_func.id_usuario
                    WHERE pv.id_funcionario = %s
                    ORDER BY pv.data_pedido DESC
                """, (id_funcionario,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            return []

    def atualizar_status(self, id_pedido_venda: int, novo_status: str) -> bool:
        """
        Atualiza o status de um pedido de venda
        
        Args:
            id_pedido_venda: ID do pedido
            novo_status: Novo status (Pendente, Confirmado, Separado, Enviado, Entregue, Cancelado)
        
        Returns:
            True se atualizado com sucesso, False caso contrário
        """
        try:
            with get_cursor() as cursor:
                cursor.execute("""
                    UPDATE Pedido_Venda
                    SET status = %s
                    WHERE id_pedido_venda = %s
                """, (novo_status, id_pedido_venda))
                
                return cursor.rowcount > 0
        except Exception as e:
            return False

    def atualizar_total(self, id_pedido_venda: int) -> bool:
        """
        Recalcula e atualiza o total do pedido baseado nos itens
        
        Args:
            id_pedido_venda: ID do pedido
        
        Returns:
            True se atualizado com sucesso, False caso contrário
        """
        try:
            with get_cursor() as cursor:
                cursor.execute("""
                    UPDATE Pedido_Venda
                    SET total = (
                        SELECT COALESCE(SUM(quantidade * preco_unitario_venda), 0)
                        FROM Item_Pedido_Venda
                        WHERE id_pedido_venda = %s
                    )
                    WHERE id_pedido_venda = %s
                """, (id_pedido_venda, id_pedido_venda))
                
                return cursor.rowcount > 0
        except Exception as e:
            return False

    def confirmar_pedido(self, id_pedido_venda: int) -> bool:
        """
        Confirma o pedido e dá baixa no estoque dos produtos
        
        Args:
            id_pedido_venda: ID do pedido
        
        Returns:
            True se confirmado com sucesso, False caso contrário
        """
        try:
            with get_cursor() as cursor:
                # Buscar itens do pedido
                cursor.execute("""
                    SELECT id_produto, quantidade
                    FROM Item_Pedido_Venda
                    WHERE id_pedido_venda = %s
                """, (id_pedido_venda,))
                
                itens = cursor.fetchall()
                
                # Verificar disponibilidade em estoque
                for item in itens:
                    id_produto = item['id_produto']
                    quantidade = item['quantidade']
                    
                    cursor.execute("""
                        SELECT estoque_atual
                        FROM Produto
                        WHERE id_produto = %s
                    """, (id_produto,))
                    
                    produto = cursor.fetchone()
                    if not produto or produto['estoque_atual'] < quantidade:
                        return False
                
                # Dar baixa no estoque
                for item in itens:
                    id_produto = item['id_produto']
                    quantidade = item['quantidade']
                    
                    cursor.execute("""
                        UPDATE Produto
                        SET estoque_atual = estoque_atual - %s
                        WHERE id_produto = %s
                    """, (quantidade, id_produto))
                
                # Atualizar status do pedido
                cursor.execute("""
                    UPDATE Pedido_Venda
                    SET status = 'Confirmado'
                    WHERE id_pedido_venda = %s
                """, (id_pedido_venda,))
                
                return True
        except Exception as e:
            return False

    def cancelar_pedido(self, id_pedido_venda: int, devolver_estoque: bool = False) -> bool:
        """
        Cancela um pedido de venda
        
        Args:
            id_pedido_venda: ID do pedido
            devolver_estoque: Se True, devolve os produtos ao estoque (se pedido já foi confirmado)
        
        Returns:
            True se cancelado com sucesso, False caso contrário
        """
        try:
            with get_cursor() as cursor:
                # Verificar status atual
                cursor.execute("""
                    SELECT status
                    FROM Pedido_Venda
                    WHERE id_pedido_venda = %s
                """, (id_pedido_venda,))
                
                row = cursor.fetchone()
                if not row:
                    return False
                
                status_atual = row['status']
                
                # Se pedido já foi confirmado e deve devolver estoque
                if devolver_estoque and status_atual in ['Confirmado', 'Separado', 'Enviado']:
                    # Buscar itens do pedido
                    cursor.execute("""
                        SELECT id_produto, quantidade
                        FROM Item_Pedido_Venda
                        WHERE id_pedido_venda = %s
                    """, (id_pedido_venda,))
                    
                    itens = cursor.fetchall()
                    
                    # Devolver ao estoque
                    for item in itens:
                        cursor.execute("""
                            UPDATE Produto
                            SET estoque_atual = estoque_atual + %s
                            WHERE id_produto = %s
                        """, (item['quantidade'], item['id_produto']))
                
                # Cancelar pedido
                cursor.execute("""
                    UPDATE Pedido_Venda
                    SET status = 'Cancelado'
                    WHERE id_pedido_venda = %s
                """, (id_pedido_venda,))
                
                return cursor.rowcount > 0
        except Exception as e:
            return False

    def deletar(self, id_pedido_venda: int) -> bool:
        """
        Deleta um pedido de venda permanentemente
        ATENÇÃO: Só deve ser usado se o pedido não tiver itens ou não foi confirmado
        
        Args:
            id_pedido_venda: ID do pedido
        
        Returns:
            True se deletado com sucesso, False caso contrário
        """
        try:
            with get_cursor() as cursor:
                cursor.execute("""
                    DELETE FROM Pedido_Venda
                    WHERE id_pedido_venda = %s
                """, (id_pedido_venda,))
                
                return cursor.rowcount > 0
        except Exception as e:
            return False

    def calcular_lucro_pedido(self, id_pedido_venda: int) -> Optional[dict]:
        """
        Calcula o lucro de um pedido de venda
        
        Args:
            id_pedido_venda: ID do pedido
        
        Returns:
            Dicionário com informações de lucro ou None se houver erro
        """
        try:
            with get_cursor(commit=False) as cursor:
                cursor.execute("""
                    SELECT 
                        pv.total as valor_venda,
                        SUM(iv.quantidade * p.preco_custo_medio) as custo_total,
                        (pv.total - SUM(iv.quantidade * p.preco_custo_medio)) as lucro_bruto,
                        CASE 
                            WHEN pv.total > 0 THEN 
                                ((pv.total - SUM(iv.quantidade * p.preco_custo_medio)) / pv.total * 100)
                            ELSE 0
                        END as margem_percentual
                    FROM Pedido_Venda pv
                    JOIN Item_Pedido_Venda iv ON pv.id_pedido_venda = iv.id_pedido_venda
                    JOIN Produto p ON iv.id_produto = p.id_produto
                    WHERE pv.id_pedido_venda = %s
                    GROUP BY pv.id_pedido_venda, pv.total
                """, (id_pedido_venda,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            return None

    def obter_relatorio_vendas(self, data_inicio: str = None, data_fim: str = None) -> List[dict]:
        """
        Obtém relatório de vendas em um período
        
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
                        DATE(pv.data_pedido) as data,
                        COUNT(pv.id_pedido_venda) as total_pedidos,
                        SUM(pv.total) as valor_total,
                        AVG(pv.total) as ticket_medio
                    FROM Pedido_Venda pv
                    WHERE pv.status IN ('Confirmado', 'Separado', 'Enviado', 'Entregue')
                """
                params = []
                
                if data_inicio:
                    query += " AND DATE(pv.data_pedido) >= %s"
                    params.append(data_inicio)
                
                if data_fim:
                    query += " AND DATE(pv.data_pedido) <= %s"
                    params.append(data_fim)
                
                query += " GROUP BY DATE(pv.data_pedido) ORDER BY data DESC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            return []

    def obter_performance_vendedor(self, id_funcionario: int) -> Optional[dict]:
        """
        Obtém estatísticas de performance de um vendedor
        
        Args:
            id_funcionario: ID do funcionário
        
        Returns:
            Dicionário com estatísticas ou None se houver erro
        """
        try:
            with get_cursor(commit=False) as cursor:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_vendas,
                        SUM(total) as valor_total_vendido,
                        AVG(total) as ticket_medio,
                        MAX(data_pedido) as ultima_venda
                    FROM Pedido_Venda
                    WHERE id_funcionario = %s 
                        AND status IN ('Confirmado', 'Separado', 'Enviado', 'Entregue')
                """, (id_funcionario,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            return None
