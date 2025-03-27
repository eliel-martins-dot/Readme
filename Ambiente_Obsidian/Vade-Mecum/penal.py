import requests
from bs4 import BeautifulSoup

def extrair_codigo_penal():
    url = "https://www.planalto.gov.br/ccivil_03/LEIS/1980-1988/L7209.htm#art1"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'  # Definir codificação correta
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Encontrar o conteúdo principal
        conteudo = soup.find('div', {'id': 'content'})
        
        if not conteudo:
            print("Não foi possível encontrar o conteúdo principal.")
            return None
        
        # Extrair título
        titulo = conteudo.find('h2').get_text(strip=True) if conteudo.find('h2') else "Título não encontrado"
        
        # Extrair ementa (se existir)
        ementa_tag = conteudo.find('div', class_='ementa')
        ementa = ementa_tag.get_text(strip=True) if ementa_tag else "Ementa não encontrada"
        
        # Extrair artigos
        artigos = []
        for artigo in conteudo.find_all('div', class_='article'):
            numero = artigo.find('p', class_='artigo').get_text(strip=True) if artigo.find('p', class_='artigo') else "Artigo sem número"
            
            # Extrair texto do artigo (removendo o número repetido)
            texto = artigo.get_text(strip=True).replace(numero, '', 1).strip()
            
            artigos.append({
                'numero': numero,
                'texto': texto
            })
        
        return {
            'titulo': titulo,
            'ementa': ementa,
            'artigos': artigos,
            'url': url
        }
        
    except Exception as e:
        print(f"Erro ao acessar o site: {e}")
        return None

# Testando a função
if __name__ == "__main__":
    dados = extrair_codigo_penal()
    
    if dados:
        print(f"\nTítulo: {dados['titulo']}")
        print(f"\nEmenta: {dados['ementa']}")
        print(f"\nTotal de artigos extraídos: {len(dados['artigos'])}")
        
        # Mostrar alguns exemplos
        for artigo in dados['artigos'][:3]:  # Primeiros 3 artigos
            print(f"\n{artigo['numero']}:")
            print(artigo['texto'][:200] + "...")  # Mostrar parte do texto
    else:
        print("Falha na extração dos dados.")