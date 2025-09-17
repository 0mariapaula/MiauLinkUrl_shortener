import json
import random
import string

def gerar_codigo(tamanho=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=tamanho))

def carregar_urls():
    try:
        with open("urls.json", "r") as f:
            conteudo = f.read().strip()
            if not conteudo:  
                return {}
            return json.loads(conteudo)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def salvar_urls(urls):
    with open("urls.json", "w") as f:
        json.dump(urls, f, indent=4)

def encurtar_url(url):
    urls = carregar_urls()
    for cod, original in urls.items():
        if original == url:
            return cod
    codigo = gerar_codigo()
    while codigo in urls:
        codigo = gerar_codigo()
    urls[codigo] = url
    salvar_urls(urls)
    return codigo

def recuperar_url(codigo):
    urls = carregar_urls()
    return urls.get(codigo, "Código não encontrado!")

if __name__ == "__main__":
    print("===== ENCURTADOR DE URL =====")
    escolha = input("Digite '1' para encurtar ou '2' para recuperar URL: ")

    if escolha == '1':
        url_longa = input("Digite a URL: ")
        codigo = encurtar_url(url_longa)
        print(f"URL encurtada: http://meusite.com/{codigo}")
    elif escolha == '2':
        codigo_input = input("Digite o código para recuperar a URL: ")
        print(f"URL original: {recuperar_url(codigo_input)}")
    else:
        print("Opção inválida!!")
