"""
DAO para manipulação da tabela Pedido_Compra no MySQL
COM LOGS DE DEBUG (print)
"""

import sys
from typing import List, Optional
from datetime import datetime
from .db_pythonanywhere import get_cursor


class PedidoCompraDAO:
    """
    Data Access Object para Pedido de Compra
    """

    def criar(self, id_fornecedor: int, id_funcionario: int, 
              status: str = 'Pendente') -> Optional[int]:
        """
        Cria um novo pedido de compra
        """
        print(f"[LOG DAO] Tentando criar PedidoCompra. Fornecedor: {id_fornecedor}, Funcionario: {id_funcionario}, Status: {status}")
        try:
            with get_cursor() as cursor:
                sql = """
                    INSERT INTO Pedido_Compra (id_fornecedor, id_funcionario, data_pedido, status, total)
                    VALUES (%s, %s, %s, %s, 0.00)
                """
                data_agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                params = (id_fornecedor, id_funcionario, data_agora, status)
                
                print(f"[LOG DAO] Executando SQL: INSERT Pedido_Compra com params {params}")
                cursor.execute(sql, params)
                
                novo_id = cursor.lastrowid
                print(f"[LOG DAO] PedidoCompra criado com sucesso. ID: {novo_id}")
                return novo_id
        except Exception as e:
            print(f"[ERRO DAO] Erro ao criar PedidoCompra: {e}", file=sys.stderr)
            return None

    def buscar_por_id(self, id_pedido_compra: int) -> Optional[dict]:
        """
        Busca pedido de compra por ID com informações do fornecedor e funcionário
        """
        print(f"[LOG DAO] Buscando PedidoCompra por ID: {id_pedido_compra}")
        try:
            with get_cursor(commit=False) as cursor:
                sql = """
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
                    LEFT JOIN Funcionario func ON pc.id_funcionario = func.id_funcionario
                    LEFT JOIN usuario u ON func.id_usuario = u.id_usuario
                    WHERE pc.id_pedido_compra = %s
                """
                params = (id_pedido_compra,)
                print(f"[LOG DAO] Executando SQL: SELECT Pedido_Compra ID {id_pedido_compra}")
                cursor.execute(sql, params)
                
                row = cursor.fetchone()
                if row:
                    print(f"[LOG DAO] PedidoCompra {id_pedido_compra} encontrado.")
                    return dict(row)
                
                print(f"[LOG DAO] PedidoCompra {id_pedido_compra} não encontrado.")
                return None
        except Exception as e:
            print(f"[ERRO DAO] Erro ao buscar PedidoCompra {id_pedido_compra}: {e}", file=sys.stderr)
            return None

    def listar_todos(self, status: str = None) -> List[dict]:
        """
        Lista todos os pedidos de compra
        """
        print(f"[LOG DAO] Listando todos PedidoCompra. Filtro Status: {status}")
        try:
            with get_cursor(commit=False) as cursor:
                params = []
                sql_base = """
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
                    LEFT JOIN Funcionario func ON pc.id_funcionario = func.id_funcionario
                    LEFT JOIN usuario u ON func.id_usuario = u.id_usuario
                """
                
                if status:
                    sql_base += " WHERE pc.status = %s"
                    params.append(status)
                
                sql_base += " ORDER BY pc.data_pedido DESC"
                
                print(f"[LOG DAO] Executando SQL: LISTAR TODOS com params {params}")
                cursor.execute(sql_base, params)
                
                rows = cursor.fetchall()
                print(f"[LOG DAO] Encontrados {len(rows)} pedidos.")
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"[ERRO DAO] Erro ao listar PedidoCompra: {e}", file=sys.stderr)
            return []

    def listar_por_fornecedor(self, id_fornecedor: int) -> List[dict]:
        """
        Lista pedidos de compra de um fornecedor específico
        """
        print(f"[LOG DAO] Listando PedidoCompra por Fornecedor ID: {id_fornecedor}")
        try:
            with get_cursor(commit=False) as cursor:
                sql = """
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
                    LEFT JOIN Funcionario func ON pc.id_funcionario = func.id_funcionario
                    LEFT JOIN usuario u ON func.id_usuario = u.id_usuario
                    WHERE pc.id_fornecedor = %s
                    ORDER BY pc.data_pedido DESC
                """
                params = (id_fornecedor,)
                print(f"[LOG DAO] Executando SQL com params {params}")
                cursor.execute(sql, params)
                
                rows = cursor.fetchall()
                print(f"[LOG DAO] Encontrados {len(rows)} pedidos para o fornecedor {id_fornecedor}.")
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"[ERRO DAO] Erro ao listar por fornecedor {id_fornecedor}: {e}", file=sys.stderr)
            return []

    def listar_por_funcionario(self, id_funcionario: int) -> List[dict]:
        """
        Lista pedidos de compra realizados por um funcionário
        """
        print(f"[LOG DAO] Listando PedidoCompra por Funcionario ID: {id_funcionario}")
        try:
            with get_cursor(commit=False) as cursor:
                sql = """
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
                    LEFT JOIN Funcionario func ON pc.id_funcionario = func.id_funcionario
                    LEFT JOIN usuario u ON func.id_usuario = u.id_usuario
                    WHERE pc.id_funcionario = %s
                    ORDER BY pc.data_pedido DESC
                """
                params = (id_funcionario,)
                print(f"[LOG DAO] Executando SQL com params {params}")
                cursor.execute(sql, params)
                
                rows = cursor.fetchall()
                print(f"[LOG DAO] Encontrados {len(rows)} pedidos para o funcionário {id_funcionario}.")
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"[ERRO DAO] Erro ao listar por funcionário {id_funcionario}: {e}", file=sys.stderr)
            return []

    def atualizar_status(self, id_pedido_compra: int, novo_status: str) -> bool:
        """
        Atualiza o status de um pedido de compra
        """
        print(f"[LOG DAO] Atualizando status PedidoCompra {id_pedido_compra} para '{novo_status}'")
        try:
            with get_cursor() as cursor:
                sql = """
                    UPDATE Pedido_Compra
                    SET status = %s
                    WHERE id_pedido_compra = %s
                """
                params = (novo_status, id_pedido_compra)
                print(f"[LOG DAO] Executando SQL: UPDATE Status com params {params}")
                cursor.execute(sql, params)
                
                sucesso = cursor.rowcount > 0
                print(f"[LOG DAO] Atualização de status para {id_pedido_compra} bem-sucedida: {sucesso}")
                return sucesso
        except Exception as e:
            print(f"[ERRO DAO] Erro ao atualizar status {id_pedido_compra}: {e}", file=sys.stderr)
            return False

    def atualizar_total(self, id_pedido_compra: int) -> bool:
        """
        Recalcula e atualiza o total do pedido baseado nos itens
        """
        print(f"[LOG DAO] Atualizando total do PedidoCompra {id_pedido_compra}")
        try:
            with get_cursor() as cursor:
                sql = """
                    UPDATE Pedido_Compra
                    SET total = (
                        SELECT COALESCE(SUM(quantidade * preco_custo_unitario), 0)
                        FROM Item_Pedido_Compra
                        WHERE id_pedido_compra = %s
                    )
                    WHERE id_pedido_compra = %s
                """
                params = (id_pedido_compra, id_pedido_compra)
                print(f"[LOG DAO] Executando SQL: UPDATE Total com params {params}")
                cursor.execute(sql, params)
                
                sucesso = cursor.rowcount > 0
                print(f"[LOG DAO] Atualização de total para {id_pedido_compra} bem-sucedida: {sucesso}")
                return sucesso
        except Exception as e:
            print(f"[ERRO DAO] Erro ao atualizar total {id_pedido_compra}: {e}", file=sys.stderr)
            return False

    def receber_pedido(self, id_pedido_compra: int) -> bool:
        """
        Marca o pedido como recebido e atualiza o estoque dos produtos
        """
        print(f"[LOG DAO] Recebendo PedidoCompra ID: {id_pedido_compra} e atualizando estoque")
        try:
            with get_cursor() as cursor:
                # Buscar itens do pedido
                print(f"[LOG DAO] Buscando itens do pedido {id_pedido_compra}")
                cursor.execute("""
                    SELECT id_produto, quantidade, preco_custo_unitario
                    FROM Item_Pedido_Compra
                    WHERE id_pedido_compra = %s
                """, (id_pedido_compra,))
                
                itens = cursor.fetchall()
                print(f"[LOG DAO] Encontrados {len(itens)} itens para o pedido {id_pedido_compra}")
                
                # Atualizar estoque de cada produto
                for item in itens:
                    id_produto = item['id_produto']
                    quantidade = item['quantidade']
                    preco_custo = item['preco_custo_unitario']
                    
                    print(f"[LOG DAO] Processando item: Produto {id_produto}, Qtd: {quantidade}, Custo: {preco_custo}")
                    
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
                        
                        print(f"[LOG DAO] Atualizando Produto {id_produto}. Novo Estoque: {novo_estoque}, Novo Custo Médio: {novo_custo_medio:.2f}")
                        
                        # Atualizar produto
                        cursor.execute("""
                            UPDATE Produto
                            SET estoque_atual = %s,
                                preco_custo_medio = %s
                            WHERE id_produto = %s
                        """, (novo_estoque, novo_custo_medio, id_produto))
                    else:
                        print(f"[AVISO DAO] Produto {id_produto} do pedido {id_pedido_compra} não encontrado. Estoque não atualizado.", file=sys.stderr)
                
                # Atualizar status do pedido
                print(f"[LOG DAO] Marcando pedido {id_pedido_compra} como 'Recebido'")
                cursor.execute("""
                    UPDATE Pedido_Compra
                    SET status = 'Recebido'
                    WHERE id_pedido_compra = %s
                """, (id_pedido_compra,))
                
                print(f"[LOG DAO] Pedido {id_pedido_compra} recebido com sucesso.")
                return True
        except Exception as e:
            print(f"[ERRO DAO] Erro ao receber PedidoCompra {id_pedido_compra}: {e}", file=sys.stderr)
            print("[ERRO DAO] Transação será revertida (rollback).")
            return False

    def cancelar_pedido(self, id_pedido_compra: int) -> bool:
        """
        Cancela um pedido de compra
        ATENÇÃO: Se o pedido já foi recebido, não deve ser cancelado
        """
        print(f"[LOG DAO] Tentando cancelar PedidoCompra ID: {id_pedido_compra}")
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
                    print(f"[AVISO DAO] Tentativa de cancelar pedido {id_pedido_compra} que já foi 'Recebido'. Ação bloqueada.")
                    return False
                
                if not row:
                    print(f"[AVISO DAO] Pedido {id_pedido_compra} não encontrado para cancelamento.")
                    return False

                print(f"[LOG DAO] Marcando pedido {id_pedido_compra} como 'Cancelado'")
                cursor.execute("""
                    UPDATE Pedido_Compra
                    SET status = 'Cancelado'
                    WHERE id_pedido_compra = %s
                """, (id_pedido_compra,))
                
                sucesso = cursor.rowcount > 0
                print(f"[LOG DAO] Pedido {id_pedido_compra} cancelado: {sucesso}")
                return sucesso
        except Exception as e:
            print(f"[ERRO DAO] Erro ao cancelar PedidoCompra {id_pedido_compra}: {e}", file=sys.stderr)
            return False

    def deletar(self, id_pedido_compra: int) -> bool:
        """
        Deleta um pedido de compra permanentemente
        ATENÇÃO: Só deve ser usado se o pedido não tiver itens ou não foi recebido
        """
        print(f"[LOG DAO] Tentando deletar PedidoCompra ID: {id_pedido_compra}")
        try:
            with get_cursor() as cursor:
                # É uma boa prática verificar o status antes de deletar
                cursor.execute("SELECT status FROM Pedido_Compra WHERE id_pedido_compra = %s", (id_pedido_compra,))
                row = cursor.fetchone()
                if row and row['status'] == 'Recebido':
                    print(f"[AVISO DAO] Não é permitido deletar pedido {id_pedido_compra} que já foi 'Recebido'.", file=sys.stderr)
                    return False
                
                print(f"[LOG DAO] Executando SQL: DELETE Pedido_Compra {id_pedido_compra}")
                cursor.execute("""
                    DELETE FROM Pedido_Compra
                    WHERE id_pedido_compra = %s
                """, (id_pedido_compra,))
                
                sucesso = cursor.rowcount > 0
                print(f"[LOG DAO] Pedido {id_pedido_compra} deletado: {sucesso}")
                return sucesso
        except Exception as e:
            # Pode falhar por restrições de chave estrangeira (itens de pedido)
            print(f"[ERRO DAO] Erro ao deletar PedidoCompra {id_pedido_compra}: {e}", file=sys.stderr)
            print("[ERRO DAO] Verifique se existem Itens_Pedido_Compra associados.")
            return False

    def obter_relatorio_compras(self, data_inicio: str = None, data_fim: str = None) -> List[dict]:
        """
        Obtém relatório de compras em um período
        """
        print(f"[LOG DAO] Gerando relatório de compras. Início: {data_inicio}, Fim: {data_fim}")
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
                
                print(f"[LOG DAO] Executando SQL relatório com params: {params}")
                cursor.execute(query, params)
                rows = cursor.fetchall()
                print(f"[LOG DAO] Relatório gerado com {len(rows)} linhas.")
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"[ERRO DAO] Erro ao gerar relatório de compras: {e}", file=sys.stderr)
            return []