#!/bin/bash
set -euo pipefail

# Deployment Configuration
DOMAIN="health.agentprovision.com"
ADDITIONAL_DOMAIN="zenbud.cl"
EMAIL="saguilera1608@gmail.com"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.prod.yml"

# Port Configuration
# Port Configuration
BACKEND_PORT=8090
FRONTEND_PORT=3090

# Security Configuration
JWT_SECRET=${JWT_SECRET:-}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-}

# Detect deployment mode: local or vm
DEPLOY_MODE=${DEPLOY_MODE:-auto}
if [ "$DEPLOY_MODE" = "auto" ]; then
  # Auto-detect: if nginx and certbot are installed, assume VM deployment
  if command -v nginx >/dev/null 2>&1 && command -v certbot >/dev/null 2>&1; then
    DEPLOY_MODE="vm"
  else
    DEPLOY_MODE="local"
  fi
fi

SERVICES=(postgres redis backend-prod frontend-prod)

info() { echo "[deploy] $1"; }
error() { echo "[deploy] ERROR: $1" >&2; }

info "Deployment Mode: $DEPLOY_MODE"
if [ "$DEPLOY_MODE" = "vm" ]; then
  info "Starting VM deployment for $DOMAIN"
else
  info "Starting local deployment (no nginx/SSL configuration)"
fi

# --- 1. Prerequisite checks ---
if [ "$DEPLOY_MODE" = "vm" ]; then
  REQUIRED_CMDS=(docker docker-compose nginx certbot)
else
  REQUIRED_CMDS=(docker docker-compose)
fi

missing_cmds=()
for cmd in "${REQUIRED_CMDS[@]}"; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    missing_cmds+=("$cmd")
  fi
done

if [ ${#missing_cmds[@]} -ne 0 ]; then
  error "Missing prerequisites: ${missing_cmds[*]}"
  error "Install required tools before running deployment."
  exit 1
fi

info "Prerequisites verified: ${REQUIRED_CMDS[*]}"

# --- 2. Validate production secrets ---
if [ "$DEPLOY_MODE" = "vm" ]; then
  if [[ -z "${JWT_SECRET:-}" ]] || [[ "${#JWT_SECRET}" -lt 32 ]]; then
    error "JWT_SECRET must be set and at least 32 characters for VM deployment."
    error "Generate one with: openssl rand -hex 32"
    exit 1
  fi

  if [[ -z "${POSTGRES_PASSWORD:-}" ]] || [[ "${#POSTGRES_PASSWORD}" -lt 16 ]]; then
    error "POSTGRES_PASSWORD must be set and at least 16 characters for VM deployment."
    error "Generate one with: openssl rand -hex 16"
    exit 1
  fi

  info "Production secrets validated"
else
  # Set defaults for local development
  JWT_SECRET=${JWT_SECRET:-dev_secret_change_in_production_min_32_chars}
  POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-psyprotocol_dev_password}
  info "Local mode: Using development secrets (OK for local testing)"
fi

# Export environment variables
export JWT_SECRET
export POSTGRES_PASSWORD
export BACKEND_PORT
export FRONTEND_PORT
export ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}
export GEMINI_API_KEY=${GEMINI_API_KEY:-}
export STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY:-}

info "Resolved configuration:"
info "  BACKEND_PORT=$BACKEND_PORT"
info "  FRONTEND_PORT=$FRONTEND_PORT"
info "  JWT_SECRET: ${JWT_SECRET:0:8}..."
info "  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:0:4}..."

# --- 3. Stop existing services ---
info "Stopping existing Docker Compose stack"
docker-compose -f "$COMPOSE_FILE" down --remove-orphans || true

# --- 4. Build & start services ---
info "Building and starting services: ${SERVICES[*]}"
docker-compose -f "$COMPOSE_FILE" build --no-cache "${SERVICES[@]}"
docker-compose -f "$COMPOSE_FILE" up -d "${SERVICES[@]}"

info "Docker services running. Current status:"
docker ps --filter "name=psyprotocol" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# --- 5. Run database migrations and seeding ---
info "Waiting for database to be ready..."
sleep 5

info "Running database migrations..."
docker exec psyprotocol-backend-prod alembic upgrade head

info "Seeding database with demo data..."
docker exec psyprotocol-backend-prod python seed_database.py || info "Database already seeded"

# --- 6. Configure Nginx (VM mode only) ---
if [ "$DEPLOY_MODE" != "vm" ]; then
  info "Skipping Nginx/SSL configuration (local mode)"
  info "Deployment complete (local mode)"
  info "Services available at:"
  info "  - Frontend: http://localhost:$FRONTEND_PORT"
  info "  - Backend API: http://localhost:$BACKEND_PORT"
  info "  - API Docs: http://localhost:$BACKEND_PORT/docs"
  exit 0
fi

# Main Domain Configuration
NGINX_CONF_PATH="/etc/nginx/sites-available/$DOMAIN"
SERVER_NAMES="$DOMAIN $ADDITIONAL_DOMAIN"

info "Writing Nginx configuration to $NGINX_CONF_PATH"
sudo bash -c "cat > $NGINX_CONF_PATH" <<EOF
server {
    listen 80;
    server_name $SERVER_NAMES;
    return 301 https://$DOMAIN\$request_uri;
}

server {
    listen 443 ssl;
    server_name $SERVER_NAMES;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Frontend
    location / {
        proxy_pass http://127.0.0.1:$FRONTEND_PORT;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:$BACKEND_PORT;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;

        # Timeouts for API
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # API Documentation
    location /docs {
        proxy_pass http://127.0.0.1:$BACKEND_PORT/docs;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /redoc {
        proxy_pass http://127.0.0.1:$BACKEND_PORT/redoc;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Health check endpoint
    location = /health {
        proxy_pass http://127.0.0.1:$BACKEND_PORT/health;
        access_log off;
    }
}
EOF

if [ ! -L "/etc/nginx/sites-enabled/$DOMAIN" ]; then
  sudo ln -s "$NGINX_CONF_PATH" "/etc/nginx/sites-enabled/$DOMAIN"
fi

info "Testing Nginx configuration"
sudo nginx -t

info "Reloading Nginx"
sudo systemctl reload nginx

# --- 7. Issue / renew SSL certificates ---
info "Requesting/renewing SSL certificate for $DOMAIN and $ADDITIONAL_DOMAIN"
sudo certbot --nginx -d "$DOMAIN" -d "$ADDITIONAL_DOMAIN" --email "$EMAIL" --agree-tos --non-interactive --expand || true

info "Reloading Nginx after Certbot"
sudo systemctl reload nginx

# --- 8. Wait for Services to be Ready ---
echo ""
info "Waiting for services to be ready..."
info "Checking backend health..."

MAX_RETRIES=30
RETRY_COUNT=0
BACKEND_READY=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN/health" | grep -q "200"; then
        BACKEND_READY=true
        info "✓ Backend API is ready!"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    info "Waiting for backend... (attempt $RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

if [ "$BACKEND_READY" = false ]; then
    info "⚠️  WARNING: Backend did not become ready within expected time"
    info "You may need to check the logs: docker-compose -f $COMPOSE_FILE logs backend-prod"
fi

# --- 9. Post-deployment summary ---
echo ""
echo "==========================================="
echo "Deployment Complete!"
echo "==========================================="
info "Application available at https://$DOMAIN"
echo ""
echo "Service Details:"
echo "  - Frontend: https://$DOMAIN"
echo "  - Backend API: https://$DOMAIN/api"
echo "  - API Documentation: https://$DOMAIN/docs"
echo "  - Health Check: https://$DOMAIN/health"
echo ""
echo "Demo Login Credentials:"
echo "  - Admin: admin@psyprotocol.com / Admin123!"
echo "  - Therapist: therapist1@psyprotocol.com / Therapist123!"
echo "  - Patient: patient1@psyprotocol.com / Patient123!"
echo ""
echo "Useful Commands:"
echo "  - View backend logs: docker-compose -f $COMPOSE_FILE logs -f backend-prod"
echo "  - View frontend logs: docker-compose -f $COMPOSE_FILE logs -f frontend-prod"
echo "  - Restart services: docker-compose -f $COMPOSE_FILE restart"
echo "  - Stop services: docker-compose -f $COMPOSE_FILE down"
echo "  - View all containers: docker ps"
echo ""
