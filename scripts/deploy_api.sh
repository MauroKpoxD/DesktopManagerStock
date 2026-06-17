#!/bin/bash
# deploy_api.sh - Despliegue automático de DesktopManagerStock API con Docker
# Uso: ./deploy_api.sh

set -e  # Detener si hay error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # Sin color

# ------------------------------------------------------------
# 1. Funciones auxiliares
# ------------------------------------------------------------
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 no está instalado. Instalando..."
        return 1
    fi
    return 0
}

# ------------------------------------------------------------
# 2. Verificar e instalar dependencias
# ------------------------------------------------------------
log_info "Verificando dependencias..."

# Actualizar repositorios
if ! ping -c 1 google.com &> /dev/null; then
    log_warn "DNS no funciona. Configurando DNS público..."
    echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
    echo "nameserver 1.1.1.1" | sudo tee -a /etc/resolv.conf
fi

sudo apt update -qq

# Instalar git si falta
if ! check_command git; then
    sudo apt install git -y
fi

# Instalar Docker si falta
if ! check_command docker; then
    log_info "Instalando Docker..."
    curl -fsSL https://get.docker.com | sudo sh
    sudo usermod -aG docker $USER
    newgrp docker <<EOF
    # Esto recarga grupos sin logout
EOF
fi

# Instalar docker-compose (plugin o standalone)
if ! docker compose version &> /dev/null; then
    log_info "Instalando docker-compose..."
    sudo apt install docker-compose-plugin -y
fi

# ------------------------------------------------------------
# 3. Clonar o actualizar el repositorio
# ------------------------------------------------------------
REPO_URL="https://github.com/MauroKpoxD/DesktopManagerStock.git"
PROJECT_DIR="$HOME/DesktopManagerStock"

if [ -d "$PROJECT_DIR" ]; then
    log_info "Repositorio ya existe en $PROJECT_DIR. Actualizando..."
    cd "$PROJECT_DIR"
    git pull origin main  # o s4ndulos, según tu rama
else
    log_info "Clonando repositorio..."
    git clone "$REPO_URL" "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

# ------------------------------------------------------------
# 4. Configurar variables de entorno (.env)
# ------------------------------------------------------------
cd "$PROJECT_DIR/server"

if [ ! -f ".env" ]; then
    log_info "Creando .env desde .env.example..."
    cp .env.example .env
    # Generar SECRET_KEY segura
    SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    sed -i "s/^SECRET_KEY=.*/SECRET_KEY=$SECRET/" .env
    # Ajustar para que escuche en todas las interfaces
    sed -i 's/^API_HOST=.*/API_HOST=0.0.0.0/' .env
    # Desactivar rate limiting en desarrollo (opcional)
    sed -i 's/^RATE_LIMIT_ENABLED=.*/RATE_LIMIT_ENABLED=false/' .env
    log_info ".env configurado correctamente."
else
    log_info ".env ya existe. No se modifica."
fi

# ------------------------------------------------------------
# 5. Detener Tailscale si está activo (para evitar problemas DNS)
# ------------------------------------------------------------
if systemctl is-active --quiet tailscaled; then
    log_warn "Tailscale está activo. Deteniéndolo temporalmente..."
    sudo systemctl stop tailscaled
    TAILSCALE_STOPPED=true
else
    TAILSCALE_STOPPED=false
fi

# ------------------------------------------------------------
# 6. Construir y levantar contenedores con docker-compose
# ------------------------------------------------------------
log_info "Construyendo y levantando contenedores..."
docker compose up -d --build

# ------------------------------------------------------------
# 7. (Opcional) Restaurar Tailscale si se detuvo
# ------------------------------------------------------------
if [ "$TAILSCALE_STOPPED" = true ]; then
    log_info "Reiniciando Tailscale..."
    sudo systemctl start tailscaled
fi

# ------------------------------------------------------------
# 8. Mostrar estado final
# ------------------------------------------------------------
log_info "Despliegue completado."
docker compose ps
log_info "Logs en tiempo real (Ctrl+C para salir sin detener):"
docker compose logs -f