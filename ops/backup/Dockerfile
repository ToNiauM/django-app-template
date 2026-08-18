# O cliente pg_dump acompanha o PostgreSQL 17 da stack, evitando incompatibilidade.
FROM postgres:17-alpine

RUN apk add --no-cache curl unzip dcron tzdata

# Release fixado e verificado contra o SHA256SUMS publicado pelo rclone.
ARG PIN_RCLONE_VERSION=v1.68.2
RUN set -eu; \
    cd /tmp; \
    curl -fsSO "https://downloads.rclone.org/${PIN_RCLONE_VERSION}/rclone-${PIN_RCLONE_VERSION}-linux-amd64.zip"; \
    curl -fsSO "https://downloads.rclone.org/${PIN_RCLONE_VERSION}/SHA256SUMS"; \
    grep " rclone-${PIN_RCLONE_VERSION}-linux-amd64.zip$" SHA256SUMS | sha256sum -c -; \
    unzip -q "rclone-${PIN_RCLONE_VERSION}-linux-amd64.zip"; \
    install -m 755 "rclone-${PIN_RCLONE_VERSION}-linux-amd64/rclone" /usr/bin/rclone; \
    rm -rf /tmp/rclone-* /tmp/SHA256SUMS; \
    rclone version

COPY entrypoint.sh /entrypoint.sh
COPY backup.sh /backup.sh
COPY retencao.sh /retencao.sh
COPY testar_retencao.sh /testar_retencao.sh
RUN chmod 755 /entrypoint.sh /backup.sh /retencao.sh /testar_retencao.sh

ENV TZ=America/Sao_Paulo

ENTRYPOINT ["/entrypoint.sh"]
