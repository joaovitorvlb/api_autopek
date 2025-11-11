class Produto:
    def __init__(self, id_produto, nome, sku, preco_venda, estoque_atual, descricao=None, preco_custo_medio=0.0, nome_imagem=None):
        self.id_produto = id_produto
        self.nome = nome
        self.descricao = descricao
        self.sku = sku
        self.preco_venda = preco_venda
        self.preco_custo_medio = preco_custo_medio
        self.estoque_atual = estoque_atual
        self.nome_imagem = nome_imagem

    def __repr__(self):
        return (
            f"<Produto id={self.id_produto} nome='{self.nome}' sku='{self.sku}' "
            f"preco_venda={self.preco_venda} estoque_atual={self.estoque_atual}>"
        )

    def to_dict(self):
        return {
            'id_produto': self.id_produto,
            'nome': self.nome,
            'descricao': self.descricao,
            'sku': self.sku,
            'preco_venda': self.preco_venda,
            'preco_custo_medio': self.preco_custo_medio,
            'estoque_atual': self.estoque_atual,
            'nome_imagem': self.nome_imagem,
        }
