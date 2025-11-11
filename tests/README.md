# 🧪 Testes da API AutoPek

Estrutura de testes organizada por módulos para facilitar manutenção, execução seletiva e escalabilidade.

## 📁 Estrutura

```
tests/
├── __init__.py              # Pacote de testes
├── config.py                # Configurações compartilhadas (URLs, credenciais)
├── utils.py                 # Utilitários (print, validações, contador de resultados)
├── run_all_tests.py         # ⭐ Executor principal - roda TODOS os testes
├── test_auth.py             # 🔐 Testes de autenticação
├── test_produtos.py         # 📦 Testes de produtos
├── test_clientes.py         # 👥 Testes de clientes (TODO)
└── test_funcionarios.py     # 👔 Testes de funcionários (TODO)
```

## 🚀 Como Executar

### Todos os testes (recomendado)
```bash
python tests/run_all_tests.py
```

### Testes específicos por módulo
```bash
# Apenas autenticação
python tests/test_auth.py

# Apenas produtos
python tests/test_produtos.py
```

### Pré-requisitos
1. **API rodando**: `python app.py`
2. **Banco de dados inicializado** com usuário admin

## 📊 Módulos de Teste

### 🔐 Autenticação (`test_auth.py`)
Testa todas as funcionalidades de autenticação JWT:

- ✅ Login com credenciais válidas
- ✅ Login com senha incorreta (deve falhar)
- ✅ Login sem email (deve falhar)
- ✅ Verificação de token válido
- ✅ Verificação de token inválido (deve falhar)
- ✅ Requisição sem token (deve falhar)
- ✅ Obtenção de dados do usuário autenticado
- ✅ Logout (invalidação de token)
- ✅ Verificação de token após logout (deve falhar)

**Total**: 9 testes

### 📦 Produtos (`test_produtos.py`)
Testa CRUD completo de produtos:

- ✅ Listar todos os produtos (rota pública)
- ✅ Criar produto com dados válidos
- ✅ Criar produto sem nome (deve falhar)
- ✅ Buscar produto por ID
- ✅ Buscar produto inexistente (deve retornar 404)
- ✅ Buscar produtos por nome
- ✅ Atualizar produto
- ✅ Deletar produto
- ✅ Verificar se produto foi deletado

**Total**: 9 testes

### 👥 Clientes (`test_clientes.py`) - TODO
- [ ] Registrar cliente
- [ ] Listar clientes (requer auth)
- [ ] Buscar cliente por ID
- [ ] Buscar cliente por CPF
- [ ] Atualizar dados do cliente
- [ ] Alterar senha
- [ ] Desativar/Ativar conta

### 👔 Funcionários (`test_funcionarios.py`) - TODO
- [ ] Criar funcionário (admin only)
- [ ] Listar funcionários
- [ ] Buscar por ID
- [ ] Buscar por cargo
- [ ] Atualizar dados
- [ ] Promover funcionário
- [ ] Dar aumento
- [ ] Alterar nível de acesso
- [ ] Alterar senha

## 🎯 Vantagens dessa Estrutura

### ✅ Organização
- Cada módulo tem seu arquivo
- Fácil localizar e editar testes
- Código reutilizável em `utils.py`

### ✅ Execução Seletiva
```bash
# Só testa o que mudou
python tests/test_produtos.py
```

### ✅ Manutenibilidade
- Um bug no módulo de produtos? Edite só `test_produtos.py`
- Novo endpoint de produtos? Adicione no mesmo arquivo
- Configurações centralizadas em `config.py`

### ✅ Escalabilidade
```python
# Adicionar novo módulo é simples:
# 1. Criar tests/test_novo_modulo.py
# 2. Adicionar import em run_all_tests.py
from tests.test_novo_modulo import run_all_novo_modulo_tests

resultados['novo_modulo'] = run_all_novo_modulo_tests()
```

### ✅ Relatório Claro
```
📊 Resultados por Módulo:
   AUTH: ✅ PASSOU
   PRODUTOS: ✅ PASSOU
   CLIENTES: ❌ FALHOU

📈 Resumo Geral:
   Total de módulos testados: 3
   ✅ Módulos com sucesso: 2
   ❌ Módulos com falhas: 1
```

### ✅ CI/CD Ready
```yaml
# .github/workflows/tests.yml
- name: Run Tests
  run: python tests/run_all_tests.py
```

## 📝 Padrão de Teste

Cada arquivo de teste segue o mesmo padrão:

```python
#!/usr/bin/env python3
"""
Descrição do módulo de teste
"""

import sys
sys.path.append('.')

from tests.config import *
from tests.utils import *


def setup():
    """Preparação antes dos testes (login, etc)"""
    pass


def test_funcionalidade_1():
    """Testa funcionalidade específica"""
    print_separador("1. NOME DO TESTE")
    contador = TestResultCounter()
    
    # Fazer request
    sucesso, response, erro = fazer_request(...)
    
    # Validar resposta
    if valido:
        contador.registrar_sucesso("Teste passou")
    else:
        contador.registrar_falha("Teste falhou", "motivo")
    
    return contador


def run_all_xxx_tests():
    """Executa todos os testes do módulo"""
    # Setup
    # Executar testes
    # Consolidar resultados
    # Retornar sucesso/falha
    pass


if __name__ == '__main__':
    sucesso = run_all_xxx_tests()
    sys.exit(0 if sucesso else 1)
```

## 🔧 Customização

### Mudar URL da API
Edite `tests/config.py`:
```python
API_BASE_URL = "http://localhost:3000"  # Sua porta
```

### Adicionar novos testes
1. Crie função `test_nova_funcionalidade()` no arquivo apropriado
2. Retorne `TestResultCounter`
3. Adicione no `run_all_xxx_tests()` do módulo

### Desabilitar módulo temporariamente
Comente no `run_all_tests.py`:
```python
# resultados['produtos'] = run_all_produto_tests()  # Desabilitado
```

## 📈 Cobertura Atual

- **Autenticação**: ✅ 100% (9/9 testes)
- **Produtos**: ✅ 100% (9/9 testes)
- **Clientes**: ⏳ 0% (0 testes)
- **Funcionários**: ⏳ 0% (0 testes)

**Total**: 18 testes implementados

## 🎓 Próximos Passos

1. **Implementar `test_clientes.py`** - Testar CRUD de clientes
2. **Implementar `test_funcionarios.py`** - Testar gestão de funcionários
3. **Adicionar testes de permissões** - Verificar RBAC (admin/funcionario/cliente)
4. **Testes de upload** - Upload de imagens de produtos
5. **Testes de performance** - Listar 1000+ produtos
6. **Testes de concorrência** - Múltiplas requisições simultâneas

## 💡 Dicas

- Execute `run_all_tests.py` antes de fazer commit
- Se um teste falhar, execute o módulo específico para debug
- Use `print_json()` para visualizar respostas da API
- Adicione `print_info()` para debug durante desenvolvimento
- Contador de testes ajuda a medir evolução da cobertura

---

**Estrutura criada para facilitar desenvolvimento e manutenção! 🚀**
