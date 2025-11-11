# 📂 Scripts - API AutoPek

Esta pasta contém scripts utilitários para gerenciar a API AutoPek.

## 📋 Scripts Disponíveis

### 🧹 Scripts de Limpeza/Inicialização

#### `limpar_producao_sqlite.py`
Reseta o banco de dados SQLite para o estado inicial.

**O que faz:**
- Remove todas as imagens de produtos
- Limpa todos os dados das tabelas
- Recria a estrutura do banco
- Insere dados padrão (níveis de acesso)
- Cria usuário administrador padrão

**Uso:**
```bash
python scripts/limpar_producao_sqlite.py
```

**Credenciais criadas:**
- Email: `admin@autopeck.com`
- Senha: `admin123`

---

#### `limpar_producao_mysql.py`
Mesma funcionalidade do script SQLite, mas para banco MySQL/PythonAnywhere.

**Uso:**
```bash
python scripts/limpar_producao_mysql.py
```

---

### 📦 Scripts de População de Dados

#### `popular_produtos_com_imagens.py` ⭐
Popula o banco com produtos reais e suas imagens.

**O que faz:**
- 🚗 Cria 4 produtos automotivos reais
- 📸 Faz upload das imagens (multipart/form-data)
- 🖼️ Processa imagens em 3 resoluções (thumbnail, medium, large)
- 💰 Define preços e estoques realistas
- 📝 Descrições técnicas detalhadas

**Produtos incluídos:**
1. **Carburador Brosol 3E Opala 6cc** - R$ 1.250,00 (8 unidades)
2. **Injeção Fueltech FT450 + Chicote** - R$ 4.890,00 (5 unidades)
3. **Coletor de Admissão Opala 6cc Weber** - R$ 2.150,00 (12 unidades)
4. **Turbina Garrett .70 ZR6064** - R$ 6.200,00 (3 unidades)

**Uso:**
```bash
python scripts/popular_produtos_com_imagens.py
```

**Saída:**
```
✅ Produto criado - ID: 1 | SKU: CARB-BROSOL-3E-OPALA6
   Nome: Carburador Brosol 3E Opala 6cc...
   Preço: R$ 1250.00
   Estoque: 8 unidades
   Imagem processada: Produto_1_abc123
   📸 Thumbnail: http://localhost:5000/static/images/produtos/Produto_1_abc123_thumbnail.png
   📸 Medium: http://localhost:5000/static/images/produtos/Produto_1_abc123_medium.png
   📸 Large: http://localhost:5000/static/images/produtos/Produto_1_abc123_large.png

📊 Estatísticas:
   Produtos tentados: 4
   ✅ Criados com sucesso: 4
   Estoque total: 28 peças
   Valor em estoque: R$ 78,850.00
```

---

## 🧪 Para Testes

Os testes foram movidos para o diretório **`tests/`** com estrutura modular e profissional:

- **`tests/test_auth.py`** - Testes de autenticação (login, verificação, logout)
- **`tests/test_produtos.py`** - Testes completos de produtos (CRUD + upload de imagens)
- **`tests/run_all_tests.py`** - Executor de todos os testes

**Executar testes:**
```bash
# Testes de autenticação
python tests/test_auth.py

# Testes de produtos
python tests/test_produtos.py

# Todos os testes
python tests/run_all_tests.py
```

---

## 📋 Fluxo de Uso Recomendado

### 1. Inicialização do Sistema
```bash
# Resetar banco de dados
python scripts/limpar_producao_sqlite.py

# Iniciar API (em outro terminal)
python app.py

# Popular com dados de exemplo
python scripts/popular_produtos_com_imagens.py
```

### 2. Testes Durante o Desenvolvimento
```bash
# Testes de autenticação
python tests/test_auth.py

# Testes de produtos
python tests/test_produtos.py

# Todos os testes
python tests/run_all_tests.py
```

---

## 🔧 Requisitos

### Para scripts Python:
```bash
pip install -r requirements.txt
```

### Bibliotecas necessárias:
- `requests` - Para fazer requisições HTTP
- `Pillow` - Para processamento de imagens

---

## ⚠️ Importante

Antes de executar qualquer script, certifique-se de que a API está rodando:

```bash
python app.py
```

A API deve estar disponível em: `http://localhost:5000`

---

## 📖 Exemplos de Uso

### Exemplo 1: Setup Inicial Completo
```bash
# Terminal 1: Resetar banco
python scripts/limpar_producao_sqlite.py

# Terminal 2: Iniciar API
python app.py

# Terminal 1: Popular dados e testar
python scripts/popular_produtos_com_imagens.py
python tests/run_all_tests.py
```

### Exemplo 2: Apenas Popular Dados
```bash
# API deve estar rodando
python scripts/popular_produtos_com_imagens.py
```

---

## 🎯 Estrutura de Arquivos

```
scripts/
├── README.md                          # Este arquivo
├── limpar_producao_sqlite.py         # Limpar banco SQLite
├── limpar_producao_mysql.py          # Limpar banco MySQL
└── popular_produtos_com_imagens.py   # Popular com dados reais

tests/
├── README.md                          # Documentação dos testes
├── config.py                          # Configurações
├── utils.py                           # Funções utilitárias
├── test_auth.py                       # Testes de autenticação
├── test_produtos.py                   # Testes de produtos
└── run_all_tests.py                   # Executor de todos os testes
```

---

## 🐛 Troubleshooting

### Erro: "Não foi possível conectar à API"
**Solução:** Certifique-se de que `app.py` está rodando

### Erro: "Login falhou"
**Solução:** Execute o script de limpeza para criar o usuário admin
```bash
python scripts/limpar_producao_sqlite.py
```

### Erro: "Imagem não encontrada"
**Solução:** Certifique-se de que as imagens estão na pasta `docs/`

---

## 💡 Dicas

### Limpar apenas produtos mantendo usuários
Use a interface de administração da API ou exclua manualmente via SQL.

### Adicionar novos produtos
Edite `popular_produtos_com_imagens.py` e adicione novos produtos na lista.

### Desenvolvimento com dados limpos
```bash
# Resetar e popular rapidamente
python scripts/limpar_producao_sqlite.py && \
python scripts/popular_produtos_com_imagens.py && \
python tests/run_all_tests.py
```

---

## 📞 Suporte

Para mais informações, consulte:
- `tests/README.md` - Documentação completa dos testes
- `docs/modelagem_geral.md` - Documentação técnica do sistema
- README.md na raiz do projeto
