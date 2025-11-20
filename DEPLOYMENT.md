# PsyProtocol GCP Deployment Guide

## Prerequisites

### On Your Local Machine
1. **GCP CLI** installed and configured
2. **SSH access** to your GCP VM
3. **Domain DNS** configured to point to your VM's IP address

### On the GCP VM
The deployment script will check for these, but ensure you have:
- Docker
- Docker Compose
- Nginx
- Certbot (for SSL certificates)

## Quick Start Deployment

### 1. Generate Production Secrets

On your local machine, generate secure secrets:

```bash
# Generate JWT secret (32+ characters)
export JWT_SECRET=$(openssl rand -hex 32)

# Generate database password (16+ characters)
export POSTGRES_PASSWORD=$(openssl rand -hex 16)

# Optional: Set API keys if you have them
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export STRIPE_SECRET_KEY="your-stripe-secret-key"
```

### 2. Copy Project to GCP VM

```bash
# Set your VM details
VM_NAME="your-vm-name"
ZONE="us-central1-a"
PROJECT="your-gcp-project"

# Copy the entire project
gcloud compute scp --recurse \
  --project=$PROJECT \
  --zone=$ZONE \
  ./ $VM_NAME:~/psyprotocol/
```

### 3. SSH into VM and Deploy

```bash
# SSH into your VM
gcloud compute ssh $VM_NAME --project=$PROJECT --zone=$ZONE

# Navigate to project directory
cd ~/psyprotocol

# Set production secrets
export JWT_SECRET="your-generated-jwt-secret"
export POSTGRES_PASSWORD="your-generated-db-password"
export ANTHROPIC_API_KEY="your-anthropic-key"  # Optional
export STRIPE_SECRET_KEY="your-stripe-key"      # Optional

# Make deploy script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

## Deployment Script Features

The `deploy.sh` script automatically:

1. ✅ **Detects deployment mode** (VM vs local)
2. ✅ **Validates prerequisites** (Docker, Nginx, Certbot)
3. ✅ **Checks production secrets** (JWT, database password)
4. ✅ **Builds Docker containers** (backend, frontend)
5. ✅ **Runs database migrations** (Alembic)
6. ✅ **Seeds demo data** (users, protocols, treatment plans)
7. ✅ **Configures Nginx** (reverse proxy)
8. ✅ **Issues SSL certificates** (Let's Encrypt via Certbot)
9. ✅ **Health checks** (waits for services to be ready)
10. ✅ **Provides deployment summary** (URLs, credentials, commands)

## DNS Configuration

Before deploying, ensure your domain is configured:

```bash
# Check DNS resolution
dig psycoprotocol.agentprovision.com

# Should return your VM's IP address
```

If DNS is not configured:
1. Go to your DNS provider (e.g., Cloudflare, Google Domains)
2. Add an A record:
   - **Name**: `psycoprotocol`
   - **Type**: `A`
   - **Value**: `YOUR_VM_IP_ADDRESS`
   - **TTL**: `Auto` or `300`

## VM Setup (First Time Only)

If your VM doesn't have the prerequisites, run these commands:

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Nginx
sudo apt-get install -y nginx

# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Log out and back in for Docker group to take effect
exit
```

## Environment Variables

### Required for Production
- `JWT_SECRET`: 32+ character secret for JWT tokens
- `POSTGRES_PASSWORD`: 16+ character database password

### Optional
- `ANTHROPIC_API_KEY`: For AI-powered features
- `STRIPE_SECRET_KEY`: For payment processing
- `BACKEND_PORT`: Backend port (default: 8000)
- `FRONTEND_PORT`: Frontend port (default: 3000)

## Post-Deployment

### Access the Application

After successful deployment:

- **Frontend**: https://psycoprotocol.agentprovision.com
- **API Docs**: https://psycoprotocol.agentprovision.com/docs
- **Health Check**: https://psycoprotocol.agentprovision.com/health

### Demo Credentials

```
Admin:
  Email: admin@psyprotocol.com
  Password: Admin123!

Therapist:
  Email: therapist1@psyprotocol.com
  Password: Therapist123!

Patient:
  Email: patient1@psyprotocol.com
  Password: Patient123!
```

### Useful Commands

```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f backend-prod
docker-compose -f docker-compose.prod.yml logs -f frontend-prod

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Stop services
docker-compose -f docker-compose.prod.yml down

# View running containers
docker ps

# Check Nginx status
sudo systemctl status nginx

# View Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Renew SSL certificates manually
sudo certbot renew

# Test Nginx configuration
sudo nginx -t
```

## Troubleshooting

### Services Not Starting

```bash
# Check Docker logs
docker-compose -f docker-compose.prod.yml logs

# Check if ports are in use
sudo netstat -tulpn | grep -E ':(8000|3000|80|443)'

# Restart Docker
sudo systemctl restart docker
```

### SSL Certificate Issues

```bash
# Check certificate status
sudo certbot certificates

# Renew certificates
sudo certbot renew --dry-run

# Force renewal
sudo certbot renew --force-renewal
```

### Database Connection Issues

```bash
# Check if PostgreSQL container is running
docker ps | grep postgres

# Check database logs
docker logs psyprotocol-db-prod

# Connect to database
docker exec -it psyprotocol-db-prod psql -U psyprotocol -d psyprotocol
```

### Nginx Configuration Issues

```bash
# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

# Restart Nginx
sudo systemctl restart nginx

# Check Nginx status
sudo systemctl status nginx
```

## Updating the Application

To deploy updates:

```bash
# On local machine: Copy updated files
gcloud compute scp --recurse \
  --project=$PROJECT \
  --zone=$ZONE \
  ./ $VM_NAME:~/psyprotocol/

# On VM: Redeploy
cd ~/psyprotocol
export JWT_SECRET="your-jwt-secret"
export POSTGRES_PASSWORD="your-db-password"
./deploy.sh
```

## Backup and Restore

### Backup Database

```bash
# Create backup
docker exec psyprotocol-db-prod pg_dump -U psyprotocol psyprotocol > backup_$(date +%Y%m%d_%H%M%S).sql

# Copy backup to local machine
gcloud compute scp $VM_NAME:~/psyprotocol/backup_*.sql ./backups/
```

### Restore Database

```bash
# Copy backup to VM
gcloud compute scp ./backups/backup_YYYYMMDD_HHMMSS.sql $VM_NAME:~/psyprotocol/

# Restore on VM
docker exec -i psyprotocol-db-prod psql -U psyprotocol psyprotocol < backup_YYYYMMDD_HHMMSS.sql
```

## Security Recommendations

1. **Change default passwords** immediately after first deployment
2. **Use strong secrets** (32+ characters for JWT_SECRET)
3. **Enable firewall** on your VM:
   ```bash
   sudo ufw allow 22/tcp    # SSH
   sudo ufw allow 80/tcp    # HTTP
   sudo ufw allow 443/tcp   # HTTPS
   sudo ufw enable
   ```
4. **Regular updates**:
   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   ```
5. **Monitor logs** regularly for suspicious activity
6. **Set up automated backups** (daily recommended)

## Monitoring

### Health Checks

```bash
# Check application health
curl https://psycoprotocol.agentprovision.com/health

# Check API status
curl https://psycoprotocol.agentprovision.com/api/health
```

### Resource Usage

```bash
# Check Docker container stats
docker stats

# Check disk usage
df -h

# Check memory usage
free -h

# Check system load
top
```

## Support

For issues or questions:
1. Check the logs first
2. Review this troubleshooting guide
3. Check the main README.md
4. Review the PROTOCOL_WORKFLOW_SYSTEM.md for protocol-specific issues

## Architecture

```
┌─────────────────────────────────────────────┐
│         psycoprotocol.agentprovision.com    │
│                  (Nginx + SSL)              │
└────────────┬────────────────────────────────┘
             │
     ┌───────┴────────┐
     │                │
┌────▼─────┐    ┌────▼─────┐
│ Frontend │    │ Backend  │
│  (React) │    │ (FastAPI)│
│  :3000   │    │  :8000   │
└──────────┘    └────┬─────┘
                     │
              ┌──────┴──────┐
              │             │
         ┌────▼────┐   ┌───▼────┐
         │PostgreSQL│   │ Redis  │
         │  :5432   │   │ :6379  │
         └──────────┘   └────────┘
```
