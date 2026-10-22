#!/bin/sh
# Aplica o nome "VF Guard" aos textos do web vault durante o build Docker.
# Uso: sh rebrand-web-vault.sh /web-vault
#
# Nomes de produtos reais do Bitwarden (extensão de navegador, apps, Authenticator,
# Send, Gerenciador de Segredos, CLI etc.) e avisos legais são mantidos, pois o
# usuário precisa reconhecê-los para baixar ou usar essas ferramentas.
set -e

WEB_VAULT="${1:-/web-vault}"
KEEP="__BW_KEEP__"

# Título, manifesto e textos fixos do aplicativo
sed -i 's/Vaultwarden Web/VF Guard/g; s/#175DDC/#1D469B/g' \
    "${WEB_VAULT}/index.html" "${WEB_VAULT}/manifest.json" "${WEB_VAULT}"/app/main.*.js

for lang in pt_BR en; do
    file="${WEB_VAULT}/locales/${lang}/messages.json"
    [ -f "${file}" ] || continue
    sed -i -E \
        -e "/\"message\":/s/Bitwarden(®|&reg;)/${KEEP}\1/g" \
        -e "/\"message\":/s/Bitwarden( Authenticator| Gerenciador| Famílias| Familías| Send| CLI| Secrets| Password Manager| Families| Inc|, Inc)/${KEEP}\1/g" \
        -e "/\"message\":/s/(Plano Famílias|Extensão|extensão|Extensões|extensões|Aplicativo|aplicativo|Aplicativos|aplicativos|Diretório|app|apps|navegador|móvel|desktop|nuvem|API|pública|produtos|Segredos|servidores|servidor) (do |da )?Bitwarden/\1 \2${KEEP}/g" \
        -e "/\"message\":/s/Bitwarden (extension|extensions|app|apps|mobile|desktop|browser|cloud|API|products|server|servers)/${KEEP} \1/g" \
        -e "/\"message\":/s/Bitwarden/VF Guard/g" \
        -e "/\"message\":/s/${KEEP}/Bitwarden/g" \
        "${file}"
done
