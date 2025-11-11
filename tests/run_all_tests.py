#!/usr/bin/env python3
"""
Executor de Todos os Testes
Executa todos os módulos de teste e gera relatório consolidado
"""

import sys
sys.path.append('.')

import os
from datetime import datetime
from tests.utils import print_separador, print_sucesso, print_erro, print_info

# Importar módulos de teste
try:
    from tests.test_auth import run_all_auth_tests
    from tests.test_produtos import run_all_produto_tests
    from tests.test_fornecedores import run_all_fornecedor_tests
    from tests.test_pedidos_compra import run_all_pedido_compra_tests
    from tests.test_pedidos_venda import run_all_pedido_venda_tests
except ImportError as e:
    print_erro(f"Erro ao importar módulos de teste: {e}")
    sys.exit(1)


def recriar_banco():
    """Recria o banco de dados antes dos testes"""
    print_info("🔄 Recriando banco de dados...")
    
    try:
        # Importar e executar a função de limpeza diretamente
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from scripts.limpar_producao_sqlite import main as limpar_banco
        
        # Executar limpeza com confirmação automática
        limpar_banco(auto_confirm=True)
        
        print_sucesso("✅ Banco de dados recriado com sucesso\n")
        return True
    except Exception as e:
        print_erro(f"❌ Erro ao recriar banco: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Executa todos os testes"""
    print("\n" + "🧪"*35)
    print("   SUITE COMPLETA DE TESTES - API AutoPek")
    print(f"   {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("🧪"*35 + "\n")
    
    # Recriar banco de dados antes dos testes
    if not recriar_banco():
        print_erro("Não foi possível recriar o banco. Abortando testes.")
        return 1
    
    resultados = {}
    
    # Módulo 1: Autenticação
    print("\n" + "="*70)
    print("  MÓDULO 1: TESTES DE AUTENTICAÇÃO")
    print("="*70)
    resultados['auth'] = run_all_auth_tests()
    
    # Módulo 2: Produtos
    print("\n" + "="*70)
    print("  MÓDULO 2: TESTES DE PRODUTOS")
    print("="*70)
    resultados['produtos'] = run_all_produto_tests()
    
    # Módulo 3: Fornecedores
    print("\n" + "="*70)
    print("  MÓDULO 3: TESTES DE FORNECEDORES")
    print("="*70)
    resultados['fornecedores'] = run_all_fornecedor_tests()
    
    # Módulo 4: Pedidos de Compra
    print("\n" + "="*70)
    print("  MÓDULO 4: TESTES DE PEDIDOS DE COMPRA")
    print("="*70)
    resultados['pedidos_compra'] = run_all_pedido_compra_tests()
    
    # Módulo 5: Pedidos de Venda
    print("\n" + "="*70)
    print("  MÓDULO 5: TESTES DE PEDIDOS DE VENDA")
    print("="*70)
    resultados['pedidos_venda'] = run_all_pedido_venda_tests()
    
    # TODO: Adicionar mais módulos conforme necessário
    # resultados['clientes'] = run_all_cliente_tests()
    # resultados['funcionarios'] = run_all_funcionario_tests()
    
    # Relatório consolidado
    print("\n" + "="*70)
    print("  RELATÓRIO CONSOLIDADO FINAL")
    print("="*70)
    
    total_modulos = len(resultados)
    modulos_com_sucesso = sum(1 for v in resultados.values() if v)
    modulos_com_falha = total_modulos - modulos_com_sucesso
    
    print("\n📊 RESULTADOS POR MÓDULO:")
    print("─"*70)
    for modulo, sucesso in resultados.items():
        if sucesso:
            status = "✅ SATISFEITO"
            simbolo = "✓"
        else:
            status = "❌ FALHOU"
            simbolo = "✗"
        print(f"   [{simbolo}] {modulo.upper():.<50} {status}")
    
    print("\n" + "="*70)
    print("📈 RESUMO GERAL:")
    print("="*70)
    print(f"   Total de módulos testados: {total_modulos}")
    print(f"   ✅ Módulos satisfeitos: {modulos_com_sucesso}")
    print(f"   ❌ Módulos que falharam: {modulos_com_falha}")
    
    if total_modulos > 0:
        taxa_sucesso = (modulos_com_sucesso / total_modulos) * 100
        print(f"   📊 Taxa de sucesso: {taxa_sucesso:.1f}%")
    
    print("\n" + "="*70)
    if modulos_com_falha == 0:
        print("🎉 TODOS OS MÓDULOS DE TESTE FORAM SATISFEITOS COM SUCESSO! 🎉")
    else:
        print(f"⚠️  {modulos_com_falha} MÓDULO(S) FALHARAM - VERIFIQUE OS DETALHES ACIMA")
    print("="*70 + "\n")
    
    return 0 if modulos_com_falha == 0 else 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
