-- ============================================================
-- Script SQLite - Sistema de Auto Peças
-- Baseado na modelagem final com herança de usuários
-- ============================================================

-- Habilitar Foreign Keys (importante no SQLite)
PRAGMA foreign_keys = ON;

-- ============================================================
-- LIMPAR TABELAS EXISTENTES (ordem reversa por causa das FKs)
-- ============================================================

DROP TABLE IF EXISTS Item_Pedido_Venda;
DROP TABLE IF EXISTS Item_Pedido_Compra;
DROP TABLE IF EXISTS Pedido_Venda;
DROP TABLE IF EXISTS Pedido_Compra;
DROP TABLE IF EXISTS Fornecedor;
DROP TABLE IF EXISTS Produto;
DROP TABLE IF EXISTS Cliente;
DROP TABLE IF EXISTS Funcionario;
DROP TABLE IF EXISTS usuario;
DROP TABLE IF EXISTS nivel_acesso;

-- ============================================================
-- BLOCO 1: PESSOAS (Herança e Controle de Acesso)
-- ============================================================

-- Tabela de Níveis de Acesso (RBAC)
CREATE TABLE nivel_acesso (
    id_nivel_acesso INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE -- 'admin', 'funcionario', 'cliente'
);

-- Tabela Base de Usuários (Herança)
CREATE TABLE usuario (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    telefone TEXT,
    ativo INTEGER DEFAULT 1, -- 1=Ativo, 0=Inativo
    data_criacao TEXT DEFAULT CURRENT_TIMESTAMP,
    id_nivel_acesso INTEGER NOT NULL,
    
    FOREIGN KEY (id_nivel_acesso) REFERENCES nivel_acesso(id_nivel_acesso)
        ON DELETE RESTRICT
);

CREATE INDEX idx_usuario_email ON usuario(email);
CREATE INDEX idx_usuario_ativo ON usuario(ativo);

-- Tabela de Clientes (Especialização de Usuario)
CREATE TABLE Cliente (
    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL UNIQUE, -- FK para Usuario (1-para-1)
    cpf TEXT NOT NULL UNIQUE, -- CPF no formato XXX.XXX.XXX-XX
    endereco TEXT,
    
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
        ON DELETE CASCADE
);

CREATE INDEX idx_cliente_cpf ON Cliente(cpf);

-- Tabela de Funcionários (Especialização de Usuario)
CREATE TABLE Funcionario (
    id_funcionario INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL UNIQUE, -- FK para Usuario (1-para-1)
    cargo TEXT,
    salario REAL,
    data_contratacao TEXT, -- Formato: YYYY-MM-DD
    
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
        ON DELETE CASCADE
);

CREATE INDEX idx_funcionario_cargo ON Funcionario(cargo);

-- ============================================================
-- BLOCO 2: ESTOQUE (Produtos)
-- ============================================================

CREATE TABLE Produto (
    id_produto INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT,
    sku TEXT NOT NULL UNIQUE, -- Stock Keeping Unit (código único)
    estoque_atual INTEGER DEFAULT 0, -- Quantidade em estoque
    preco_venda REAL NOT NULL, -- Preço de venda ao cliente
    preco_custo_medio REAL DEFAULT 0.0, -- Custo médio ponderado
    nome_imagem TEXT,
    url TEXT
);

CREATE INDEX idx_produto_sku ON Produto(sku);
CREATE INDEX idx_produto_estoque ON Produto(estoque_atual);
CREATE INDEX idx_produto_nome ON Produto(nome);

-- ============================================================
-- BLOCO 3: PROCESSO DE SUPRIMENTOS (Compras - ENTRADA)
-- ============================================================

CREATE TABLE Fornecedor (
    id_fornecedor INTEGER PRIMARY KEY AUTOINCREMENT,
    razao_social TEXT NOT NULL, -- Nome jurídico (obrigatório para CNPJ)
    nome_fantasia TEXT NOT NULL, -- Nome comercial
    cnpj TEXT NOT NULL UNIQUE, -- CNPJ no formato XX.XXX.XXX/XXXX-XX
    email TEXT, -- Email de contato
    telefone TEXT, -- Telefone de contato
    endereco TEXT, -- Endereço completo
    ativo INTEGER DEFAULT 1, -- 1=Ativo, 0=Inativo (soft delete)
    data_criacao TEXT DEFAULT CURRENT_TIMESTAMP -- Data de cadastro
);

CREATE INDEX idx_fornecedor_cnpj ON Fornecedor(cnpj);
CREATE INDEX idx_fornecedor_nome_fantasia ON Fornecedor(nome_fantasia);
CREATE INDEX idx_fornecedor_razao_social ON Fornecedor(razao_social);
CREATE INDEX idx_fornecedor_ativo ON Fornecedor(ativo);

CREATE TABLE Pedido_Compra (
    id_pedido_compra INTEGER PRIMARY KEY AUTOINCREMENT,
    id_fornecedor INTEGER NOT NULL,
    id_funcionario INTEGER, -- Funcionário responsável pela compra
    data_pedido TEXT DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'Pendente', -- Pendente, Aprovado, Enviado, Recebido, Cancelado
    total REAL NOT NULL DEFAULT 0.0, -- Valor total da compra
    
    FOREIGN KEY (id_fornecedor) REFERENCES Fornecedor(id_fornecedor)
        ON DELETE RESTRICT,
    FOREIGN KEY (id_funcionario) REFERENCES Funcionario(id_funcionario)
        ON DELETE SET NULL
);

CREATE INDEX idx_pedido_compra_fornecedor ON Pedido_Compra(id_fornecedor);
CREATE INDEX idx_pedido_compra_funcionario ON Pedido_Compra(id_funcionario);
CREATE INDEX idx_pedido_compra_data ON Pedido_Compra(data_pedido);
CREATE INDEX idx_pedido_compra_status ON Pedido_Compra(status);

CREATE TABLE Item_Pedido_Compra (
    id_item_compra INTEGER PRIMARY KEY AUTOINCREMENT,
    id_pedido_compra INTEGER NOT NULL,
    id_produto INTEGER NOT NULL,
    quantidade INTEGER NOT NULL DEFAULT 1,
    preco_custo_unitario REAL NOT NULL, -- Snapshot do custo no momento da compra
    
    FOREIGN KEY (id_pedido_compra) REFERENCES Pedido_Compra(id_pedido_compra)
        ON DELETE CASCADE,
    FOREIGN KEY (id_produto) REFERENCES Produto(id_produto)
        ON DELETE RESTRICT
);

CREATE INDEX idx_item_compra_pedido ON Item_Pedido_Compra(id_pedido_compra);
CREATE INDEX idx_item_compra_produto ON Item_Pedido_Compra(id_produto);

-- ============================================================
-- BLOCO 4: PROCESSO DE VAREJO (Vendas - SAÍDA)
-- ============================================================

CREATE TABLE Pedido_Venda (
    id_pedido_venda INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente INTEGER NOT NULL,
    id_funcionario INTEGER, -- Vendedor responsável (NULL para vendas online)
    data_pedido TEXT DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'Pendente', -- Pendente, Confirmado, Separado, Enviado, Entregue, Cancelado
    total REAL NOT NULL DEFAULT 0.0, -- Valor total da venda
    
    FOREIGN KEY (id_cliente) REFERENCES Cliente(id_cliente)
        ON DELETE RESTRICT,
    FOREIGN KEY (id_funcionario) REFERENCES Funcionario(id_funcionario)
        ON DELETE SET NULL
);

CREATE INDEX idx_pedido_venda_cliente ON Pedido_Venda(id_cliente);
CREATE INDEX idx_pedido_venda_funcionario ON Pedido_Venda(id_funcionario);
CREATE INDEX idx_pedido_venda_data ON Pedido_Venda(data_pedido);
CREATE INDEX idx_pedido_venda_status ON Pedido_Venda(status);

CREATE TABLE Item_Pedido_Venda (
    id_item_venda INTEGER PRIMARY KEY AUTOINCREMENT,
    id_pedido_venda INTEGER NOT NULL,
    id_produto INTEGER NOT NULL,
    quantidade INTEGER NOT NULL DEFAULT 1,
    preco_unitario_venda REAL NOT NULL, -- Snapshot do preço no momento da venda
    
    FOREIGN KEY (id_pedido_venda) REFERENCES Pedido_Venda(id_pedido_venda)
        ON DELETE CASCADE,
    FOREIGN KEY (id_produto) REFERENCES Produto(id_produto)
        ON DELETE RESTRICT
);

CREATE INDEX idx_item_venda_pedido ON Item_Pedido_Venda(id_pedido_venda);
CREATE INDEX idx_item_venda_produto ON Item_Pedido_Venda(id_produto);

-- ============================================================
-- TABELA DE CONTROLE: Token Blacklist (JWT)
-- ============================================================

-- Tabela para armazenar tokens JWT revogados (logout)
-- Necessária para invalidar tokens entre múltiplos workers/processos
CREATE TABLE token_blacklist (
    jti VARCHAR(255) PRIMARY KEY,
    revoked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_token_revoked_at ON token_blacklist(revoked_at);

-- ============================================================
-- DADOS INICIAIS (Seed Data)
-- ============================================================

-- Inserir níveis de acesso padrão
INSERT INTO nivel_acesso (nome) VALUES
('admin'),
('funcionario'),
('cliente');

-- ============================================================
-- VIEWS ÚTEIS (para facilitar consultas)
-- ============================================================

-- View: Usuários com seus dados completos (Cliente ou Funcionário)
CREATE VIEW vw_usuarios_completos AS
SELECT 
    u.id_usuario,
    u.nome,
    u.email,
    u.telefone,
    u.ativo,
    u.data_criacao,
    na.nome as nivel_acesso,
    c.id_cliente,
    c.cpf,
    c.endereco,
    f.id_funcionario,
    f.cargo,
    f.salario,
    f.data_contratacao,
    CASE 
        WHEN c.id_cliente IS NOT NULL THEN 'Cliente'
        WHEN f.id_funcionario IS NOT NULL THEN 'Funcionario'
        ELSE 'Usuario'
    END as tipo_usuario
FROM usuario u
LEFT JOIN nivel_acesso na ON u.id_nivel_acesso = na.id_nivel_acesso
LEFT JOIN Cliente c ON u.id_usuario = c.id_usuario
LEFT JOIN Funcionario f ON u.id_usuario = f.id_usuario;

-- View: Produtos com informações de lucro
CREATE VIEW vw_produtos_lucro AS
SELECT 
    id_produto,
    nome,
    sku,
    estoque_atual,
    preco_custo_medio,
    preco_venda,
    (preco_venda - preco_custo_medio) as lucro_unitario,
    CASE 
        WHEN preco_custo_medio > 0 THEN 
            ((preco_venda - preco_custo_medio) / preco_custo_medio * 100)
        ELSE 0
    END as margem_percentual
FROM Produto;

-- View: Resumo de vendas por cliente
CREATE VIEW vw_vendas_por_cliente AS
SELECT 
    c.id_cliente,
    u.nome as cliente_nome,
    u.email,
    c.cpf,
    COUNT(pv.id_pedido_venda) as total_pedidos,
    SUM(pv.total) as valor_total_gasto,
    AVG(pv.total) as ticket_medio,
    MAX(pv.data_pedido) as ultima_compra
FROM Cliente c
JOIN usuario u ON c.id_usuario = u.id_usuario
LEFT JOIN Pedido_Venda pv ON c.id_cliente = pv.id_cliente
WHERE pv.status IN ('Confirmado', 'Separado', 'Enviado', 'Entregue')
GROUP BY c.id_cliente, u.nome, u.email, c.cpf;

-- View: Resumo de compras por fornecedor
CREATE VIEW vw_compras_por_fornecedor AS
SELECT 
    f.id_fornecedor,
    f.razao_social,
    f.nome_fantasia,
    f.cnpj,
    f.email,
    f.telefone,
    f.ativo,
    COUNT(pc.id_pedido_compra) as total_pedidos,
    SUM(pc.total) as valor_total_comprado,
    AVG(pc.total) as valor_medio_pedido,
    MAX(pc.data_pedido) as ultima_compra
FROM Fornecedor f
LEFT JOIN Pedido_Compra pc ON f.id_fornecedor = pc.id_fornecedor
WHERE pc.status = 'Recebido'
GROUP BY f.id_fornecedor, f.razao_social, f.nome_fantasia, f.cnpj, f.email, f.telefone, f.ativo;

-- ============================================================
-- CONSULTAS ÚTEIS (comentadas - descomente para executar)
-- ============================================================

-- Selecionar todos os registros das tabelas principais
-- SELECT * FROM nivel_acesso;
-- SELECT * FROM usuario;
-- SELECT * FROM Cliente;
-- SELECT * FROM Funcionario;
-- SELECT * FROM Produto;
-- SELECT * FROM Fornecedor;
-- SELECT * FROM Pedido_Compra;
-- SELECT * FROM Item_Pedido_Compra;
-- SELECT * FROM Pedido_Venda;
-- SELECT * FROM Item_Pedido_Venda;

-- Usar as views
-- SELECT * FROM vw_usuarios_completos;
-- SELECT * FROM vw_produtos_lucro;
-- SELECT * FROM vw_vendas_por_cliente;
-- SELECT * FROM vw_compras_por_fornecedor;

-- ============================================================
-- FIM DO SCRIPT
-- ============================================================
