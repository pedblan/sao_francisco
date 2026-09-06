"""Read-only inventory of QML strings; never includes user data or provider prompts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LITERAL = re.compile(r'"(?:\\.|[^"\\])*"')
KEEP_WORDS = {
    "Transcrever", "Sobre", "Ajuda", "Arquivo", "Sair", "Janela", "Ir", "Abrir",
    "Retomar", "Atualizar", "Cancelar", "Fechar", "Verificar", "Salvar", "Fonte",
    "Modelo", "Provedor", "Arquivos", "Original", "Idioma", "Detalhes", "Pausada",
    "Concluída", "Falhou", "Cancelada", "Iniciar", "Minimizar", "Copiar",
}


def human_text(value: str) -> bool:
    if not value or value.startswith(("http", "file:", "../", "./")):
        return False
    if value in {"São Francisco", "Pedro Duarte Blanco", "Source Sans 3", "Jost",
                 "Google Gemini", "OpenAI", "Gemini", "App", "NFD", "DOCX", "TXT",
                 "SRT", "VTT"} or value.startswith("Ctrl+"):
        return False
    if not re.search(r"[A-Za-zÀ-ÿ]", value) or re.fullmatch(r"#[0-9A-Fa-f]+", value):
        return False
    return bool(re.search(r"[À-ÿ]", value) or " " in value
                or value in KEEP_WORDS or value[0].isupper())


def qml_inventory() -> list[str]:
    values: set[str] = set()
    for path in (ROOT / "sao_francisco/qml").rglob("*.qml"):
        for line in path.read_text().splitlines():
            if line.lstrip().startswith(("//", "import ")):
                continue
            for match in LITERAL.finditer(line):
                value = json.loads(match.group())
                if human_text(value):
                    values.add(value)
    return sorted(values)


def markdown_inventory() -> str:
    sections = [
        "# Textos da GUI atual — São Francisco\n",
        "Catálogo editorial da interface implementada em 29/08/2026. Inglês é o padrão; "
        "português é a chave editorial. Edite os blocos PT/EN mantendo IDs e placeholders. "
        "Este arquivo é uma cópia para revisão humana: alterações serão incorporadas ao "
        "código e aos demais idiomas em uma próxima tarefa, não importadas automaticamente.\n",
        "Não inclui propostas futuras de fila, paralelismo ou App Store. IDs são derivados "
        "do texto-fonte. Nomes de modelos, marca, URLs, atalhos, formatos e conteúdo do "
        "usuário não são traduzidos automaticamente. Licenças integrais permanecem em "
        "[licenses](sao_francisco/licenses/).\n",
    ]
    root = ROOT / "sao_francisco/translations"
    for path in sorted(root.glob("*.json")):
        sections.append(f"## {path.stem}\n\nFonte: [{path.name}]({path.relative_to(ROOT)})\n")
        for source, translations in json.loads(path.read_text()).items():
            key = hashlib.sha256(source.encode()).hexdigest()[:12]
            sections.append(f"### GUI-{key}\n\nPT:\n\n```text\n{source}\n```\n"
                            f"\nEN:\n\n```text\n{translations[0]}\n```\n")
    sections.append("## Ajuda integral\n\nEdite os arquivos Markdown diretamente. "
                    "Todos os onze tópicos fazem parte da GUI.\n")
    for locale in ("pt-BR", "en-US", "fr-FR", "es-ES", "de-DE", "it-IT", "ru-RU", "zh-CN", "ar"):
        path = (ROOT / "sao_francisco/AJUDA.md" if locale == "pt-BR"
                else root / "help" / f"{locale}.md")
        sections.append(f"- [{locale}]({path.relative_to(ROOT)})")
    sections.append("\n### Texto da Ajuda em português\n\n```markdown\n"
                    + (ROOT / "sao_francisco/AJUDA.md").read_text().rstrip() + "\n```\n")
    sections.append("### Texto da Ajuda em inglês\n\n```markdown\n"
                    + (root / "help/en-US.md").read_text().rstrip() + "\n```\n")
    return "\n".join(sections)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--markdown", action="store_true")
    args = parser.parse_args()
    if args.markdown:
        print(markdown_inventory())
    else:
        for index, value in enumerate(qml_inventory(), 1):
            print(f"{index}: {json.dumps(value, ensure_ascii=False)}")
