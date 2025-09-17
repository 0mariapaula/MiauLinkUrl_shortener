# =============================================
# MiauLink - Encurtador de URL temático de gatos
# Desenvolvido por Maria Paula Ferreira Lins
# Contato: 82 981274764
# =============================================


import io
import qrcode
import json
import os
import string
import random
import validators
from flask import send_file
from flask import Flask, request, redirect, render_template_string
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


def gerar_codigo(tamanho=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=tamanho))

def carregar_urls():
    if not os.path.exists("urls.json"):
        return {}
    with open("urls.json", "r") as f:
        conteudo = f.read().strip()
        if not conteudo:
            return {}
        data = json.loads(conteudo)
        # Suporte retroativo: se o valor for string, converte para dict
        for k, v in list(data.items()):
            if isinstance(v, str):
                data[k] = {"url": v, "acessos": 0}
        return data

def salvar_urls(urls):
    import tempfile
    import shutil
    temp_fd, temp_path = tempfile.mkstemp(dir=".", prefix="urls_", suffix=".tmp")
    try:
        with os.fdopen(temp_fd, "w") as f:
            json.dump(urls, f, indent=4)
        shutil.move(temp_path, "urls.json")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

# Função para encurtar URL
def encurtar_url(url):
    urls = carregar_urls()
    for cod, info in urls.items():
        if info["url"] == url:
            return cod
    codigo = gerar_codigo()
    while codigo in urls:
        codigo = gerar_codigo()
    urls[codigo] = {"url": url, "acessos": 0}
    salvar_urls(urls)
    return codigo

# Função para recuperar URL original
def recuperar_url(codigo):
    urls = carregar_urls()
    info = urls.get(codigo)
    if info:
        return info["url"]
    return None


app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app, default_limits=["100 per hour"])

# Rota para verificação do Google Search Console
from flask import send_from_directory

@app.route('/google6af16fcaec3b096b.html')
def google_verify():
    return send_from_directory('static', 'google6af16fcaec3b096b.html')

# Rota para servir sitemap.xml na raiz
@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory('static', 'sitemap.xml')

# Rota para gerar QR Code
@app.route('/qr')
def qr_code():
    url = request.args.get('url')
    if not url:
        return '', 404
    img = qrcode.make(url)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

HTML_FORM = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MiauLink - Encurtador de URL</title>
    <link rel="icon" type="image/png" href="/static/iconnovo.png">
    <link rel="stylesheet" href="/static/style.css">
    <script>
    // Dark mode toggle
    function toggleDark() {
        document.body.classList.toggle('dark');
        localStorage.setItem('darkMode', document.body.classList.contains('dark'));
    }
    window.onload = function() {
        if(localStorage.getItem('darkMode') === 'true') {
            document.body.classList.add('dark');
        }
    }
    </script>
</head>
<body>
    <div class="miaulink-topbar"></div>
    <div class="miaulink-mascote-wrapper">
        <img src="/static/gatoprinci.png" alt="Logo MiauLink" class="miaulink-mascote">
    </div>
    <div class="container">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <h1 style="display:flex;align-items:center;gap:0.5rem;">
                <img src="/static/iconnovo.png" alt="MiauLink" style="height:2.2rem;vertical-align:middle;">
                <span>MiauLink</span>
            </h1>
            <button onclick="toggleDark()" style="margin-left:1rem;font-size:1.1rem;">🌙</button>
        </div>
        <form method="post">
            <input type="text" name="url" placeholder="Cole sua URL aqui" required>
            <button type="submit">Encurtar</button>
        </form>
        {% if erro %}
            <div class="msg-erro fade-in">{{ erro }}</div>
        {% endif %}
        {% if short_url %}
            <div class="msg-sucesso fade-in">
                URL encurtada: <a href="{{ short_url }}" target="_blank">{{ short_url }}</a>
                <br><br>
                <img src="/qr?url={{ short_url }}" alt="QR Code" style="margin-top:0.5rem;max-width:120px;">
                <div style="font-size:0.9rem;margin-top:0.3rem;">Escaneie para acessar</div>
            </div>
        {% endif %}
 
        {% if historico %}
        <div style="margin-top:2rem;text-align:left;">
            <h2 style="font-size:1.1rem;">Últimos links encurtados</h2>
            <table style="width:100%;background:rgba(255,255,255,0.1);color:#fff;border-radius:8px;">
                <tr><th>Código</th><th>URL</th></tr>
                {% for cod, info in historico %}
                <tr>
                    <td><a href="/{{ cod }}" style="color:#ffb347;">{{ cod }}</a></td>
                    <td style="word-break:break-all;">{{ info['url'] }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        {% endif %}
    </div>
    <footer style="margin-top:2rem;text-align:center;font-size:0.95rem;opacity:0.8;">
        Desenvolvido por Maria Paula Ferreira Lins | Contato: 82 981274764
    </footer>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
@limiter.limit("10/minute")
def index():
    short_url = None
    erro = None
    if request.method == 'POST':
        url = request.form['url'].strip()
        if not (url.startswith('http://') or url.startswith('https://')) or not validators.url(url):
            erro = 'Por favor, insira uma URL válida começando com http:// ou https://'
        else:
            codigo = encurtar_url(url)
            # Detecta IP local para gerar QR Code acessível na rede
            import socket
            hostname = socket.gethostname()
            try:
                ip_local = socket.gethostbyname(hostname)
                if ip_local.startswith('127.'):
                    # Tenta pegar IP de rede se não for válido
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    try:
                        s.connect(('8.8.8.8', 80))
                        ip_local = s.getsockname()[0]
                    except Exception:
                        pass
                    finally:
                        s.close()
            except Exception:
                ip_local = '127.0.0.1'
            short_url = f'http://{ip_local}:5000/{codigo}'
    # Pega os últimos 5 links encurtados
    urls = carregar_urls()
    historico = list(urls.items())[-5:][::-1]  # últimos 5, mais recentes primeiro
    return render_template_string(HTML_FORM, short_url=short_url, historico=historico, erro=erro)

# Preview antes do redirecionamento
import requests
from bs4 import BeautifulSoup

@app.route('/<codigo>')
def redirecionar(codigo):
    urls = carregar_urls()
    info = urls.get(codigo)
    if info:
        url_destino = info["url"]
        # Bloqueia preview de IPs internos (SSRF)
        from urllib.parse import urlparse
        import ipaddress
        parsed = urlparse(url_destino)
        host = parsed.hostname
        try:
            ip = ipaddress.ip_address(host) if ipaddress.ip_address(host) else None
        except Exception:
            import socket
            try:
                ip = ipaddress.ip_address(socket.gethostbyname(host))
            except Exception:
                ip = None
        if ip and (ip.is_private or ip.is_loopback):
            return '<h2>Preview bloqueado por segurança (IP privado/local).</h2>', 403
        # Tenta obter título da página de destino
        titulo = url_destino
        try:
            resp = requests.get(url_destino, timeout=2)
            soup = BeautifulSoup(resp.text, 'html.parser')
            titulo = soup.title.string.strip() if soup.title and soup.title.string else url_destino
        except Exception:
            pass
        # Mostra preview antes de redirecionar
        html = f'''
        <html><head><title>Preview do Destino</title><link rel="stylesheet" href="/static/style.css"></head><body>
        <div class="container">
        <h1>Preview do Destino</h1>
        <p><b>Título:</b> {titulo}</p>
        <p><b>URL:</b> <a href="{url_destino}" target="_blank">{url_destino}</a></p>
        <form method="post" action="/{codigo}/go">
            <button type="submit">Prosseguir para o site</button>
        </form>
        <a href="/" style="display:inline-block;margin-top:1.5rem;color:#ffb347;">Voltar</a>
        </div>
        <footer style="margin-top:2rem;text-align:center;font-size:0.95rem;opacity:0.8;">
            Desenvolvido por Maria Paula Ferreira Lins | Contato: 82 981274764
        </footer>
        </body></html>
        '''
        return html
    html = '''
    <html><head><title>404 - Não encontrado</title><link rel="stylesheet" href="/static/style.css"></head><body>
    <div class="container" style="text-align:center;">
        <h1 style="font-size:3rem;">404</h1>
        <div style="font-size:2rem;margin-bottom:1rem;">Código não encontrado!</div>
        <div style="font-size:1.2rem;">Oops! O link que você tentou acessar não existe ou já expirou.<br>Que tal encurtar uma nova URL?</div>
        <div style="font-size:4rem;margin:1.5rem 0;">🤔🔗</div>
        <a href="/" style="color:#ffb347;font-size:1.1rem;">Voltar para a página inicial</a>
    </div>
    <footer style="margin-top:2rem;text-align:center;font-size:0.95rem;opacity:0.8;">
        Desenvolvido por Maria Paula Ferreira Lins | Contato: 82 981274764
    </footer>
    </body></html>
    '''
    return html, 404

# Rota para efetuar o redirecionamento após preview
@app.route('/<codigo>/go', methods=['POST'])
def go_redirect(codigo):
    urls = carregar_urls()
    info = urls.get(codigo)
    if info:
        info["acessos"] += 1
        salvar_urls(urls)
        return redirect(info["url"])
    return '<h2>Código não encontrado!</h2>', 404
# Nova rota para estatísticas
@app.route('/stats')
def stats():
    urls = carregar_urls()
    html = '''
    <html><head><title>Estatísticas</title><link rel="stylesheet" href="/static/style.css"></head><body>
    <div class="container">
    <h1>Estatísticas de Acesso</h1>
    <table style="width:100%;background:rgba(255,255,255,0.1);color:#fff;border-radius:8px;">
        <tr><th>Código</th><th>URL</th><th>Acessos</th></tr>
        {% for cod, info in urls.items() %}
        <tr>
            <td><a href="/{{ cod }}" style="color:#ffb347;">{{ cod }}</a></td>
            <td style="word-break:break-all;">{{ info['url'] }}</td>
            <td style="text-align:center;">{{ info['acessos'] }}</td>
        </tr>
        {% endfor %}
    </table>
    <a href="/" style="display:inline-block;margin-top:1.5rem;color:#ffb347;">Voltar</a>
    </div>
    <footer style="margin-top:2rem;text-align:center;font-size:0.95rem;opacity:0.8;">
        Desenvolvido por Maria Paula Ferreira Lins | Contato: 82 981274764
    </footer>
    </body></html>
    '''
    from flask import render_template_string
    return render_template_string(html, urls=urls)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
