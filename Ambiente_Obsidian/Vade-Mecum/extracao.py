import requests
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime
import logging
import time
from requests.exceptions import Timeout, ConnectionError

# Configurações
OBSIDIAN_VAULT_PATH = "/caminho/para/sua/vault/Obsidian/Vade-Mecum"
PLANALTO_URL = "http://www.planalto.gov.br/ccivil_03/LEIS/2002/L10406.htm"  
MAX_RESULTS_PER_PAGE = 5

# Configuração de Log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def sanitize_filename(title):
    """Remove caracteres inválidos para nomes de arquivos"""
    return re.sub(r'[\\/*?:"<>|]', "", title).strip()

def get_legislation_content(legislation_url):
    """Extrai o conteúdo da legislação da página do Planalto"""
    try:
        response = requests.get(legislation_url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        content_div = soup.find('div', {'class': 'texto-lei'})
        if not content_div:
            logging.warning(f"Conteúdo não encontrado em: {legislation_url}")
            return None

        content = ""
        for element in content_div.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'ul', 'ol']):
            if element.name == 'p':
                content += f"{element.get_text().strip()}\n\n"
            elif element.name.startswith('h'):
                level = int(element.name[1])
                content += f"{'#' * level} {element.get_text().strip()}\n\n"
            elif element.name in ['ul', 'ol']:
                for li in element.find_all('li', recursive=False):
                    prefix = "- " if element.name == 'ul' else "1. "
                    content += f"{prefix}{li.get_text().strip()}\n"
                content += "\n"

        return content.strip()

    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao extrair conteúdo de {legislation_url}: {e}")
        return None
    except Exception as e:
        logging.error(f"Erro inesperado ao extrair conteúdo de {legislation_url}: {e}")
        return None

def save_legislation_to_obsidian(title, content, category):
    """Salva a legislação como arquivo MD no Obsidian"""
    try:
        category_path = os.path.join(OBSIDIAN_VAULT_PATH, "Leis", category)
        os.makedirs(category_path, exist_ok=True)

        filename = sanitize_filename(title) + ".md"
        filepath = os.path.join(category_path, filename)

        if os.path.exists(filepath):
            logging.warning(f"Arquivo já existe: {filepath}")
            filename = sanitize_filename(title) + "_" + datetime.now().strftime('%Y%m%d%H%M%S') + ".md"
            filepath = os.path.join(category_path, filename)

        frontmatter = f"""---
alias: {title}
tags: [legislação, {category.lower().replace(' ', '-')}]
update: {datetime.now().strftime('%Y-%m-%d')}
---\n\n"""

        full_content = frontmatter + content

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)

        logging.info(f"Arquivo salvo: {filepath}")
        return True

    except Exception as e:
        logging.error(f"Erro ao salvar arquivo: {e}")
        return False

def search_legislation(search_term, category="Leis Ordinárias", max_retries=3, retry_delay=5):
    """Busca legislação no site do Planalto com retentativas."""
    for attempt in range(max_retries):
        try:
            search_url = f"{PLANALTO_URL}{requests.utils.quote(search_term)}"
            response = requests.get(search_url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            legislation_links = soup.select('div.search-results div.result-item a')

            if not legislation_links:
                logging.warning(f"Nenhum resultado encontrado para: {search_term}")
                return

            for link in legislation_links[:MAX_RESULTS_PER_PAGE]:
                legislation_url = "http://www.planalto.gov.br/ccivil_03/LEIS/2002/L10406.htm" + link['href']
                legislation_title = link.get_text().strip()

                logging.info(f"Processando: {legislation_title}")
                content = get_legislation_content(legislation_url)

                if content:
                    save_legislation_to_obsidian(legislation_title, content, category)
            return  # Sucesso, sai da função

        except (Timeout, ConnectionError, requests.exceptions.RequestException) as e:
            logging.error(f"Erro na busca (tentativa {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                logging.info(f"Tentando novamente em {retry_delay} segundos...")
                time.sleep(retry_delay)
            else:
                logging.error(f"Falha na busca após {max_retries} tentativas.")
                return
        except Exception as e:
            logging.error(f"Erro inesperado na busca: {e}")
            return

def update_existing_legislations():
    """Verifica atualizações nas legislações já baixadas"""
    # Implementar lógica para verificar alterações
    pass

if __name__ == "__main__":
    # Exemplo de uso
    search_legislation("lei de diretrizes e bases da educação", "Leis Ordinárias")
    search_legislation("código penal", "Códigos")