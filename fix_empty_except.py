#!/usr/bin/env python3
"""
Script para corrigir blocos except vazios nos DAOs
"""

import os
import re

# Diretórios dos DAOs
DAO_DIRS = ['dao_sqlite', 'dao_mysql']

def fix_empty_except_blocks(filepath):
    """Corrige blocos except vazios adicionando return None ou []"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    modified = False
    i = 0
    
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        
        # Detecta linha com "except Exception as e:"
        if re.match(r'^(\s+)except Exception as e:\s*$', line):
            indent = re.match(r'^(\s+)', line).group(1)
            
            # Verifica se a próxima linha está vazia ou é outra função/classe
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                
                # Se próxima linha não tem indentação adequada (bloco vazio)
                if not next_line.strip() or not next_line.startswith(indent + '    '):
                    # Adiciona return apropriado baseado no contexto
                    # Procura por "List[" no método para decidir return [] ou None
                    context = ''.join(lines[max(0, i-20):i])
                    
                    if 'List[' in context or 'listar' in context.lower():
                        new_lines.append(f'{indent}    return []\n')
                    elif 'bool' in context.lower() or 'verificar' in context.lower():
                        new_lines.append(f'{indent}    return False\n')
                    elif 'contar' in context.lower() or 'calcular' in context.lower():
                        new_lines.append(f'{indent}    return 0\n')
                    else:
                        new_lines.append(f'{indent}    return None\n')
                    
                    modified = True
        
        i += 1
    
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        return True
    return False

def main():
    """Processa todos os arquivos DAO"""
    count = 0
    
    for dao_dir in DAO_DIRS:
        if not os.path.exists(dao_dir):
            continue
            
        print(f"\n📁 Processando {dao_dir}/")
        
        for filename in os.listdir(dao_dir):
            if filename.endswith('_dao.py'):
                filepath = os.path.join(dao_dir, filename)
                if fix_empty_except_blocks(filepath):
                    print(f"  ✅ {filename}: blocos except corrigidos")
                    count += 1
                else:
                    print(f"  ⚪ {filename}: nenhum problema encontrado")
    
    print(f"\n📊 Total: {count} arquivo(s) corrigido(s)")

if __name__ == '__main__':
    main()
