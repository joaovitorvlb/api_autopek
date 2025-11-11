from .db import get_cursor

class ProdutoDAO:
    def __init__(self):
        pass

    def listar_produtos(self):
        """Lista todos os produtos"""
        with get_cursor() as cur:
            sql = "SELECT id_produto, nome, descricao, sku, preco_venda, preco_custo_medio, estoque_atual, nome_imagem FROM Produto"
            cur.execute(sql)
            rows = cur.fetchall()
            return [dict(row) for row in rows]

    def inserir_produto(self, id_produto, nome, descricao, sku, preco_venda, preco_custo_medio, estoque_atual, nome_imagem=None):
        with get_cursor() as cur:
            cur.execute(
                """
                INSERT INTO Produto (id_produto, nome, descricao, sku, preco_venda, preco_custo_medio, estoque_atual, nome_imagem)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (id_produto, nome, descricao, sku, preco_venda, preco_custo_medio, estoque_atual, nome_imagem),
            )

    def buscar_produto(self, id_produto):
        """Busca um produto específico pelo ID"""
        with get_cursor() as cur:
            sql = "SELECT id_produto, nome, descricao, sku, preco_venda, preco_custo_medio, estoque_atual, nome_imagem FROM Produto WHERE id_produto = ?"
            cur.execute(sql, (id_produto,))
            row = cur.fetchone()
            return dict(row) if row else None

    def atualizar_produto(self, id_produto, nome, descricao, sku, preco_venda, preco_custo_medio, estoque_atual, nome_imagem=None):
        with get_cursor() as cur:
            cur.execute(
                """
                UPDATE Produto SET nome = ?, descricao = ?, sku = ?, preco_venda = ?, preco_custo_medio = ?, estoque_atual = ?, nome_imagem = ?
                WHERE id_produto = ?
                """,
                (nome, descricao, sku, preco_venda, preco_custo_medio, estoque_atual, nome_imagem, id_produto),
            )
        
        # Buscar e retornar o produto atualizado
        return self.buscar_por_id(id_produto)

    def deletar_produto(self, id_produto):
        with get_cursor() as cur:
            cur.execute("DELETE FROM Produto WHERE id_produto = ?;", (id_produto,))

    def inserir_produto_obj(self, produto):
        return self.inserir_produto(
            produto.id_produto,
            produto.nome,
            produto.descricao,
            produto.sku,
            produto.preco_venda,
            produto.preco_custo_medio,
            produto.estoque_atual,
            getattr(produto, 'nome_imagem', None),
        )

    def criar_produto(self, dados):
        """
        Cria um novo produto sem especificar ID (auto-increment)
        Retorna o produto criado com o ID gerado
        """
        try:
            with get_cursor() as cur:
                # INSERT do produto
                sql_insert = """
                INSERT INTO Produto (nome, descricao, sku, preco_venda, preco_custo_medio, estoque_atual, nome_imagem)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                params = (
                    dados['nome'], 
                    dados.get('descricao', ''), 
                    dados['sku'],
                    dados['preco_venda'], 
                    dados.get('preco_custo_medio', 0),
                    dados['estoque_atual'], 
                    dados.get('nome_imagem')
                )
                
                cur.execute(sql_insert, params)
                
                # Obter o ID do produto criado
                produto_id = cur.lastrowid
                
                # Buscar o produto na MESMA transação
                sql_select = "SELECT id_produto, nome, descricao, sku, preco_venda, preco_custo_medio, estoque_atual, nome_imagem FROM Produto WHERE id_produto = ?"
                
                cur.execute(sql_select, (produto_id,))
                row = cur.fetchone()
                
                if row:
                    produto_criado = dict(row)
                    return produto_criado
                else:
                    return None
                
        except Exception as e:
            raise e

    def listar_todos(self):
        """Alias para listar_produtos"""
        return self.listar_produtos()

    def buscar_por_id(self, id_produto):
        """Alias para buscar_produto"""
        return self.buscar_produto(id_produto)

    def buscar_por_nome(self, nome):
        """Busca produtos por nome (case-insensitive, busca parcial)"""
        with get_cursor() as cur:
            sql = """
                SELECT id_produto, nome, descricao, sku, preco_venda, preco_custo_medio, estoque_atual, nome_imagem 
                FROM Produto 
                WHERE nome LIKE ?
            """
            cur.execute(sql, (f'%{nome}%',))
            rows = cur.fetchall()
            return [dict(row) for row in rows]

    def deletar(self, id_produto):
        """Alias para deletar_produto"""
        self.deletar_produto(id_produto)
        return True
