# MiauLink 🐾

Encurtador de URLs temático de gatos, feito com Python + Flask!

## Funcionalidades
- Encurta qualquer URL de forma simples e rápida
- Visual moderno, responsivo e com mascote de gato
- Dark mode e light mode
- Histórico dos últimos links encurtados
- Estatísticas de acesso para cada link
- Preview do destino antes do redirecionamento
- Geração de QR Code para cada link
- Proteção contra flood (rate limit por IP)
- Validação de URL (só aceita links válidos)
- Bloqueio de preview para IPs internos (protege contra SSRF)
- Escrita atômica do arquivo de dados (evita corrupção)

## Como rodar localmente
1. **Pré-requisitos:**
   - Python 3.8+
   - Instale as dependências:
     ```
     pip install flask flask-limiter validators qrcode[pil] requests beautifulsoup4
     ```
2. **Execute o app:**
   ```
   python app.py
   ```
3. **Acesse:**
   - No seu computador: http://127.0.0.1:5000
   - Em outros dispositivos da rede: http://<seu-ip-local>:5000

## Estrutura do Projeto
- `app.py` — Backend Flask e lógica principal
- `static/style.css` — Visual e responsividade
- `static/gatoprinci.png` — Mascote principal
- `static/iconnovo.png` — Favicon e ícone do site
- `urls.json` — Banco de dados simples dos links

## Segurança
- Validação de URL e bloqueio de links maliciosos
- Rate limit para evitar spam
- Preview protegido contra SSRF
- Arquivo de dados salvo de forma segura

## Produção
- Para publicar, use um servidor WSGI (ex: gunicorn, waitress) atrás de um proxy reverso (Nginx, etc)
- Recomenda-se usar HTTPS para remover o aviso "Não seguro"

## Licença
MIT

---
Feito com carinho e muitos miaus por [Seu Nome].
