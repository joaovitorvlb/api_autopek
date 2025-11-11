# DAOs Implementados - API AutoPek

Este documento lista todos os DAOs (Data Access Objects) implementados para o sistema.

## 📦 DAOs Disponíveis

### 1. **FornecedorDAO** (`fornecedor_dao.py`)
Gerencia operações com fornecedores.

**Versões:** SQLite e MySQL

**Métodos principais:**
- `criar(razao_social, nome_fantasia, cnpj, email, telefone, endereco)` - Cria novo fornecedor
- `buscar_por_id(id_fornecedor)` - Busca fornecedor por ID
- `buscar_por_cnpj(cnpj)` - Busca fornecedor por CNPJ
- `listar_todos(apenas_ativos)` - Lista todos os fornecedores (com filtro de ativos)
- `buscar_por_nome(nome, apenas_ativos)` - Busca por razão social ou nome fantasia (parcial)
- `atualizar(id_fornecedor, razao_social, nome_fantasia, cnpj, email, telefone, endereco)` - Atualiza dados do fornecedor
- `desativar(id_fornecedor)` - Desativa fornecedor (soft delete)
- `ativar(id_fornecedor)` - Ativa fornecedor
- `deletar(id_fornecedor)` - Deleta permanentemente
- `contar_pedidos_compra(id_fornecedor)` - Conta pedidos do fornecedor
- `obter_estatisticas(id_fornecedor)` - Estatísticas de compras

**Campos da tabela:**
- `id_fornecedor` - ID único
- `razao_social` - Nome jurídico (obrigatório)
- `nome_fantasia` - Nome comercial (obrigatório)
- `cnpj` - CNPJ único (obrigatório)
- `email` - Email de contato (opcional)
- `telefone` - Telefone de contato (opcional)
- `endereco` - Endereço completo (opcional)
- `ativo` - Status (1=ativo, 0=inativo)
- `data_criacao` - Data de cadastro (automático)

---

### 2. **PedidoCompraDAO** (`pedido_compra_dao.py`)
Gerencia pedidos de compra (entrada de estoque).

**Métodos principais:**
- `criar(id_fornecedor, id_funcionario, status)` - Cria novo pedido de compra
- `buscar_por_id(id_pedido_compra)` - Busca pedido por ID (com JOINs)
- `listar_todos(status)` - Lista todos os pedidos (opcional filtro por status)
- `listar_por_fornecedor(id_fornecedor)` - Lista pedidos de um fornecedor
- `listar_por_funcionario(id_funcionario)` - Lista pedidos de um funcionário
- `atualizar_status(id_pedido_compra, novo_status)` - Atualiza status do pedido
- `atualizar_total(id_pedido_compra)` - Recalcula total baseado nos itens
- `receber_pedido(id_pedido_compra)` - **Marca como recebido e atualiza estoque**
- `cancelar_pedido(id_pedido_compra)` - Cancela pedido (se não foi recebido)
- `deletar(id_pedido_compra)` - Deleta permanentemente
- `obter_relatorio_compras(data_inicio, data_fim)` - Relatório de compras por período

**Status do pedido:** Pendente → Aprovado → Enviado → Recebido | Cancelado

---

### 3. **ItemPedidoCompraDAO** (`item_pedido_compra_dao.py`)
Gerencia itens de pedidos de compra.

**Métodos principais:**
- `criar(id_pedido_compra, id_produto, quantidade, preco_custo_unitario)` - Adiciona item ao pedido
- `buscar_por_id(id_item_pedido_compra)` - Busca item por ID
- `listar_por_pedido(id_pedido_compra)` - Lista itens de um pedido
- `listar_por_produto(id_produto)` - Lista pedidos que contêm o produto
- `atualizar(id_item_pedido_compra, quantidade, preco_custo_unitario)` - Atualiza item
- `deletar(id_item_pedido_compra)` - Deleta item
- `deletar_por_pedido(id_pedido_compra)` - Deleta todos os itens do pedido
- `calcular_total_pedido(id_pedido_compra)` - Calcula total do pedido
- `contar_itens_pedido(id_pedido_compra)` - Conta itens do pedido
- `verificar_produto_em_pedido(id_pedido_compra, id_produto)` - Verifica se produto já está no pedido
- `obter_historico_compras_produto(id_produto, limite)` - Histórico de compras de um produto

---

### 4. **PedidoVendaDAO** (`pedido_venda_dao.py`)
Gerencia pedidos de venda (saída de estoque).

**Métodos principais:**
- `criar(id_cliente, id_funcionario, status)` - Cria novo pedido de venda
- `buscar_por_id(id_pedido_venda)` - Busca pedido por ID (com JOINs)
- `listar_todos(status)` - Lista todos os pedidos (opcional filtro por status)
- `listar_por_cliente(id_cliente)` - Lista pedidos de um cliente
- `listar_por_funcionario(id_funcionario)` - Lista vendas de um funcionário
- `atualizar_status(id_pedido_venda, novo_status)` - Atualiza status do pedido
- `atualizar_total(id_pedido_venda)` - Recalcula total baseado nos itens
- `confirmar_pedido(id_pedido_venda)` - **Confirma pedido e dá baixa no estoque**
- `cancelar_pedido(id_pedido_venda, devolver_estoque)` - Cancela pedido (opcional devolver estoque)
- `deletar(id_pedido_venda)` - Deleta permanentemente
- `calcular_lucro_pedido(id_pedido_venda)` - Calcula lucro do pedido
- `obter_relatorio_vendas(data_inicio, data_fim)` - Relatório de vendas por período
- `obter_performance_vendedor(id_funcionario)` - Estatísticas de vendas do funcionário

**Status do pedido:** Pendente → Confirmado → Separado → Enviado → Entregue | Cancelado

---

### 5. **ItemPedidoVendaDAO** (`item_pedido_venda_dao.py`)
Gerencia itens de pedidos de venda.

**Métodos principais:**
- `criar(id_pedido_venda, id_produto, quantidade, preco_unitario_venda)` - Adiciona item ao pedido
- `buscar_por_id(id_item_pedido_venda)` - Busca item por ID
- `listar_por_pedido(id_pedido_venda)` - Lista itens de um pedido (com cálculo de lucro)
- `listar_por_produto(id_produto)` - Lista vendas que contêm o produto
- `atualizar(id_item_pedido_venda, quantidade, preco_unitario_venda)` - Atualiza item
- `deletar(id_item_pedido_venda)` - Deleta item
- `deletar_por_pedido(id_pedido_venda)` - Deleta todos os itens do pedido
- `calcular_total_pedido(id_pedido_venda)` - Calcula total do pedido
- `contar_itens_pedido(id_pedido_venda)` - Conta itens do pedido
- `verificar_produto_em_pedido(id_pedido_venda, id_produto)` - Verifica se produto já está no pedido
- `verificar_disponibilidade_estoque(id_pedido_venda)` - Verifica se há estoque suficiente
- `obter_produtos_mais_vendidos(limite, data_inicio, data_fim)` - Top produtos mais vendidos
- `obter_historico_vendas_produto(id_produto, limite)` - Histórico de vendas de um produto

---

## 📊 Fluxos de Negócio Implementados

### 🔵 Fluxo de Compra (Entrada de Estoque)

```python
from dao_sqlite import PedidoCompraDAO, ItemPedidoCompraDAO

# 1. Criar pedido de compra
pedido_dao = PedidoCompraDAO()
id_pedido = pedido_dao.criar(
    id_fornecedor=1,
    id_funcionario=5,
    status='Pendente'
)

# 2. Adicionar itens ao pedido
item_dao = ItemPedidoCompraDAO()
item_dao.criar(id_pedido, id_produto=10, quantidade=50, preco_custo_unitario=25.00)
item_dao.criar(id_pedido, id_produto=15, quantidade=30, preco_custo_unitario=45.00)

# 3. Atualizar total do pedido
pedido_dao.atualizar_total(id_pedido)

# 4. Receber mercadoria (atualiza estoque automaticamente)
pedido_dao.receber_pedido(id_pedido)  # Dá entrada no estoque!
```

---

### 🔴 Fluxo de Venda (Saída de Estoque)

```python
from dao_sqlite import PedidoVendaDAO, ItemPedidoVendaDAO

# 1. Criar pedido de venda
pedido_dao = PedidoVendaDAO()
id_pedido = pedido_dao.criar(
    id_cliente=3,
    id_funcionario=5,  # Ou None para venda online
    status='Pendente'
)

# 2. Adicionar itens ao carrinho
item_dao = ItemPedidoVendaDAO()
item_dao.criar(id_pedido, id_produto=10, quantidade=2, preco_unitario_venda=50.00)
item_dao.criar(id_pedido, id_produto=15, quantidade=4, preco_unitario_venda=80.00)

# 3. Atualizar total do pedido
pedido_dao.atualizar_total(id_pedido)

# 4. Verificar estoque disponível
produtos_sem_estoque = item_dao.verificar_disponibilidade_estoque(id_pedido)
if not produtos_sem_estoque:
    # 5. Confirmar venda (dá baixa no estoque automaticamente)
    pedido_dao.confirmar_pedido(id_pedido)
```

---

## 🎯 Características Importantes

### ✅ Controle de Estoque Automático
- **Compra recebida:** Incrementa estoque e atualiza custo médio ponderado
- **Venda confirmada:** Decrementa estoque
- **Venda cancelada:** Opção de devolver ao estoque

### ✅ Snapshot de Preços
- Preços são salvos no momento da compra/venda
- Alterações futuras de preço não afetam pedidos antigos

### ✅ Validações
- Verificação de estoque antes de confirmar venda
- Não permite cancelar pedido de compra já recebido
- Previne vendas sem estoque suficiente

### ✅ Relatórios e Estatísticas
- Produtos mais vendidos
- Performance de vendedores
- Histórico de compras por fornecedor
- Cálculo de lucro por pedido

### ✅ Relacionamentos com JOIN
- Busca de pedidos retorna dados de fornecedor/cliente/funcionário
- Busca de itens retorna dados do produto

---

## 📝 Exemplo de Uso Completo

```python
from dao_sqlite import (
    FornecedorDAO, PedidoCompraDAO, ItemPedidoCompraDAO,
    PedidoVendaDAO, ItemPedidoVendaDAO
)

# === CADASTRAR FORNECEDOR ===
fornecedor_dao = FornecedorDAO()
id_fornecedor = fornecedor_dao.criar(
    razao_social="Auto Peças Brasil LTDA",
    nome_fantasia="Auto Peças Brasil",
    cnpj="12.345.678/0001-90",
    email="compras@autopecas.com",
    telefone="11999999999",
    endereco="Rua das Peças, 123 - São Paulo, SP"
)

# === FAZER COMPRA ===
pedido_compra_dao = PedidoCompraDAO()
item_compra_dao = ItemPedidoCompraDAO()

# Criar pedido
id_compra = pedido_compra_dao.criar(id_fornecedor, id_funcionario=1)

# Adicionar produtos
item_compra_dao.criar(id_compra, id_produto=1, quantidade=100, preco_custo_unitario=20.00)

# Atualizar total e receber
pedido_compra_dao.atualizar_total(id_compra)
pedido_compra_dao.receber_pedido(id_compra)  # Estoque += 100

# === FAZER VENDA ===
pedido_venda_dao = PedidoVendaDAO()
item_venda_dao = ItemPedidoVendaDAO()

# Criar pedido
id_venda = pedido_venda_dao.criar(id_cliente=1, id_funcionario=1)

# Adicionar ao carrinho
item_venda_dao.criar(id_venda, id_produto=1, quantidade=2, preco_unitario_venda=45.00)

# Verificar estoque e confirmar
pedido_venda_dao.atualizar_total(id_venda)
if not item_venda_dao.verificar_disponibilidade_estoque(id_venda):
    pedido_venda_dao.confirmar_pedido(id_venda)  # Estoque -= 2

# === RELATÓRIOS ===
# Produtos mais vendidos
top_produtos = item_venda_dao.obter_produtos_mais_vendidos(limite=10)

# Performance de vendedor
stats = pedido_venda_dao.obter_performance_vendedor(id_funcionario=1)

# Relatório de vendas
relatorio = pedido_venda_dao.obter_relatorio_vendas(
    data_inicio='2024-01-01',
    data_fim='2024-12-31'
)
```

---

## 🔧 Próximos Passos

Para completar o sistema, você pode implementar:

1. **Services** para lógica de negócio dos novos módulos
2. **Routes** para expor endpoints REST
3. **Validações** de negócio adicionais
4. **Testes unitários** para os DAOs
5. **Triggers** no banco para automações adicionais

---

## 📚 Documentação Relacionada

- [Modelagem Geral](modelagem_geral.md) - Diagrama ER e fluxos de negócio
- [Guia Frontend](API_GUIA_FRONTEND.md) - Documentação da API REST
- [Script SQLite](banco_sqlite.sql) - Estrutura completa do banco
