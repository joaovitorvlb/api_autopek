"""
Script de teste para verificar se todas as rotas foram registradas corretamente
"""

import sys
sys.path.insert(0, '/home/joaovitor/Documents/faculdade/semestre_8/banco_de_dados/api_autopek')

from app import create_app

def testar_rotas():
    """Testa se todas as rotas foram registradas"""
    app = create_app()
    
    print("=" * 60)
    print("ROTAS REGISTRADAS NA API")
    print("=" * 60)
    
    # Agrupar rotas por blueprint
    rotas_por_blueprint = {}
    
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            blueprint = rule.endpoint.split('.')[0] if '.' in rule.endpoint else 'root'
            
            if blueprint not in rotas_por_blueprint:
                rotas_por_blueprint[blueprint] = []
            
            metodos = ', '.join([m for m in rule.methods if m not in ['HEAD', 'OPTIONS']])
            rotas_por_blueprint[blueprint].append({
                'rota': str(rule),
                'metodos': metodos,
                'endpoint': rule.endpoint
            })
    
    # Exibir rotas organizadas
    for blueprint, rotas in sorted(rotas_por_blueprint.items()):
        print(f"\n📦 Blueprint: {blueprint}")
        print("-" * 60)
        for rota in sorted(rotas, key=lambda x: x['rota']):
            print(f"  [{rota['metodos']}] {rota['rota']}")
    
    print("\n" + "=" * 60)
    print(f"Total de rotas: {sum(len(r) for r in rotas_por_blueprint.values())}")
    print("=" * 60)
    
    # Verificar se novos blueprints foram registrados
    blueprints_esperados = [
        'auth', 'cliente', 'funcionario', 'produto',
        'fornecedor', 'pedido_compra', 'pedido_venda'
    ]
    
    blueprints_registrados = list(rotas_por_blueprint.keys())
    
    print("\n✅ VERIFICAÇÃO DE BLUEPRINTS:")
    for bp in blueprints_esperados:
        if bp in blueprints_registrados:
            print(f"  ✓ {bp}")
        else:
            print(f"  ✗ {bp} (NÃO REGISTRADO)")
    
    print("\n")

if __name__ == '__main__':
    testar_rotas()
