#!/usr/bin/env python3
"""
Script para limpar dados de teste no PythonAnywhere
Uso: python scripts/limpar_producao.py

ATENÇÃO: Este script irá:
1. Remover todas as imagens de produtos (exceto README.md)
2. Limpar dados de teste das tabelas
3. Inserir dados padrão iniciais

Execute apenas em ambiente de produção após testes!
"""

import os
import sys
import hashlib

# Adicionar o diretório raiz ao path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, BASE_DIR)

# Carregar variáveis de ambiente do arquivo .env
def load_env_file(env_path):
    """Carrega variáveis de ambiente de um arquivo .env"""
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove aspas se existirem
                    value = value.strip().strip('"').strip("'")
                    os.environ[key] = value
        print(f"✅ Variáveis de ambiente carregadas de {env_path}")
    else:
        print(f"⚠️  Arquivo .env não encontrado em {env_path}")

# Carregar .env
env_file = os.path.join(BASE_DIR, '.env')
load_env_file(env_file)

def limpar_imagens():
    """Remove todas as imagens de teste do diretório de uploads"""
    print("\n🗑️  Limpando imagens de teste...")
    
    # Caminho absoluto para o diretório de imagens
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
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

def resetar_banco_mysql():
    """Reseta o banco de dados MySQL para estado padrão"""
    print("\n🗄️  Resetando banco de dados MySQL...")
    
    try:
        # Carregar variáveis de ambiente do .env (necessário para scripts locais)
        env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
        if os.path.exists(env_file):
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        value = value.strip().strip('"').strip("'")
                        os.environ[key] = value
            print("  ✅ Variáveis de ambiente carregadas do .env")
        
        # Tentar importar DAO do MySQL
        from dao_mysql.db_pythonanywhere import init_db, get_cursor
        
        # Inicializar banco
        init_db()
        
        print("  🔗 Conectado ao MySQL")
        
        with get_cursor() as cur:
            # Desabilitar verificação de chaves estrangeiras temporariamente
            cur.execute("SET FOREIGN_KEY_CHECKS = 0")
            
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
            
            # Reabilitar verificação de chaves estrangeiras
            cur.execute("SET FOREIGN_KEY_CHECKS = 1")
            
            # 2. Criar tabelas do zero (Nova Modelagem)
            print("  🔧 Criando estrutura do banco do zero (Nova Modelagem)...")
            
            # Tabela nivel_acesso
            cur.execute("""
                CREATE TABLE nivel_acesso (
                    id_nivel_acesso INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(50) NOT NULL UNIQUE COMMENT 'admin, funcionario, cliente'
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabela usuario (Base para herança)
            cur.execute("""
                CREATE TABLE usuario (
                    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    senha_hash VARCHAR(255) NOT NULL,
                    telefone VARCHAR(20),
                    ativo BOOLEAN DEFAULT 1 COMMENT '1=Ativo, 0=Inativo',
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    id_nivel_acesso INT NOT NULL,
                    KEY idx_usuario_email (email),
                    KEY idx_usuario_ativo (ativo),
                    CONSTRAINT fk_usuario_nivel
                        FOREIGN KEY (id_nivel_acesso) 
                        REFERENCES nivel_acesso(id_nivel_acesso)
                        ON DELETE RESTRICT
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabela Cliente (herda de Usuario - 1-para-1)
            cur.execute("""
                CREATE TABLE Cliente (
                    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
                    id_usuario INT NOT NULL UNIQUE COMMENT 'FK para Usuario (1-para-1)',
                    cpf VARCHAR(14) NOT NULL UNIQUE COMMENT 'CPF no formato XXX.XXX.XXX-XX',
                    endereco TEXT,
                    KEY idx_cliente_cpf (cpf),
                    CONSTRAINT fk_cliente_usuario
                        FOREIGN KEY (id_usuario) 
                        REFERENCES usuario(id_usuario)
                        ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabela Funcionario (herda de Usuario - 1-para-1)
            cur.execute("""
                CREATE TABLE Funcionario (
                    id_funcionario INT AUTO_INCREMENT PRIMARY KEY,
                    id_usuario INT NOT NULL UNIQUE COMMENT 'FK para Usuario (1-para-1)',
                    cargo VARCHAR(100),
                    salario DECIMAL(10,2),
                    data_contratacao DATE,
                    KEY idx_funcionario_cargo (cargo),
                    CONSTRAINT fk_funcionario_usuario
                        FOREIGN KEY (id_usuario) 
                        REFERENCES usuario(id_usuario)
                        ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabela Produto (com SKU e custo médio)
            cur.execute("""
                CREATE TABLE Produto (
                    id_produto INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(255) NOT NULL,
                    descricao TEXT,
                    sku VARCHAR(100) NOT NULL UNIQUE COMMENT 'Stock Keeping Unit',
                    estoque_atual INT DEFAULT 0 COMMENT 'Quantidade em estoque',
                    preco_venda DECIMAL(10,2) NOT NULL COMMENT 'Preço de venda ao cliente',
                    preco_custo_medio DECIMAL(10,2) DEFAULT 0.00 COMMENT 'Custo médio ponderado',
                    nome_imagem VARCHAR(255),
                    url VARCHAR(255),
                    KEY idx_produto_sku (sku),
                    KEY idx_produto_estoque (estoque_atual),
                    KEY idx_produto_nome (nome)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabela Fornecedor (estrutura melhorada)
            cur.execute("""
                CREATE TABLE Fornecedor (
                    id_fornecedor INT AUTO_INCREMENT PRIMARY KEY,
                    razao_social VARCHAR(255) NOT NULL COMMENT 'Nome jurídico (obrigatório para CNPJ)',
                    nome_fantasia VARCHAR(255) NOT NULL COMMENT 'Nome comercial',
                    cnpj VARCHAR(18) NOT NULL UNIQUE COMMENT 'CNPJ no formato XX.XXX.XXX/XXXX-XX',
                    email VARCHAR(100) COMMENT 'Email de contato',
                    telefone VARCHAR(20) COMMENT 'Telefone de contato',
                    endereco TEXT COMMENT 'Endereço completo',
                    ativo BOOLEAN DEFAULT 1 COMMENT '1=Ativo, 0=Inativo (soft delete)',
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Data de cadastro',
                    KEY idx_fornecedor_cnpj (cnpj),
                    KEY idx_fornecedor_nome_fantasia (nome_fantasia),
                    KEY idx_fornecedor_razao_social (razao_social),
                    KEY idx_fornecedor_ativo (ativo)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabela Pedido_Compra (ENTRADA de estoque)
            cur.execute("""
                CREATE TABLE Pedido_Compra (
                    id_pedido_compra INT AUTO_INCREMENT PRIMARY KEY,
                    id_fornecedor INT NOT NULL,
                    id_funcionario INT COMMENT 'Funcionário responsável',
                    data_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(50) DEFAULT 'Pendente' COMMENT 'Pendente, Aprovado, Enviado, Recebido, Cancelado',
                    total DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                    KEY idx_pedido_compra_fornecedor (id_fornecedor),
                    KEY idx_pedido_compra_funcionario (id_funcionario),
                    KEY idx_pedido_compra_data (data_pedido),
                    KEY idx_pedido_compra_status (status),
                    CONSTRAINT fk_pedido_compra_fornecedor
                        FOREIGN KEY (id_fornecedor) 
                        REFERENCES Fornecedor(id_fornecedor)
                        ON DELETE RESTRICT,
                    CONSTRAINT fk_pedido_compra_funcionario
                        FOREIGN KEY (id_funcionario) 
                        REFERENCES Funcionario(id_funcionario)
                        ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabela Item_Pedido_Compra
            cur.execute("""
                CREATE TABLE Item_Pedido_Compra (
                    id_item_compra INT AUTO_INCREMENT PRIMARY KEY,
                    id_pedido_compra INT NOT NULL,
                    id_produto INT NOT NULL,
                    quantidade INT NOT NULL DEFAULT 1,
                    preco_custo_unitario DECIMAL(10,2) NOT NULL COMMENT 'Snapshot do custo',
                    KEY idx_item_compra_pedido (id_pedido_compra),
                    KEY idx_item_compra_produto (id_produto),
                    CONSTRAINT fk_item_compra_pedido
                        FOREIGN KEY (id_pedido_compra) 
                        REFERENCES Pedido_Compra(id_pedido_compra)
                        ON DELETE CASCADE,
                    CONSTRAINT fk_item_compra_produto
                        FOREIGN KEY (id_produto) 
                        REFERENCES Produto(id_produto)
                        ON DELETE RESTRICT
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabela Pedido_Venda (SAÍDA de estoque)
            cur.execute("""
                CREATE TABLE Pedido_Venda (
                    id_pedido_venda INT AUTO_INCREMENT PRIMARY KEY,
                    id_cliente INT NOT NULL,
                    id_funcionario INT COMMENT 'Vendedor (NULL para vendas online)',
                    data_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(50) DEFAULT 'Pendente' COMMENT 'Pendente, Confirmado, Separado, Enviado, Entregue, Cancelado',
                    total DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                    KEY idx_pedido_venda_cliente (id_cliente),
                    KEY idx_pedido_venda_funcionario (id_funcionario),
                    KEY idx_pedido_venda_data (data_pedido),
                    KEY idx_pedido_venda_status (status),
                    CONSTRAINT fk_pedido_venda_cliente
                        FOREIGN KEY (id_cliente) 
                        REFERENCES Cliente(id_cliente)
                        ON DELETE RESTRICT,
                    CONSTRAINT fk_pedido_venda_funcionario
                        FOREIGN KEY (id_funcionario) 
                        REFERENCES Funcionario(id_funcionario)
                        ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabela Item_Pedido_Venda
            cur.execute("""
                CREATE TABLE Item_Pedido_Venda (
                    id_item_venda INT AUTO_INCREMENT PRIMARY KEY,
                    id_pedido_venda INT NOT NULL,
                    id_produto INT NOT NULL,
                    quantidade INT NOT NULL DEFAULT 1,
                    preco_unitario_venda DECIMAL(10,2) NOT NULL COMMENT 'Snapshot do preço',
                    KEY idx_item_venda_pedido (id_pedido_venda),
                    KEY idx_item_venda_produto (id_produto),
                    CONSTRAINT fk_item_venda_pedido
                        FOREIGN KEY (id_pedido_venda) 
                        REFERENCES Pedido_Venda(id_pedido_venda)
                        ON DELETE CASCADE,
                    CONSTRAINT fk_item_venda_produto
                        FOREIGN KEY (id_produto) 
                        REFERENCES Produto(id_produto)
                        ON DELETE RESTRICT
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            print("  ✅ Estrutura do banco criada do zero (Nova Modelagem)")
            
            # 3. Inserir dados padrão
            print("  📝 Inserindo dados padrão...")
            
            # Níveis de acesso (único dado padrão)
            cur.execute("""
                INSERT INTO nivel_acesso (nome) VALUES
                ('admin'),
                ('funcionario'),
                ('cliente')
            """)
            print("  ✅ Níveis de acesso inseridos")
            
            # Criar usuário admin padrão
            senha_padrao = "admin123"  # Senha padrão
            senha_hash = hashlib.sha256(senha_padrao.encode()).hexdigest()
            
            cur.execute("""
                INSERT INTO usuario (nome, email, senha_hash, telefone, ativo, id_nivel_acesso)
                VALUES ('Administrador', 'admin@autopeck.com', %s, '11999999999', 1, 
                        (SELECT id_nivel_acesso FROM nivel_acesso WHERE nome = 'admin'))
            """, (senha_hash,))
            
            # Obter ID do usuário admin usando lastrowid
            id_usuario_admin = cur.lastrowid
            
            # Criar funcionário vinculado ao admin (para pedidos de compra)
            cur.execute("""
                INSERT INTO Funcionario (id_usuario, cargo, salario, data_contratacao)
                VALUES (%s, 'Administrador', 0.0, CURDATE())
            """, (id_usuario_admin,))
            
            print("  ✅ Usuário admin criado (email: admin@autopeck.com, senha: admin123)")
            print("  ✅ Funcionário admin criado (vinculado ao usuário)")
            print("  ⚠️  IMPORTANTE: Altere a senha do admin após o primeiro login!")
            print("  ℹ️  Todas as outras tabelas estão vazias")
        
        print("\n✅ Banco de dados resetado com sucesso!")
        return True
        
    except ImportError:
        print("  ⚠️  DAO MySQL não disponível. Tentando SQLite...")
        return resetar_banco_sqlite()
    except Exception as e:
        print(f"  ❌ Erro ao resetar banco MySQL: {e}")
        return False

def resetar_banco_sqlite():
    """Reseta o banco de dados SQLite para estado padrão"""
    print("\n🗄️  Resetando banco de dados SQLite...")
    
    try:
        from dao_sqlite.db import init_db, get_cursor
        
        # Inicializar banco
        init_db()
        
        print("  🔗 Conectado ao SQLite")
        
        with get_cursor() as cur:
            # 1. Limpar todas as tabelas (ordem reversa por causa das FKs)
            print("  🗑️  Limpando tabelas (Nova Modelagem)...")
            cur.execute("DELETE FROM Item_Pedido_Venda")
            cur.execute("DELETE FROM Item_Pedido_Compra")
            cur.execute("DELETE FROM Pedido_Venda")
            cur.execute("DELETE FROM Pedido_Compra")
            cur.execute("DELETE FROM Fornecedor")
            cur.execute("DELETE FROM Produto")
            cur.execute("DELETE FROM Cliente")
            cur.execute("DELETE FROM Funcionario")
            cur.execute("DELETE FROM usuario")
            cur.execute("DELETE FROM nivel_acesso")
            print("  ✅ Tabelas limpas")
            
            # 2. Resetar auto-increment
            cur.execute("DELETE FROM sqlite_sequence")
            
            # 3. Inserir apenas dados padrão de nivel_acesso
            print("  📝 Inserindo dados padrão...")
            
            cur.execute("""
                INSERT INTO nivel_acesso (nome) VALUES
                ('admin'),
                ('funcionario'),
                ('cliente')
            """)
            
            print("  ✅ Níveis de acesso inseridos")
            
            # Criar usuário admin padrão
            senha_padrao = "admin123"  # Senha padrão
            senha_hash = hashlib.sha256(senha_padrao.encode()).hexdigest()
            
            cur.execute("""
                INSERT INTO usuario (nome, email, senha_hash, telefone, ativo, id_nivel_acesso)
                VALUES ('Administrador', 'admin@autopeck.com', ?, '11999999999', 1, 
                        (SELECT id_nivel_acesso FROM nivel_acesso WHERE nome = 'admin'))
            """, (senha_hash,))
            
            print("  ✅ Usuário admin criado (email: admin@autopeck.com, senha: admin123)")
            print("  ⚠️  IMPORTANTE: Altere a senha do admin após o primeiro login!")
            print("  ℹ️  Todas as outras tabelas estão vazias")
        
        print("\n✅ Banco de dados resetado com sucesso!")
        return True
        
    except Exception as e:
        print(f"  ❌ Erro ao resetar banco SQLite: {e}")
        return False

def confirmar_acao():
    """Solicita confirmação do usuário antes de executar"""
    print("\n" + "="*60)
    print("⚠️  ATENÇÃO: OPERAÇÃO DESTRUTIVA ⚠️")
    print("="*60)
    print("\nEste script irá:")
    print("  1. ❌ Remover TODAS as imagens de produtos")
    print("  2. ❌ Apagar TODOS os dados de teste do banco")
    print("  3. ✅ Inserir apenas dados padrão iniciais")
    print("\n⚠️  Esta ação NÃO PODE SER DESFEITA!")
    print("="*60)
    
    resposta = input("\nDeseja continuar? Digite 'SIM' para confirmar: ")
    
    return resposta.strip().upper() == 'SIM'

def main():
    """Função principal"""
    print("\n🧹 Script de Limpeza - Ambiente de Produção")
    print("="*60)
    
    # Confirmar ação
    if not confirmar_acao():
        print("\n❌ Operação cancelada pelo usuário.")
        print("   Nenhuma alteração foi feita.")
        sys.exit(0)
    
    print("\n🚀 Iniciando limpeza...")
    
    # 1. Limpar imagens
    limpar_imagens()
    
    # 2. Resetar banco
    sucesso = resetar_banco_mysql()
    
    if sucesso:
        print("\n" + "="*60)
        print("✅ LIMPEZA CONCLUÍDA COM SUCESSO!")
        print("="*60)
        print("\n📋 Próximos passos:")
        print("  1. Fazer reload da aplicação no PythonAnywhere")
        print("  2. Testar login com usuário padrão")
        print("  3. Verificar se produtos estão listando corretamente")
        print("\n💡 Usuário padrão para primeiro login:")
        print("  - Email: admin@autopeck.com")
        print("  - Senha: admin123")
        print("  ⚠️  IMPORTANTE: Altere a senha após o primeiro login!")
        print("\n")
    else:
        print("\n❌ Erro durante a limpeza.")
        print("   Verifique os logs acima para mais detalhes.")
        sys.exit(1)

if __name__ == "__main__":
    main()
