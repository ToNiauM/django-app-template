#!/usr/bin/env python3
"""Gera os ícones placeholder da PWA (D-20) — roda no HOST, nunca no container.

O container de produção não tem (e não deve ganhar) Pillow: os PNGs são
binários gerados UMA vez e commitados (Assumption A2); a regeneração é um
passo documentado do nascimento de um sistema, não parte do build.

Sem argumentos, a cor e a sigla são lidas obrigatoriamente do `.env`. Os
dois argumentos posicionais são overrides úteis para uma execução pontual:

    python3 ops/gerar_icones_pwa.py "#0f766e" "SA"

Saída (em core/static/img/):
  - icon-192.png            192x192, quadrado chapado na cor + sigla branca
  - icon-512.png            512x512, mesmo desenho
  - icon-512-maskable.png   512x512, mesmo desenho com padding de 20%
                            (safe zone exigida por "purpose": "maskable")
"""

import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Raiz do repositório: o script vive em ops/, os ícones em core/static/img/.
RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "core" / "static" / "img"


def carregar_env(caminho: Path) -> dict[str, str]:
    """Lê pares simples do `.env` com a biblioteca padrão, sem defaults."""
    valores = dict(os.environ)
    if not caminho.is_file():
        return valores

    for linha in caminho.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, valor = linha.split("=", 1)
        chave, valor = chave.strip(), valor.strip().strip('"').strip("'")
        if chave and chave not in valores:
            valores[chave] = valor
    return valores


def valor_obrigatorio(valores: dict[str, str], chave: str) -> str:
    valor = valores.get(chave, "").strip()
    if not valor:
        raise SystemExit(f"{chave} é obrigatório no .env ou como argumento explícito.")
    return valor


def _desenhar(tamanho: int, cor: str, sigla: str, padding_ratio: float = 0.0) -> Image.Image:
    """Quadrado chapado na cor com a sigla centrada em branco.

    `padding_ratio` > 0 encolhe o desenho para dentro (variante maskable:
    o launcher pode recortar até 20% das bordas, então a sigla precisa
    caber na safe zone central).
    """
    imagem = Image.new("RGB", (tamanho, tamanho), cor)
    desenho = ImageDraw.Draw(imagem)

    # Área útil após o padding (na variante maskable, 20% de cada lado).
    util = tamanho * (1 - 2 * padding_ratio)

    # Fonte default do Pillow escalada — sem dependência de fontes do host
    # (portabilidade: o resultado é o mesmo em qualquer máquina).
    fonte = ImageFont.load_default(size=int(util * 0.42))

    # Centraliza pela caixa real do texto (anchor "mm" = middle/middle).
    desenho.text(
        (tamanho / 2, tamanho / 2),
        sigla,
        fill="#ffffff",
        font=fonte,
        anchor="mm",
    )
    return imagem


def main() -> None:
    valores = carregar_env(RAIZ / ".env")
    cor = sys.argv[1] if len(sys.argv) > 1 else valor_obrigatorio(valores, "COR_PRIMARIA")
    sigla = sys.argv[2] if len(sys.argv) > 2 else valor_obrigatorio(valores, "SISTEMA_SIGLA")

    DESTINO.mkdir(parents=True, exist_ok=True)

    _desenhar(192, cor, sigla).save(DESTINO / "icon-192.png")
    _desenhar(512, cor, sigla).save(DESTINO / "icon-512.png")
    _desenhar(512, cor, sigla, padding_ratio=0.2).save(
        DESTINO / "icon-512-maskable.png"
    )

    print(f"Ícones gerados em {DESTINO} (cor={cor}, sigla={sigla})")


if __name__ == "__main__":
    main()
