"""
ProdutoService - Serviço de Produtos
Responsável pela lógica de negócio de produtos, incluindo validações e processamento de imagens.
"""

import os
import uuid
from PIL import Image

# Configuração de resoluções de imagem
IMAGE_RESOLUTIONS = {
    'thumbnail': (150, 150),
    'medium': (400, 400),
    'large': (800, 800)
}

# Verificar compatibilidade da versão do Pillow
try:
    RESAMPLE_FILTER = Image.Resampling.LANCZOS
except AttributeError:
    # Pillow < 10.0
    RESAMPLE_FILTER = Image.LANCZOS


class ProdutoService:
    """Serviço de produtos com validações e processamento de imagens"""
    
    @staticmethod
    def validar_preco(preco):
        """
        Valida o preço do produto.
        
        Args:
            preco: Preço a ser validado
        
        Returns:
            dict: {'valido': bool, 'mensagem': str, 'preco': float}
        """
        try:
            preco_float = float(preco)
            
            if preco_float < 0:
                return {
                    'valido': False,
                    'mensagem': 'Preço não pode ser negativo'
                }
            
            if preco_float > 999999.99:
                return {
                    'valido': False,
                    'mensagem': 'Preço muito alto (máximo: 999999.99)'
                }
            
            return {
                'valido': True,
                'mensagem': 'Preço válido',
                'preco': round(preco_float, 2)
            }
        
        except (ValueError, TypeError):
            return {
                'valido': False,
                'mensagem': 'Preço deve ser um número válido'
            }
    
    @staticmethod
    def validar_estoque(estoque):
        """
        Valida o estoque do produto.
        
        Args:
            estoque: Estoque a ser validado
        
        Returns:
            dict: {'valido': bool, 'mensagem': str, 'estoque': int}
        """
        try:
            estoque_int = int(estoque)
            
            if estoque_int < 0:
                return {
                    'valido': False,
                    'mensagem': 'Estoque não pode ser negativo'
                }
            
            if estoque_int > 999999:
                return {
                    'valido': False,
                    'mensagem': 'Estoque muito alto (máximo: 999999)'
                }
            
            return {
                'valido': True,
                'mensagem': 'Estoque válido',
                'estoque': estoque_int
            }
        
        except (ValueError, TypeError):
            return {
                'valido': False,
                'mensagem': 'Estoque deve ser um número inteiro válido'
            }
    
    @staticmethod
    def validar_nome(nome):
        """
        Valida o nome do produto.
        
        Args:
            nome (str): Nome do produto
        
        Returns:
            dict: {'valido': bool, 'mensagem': str}
        """
        if not nome or not isinstance(nome, str):
            return {'valido': False, 'mensagem': 'Nome é obrigatório'}
        
        nome = nome.strip()
        
        if len(nome) < 3:
            return {'valido': False, 'mensagem': 'Nome deve ter no mínimo 3 caracteres'}
        
        if len(nome) > 200:
            return {'valido': False, 'mensagem': 'Nome deve ter no máximo 200 caracteres'}
        
        return {'valido': True, 'mensagem': 'Nome válido'}
    
    @staticmethod
    def criar_produto(produto_dao, nome, preco, estoque, descricao=None, sku=None, imagem=None, request_host=None):
        """
        Cria um novo produto com validações e processamento de imagem.
        
        Args:
            produto_dao: Instância de ProdutoDAO
            nome (str): Nome do produto
            preco (float): Preço do produto
            estoque (int): Quantidade em estoque
            descricao (str, optional): Descrição do produto
            sku (str, optional): SKU do produto (gerado automaticamente se não fornecido)
            imagem (FileStorage, optional): Arquivo de imagem do produto
            request_host (str, optional): Host da requisição para URLs completas
        
        Returns:
            dict: {'success': True, 'produto': dict} ou {'success': False, 'message': str}
        """
        # Validar nome
        validacao_nome = ProdutoService.validar_nome(nome)
        if not validacao_nome['valido']:
            return {'success': False, 'message': validacao_nome['mensagem']}
        
        # Validar preço
        validacao_preco = ProdutoService.validar_preco(preco)
        if not validacao_preco['valido']:
            return {'success': False, 'message': validacao_preco['mensagem']}
        
        # Validar estoque
        validacao_estoque = ProdutoService.validar_estoque(estoque)
        if not validacao_estoque['valido']:
            return {'success': False, 'message': validacao_estoque['mensagem']}
        
        # Gerar SKU se não fornecido
        if not sku:
            sku = f"SKU-{uuid.uuid4().hex[:8].upper()}"
        
        # Criar produto sem imagem primeiro (para obter ID)
        produto_data = {
            'nome': nome.strip(),
            'descricao': descricao.strip() if descricao else '',
            'sku': sku,
            'preco_venda': validacao_preco['preco'],
            'preco_custo_medio': validacao_preco['preco'] * 0.7,  # Estimativa: 70% do preço de venda
            'estoque_atual': validacao_estoque['estoque'],
            'nome_imagem': None  # Será atualizado após processar imagem
        }
        
        produto_criado = produto_dao.criar_produto(produto_data)
        
        if not produto_criado:
            return {'success': False, 'message': 'Erro ao criar produto no banco de dados'}
        
        # Processar imagem se fornecida
        if imagem:
            resultado_imagem = ProdutoService.processar_e_salvar_imagem(
                imagem, 
                produto_criado['id_produto']
            )
            
            if resultado_imagem['success']:
                # Atualizar produto com nome da imagem
                produto_criado['nome_imagem'] = resultado_imagem['nome_imagem']
                
                # Atualizar no banco
                produto_dao.atualizar_produto(
                    produto_criado['id_produto'],
                    produto_criado['nome'],
                    produto_criado['descricao'],
                    produto_criado['sku'],
                    produto_criado['preco_venda'],
                    produto_criado['preco_custo_medio'],
                    produto_criado['estoque_atual'],
                    resultado_imagem['nome_imagem']
                )
                
                produto_criado = produto_dao.buscar_por_id(produto_criado['id_produto'])
        
        # Processar URLs de imagem com host da requisição
        produto_processado = ProdutoService.process_product_images(produto_criado, request_host)
        
        return {
            'success': True,
            'message': 'Produto criado com sucesso',
            'produto': produto_processado
        }
    
    @staticmethod
    def atualizar_produto(produto_dao, id_produto, request_host=None, **kwargs):
        """
        Atualiza um produto existente.
        
        Args:
            produto_dao: Instância de ProdutoDAO
            id_produto (int): ID do produto
            request_host (str, optional): Host da requisição para URLs completas
            **kwargs: Campos a serem atualizados
        
        Returns:
            dict: {'success': True, 'produto': dict} ou {'success': False, 'message': str}
        """
        try:
            # Buscar produto
            produto = produto_dao.buscar_por_id(id_produto)
            if not produto:
                return {'success': False, 'message': 'Produto não encontrado'}
            
            # Validar campos fornecidos
            if 'nome' in kwargs:
                validacao = ProdutoService.validar_nome(kwargs['nome'])
                if not validacao['valido']:
                    return {'success': False, 'message': validacao['mensagem']}
                kwargs['nome'] = kwargs['nome'].strip()
            
            if 'preco' in kwargs:
                validacao = ProdutoService.validar_preco(kwargs['preco'])
                if not validacao['valido']:
                    return {'success': False, 'message': validacao['mensagem']}
                kwargs['preco_venda'] = validacao['preco']
                del kwargs['preco']  # Remover 'preco' e usar 'preco_venda'
            
            if 'estoque' in kwargs:
                validacao = ProdutoService.validar_estoque(kwargs['estoque'])
                if not validacao['valido']:
                    return {'success': False, 'message': validacao['mensagem']}
                kwargs['estoque_atual'] = validacao['estoque']
                del kwargs['estoque']  # Remover 'estoque' e usar 'estoque_atual'
            
            if 'descricao' in kwargs and kwargs['descricao']:
                kwargs['descricao'] = kwargs['descricao'].strip()
            
            # Mesclar dados atuais com atualizações
            dados_atualizados = {**produto, **kwargs}
            
            # Atualizar produto com todos os campos obrigatórios do DAO
            produto_atualizado = produto_dao.atualizar_produto(
                id_produto,
                dados_atualizados['nome'],
                dados_atualizados.get('descricao', ''),
                dados_atualizados['sku'],
                dados_atualizados['preco_venda'],
                dados_atualizados.get('preco_custo_medio', 0),
                dados_atualizados['estoque_atual'],
                dados_atualizados.get('nome_imagem')
            )
            
            if not produto_atualizado:
                return {'success': False, 'message': 'Erro ao atualizar produto no banco de dados'}
            
            # Processar URLs de imagem com host da requisição
            produto_processado = ProdutoService.process_product_images(produto_atualizado, request_host)
            
            return {
                'success': True,
                'message': 'Produto atualizado com sucesso',
                'produto': produto_processado
            }
        except Exception as e:
            print(f"❌ Erro em atualizar_produto: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'message': f'Erro ao processar atualização: {str(e)}'}
    
    @staticmethod
    def processar_e_salvar_imagem(imagem_file, produto_id):
        """
        Processa e salva imagem em múltiplas resoluções.
        Padrão de nome: Produto_{id}_{uuid}_{resolução}.png
        
        Args:
            imagem_file (FileStorage): Arquivo de imagem do Flask
            produto_id (int): ID do produto
        
        Returns:
            dict: {'success': True, 'nome_imagem': str, 'paths': dict} ou {'success': False, 'message': str}
        """
        try:
            # Validar extensão do arquivo
            extensoes_permitidas = {'png', 'jpg', 'jpeg'}
            nome_arquivo = imagem_file.filename.lower()
            
            if not nome_arquivo or '.' not in nome_arquivo:
                return {'success': False, 'message': 'Nome de arquivo inválido'}
            
            extensao = nome_arquivo.rsplit('.', 1)[1]
            if extensao not in extensoes_permitidas:
                return {
                    'success': False, 
                    'message': f'Extensão não permitida. Use: {", ".join(extensoes_permitidas)}'
                }
            
            # Gerar UUID único para este conjunto de imagens
            unique_id = uuid.uuid4().hex[:8]
            
            # Diretório de destino
            from pathlib import Path
            base_dir = Path('static/images/produtos')
            base_dir.mkdir(parents=True, exist_ok=True)
            
            # Abrir imagem original
            imagem = Image.open(imagem_file.stream)
            
            # Converter para RGB se necessário (para salvar como PNG)
            if imagem.mode in ('RGBA', 'LA', 'P'):
                # Criar fundo branco
                background = Image.new('RGB', imagem.size, (255, 255, 255))
                if imagem.mode == 'P':
                    imagem = imagem.convert('RGBA')
                background.paste(imagem, mask=imagem.split()[-1] if imagem.mode == 'RGBA' else None)
                imagem = background
            elif imagem.mode != 'RGB':
                imagem = imagem.convert('RGB')
            
            # Salvar em múltiplas resoluções
            paths = {}
            
            # 1. Thumbnail (150x150)
            thumbnail = imagem.copy()
            thumbnail.thumbnail(IMAGE_RESOLUTIONS['thumbnail'], RESAMPLE_FILTER)
            thumbnail_name = f"Produto_{produto_id}_{unique_id}_thumbnail.png"
            thumbnail_path = base_dir / thumbnail_name
            thumbnail.save(thumbnail_path, 'PNG', optimize=True)
            paths['thumbnail'] = f"/static/images/produtos/{thumbnail_name}"
            
            # 2. Medium (400x400)
            medium = imagem.copy()
            medium.thumbnail(IMAGE_RESOLUTIONS['medium'], RESAMPLE_FILTER)
            medium_name = f"Produto_{produto_id}_{unique_id}_medium.png"
            medium_path = base_dir / medium_name
            medium.save(medium_path, 'PNG', optimize=True)
            paths['medium'] = f"/static/images/produtos/{medium_name}"
            
            # 3. Large (800x800)
            large = imagem.copy()
            large.thumbnail(IMAGE_RESOLUTIONS['large'], RESAMPLE_FILTER)
            large_name = f"Produto_{produto_id}_{unique_id}_large.png"
            large_path = base_dir / large_name
            large.save(large_path, 'PNG', optimize=True)
            paths['large'] = f"/static/images/produtos/{large_name}"
            
            # Nome base para armazenar no banco (sem resolução)
            nome_base = f"Produto_{produto_id}_{unique_id}"
            
            return {
                'success': True,
                'nome_imagem': nome_base,
                'paths': paths
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao processar imagem: {str(e)}'
            }
    
    @staticmethod
    def process_product_images(produto, request_host=None):
        """
        Processa URLs completas de imagens para um produto.
        
        Args:
            produto (dict): Dados do produto
            request_host (str, optional): Host da requisição (ex: http://localhost:5000)
        
        Returns:
            dict: Produto com URLs completas de imagens
        """
        # Usar host fornecido ou fallback para localhost
        if not request_host:
            request_host = 'http://localhost:5000'
        
        # Remover barra final se existir
        request_host = request_host.rstrip('/')
        
        produto_id = produto.get('id_produto')
        nome_imagem = produto.get('nome_imagem')
        
        # Se tem nome_imagem no banco, usar o padrão real
        if nome_imagem:
            produto['imagens'] = {
                'thumbnail': f"{request_host}/static/images/produtos/{nome_imagem}_thumbnail.png",
                'medium': f"{request_host}/static/images/produtos/{nome_imagem}_medium.png",
                'large': f"{request_host}/static/images/produtos/{nome_imagem}_large.png"
            }
        else:
            # Fallback: URLs genéricas (mantém compatibilidade com produtos antigos)
            produto['imagens'] = {
                'thumbnail': f"{request_host}/static/images/produtos/produto_{produto_id}_thumbnail.jpg",
                'medium': f"{request_host}/static/images/produtos/produto_{produto_id}_medium.jpg",
                'large': f"{request_host}/static/images/produtos/produto_{produto_id}_large.jpg"
            }
        
        return produto
    
    @staticmethod
    def salvar_imagem_produto(file, produto_id, upload_folder):
        """
        Salva e processa imagem de produto em múltiplas resoluções.
        
        Args:
            file: Arquivo de imagem (FileStorage)
            produto_id (int): ID do produto
            upload_folder (str): Pasta de upload
        
        Returns:
            dict: {'success': True, 'imagens': dict} ou {'success': False, 'message': str}
        """
        try:
            # Validar extensão
            extensoes_permitidas = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
            extensao = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
            
            if extensao not in extensoes_permitidas:
                return {
                    'success': False,
                    'message': f'Extensão inválida. Permitidas: {", ".join(extensoes_permitidas)}'
                }
            
            # Abrir imagem original
            imagem = Image.open(file.stream)
            
            # Converter RGBA para RGB se necessário
            if imagem.mode == 'RGBA':
                imagem = imagem.convert('RGB')
            
            imagens_salvas = {}
            
            # Salvar original
            nome_original = f'produto_{produto_id}_original.jpg'
            caminho_original = os.path.join(upload_folder, nome_original)
            imagem.save(caminho_original, 'JPEG', quality=95)
            imagens_salvas['original'] = nome_original
            
            # Salvar em múltiplas resoluções
            for resolucao_nome, dimensoes in IMAGE_RESOLUTIONS.items():
                imagem_redimensionada = imagem.copy()
                imagem_redimensionada.thumbnail(dimensoes, RESAMPLE_FILTER)
                
                nome_arquivo = f'produto_{produto_id}_{resolucao_nome}.jpg'
                caminho = os.path.join(upload_folder, nome_arquivo)
                imagem_redimensionada.save(caminho, 'JPEG', quality=85)
                
                imagens_salvas[resolucao_nome] = nome_arquivo
            
            return {
                'success': True,
                'message': 'Imagens salvas com sucesso',
                'imagens': imagens_salvas
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao processar imagem: {str(e)}'
            }
