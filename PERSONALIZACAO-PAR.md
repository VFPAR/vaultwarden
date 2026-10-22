# VF Guard — personalização e deploy

Este fork do [Vaultwarden](https://github.com/dani-garcia/vaultwarden) foi personalizado com a identidade visual da **PAR Participações**.

## O que foi personalizado

| Área | Onde | O que mudou |
|---|---|---|
| Imagens da marca | `branding/source/` → `branding/generate.py` | Logos e ícones originais; o script gera todas as variações |
| Imagens do servidor | `src/static/images/` | Logo dos e-mails, ícone do painel admin, favicon, imagem 404 |
| Web vault (interface) | `src/static/templates/scss/user.vaultwarden.scss.hbs` | Paleta azul PAR, logo no login e na barra lateral, aviso de não compartilhamento de senhas |
| Web vault (arquivos) | `branding/web-vault/` + Dockerfiles | Favicons, ícones do app, título "VF Guard" |
| Web vault (textos) | `branding/rebrand-web-vault.sh` | Troca "Bitwarden" por "VF Guard" nos textos (pt-BR e inglês), mantendo nomes de produtos como extensão, apps, Authenticator e Send |
| E-mails | `src/static/templates/email/` | Todos em português formal, com saudação, assinatura da equipe de TI e aviso de segurança |
| Painel admin e 404 | `src/static/templates/admin/`, `404.hbs` | Marca PAR, navegação e login em português |
| Padrões | `src/config.rs` | `INVITATION_ORG_NAME` = "PAR Participações", `SMTP_FROM_NAME` = "VF Guard" |

### Trocar o logo ou as cores no futuro

1. Substitua `branding/source/par-logo.png` (logo horizontal) e/ou `branding/source/par-icon.png` (ícone quadrado).
2. Rode `pip install pillow` e depois `python branding/generate.py`.
3. As cores do web vault ficam no topo de `src/static/templates/scss/user.vaultwarden.scss.hbs`; as dos e-mails estão em `email_footer.hbs` e nos botões dos templates (`#1d469b`).
4. Faça commit e publique de novo no Easypanel.

---

## Deploy no Easypanel

### 1. Criar o serviço

1. No projeto do Easypanel: **+ Service → App**, nome sugerido: `cofre`.
2. **Source → GitHub**: selecione este fork e a branch `main`.
3. **Build → Dockerfile**, com o caminho **`docker/Dockerfile.debian`**.
   - O build compila o servidor em Rust. Leva de 15 a 30 minutos e precisa de cerca de **4 GB de RAM** livres no servidor. Se a VPS tiver pouca memória, adicione swap antes do primeiro build.

### 2. Volume (obrigatório)

Em **Mounts → Add Volume**:

| Nome | Mount path |
|---|---|
| `data` | `/data` |

É nele que ficam o banco SQLite, os anexos e as chaves. **Sem ele, tudo se perde a cada deploy.**

### 3. Domínio

Em **Domains**: adicione `cofre.suaempresa.com.br` (exemplo) apontando para a **porta 80** do container e com HTTPS ativado. O Easypanel emite o certificado sozinho.

> O Vaultwarden exige HTTPS: o web vault não funciona em HTTP puro.

### 4. Variáveis de ambiente

Em **Environment**, cole o conteúdo abaixo e ajuste os valores:

```env
DOMAIN=https://cofre.suaempresa.com.br

# Cadastro: apenas por convite
SIGNUPS_ALLOWED=false
INVITATIONS_ALLOWED=true
SIGNUPS_VERIFY=true
# Opcional: libera cadastro livre só para e-mails do domínio da empresa
# SIGNUPS_DOMAINS_WHITELIST=suaempresa.com.br

# Painel administrativo (/admin). Gere o hash com:
#   docker run --rm -it vaultwarden/server /vaultwarden hash
ADMIN_TOKEN='$argon2id$v=19$m=65540,t=3,p=4$...'

# Segurança
PASSWORD_HINTS_ALLOWED=false
SHOW_PASSWORD_HINT=false
EMERGENCY_ACCESS_ALLOWED=false
SENDS_ALLOWED=true
ORG_CREATION_USERS=ti@suaempresa.com.br
LOGIN_RATELIMIT_MAX_BURST=5
ADMIN_RATELIMIT_MAX_BURST=3

# E-mail (SMTP)
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_SECURITY=starttls
SMTP_FROM=cofre@suaempresa.com.br
SMTP_USERNAME=cofre@suaempresa.com.br
SMTP_PASSWORD=troque-aqui

# Fuso horário dos e-mails e logs
TZ=America/Sao_Paulo
```

Observações:
- **`ADMIN_TOKEN`**: o hash Argon2 contém `$`. Mantenha o valor entre aspas simples. Se o painel admin recusar a senha, confira se o Easypanel não removeu os `$`.
- `SMTP_FROM_NAME` e `INVITATION_ORG_NAME` já vêm com os nomes da PAR. Só defina essas variáveis se quiser outro texto.
- Para usar PostgreSQL em vez de SQLite, crie um serviço Postgres no Easypanel e defina `DATABASE_URL=postgresql://usuario:senha@host:5432/vaultwarden`.

### 5. Deploy

Clique em **Deploy** e acompanhe os logs do build. Ao terminar:
1. Acesse `https://cofre.suaempresa.com.br/admin`, entre com a senha do `ADMIN_TOKEN` e envie um e-mail de teste em **Configurações → SMTP Email Settings → Send test email**.
2. Convide os usuários em **Usuários → Invite User**.

### 6. Backup

Faça backup periódico do volume `/data`. Ele contém `db.sqlite3`, `attachments/`, `sends/` e `rsa_key*`. Ver: [Backing up your vault](https://github.com/dani-garcia/vaultwarden/wiki/Backing-up-your-vault).

---

## Manter o fork atualizado

```bash
git remote add upstream https://github.com/dani-garcia/vaultwarden.git   # só na primeira vez
git fetch upstream
git merge upstream/main
```

Os conflitos, quando houver, ficam quase sempre nos arquivos da tabela acima. Na dúvida, mantenha a versão da PAR (textos e imagens) e aceite a do projeto original no restante. Se o projeto original criar um template de e-mail novo, ele chegará em inglês e precisará ser traduzido.
