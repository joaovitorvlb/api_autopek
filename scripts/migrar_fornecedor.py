"""
Script de Migração da Tabela Fornecedor
Atualiza a estrutura da tabela Fornecedor seguindo a nova modelagem
"""

import sqlite3
import os

# Caminho para o banco de dados
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'autopek.db')


def migrar_fornecedor():
    """
    Migra a estrutura antiga de Fornecedor para a nova estrutura
    """
    print("🔄 Iniciando migração da tabela Fornecedor...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar estrutura atual
        cursor.execute("PRAGMA table_info(Fornecedor)")
        colunas_existentes = [col[1] for col in cursor.fetchall()]
        print(f"📋 Colunas atuais: {', '.join(colunas_existentes)}")
        
        # Verificar se já está migrado
        if 'razao_social' in colunas_existentes and 'email' in colunas_existentes:
            print("✅ Tabela Fornecedor já está atualizada!")
            conn.close()
            return
        
        print("\n📝 Criando nova tabela Fornecedor...")
        
        # Criar nova tabela com estrutura atualizada
        cursor.execute("""
            CREATE TABLE Fornecedor_novo (
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
        
        # Migrar dados da tabela antiga para a nova
        print("📦 Migrando dados existentes...")
        
        cursor.execute("SELECT id_fornecedor, nome_fantasia, cnpj, contato FROM Fornecedor")
        fornecedores_antigos = cursor.fetchall()
        
        for fornecedor in fornecedores_antigos:
            id_forn, nome_fantasia, cnpj, contato = fornecedor
            
            # Usar nome_fantasia como razão_social temporariamente
            razao_social = nome_fantasia
            
            # Tentar separar email e telefone do campo contato
            email = None
            telefone = None
            
            if contato:
                # Se contém @, provavelmente é email
                if '@' in contato:
                    email = contato
                else:
                    telefone = contato
            
            # Inserir na nova tabela
            cursor.execute("""
                INSERT INTO Fornecedor_novo (id_fornecedor, razao_social, nome_fantasia, cnpj, email, telefone)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (id_forn, razao_social, nome_fantasia, cnpj, email, telefone))
        
        print(f"✅ {len(fornecedores_antigos)} fornecedores migrados")
        
        # Renomear tabelas
        print("🔄 Substituindo tabela antiga...")
        cursor.execute("DROP TABLE Fornecedor")
        cursor.execute("ALTER TABLE Fornecedor_novo RENAME TO Fornecedor")
        
        # Criar índices
        print("📊 Criando índices...")
        cursor.execute("CREATE INDEX idx_fornecedor_cnpj ON Fornecedor(cnpj)")
        cursor.execute("CREATE INDEX idx_fornecedor_nome_fantasia ON Fornecedor(nome_fantasia)")
        cursor.execute("CREATE INDEX idx_fornecedor_razao_social ON Fornecedor(razao_social)")
        cursor.execute("CREATE INDEX idx_fornecedor_ativo ON Fornecedor(ativo)")
        
        # Commit
        conn.commit()
        
        print("\n✅ Migração concluída com sucesso!")
        print("\n⚠️  ATENÇÃO:")
        print("   - razao_social foi preenchida com nome_fantasia")
        print("   - Revise os dados e atualize a razão social correta de cada fornecedor")
        print("   - Campo 'contato' foi separado em 'email' e 'telefone'")
        
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()


if __name__ == '__main__':
    print("=" * 60)
    print("  SCRIPT DE MIGRAÇÃO - TABELA FORNECEDOR")
    print("=" * 60)
    print()
    
    resposta = input("⚠️  Este script alterará a estrutura do banco de dados.\n   Deseja continuar? (s/n): ")
    
    if resposta.lower() == 's':
        migrar_fornecedor()
    else:
        print("❌ Migração cancelada.")
