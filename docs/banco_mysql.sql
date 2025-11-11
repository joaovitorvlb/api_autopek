-- -*- mode: sql; -*-
-- Script MySQL para PythonAnywhere (Compatibilidade garantida)
-- Substitua SEU_USUARIO pelo seu nome de usuário PythonAnywhere

-- INSTRUÇÕES:
-- 1. Acesse Dashboard do PythonAnywhere
-- 2. Vá em "Databases" 
-- 3. Clique em "Open MySQL console"
-- 4. Cole e execute este script

-- Limpar tabelas existentes se necessário (ordem reversa por causa das FKs)
SET FOREIGN_KEY_CHECKS = 0;
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
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- BLOCO 1: PESSOAS (Herança e Controle de Acesso)
-- ============================================================

-- Tabela de Níveis de Acesso (RBAC)
CREATE TABLE nivel_acesso (
    id_nivel_acesso INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) NOT NULL UNIQUE COMMENT 'admin, funcionario, cliente'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT 'Tabela de controle de acesso (RBAC)';

-- Tabela Base de Usuários (Herança)
CREATE TABLE usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    telefone VARCHAR(20),
    ativo BOOLEAN DEFAULT 1 COMMENT '1=Ativo, 0=Inativo',
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_nivel_acesso INT NOT NULL,
    
    -- Índices
    KEY idx_usuario_email (email),
    KEY idx_usuario_ativo (ativo),
    
    -- Chave Estrangeira
    CONSTRAINT fk_usuario_nivel
        FOREIGN KEY (id_nivel_acesso) 
        REFERENCES nivel_acesso(id_nivel_acesso)
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT 'Tabela central de usuários (base para Cliente e Funcionario)';

-- Tabela de Clientes (Especialização de Usuario)
CREATE TABLE Cliente (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL UNIQUE COMMENT 'FK para Usuario (1-para-1)',
    cpf VARCHAR(14) NOT NULL UNIQUE COMMENT 'CPF no formato XXX.XXX.XXX-XX',
    endereco TEXT,
    
    -- Índices
    KEY idx_cliente_cpf (cpf),
    
    -- Chave Estrangeira
    CONSTRAINT fk_cliente_usuario
        FOREIGN KEY (id_usuario) 
        REFERENCES usuario(id_usuario)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT 'Tabela de clientes (herda de Usuario)';

-- Tabela de Funcionários (Especialização de Usuario)
CREATE TABLE Funcionario (
    id_funcionario INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL UNIQUE COMMENT 'FK para Usuario (1-para-1)',
    cargo VARCHAR(100),
    salario DECIMAL(10,2),
    data_contratacao DATE,
    
    -- Índices
    KEY idx_funcionario_cargo (cargo),
    
    -- Chave Estrangeira
    CONSTRAINT fk_funcionario_usuario
        FOREIGN KEY (id_usuario) 
        REFERENCES usuario(id_usuario)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT 'Tabela de funcionários (herda de Usuario)';

-- ============================================================
-- BLOCO 2: ESTOQUE (Produtos)
-- ============================================================

CREATE TABLE Produto (
    id_produto INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    sku VARCHAR(100) NOT NULL UNIQUE COMMENT 'Stock Keeping Unit (código único)',
    estoque_atual INT DEFAULT 0 COMMENT 'Quantidade em estoque',
    preco_venda DECIMAL(10,2) NOT NULL COMMENT 'Preço de venda ao cliente',
    preco_custo_medio DECIMAL(10,2) DEFAULT 0.00 COMMENT 'Custo médio ponderado',
    nome_imagem VARCHAR(255),
    url VARCHAR(255),
    
    -- Índices
    KEY idx_produto_sku (sku),
    KEY idx_produto_estoque (estoque_atual),
    KEY idx_produto_nome (nome)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT 'Tabela central de produtos';

-- ============================================================
-- BLOCO 3: PROCESSO DE SUPRIMENTOS (Compras - ENTRADA)
-- ============================================================

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
    
    -- Índices
    KEY idx_fornecedor_cnpj (cnpj),
    KEY idx_fornecedor_nome_fantasia (nome_fantasia),
    KEY idx_fornecedor_razao_social (razao_social),
    KEY idx_fornecedor_ativo (ativo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT 'Tabela de fornecedores';

CREATE TABLE Pedido_Compra (
    id_pedido_compra INT AUTO_INCREMENT PRIMARY KEY,
    id_fornecedor INT NOT NULL,
    id_funcionario INT COMMENT 'Funcionário responsável pela compra',
    data_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'Pendente' COMMENT 'Pendente, Aprovado, Enviado, Recebido, Cancelado',
    total DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT 'Valor total da compra',
    
    -- Índices
    KEY idx_pedido_compra_fornecedor (id_fornecedor),
    KEY idx_pedido_compra_funcionario (id_funcionario),
    KEY idx_pedido_compra_data (data_pedido),
    KEY idx_pedido_compra_status (status),
    
    -- Chaves Estrangeiras
    CONSTRAINT fk_pedido_compra_fornecedor
        FOREIGN KEY (id_fornecedor) 
        REFERENCES Fornecedor(id_fornecedor)
        ON DELETE RESTRICT,
    
    CONSTRAINT fk_pedido_compra_funcionario
        FOREIGN KEY (id_funcionario) 
        REFERENCES Funcionario(id_funcionario)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT 'Tabela de pedidos de compra (ENTRADA de estoque)';

CREATE TABLE Item_Pedido_Compra (
    id_item_compra INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido_compra INT NOT NULL,
    id_produto INT NOT NULL,
    quantidade INT NOT NULL DEFAULT 1,
    preco_custo_unitario DECIMAL(10,2) NOT NULL COMMENT 'Snapshot do custo no momento da compra',
    
    -- Índices
    KEY idx_item_compra_pedido (id_pedido_compra),
    KEY idx_item_compra_produto (id_produto),
    
    -- Chaves Estrangeiras
    CONSTRAINT fk_item_compra_pedido
        FOREIGN KEY (id_pedido_compra) 
        REFERENCES Pedido_Compra(id_pedido_compra)
        ON DELETE CASCADE,
    
    CONSTRAINT fk_item_compra_produto
        FOREIGN KEY (id_produto) 
        REFERENCES Produto(id_produto)
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT 'Itens do pedido de compra';

-- ============================================================
-- BLOCO 4: PROCESSO DE VAREJO (Vendas - SAÍDA)
-- ============================================================

CREATE TABLE Pedido_Venda (
    id_pedido_venda INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    id_funcionario INT COMMENT 'Vendedor responsável (NULL para vendas online)',
    data_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'Pendente' COMMENT 'Pendente, Confirmado, Separado, Enviado, Entregue, Cancelado',
    total DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT 'Valor total da venda',
    
    -- Índices
    KEY idx_pedido_venda_cliente (id_cliente),
    KEY idx_pedido_venda_funcionario (id_funcionario),
    KEY idx_pedido_venda_data (data_pedido),
    KEY idx_pedido_venda_status (status),
    
    -- Chaves Estrangeiras
    CONSTRAINT fk_pedido_venda_cliente
        FOREIGN KEY (id_cliente) 
        REFERENCES Cliente(id_cliente)
        ON DELETE RESTRICT,
    
    CONSTRAINT fk_pedido_venda_funcionario
        FOREIGN KEY (id_funcionario) 
        REFERENCES Funcionario(id_funcionario)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT 'Tabela de pedidos de venda (SAÍDA de estoque)';

CREATE TABLE Item_Pedido_Venda (
    id_item_venda INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido_venda INT NOT NULL,
    id_produto INT NOT NULL,
    quantidade INT NOT NULL DEFAULT 1,
    preco_unitario_venda DECIMAL(10,2) NOT NULL COMMENT 'Snapshot do preço no momento da venda',
    
    -- Índices
    KEY idx_item_venda_pedido (id_pedido_venda),
    KEY idx_item_venda_produto (id_produto),
    
    -- Chaves Estrangeiras
    CONSTRAINT fk_item_venda_pedido
        FOREIGN KEY (id_pedido_venda) 
        REFERENCES Pedido_Venda(id_pedido_venda)
        ON DELETE CASCADE,
    
    CONSTRAINT fk_item_venda_produto
        FOREIGN KEY (id_produto) 
        REFERENCES Produto(id_produto)
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT 'Itens do pedido de venda';


-- ============================================================
-- TABELA DE CONTROLE: Token Blacklist (JWT)
-- ============================================================

-- Tabela para armazenar tokens JWT revogados (logout)
-- Necessária para invalidar tokens entre múltiplos workers/processos
CREATE TABLE token_blacklist (
    jti VARCHAR(255) PRIMARY KEY COMMENT 'JWT ID (identificador único do token)',
    revoked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Data/hora da revogação',
    KEY idx_revoked_at (revoked_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT 'Tokens JWT revogados (logout) - persistência entre workers';


-- ============================================================
-- DADOS INICIAIS (Seed Data)
-- ============================================================

-- Inserir níveis de acesso padrão
INSERT INTO nivel_acesso (nome) VALUES
('admin'),
('funcionario'),
('cliente');

-- ============================================================
-- VIEWS ÚTEIS (Opcional - para facilitar consultas)
-- ============================================================

-- View: Usuários com seus dados completos (Cliente ou Funcionário)
CREATE OR REPLACE VIEW vw_usuarios_completos AS
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
CREATE OR REPLACE VIEW vw_produtos_lucro AS
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
CREATE OR REPLACE VIEW vw_vendas_por_cliente AS
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
CREATE OR REPLACE VIEW vw_compras_por_fornecedor AS
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
-- FIM DO SCRIPT
-- ============================================================
