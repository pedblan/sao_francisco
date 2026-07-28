#!/usr/bin/env bash
set -euo pipefail

echo "O São Francisco precisa de FFmpeg/FFprobe."
echo "Deno é recomendado para ampliar a compatibilidade do yt-dlp com o YouTube."
read -r -p "Instalar as dependências disponíveis neste sistema? [s/N] " answer

case "$answer" in
    [sSyY]*) ;;
    *) echo "Instalação cancelada."; exit 0 ;;
esac

if command -v brew >/dev/null 2>&1; then
    brew install ffmpeg deno
elif command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y ffmpeg
    echo
    echo "FFmpeg instalado."
    echo "Instale o Deno pelas instruções oficiais:"
    echo "https://docs.deno.com/runtime/getting_started/installation/"
elif command -v winget >/dev/null 2>&1; then
    winget install --exact --id Gyan.FFmpeg
    winget install --exact --id DenoLand.Deno
else
    echo "Nenhum gerenciador compatível foi encontrado." >&2
    echo "Instale FFmpeg, FFprobe e, para URLs, Deno manualmente." >&2
    exit 1
fi

echo "Dependências do sistema verificadas."
