#!/usr/bin/env python3
"""
Script para limpar dados de teste - SQLite
Uso: python scripts/limpar_producao_sqlite.py

ATENÇÃO: Este script irá:
1. Remover todas as imagens de produtos (exceto README.md)
2. Limpar dados de teste das tabelas
3. Inserir dados padrão iniciais
4. Criar estrutura completa baseada na nova modelagem

Execute apenas após backup!
"""

import os
import sys
import hashlib

# Adicionar o diretório raiz ao path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, BASE_DIR)

def limpar_imagens():
    """Remove todas as imagens de teste do diretório de uploads"""
    print("\n🗑️  Limpando imagens de teste...")
    
    upload_folder = os.path.join(BASE_DIR, 'static', 'images', 'produtos')
    
    if not os.path.exists(upload_folder):
        print(f"⚠️  Diretório não encontrado: {upload_folder}")
        return
    
    removidos = 0
    erros = 0
    
    for filename in os.listdir(upload_folder):
        # Não remover README.md
        if filename == 'README.md':
            continue
        
        filepath = os.path.join(upload_folder, filename)
        
        try:
            if os.path.isfile(filepath):
                os.remove(filepath)
                print(f"  ✅ Removido: {filename}")
                removidos += 1
        except Exception as e:
            print(f"  ❌ Erro ao remover {filename}: {e}")
            erros += 1
    
    print(f"\n📊 Resultado:")
    print(f"  - Arquivos removidos: {removidos}")
    print(f"  - Erros: {erros}")

def resetar_banco_sqlite():
    """Reseta o banco de dados SQLite para estado padrão com nova modelagem"""
    print("\n🗄️  Resetando banco de dados SQLite (Nova Modelagem)...")
    
    try:
        from dao_sqlite.db import init_db, get_cursor
        
        # Inicializar banco
        init_db()
        
        print("  🔗 Conectado ao SQLite")
        
        with get_cursor() as cur:
            # Habilitar Foreign Keys
            cur.execute("PRAGMA foreign_keys = OFF")
            
            # 1. Remover todas as tabelas existentes
            print("  🗑️  Removendo tabelas existentes...")
            cur.execute("DROP TABLE IF EXISTS Item_Pedido_Venda")
            cur.execute("DROP TABLE IF EXISTS Item_Pedido_Compra")
            cur.execute("DROP TABLE IF EXISTS Pedido_Venda")
            cur.execute("DROP TABLE IF EXISTS Pedido_Compra")
            cur.execute("DROP TABLE IF EXISTS Fornecedor")
            cur.execute("DROP TABLE IF EXISTS Produto")
            cur.execute("DROP TABLE IF EXISTS Cliente")
            cur.execute("DROP TABLE IF EXISTS Funcionario")
            cur.execute("DROP TABLE IF EXISTS usuario")
            cur.execute("DROP TABLE IF EXISTS nivel_acesso")
            print("  ✅ Tabelas removidas")
            
            # Habilitar Foreign Keys novamente
            cur.execute("PRAGMA foreign_keys = ON")
            
            # 2. Criar tabelas do zero (Nova Modelagem)
            print("  🔧 Criando estrutura do banco do zero (Nova Modelagem)...")
            
            # Tabela nivel_acesso
            cur.execute("""
                CREATE TABLE nivel_acesso (
                    id_nivel_acesso INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL UNIQUE
                )
            """)
            
            # Tabela usuario (Base para herança)
            cur.execute("""
                CREATE TABLE usuario (
                    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    senha_hash TEXT NOT NULL,
                    telefone TEXT,
                    ativo INTEGER DEFAULT 1,
                    data_criacao TEXT DEFAULT CURRENT_TIMESTAMP,
                    id_nivel_acesso INTEGER NOT NULL,
                    FOREIGN KEY (id_nivel_acesso) REFERENCES nivel_acesso(id_nivel_acesso)
                        ON DELETE RESTRICT
                )
            """)
            cur.execute("CREATE INDEX idx_usuario_email ON usuario(email)")
            cur.execute("CREATE INDEX idx_usuario_ativo ON usuario(ativo)")
            
            # Tabela Cliente (herda de Usuario - 1-para-1)
            cur.execute("""
                CREATE TABLE Cliente (
                    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_usuario INTEGER NOT NULL UNIQUE,
                    cpf TEXT NOT NULL UNIQUE,
                    endereco TEXT,
                    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
                        ON DELETE CASCADE
                )
            """)
            cur.execute("CREATE INDEX idx_cliente_cpf ON Cliente(cpf)")
            
            # Tabela Funcionario (herda de Usuario - 1-para-1)
            cur.execute("""
                CREATE TABLE Funcionario (
                    id_funcionario INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_usuario INTEGER NOT NULL UNIQUE,
                    cargo TEXT,
                    salario REAL,
                    data_contratacao TEXT,
                    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
                        ON DELETE CASCADE
                )
            """)
            cur.execute("CREATE INDEX idx_funcionario_cargo ON Funcionario(cargo)")
            
            # Tabela Produto (com SKU e custo médio)
            cur.execute("""
                CREATE TABLE Produto (
                    id_produto INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    descricao TEXT,
                    sku TEXT NOT NULL UNIQUE,
                    estoque_atual INTEGER DEFAULT 0,
                    preco_venda REAL NOT NULL,
                    preco_custo_medio REAL DEFAULT 0.0,
                    nome_imagem TEXT,
                    url TEXT
                )
            """)
            cur.execute("CREATE INDEX idx_produto_sku ON Produto(sku)")
            cur.execute("CREATE INDEX idx_produto_estoque ON Produto(estoque_atual)")
            cur.execute("CREATE INDEX idx_produto_nome ON Produto(nome)")
            
            # Tabela Fornecedor (estrutura melhorada)
            cur.execute("""
                CREATE TABLE Fornecedor (
                    id_fornecedor INTEGER PRIMARY KEY AUTOINCREMENT,
                    razao_social TEXT NOT NULL,
                    nome_fantasia TEXT NOT NULL,
                    cnpj TEXT NOT NULL UNIQUE,
                    email TEXT,
                    telefone TEXT,
                    endereco TEXT,
                    ativo INTEGER DEFAULT 1,
                    data_criacao TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("CREATE INDEX idx_fornecedor_cnpj ON Fornecedor(cnpj)")
            cur.execute("CREATE INDEX idx_fornecedor_nome_fantasia ON Fornecedor(nome_fantasia)")
            cur.execute("CREATE INDEX idx_fornecedor_razao_social ON Fornecedor(razao_social)")
            cur.execute("CREATE INDEX idx_fornecedor_ativo ON Fornecedor(ativo)")
            
            # Tabela Pedido_Compra (ENTRADA de estoque)
            cur.execute("""
                CREATE TABLE Pedido_Compra (
                    id_pedido_compra INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_fornecedor INTEGER NOT NULL,
                    id_funcionario INTEGER,
                    data_pedido TEXT DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'Pendente',
                    total REAL NOT NULL DEFAULT 0.0,
                    FOREIGN KEY (id_fornecedor) REFERENCES Fornecedor(id_fornecedor)
                        ON DELETE RESTRICT,
                    FOREIGN KEY (id_funcionario) REFERENCES Funcionario(id_funcionario)
                        ON DELETE SET NULL
                )
            """)
            cur.execute("CREATE INDEX idx_pedido_compra_fornecedor ON Pedido_Compra(id_fornecedor)")
            cur.execute("CREATE INDEX idx_pedido_compra_funcionario ON Pedido_Compra(id_funcionario)")
            cur.execute("CREATE INDEX idx_pedido_compra_data ON Pedido_Compra(data_pedido)")
            cur.execute("CREATE INDEX idx_pedido_compra_status ON Pedido_Compra(status)")
            
            # Tabela Item_Pedido_Compra
            cur.execute("""
                CREATE TABLE Item_Pedido_Compra (
                    id_item_compra INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_pedido_compra INTEGER NOT NULL,
                    id_produto INTEGER NOT NULL,
                    quantidade INTEGER NOT NULL DEFAULT 1,
                    preco_custo_unitario REAL NOT NULL,
                    FOREIGN KEY (id_pedido_compra) REFERENCES Pedido_Compra(id_pedido_compra)
                        ON DELETE CASCADE,
                    FOREIGN KEY (id_produto) REFERENCES Produto(id_produto)
                        ON DELETE RESTRICT
                )
            """)
            cur.execute("CREATE INDEX idx_item_compra_pedido ON Item_Pedido_Compra(id_pedido_compra)")
            cur.execute("CREATE INDEX idx_item_compra_produto ON Item_Pedido_Compra(id_produto)")
            
            # Tabela Pedido_Venda (SAÍDA de estoque)
            cur.execute("""
                CREATE TABLE Pedido_Venda (
                    id_pedido_venda INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_cliente INTEGER NOT NULL,
                    id_funcionario INTEGER,
                    data_pedido TEXT DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'Pendente',
                    total REAL NOT NULL DEFAULT 0.0,
                    FOREIGN KEY (id_cliente) REFERENCES Cliente(id_cliente)
                        ON DELETE RESTRICT,
                    FOREIGN KEY (id_funcionario) REFERENCES Funcionario(id_funcionario)
                        ON DELETE SET NULL
                )
            """)
            cur.execute("CREATE INDEX idx_pedido_venda_cliente ON Pedido_Venda(id_cliente)")
            cur.execute("CREATE INDEX idx_pedido_venda_funcionario ON Pedido_Venda(id_funcionario)")
            cur.execute("CREATE INDEX idx_pedido_venda_data ON Pedido_Venda(data_pedido)")
            cur.execute("CREATE INDEX idx_pedido_venda_status ON Pedido_Venda(status)")
            
            # Tabela Item_Pedido_Venda
            cur.execute("""
                CREATE TABLE Item_Pedido_Venda (
                    id_item_venda INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_pedido_venda INTEGER NOT NULL,
                    id_produto INTEGER NOT NULL,
                    quantidade INTEGER NOT NULL DEFAULT 1,
                    preco_unitario_venda REAL NOT NULL,
                    FOREIGN KEY (id_pedido_venda) REFERENCES Pedido_Venda(id_pedido_venda)
                        ON DELETE CASCADE,
                    FOREIGN KEY (id_produto) REFERENCES Produto(id_produto)
                        ON DELETE RESTRICT
                )
            """)
            cur.execute("CREATE INDEX idx_item_venda_pedido ON Item_Pedido_Venda(id_pedido_venda)")
            cur.execute("CREATE INDEX idx_item_venda_produto ON Item_Pedido_Venda(id_produto)")
            
            print("  ✅ Estrutura do banco criada do zero (Nova Modelagem)")
            
            # 3. Inserir dados padrão
            print("  📝 Inserindo dados padrão...")
            
            # Níveis de acesso
            cur.execute("""
                INSERT INTO nivel_acesso (nome) VALUES
                ('admin'),
                ('funcionario'),
                ('cliente')
            """)
            print("  ✅ Níveis de acesso inseridos")
            
            # Criar usuário admin padrão
            senha_padrao = "admin123"
            senha_hash = hashlib.sha256(senha_padrao.encode()).hexdigest()
            
            cur.execute("""
                INSERT INTO usuario (nome, email, senha_hash, telefone, ativo, id_nivel_acesso)
                VALUES ('Administrador', 'admin@autopeck.com', ?, '11999999999', 1, 
                        (SELECT id_nivel_acesso FROM nivel_acesso WHERE nome = 'admin'))
            """, (senha_hash,))
            
            id_usuario_admin = cur.lastrowid
            
            # Criar funcionário vinculado ao admin (para pedidos de compra)
            cur.execute("""
                INSERT INTO Funcionario (id_usuario, cargo, salario, data_contratacao)
                VALUES (?, 'Administrador', 0.0, date('now'))
            """, (id_usuario_admin,))
            
            print("  ✅ Usuário admin criado (email: admin@autopeck.com, senha: admin123)")
            print("  ✅ Funcionário admin criado (vinculado ao usuário)")
            print("  ⚠️  IMPORTANTE: Altere a senha do admin após o primeiro login!")
            print("  ℹ️  Todas as outras tabelas estão vazias")
        
        print("\n✅ Banco de dados resetado com sucesso!")
        return True
        
    except Exception as e:
        print(f"  ❌ Erro ao resetar banco SQLite: {e}")
        import traceback
        traceback.print_exc()
        return False

def confirmar_acao():
    """Solicita confirmação do usuário antes de executar"""
    print("\n" + "="*60)
    print("⚠️  ATENÇÃO: OPERAÇÃO DESTRUTIVA ⚠️")
    print("="*60)
    print("\nEste script irá:")
    print("  1. ❌ Remover TODAS as imagens de produtos")
    print("  2. ❌ Apagar TODOS os dados de teste do banco")
    print("  3. ✅ Criar estrutura da NOVA MODELAGEM")
    print("  4. ✅ Inserir apenas dados padrão iniciais")
    print("\n⚠️  Esta ação NÃO PODE SER DESFEITA!")
    print("="*60)
    
    resposta = input("\nDeseja continuar? Digite 'SIM' para confirmar: ")
    
    return resposta.strip().upper() == 'SIM'

def main(auto_confirm=False):
    """Função principal"""
    print("\n🧹 Script de Limpeza - SQLite (Nova Modelagem)")
    print("="*60)
    
    # Confirmar ação (pular se auto_confirm=True)
    if not auto_confirm and not confirmar_acao():
        print("\n❌ Operação cancelada pelo usuário.")
        print("   Nenhuma alteração foi feita.")
        sys.exit(0)
    
    print("\n🚀 Iniciando limpeza...")
    
    # 1. Limpar imagens
    limpar_imagens()
    
    # 2. Resetar banco
    sucesso = resetar_banco_sqlite()
    
    if sucesso:
        print("\n" + "="*60)
        print("✅ LIMPEZA CONCLUÍDA COM SUCESSO!")
        print("="*60)
        print("\n📋 Próximos passos:")
        print("  1. Testar criação de usuários")
        print("  2. Testar criação de clientes e funcionários")
        print("  3. Testar cadastro de produtos com SKU")
        print("  4. Testar fluxo de compras (fornecedores)")
        print("  5. Testar fluxo de vendas")
        print("\n💡 Usuário padrão para login:")
        print("  - Email: admin@autopeck.com")
        print("  - Senha: admin123")
        print("\n📚 Estrutura criada:")
        print("  ✅ Herança: Usuario → Cliente/Funcionario")
        print("  ✅ Fornecedor + Pedido_Compra (entrada)")
        print("  ✅ Pedido_Venda (saída)")
        print("  ✅ Produto com SKU e custo médio")
        print("\n")
    else:
        print("\n❌ Erro durante a limpeza.")
        print("   Verifique os logs acima para mais detalhes.")
        sys.exit(1)

if __name__ == "__main__":
    main()
