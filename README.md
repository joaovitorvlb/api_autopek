# 🚗 API AutoPek

Sistema completo de gestão para loja de peças automotivas desenvolvido com Flask.

## 📋 Descrição

API RESTful completa com **56 endpoints** para gerenciamento de:
- � **Autenticação** (4 rotas) - Login, logout, verificação JWT
- 🛍️ **Produtos** (7 rotas) - Catálogo com upload de imagens (públicas + protegidas)
- 👥 **Clientes** (8 rotas) - Cadastro público e gestão
- 👔 **Funcionários** (11 rotas) - Gestão de equipe com RBAC
- 🏪 **Fornecedores** (7 rotas) - Cadastro de suppliers com validação CNPJ
- 📦 **Pedidos de Compra** (8 rotas) - Entrada de estoque automática
- 🛒 **Pedidos de Venda** (11 rotas) - Saída de estoque e cálculo de lucro

### ✨ Funcionalidades Principais

- ✅ **Controle automático de estoque** (entrada/saída)
- ✅ **Cálculo de custo médio ponderado** em compras
- ✅ **Validação de CNPJ** (algoritmo brasileiro)
- ✅ **Relatórios de vendas e compras** por período
- ✅ **Cálculo de lucro** bruto e margem percentual
- ✅ **Produtos mais vendidos** (ranking)
- ✅ **Upload de imagens** com 3 resoluções automáticas
- ✅ **Autenticação JWT** com blacklist

## 🚀 Tecnologias

- **Backend**: Flask 2.2.5
- **Banco de Dados**: SQLite (desenvolvimento) / MySQL (produção)
- **Autenticação**: JWT (flask_jwt_extended) - 24h de validade
- **Upload**: PIL/Pillow para processamento de imagens
- **Segurança**: CORS, bcrypt para senhas

## 📁 Estrutura do Projeto

```
api_autopek/
├── app.py                      # Aplicação Flask principal (56 rotas registradas)
├── requirements.txt            # Dependências Python
├── dao_sqlite/                 # Data Access Objects (SQLite)
│   ├── cliente_dao.py
│   ├── funcionario_dao.py
│   ├── produto_dao.py
│   ├── fornecedor_dao.py      # ✨ Novo
│   ├── pedido_compra_dao.py   # ✨ Novo - Controle de entrada
│   ├── pedido_venda_dao.py    # ✨ Novo - Controle de saída
│   ├── item_pedido_compra_dao.py
│   └── item_pedido_venda_dao.py
├── dao_mysql/                  # Data Access Objects (MySQL)
├── models/                     # Modelos de dados (10 tabelas)
├── routes/                     # Blueprints das rotas (7 módulos)
│   ├── auth_routes.py
│   ├── produto_routes.py
│   ├── cliente_routes.py
│   ├── funcionario_routes.py
│   ├── fornecedor_routes.py        # ✨ Novo
│   ├── pedido_compra_routes.py     # ✨ Novo
│   └── pedido_venda_routes.py      # ✨ Novo
├── service/                    # Lógica de negócio (8 services)
│   ├── auth_service.py
│   ├── produto_service.py
│   ├── fornecedor_service.py       # ✨ Novo - Validação CNPJ
│   ├── pedido_compra_service.py    # ✨ Novo - Custo médio
│   └── pedido_venda_service.py     # ✨ Novo - Lucro
├── static/images/produtos/     # Imagens (thumbnail, medium, large)
├── tests/                      # Scripts de teste
└── docs/                       # Documentação completa
    ├── API_GUIA_FRONTEND.md    # 📖 GUIA COMPLETO PARA FRONTEND
    ├── DAOS_IMPLEMENTADOS.md
    ├── modelagem_geral.md
    ├── banco_sqlite.sql
    └── banco_mysql.sql
```

## ⚙️ Instalação

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd api_autopek
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure o banco de dados
```bash
# Para SQLite (desenvolvimento)
python scripts/limpar_producao_sqlite.py

# Para MySQL (produção)
python scripts/limpar_producao_mysql.py
```

## 🎯 Executar a Aplicação

```bash
python app.py
```

A API estará disponível em: `http://localhost:5000`

## 🔑 Credenciais Padrão

Após executar o script de inicialização, use estas credenciais para o primeiro acesso:

- **Email**: `admin@autopeck.com`
- **Senha**: `admin123`

⚠️ **IMPORTANTE**: Altere a senha após o primeiro login!

## 📚 Documentação Completa

### 📖 Para Desenvolvedores Frontend

**[API_GUIA_FRONTEND.md](docs/API_GUIA_FRONTEND.md)** - Documentação completa e organizada por ordem de uso

Este guia contém:
- ✅ **56 endpoints** com exemplos curl
- ✅ Organização por **fluxo de uso típico** da aplicação
- ✅ Estruturas JSON de request/response
- ✅ Indicação de rotas **públicas** vs **protegidas**
- ✅ Níveis de acesso requeridos
- ✅ Fluxo completo do login à primeira venda
- ✅ Documentação de validações e regras de negócio

**Ordem recomendada:**
1. 🔐 Autenticação → Login
2. 🛍️ Produtos → Catálogo (muitas públicas)
3. 👥 Clientes → Cadastro
4. 👔 Funcionários → Gestão de equipe
5. 🏪 Fornecedores → Suppliers
6. 📦 Pedidos de Compra → Entrada de estoque
7. 🛒 Pedidos de Venda → Saída e faturamento

### 📋 Outras Documentações

- **[modelagem_geral.md](docs/modelagem_geral.md)** - Modelagem completa do banco de dados
- **[DAOS_IMPLEMENTADOS.md](docs/DAOS_IMPLEMENTADOS.md)** - Documentação dos DAOs com exemplos
- **[banco_sqlite.sql](docs/banco_sqlite.sql)** - Script SQL para SQLite
- **[banco_mysql.sql](docs/banco_mysql.sql)** - Script SQL para MySQL

---

## 🎯 Quick Start

### Instalação

```bash
# 1. Clonar repositório
git clone https://github.com/joaovitorvlb/api_autopek.git
cd api_autopek

# 2. Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Inicializar banco
python scripts/limpar_producao_sqlite.py

# 5. Executar servidor
python app.py
```

API disponível em: `http://localhost:5000`

### Primeiro Acesso

```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@autopeck.com",
    "senha": "admin123"
  }'
```

⚠️ **Altere a senha após o primeiro login!**

---

## 📊 Resumo de Endpoints

| Módulo | GET | POST | PUT | DELETE | Total |
|--------|-----|------|-----|--------|-------|
| **Autenticação** | 2 | 2 | 0 | 0 | **4** |
| **Produtos** | 3 | 2 | 1 | 1 | **7** |
| **Clientes** | 2 | 1 | 5 | 0 | **8** |
| **Funcionários** | 3 | 1 | 7 | 0 | **11** |
| **Fornecedores** | 3 | 1 | 2 | 1 | **7** |
| **Pedidos Compra** | 3 | 4 | 1 | 0 | **8** |
| **Pedidos Venda** | 5 | 4 | 2 | 0 | **11** |
| **TOTAL** | **21** | **15** | **18** | **2** | **56** |

---

## 🔄 Fluxo de Negócio

## 🔐 Níveis de Acesso

O sistema implementa RBAC (Role-Based Access Control) com três níveis:

1. **Cliente** (`cliente`)
   - Registrar-se publicamente
   - Visualizar produtos
   - Visualizar/editar próprios dados
   - Realizar compras

2. **Funcionário** (`funcionario`)
   - Acesso de clientes +
   - Gerenciar produtos
   - Visualizar clientes
   - Processar vendas

3. **Administrador** (`admin`)
   - Acesso total
   - Gerenciar funcionários
   - Acesso a todos os relatórios
   - Configurações do sistema

---

## � Fluxo de Negócio

### 📦 Entrada de Estoque (Pedido de Compra)

```
1. Cadastrar Fornecedor
   └─> POST /api/fornecedores (validação CNPJ)

2. Criar Pedido de Compra
   └─> POST /api/pedidos-compra (status: Pendente)
       ├─> Adicionar itens
       │   └─> POST /api/pedidos-compra/{id}/itens
       └─> Atualizar status
           └─> PUT /api/pedidos-compra/{id}/status (Aprovado → Enviado)

3. Receber Pedido ⭐ ENTRADA NO ESTOQUE
   └─> POST /api/pedidos-compra/{id}/receber
       ├─> Status → Recebido
       ├─> Estoque ↑ (incrementa quantidade)
       └─> Custo médio ↑ (recalcula com nova compra)
```

### 🛒 Saída de Estoque (Pedido de Venda)

```
1. Cliente se Cadastra
   └─> POST /api/clientes/register (público)

2. Criar Pedido de Venda
   └─> POST /api/pedidos-venda (status: Pendente)
       ├─> Validação de estoque ✓
       └─> Adicionar itens
           └─> POST /api/pedidos-venda/{id}/itens

3. Confirmar Pedido ⭐ SAÍDA DO ESTOQUE
   └─> POST /api/pedidos-venda/{id}/confirmar
       ├─> Valida estoque disponível ✓
       ├─> Status → Confirmado
       └─> Estoque ↓ (decrementa quantidade)

4. Ver Lucro 💰
   └─> GET /api/pedidos-venda/{id}/lucro
       ├─> Valor de venda
       ├─> Custo total
       ├─> Lucro bruto
       └─> Margem percentual
```

### 🔄 Cancelamento

```
Cancelar Compra (antes de receber)
└─> POST /api/pedidos-compra/{id}/cancelar
    └─> Status → Cancelado (sem impacto no estoque)

Cancelar Venda
└─> POST /api/pedidos-venda/{id}/cancelar?devolver_estoque=true
    ├─> Status → Cancelado
    └─> Estoque ↑ (devolve se pedido estava confirmado)
```

---

## 💰 Cálculos Automáticos

### Custo Médio Ponderado (Entrada)

Ao **receber pedido de compra**:

```python
novo_custo = (estoque_antigo × custo_antigo) + (qtd_recebida × custo_novo)
             ─────────────────────────────────────────────────────────────
                        estoque_antigo + qtd_recebida
```

**Exemplo:**
```
Estoque atual: 10 unidades × R$ 20,00 = R$ 200,00
Nova compra:    5 unidades × R$ 25,00 = R$ 125,00
───────────────────────────────────────────────────
Novo custo médio: (200 + 125) / (10 + 5) = R$ 21,67
```

### Lucro Bruto e Margem (Saída)

Ao **vender produtos**:

```python
lucro_bruto = valor_venda - custo_total
margem (%) = (lucro_bruto / valor_venda) × 100
```

**Exemplo:**
```
Venda de 5 unidades × R$ 45,90 = R$ 229,50
Custo de 5 unidades × R$ 21,67 = R$ 108,35
──────────────────────────────────────────
Lucro bruto: R$ 121,15
Margem: 52,8%
```

---

## ✅ Validações Implementadas

| Validação | Descrição | Endpoint Afetado |
|-----------|-----------|------------------|
| **CNPJ** | Algoritmo brasileiro (14 dígitos + 2 verificadores) | `POST /api/fornecedores` |
| **CPF** | 11 dígitos (formato: 12345678900) | `POST /api/clientes/register` |
| **Estoque** | Valida disponibilidade antes de vender | `POST /api/pedidos-venda/{id}/confirmar` |
| **Preços** | Devem ser > 0 | Todos os endpoints de produtos/pedidos |
| **Status** | Pedidos finalizados não podem ser modificados | PUT status, cancelar, confirmar |
| **Fornecedor** | Não deleta se tiver pedidos vinculados | `DELETE /api/fornecedores/{id}` |
| **Duplicatas** | Produto não pode estar 2x no mesmo pedido | Adicionar itens |

---

## 🗄️ Modelagem do Banco de Dados

### Herança de Usuários
```
nivel_acesso
    ↓
 Usuario (abstrato)
    ├─> Cliente
    └─> Funcionario
```

### Fluxo de Compras (Entrada)
```
Fornecedor → Pedido_Compra → Item_Pedido_Compra → Produto (↑ estoque)
```

### Fluxo de Vendas (Saída)
```
Cliente → Pedido_Venda → Item_Pedido_Venda → Produto (↓ estoque)
```

### Tabelas (10 no total)

| Tabela | Função | Chave Estrangeira |
|--------|--------|-------------------|
| **nivel_acesso** | Níveis: cliente, funcionario, admin | - |
| **Usuario** | Tabela pai (herança) | id_nivel_acesso |
| **Cliente** | Herda de Usuario | id_usuario |
| **Funcionario** | Herda de Usuario | id_usuario |
| **Produto** | Catálogo de produtos | - |
| **Fornecedor** | Cadastro de suppliers | - |
| **Pedido_Compra** | Pedidos de entrada | id_fornecedor, id_funcionario |
| **Item_Pedido_Compra** | Itens do pedido de compra | id_pedido_compra, id_produto |
| **Pedido_Venda** | Pedidos de saída | id_cliente, id_funcionario |
| **Item_Pedido_Venda** | Itens do pedido de venda | id_pedido_venda, id_produto |

---

## 🛠️ Scripts Úteis

### Limpar banco de dados
```bash
# SQLite
python scripts/limpar_producao_sqlite.py

# MySQL
python scripts/limpar_producao_mysql.py
```

## 📝 Exemplo de Uso

### 1. Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@autopeck.com",
    "senha": "admin123"
  }'
```

### 2. Criar Produto (com token)
```bash
curl -X POST http://localhost:5000/api/produtos \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -d '{
    "nome": "Filtro de Óleo",
    "preco": 45.90,
    "estoque": 100,
    "descricao": "Filtro de óleo compatível com diversos modelos"
  }'
```

## 📄 Documentação Completa

Para documentação detalhada sobre:
- Modelagem do banco de dados
- Fluxos de negócio
- Exemplos SQL
- Regras de negócio

Consulte: `docs/modelagem_geral.md`

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📞 Suporte

Para dúvidas ou problemas, abra uma issue no repositório.

## 📜 Licença

Este projeto é de uso acadêmico.

---

**Desenvolvido para o curso de Banco de Dados - Semestre 8**
