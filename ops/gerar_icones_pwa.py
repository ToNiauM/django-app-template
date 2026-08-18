#!/usr/bin/env python3
"""Gera os ícones placeholder da PWA (D-20) — roda no HOST, nunca no container.

O container de produção não tem (e não deve ganhar) Pillow: os PNGs são
binários gerados UMA vez e commitados (Assumption A2); a regeneração é um
passo documentado do nascimento de um sistema, não parte do build.

Os defaults abaixo (`#1e40af` / `SB`) espelham os defaults de
`COR_PRIMARIA` / `SISTEMA_SIGLA` do settings. Ao nascer um sistema novo,
rode com os valores do SEU `.env` — este é um item de substituição
documentado (D-20):

    python3 ops/gerar_icones_pwa.py "#0f766e" "OR"

Saída (em core/static/img/):
  - icon-192.png            192x192, quadrado chapado na cor + sigla branca
  - icon-512.png            512x512, mesmo desenho
  - icon-512-maskable.png   512x512, mesmo desenho com padding de 20%
                            (safe zone exigida por "purpose": "maskable")
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Raiz do repositório: o script vive em ops/, os ícones em core/static/img/.
RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "core" / "static" / "img"


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
    cor = sys.argv[1] if len(sys.argv) > 1 else "#1e40af"
    sigla = sys.argv[2] if len(sys.argv) > 2 else "SB"

    DESTINO.mkdir(parents=True, exist_ok=True)

    _desenhar(192, cor, sigla).save(DESTINO / "icon-192.png")
    _desenhar(512, cor, sigla).save(DESTINO / "icon-512.png")
    _desenhar(512, cor, sigla, padding_ratio=0.2).save(
        DESTINO / "icon-512-maskable.png"
    )

    print(f"Ícones gerados em {DESTINO} (cor={cor}, sigla={sigla})")


if __name__ == "__main__":
    main()
