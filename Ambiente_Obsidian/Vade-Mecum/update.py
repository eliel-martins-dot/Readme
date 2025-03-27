def check_for_updates():
    """Verifica se há alterações nas leis já baixadas"""
    # Carregar o último estado conhecido
    try:
        with open(os.path.join(OBSIDIAN_VAULT_PATH, 'Atualizações', 'last_known.json'), 'r') as f:
            last_known = json.load(f)
    except:
        last_known = {}
    
    # Verificar cada lei
    for law_path, last_hash in last_known.items():
        current_content = open(law_path, 'r', encoding='utf-8').read()
        current_hash = hash(current_content)
        
        if current_hash != last_hash:
            print(f"Lei alterada: {law_path}")
            # Processar alterações e criar notas de atualização
    
    # Salvar novo estado
    with open(os.path.join(OBSIDIAN_VAULT_PATH, 'Atualizações', 'last_known.json'), 'w') as f:
        json.dump(updated_last_known, f)