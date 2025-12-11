# ==============================================================================
# Lavalink Dockerfile for Pterodactyl
# Production-Grade with Multi-IP Support
# ==============================================================================

FROM eclipse-temurin:21-jre-alpine

LABEL maintainer="lavalink-server"
LABEL description="Production Lavalink Server with Anti-Block"

# Install dependencies
RUN apk add --no-cache \
    curl \
    wget \
    bash \
    ca-certificates \
    tzdata \
    tini \
    && rm -rf /var/cache/apk/*

# Create lavalink user
RUN addgroup -S lavalink && adduser -S -G lavalink lavalink

# Set working directory
WORKDIR /opt/lavalink

# Create directories
RUN mkdir -p /opt/lavalink/plugins /opt/lavalink/logs && \
    chown -R lavalink:lavalink /opt/lavalink

# Download Lavalink
ARG LAVALINK_VERSION=latest
RUN if [ "$LAVALINK_VERSION" = "latest" ]; then \
        curl -Lo Lavalink.jar https://github.com/lavalink-devs/Lavalink/releases/latest/download/Lavalink.jar; \
    else \
        curl -Lo Lavalink.jar https://github.com/lavalink-devs/Lavalink/releases/download/${LAVALINK_VERSION}/Lavalink.jar; \
    fi && \
    chown lavalink:lavalink Lavalink.jar

# Copy configuration
COPY --chown=lavalink:lavalink application.yml /opt/lavalink/application.yml

# Environment variables
ENV SERVER_PORT=2333 \
    LAVALINK_PASSWORD=youshallnotpass \
    JAVA_OPTS="-Xmx4G -Xms2G -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200"

# Switch to non-root user
USER lavalink

# Expose port
EXPOSE ${SERVER_PORT}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${SERVER_PORT}/version || exit 1

# Entrypoint
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["sh", "-c", "java ${JAVA_OPTS} -jar Lavalink.jar"]
