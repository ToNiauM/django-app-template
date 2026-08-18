FROM node:20-alpine AS assets

WORKDIR /build
COPY tailwind.config.js ./
COPY core/static/src/input.css ./core/static/src/input.css
# Os `content` globs do tailwind.config.js apontam para os templates. Sem eles
# presentes aqui, o JIT varre zero arquivos, não encontra nenhuma classe em uso
# e emite só o preflight (~4,7 KB) — a página sai sem estilo nenhum e o build
# não falha, porque para o Tailwind "nenhuma classe usada" é um resultado
# válido. Este estágio é descartado, então copiar os templates não pesa na
# imagem final. O diretório `apps/` ainda não existe nesta fase (só nasce na
# Fase 3/4), por isso não há instrução de cópia referenciando esse caminho.
COPY core/templates ./core/templates
RUN npx --yes tailwindcss@3.4.17 \
    -i ./core/static/src/input.css \
    -o ./core/static/dist/tailwind.css \
    --minify \
    && CSS_BYTES=$(wc -c < ./core/static/dist/tailwind.css) \
    && echo "tailwind.css gerado: ${CSS_BYTES} bytes" \
    && if [ "$CSS_BYTES" -lt 5000 ]; then \
         echo "ERRO: CSS com ${CSS_BYTES} bytes — abaixo do piso de 5000 (preflight puro)." >&2; \
         echo "Os content globs do tailwind.config.js não casaram com nenhum template." >&2; \
         exit 1; \
       fi

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install --no-install-recommends -y curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY --from=assets /build/core/static/dist/tailwind.css ./core/static/dist/tailwind.css

RUN SECRET_KEY=build \
    DATABASE_URL=sqlite:///tmp/build.db \
    DJANGO_SETTINGS_MODULE=config.settings.prod \
    python manage.py collectstatic --noinput

RUN chmod +x /app/entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]
