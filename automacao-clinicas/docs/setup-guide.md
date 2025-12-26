# Guia Completo de Setup - Automação WhatsApp para Clínicas

## 📋 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Configuração da VPS Hostinger](#configuração-da-vps-hostinger)
3. [Instalação do Docker](#instalação-do-docker)
4. [Configuração do Evolution API](#configuração-do-evolution-api)
5. [Configuração do n8n](#configuração-do-n8n)
6. [Configuração do Redis](#configuração-do-redis)
7. [Configuração de HTTPS](#configuração-de-https)
8. [Importação de Workflows](#importação-de-workflows)
9. [Configuração do WhatsApp](#configuração-do-whatsapp)
10. [Testes e Validação](#testes-e-validação)

---

## 1. Pré-requisitos

### Hardware Mínimo (VPS Hostinger)
- **CPU**: 2 vCPU
- **RAM**: 2GB (recomendado 4GB para produção)
- **Disco**: 40GB SSD
- **Banda**: 1TB/mês

### Software Necessário
- Ubuntu 22.04 LTS (recomendado)
- Docker 24.0+
- Docker Compose 2.20+
- Nginx
- Certbot (Let's Encrypt)

### Recursos Externos
- Domínio próprio (ex: clinica.com.br)
- Número WhatsApp Business válido
- Google Cloud Console (para Calendar API - opcional)

### Custos Estimados (Hostinger)
- **VPS 2**: ~R$ 29,99/mês (início)
- **VPS 4**: ~R$ 59,99/mês (produção)
- **Domínio**: ~R$ 40/ano
- **Total inicial**: ~R$ 70-100/mês

---

## 2. Configuração da VPS Hostinger

### 2.1 Acesso Inicial

```bash
# Conecte via SSH
ssh root@seu-ip-vps

# Atualize o sistema
apt update && apt upgrade -y

# Crie um usuário não-root
adduser deploy
usermod -aG sudo deploy
```

### 2.2 Configuração de Firewall

```bash
# Instale UFW
apt install ufw -y

# Configure regras básicas
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable

# Verifique o status
ufw status
```

### 2.3 Configuração de Swap (Recomendado para 2GB RAM)

```bash
# Crie arquivo de swap de 2GB
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# Torne permanente
echo '/swapfile none swap sw 0 0' | tee -a /etc/fstab
```

---

## 3. Instalação do Docker

### 3.1 Instalar Docker Engine

```bash
# Remova versões antigas
apt remove docker docker-engine docker.io containerd runc

# Instale dependências
apt install apt-transport-https ca-certificates curl software-properties-common -y

# Adicione repositório Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instale Docker
apt update
apt install docker-ce docker-ce-cli containerd.io -y

# Verifique instalação
docker --version
```

### 3.2 Instalar Docker Compose

```bash
# Baixe Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Dê permissão de execução
chmod +x /usr/local/bin/docker-compose

# Verifique instalação
docker-compose --version
```

### 3.3 Configure Usuário Docker

```bash
# Adicione usuário ao grupo docker
usermod -aG docker deploy

# Aplique mudanças (ou faça logout/login)
newgrp docker
```

---

## 4. Configuração do Evolution API

### 4.1 Estrutura de Diretórios

```bash
# Como usuário deploy
cd /home/deploy
mkdir -p automacao-clinicas
cd automacao-clinicas
```

### 4.2 Criar docker-compose.yml

Crie o arquivo `docker-compose.yml`:

```yaml
version: '3.8'

services:
  # Evolution API
  evolution-api:
    image: atendai/evolution-api:latest
    container_name: evolution-api
    restart: unless-stopped
    ports:
      - "8080:8080"
    environment:
      - SERVER_URL=https://api.seu-dominio.com.br
      - AUTHENTICATION_API_KEY=${EVOLUTION_API_KEY}
      - DATABASE_ENABLED=true
      - DATABASE_CONNECTION_URI=postgresql://postgres:${POSTGRES_PASSWORD}@postgres:5432/evolution
      - REDIS_ENABLED=true
      - REDIS_URI=redis://redis:6379
      - WEBHOOK_GLOBAL_ENABLED=true
      - WEBHOOK_GLOBAL_URL=https://n8n.seu-dominio.com.br/webhook/whatsapp
    depends_on:
      - postgres
      - redis
    volumes:
      - evolution_data:/evolution/instances
    networks:
      - automation-network

  # n8n
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=n8n.seu-dominio.com.br
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - NODE_ENV=production
      - WEBHOOK_URL=https://n8n.seu-dominio.com.br/
      - GENERIC_TIMEZONE=America/Sao_Paulo
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=postgres
      - DB_POSTGRESDB_PASSWORD=${POSTGRES_PASSWORD}
    depends_on:
      - postgres
      - redis
    volumes:
      - n8n_data:/home/node/.n8n
    networks:
      - automation-network

  # Redis
  redis:
    image: redis:7-alpine
    container_name: redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - automation-network

  # PostgreSQL
  postgres:
    image: postgres:15-alpine
    container_name: postgres
    restart: unless-stopped
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_MULTIPLE_DATABASES=evolution,n8n
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-multiple-databases.sh:/docker-entrypoint-initdb.d/init-multiple-databases.sh
    networks:
      - automation-network

volumes:
  evolution_data:
  n8n_data:
  redis_data:
  postgres_data:

networks:
  automation-network:
    driver: bridge
```

### 4.3 Criar .env

```bash
# Crie arquivo .env
cat > .env << 'EOF'
# Senhas e chaves - ALTERE TODOS OS VALORES
POSTGRES_PASSWORD=sua_senha_forte_postgres_aqui
REDIS_PASSWORD=sua_senha_forte_redis_aqui
EVOLUTION_API_KEY=sua_chave_api_evolution_aqui
N8N_ENCRYPTION_KEY=sua_chave_encriptacao_n8n_aqui

# Domínios
DOMAIN_API=api.seu-dominio.com.br
DOMAIN_N8N=n8n.seu-dominio.com.br
EOF

# Gere senhas fortes
openssl rand -base64 32
```

### 4.4 Script para Múltiplos Databases

```bash
# Crie o script init-multiple-databases.sh
cat > init-multiple-databases.sh << 'EOF'
#!/bin/bash
set -e
set -u

function create_database() {
    local database=$1
    echo "Creating database '$database'"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
        CREATE DATABASE $database;
        GRANT ALL PRIVILEGES ON DATABASE $database TO $POSTGRES_USER;
EOSQL
}

if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
    echo "Multiple database creation requested: $POSTGRES_MULTIPLE_DATABASES"
    for db in $(echo $POSTGRES_MULTIPLE_DATABASES | tr ',' ' '); do
        create_database $db
    done
    echo "Multiple databases created"
fi
EOF

chmod +x init-multiple-databases.sh
```

---

## 5. Configuração do n8n

### 5.1 Inicie os Serviços

```bash
# Inicie todos os containers
docker-compose up -d

# Verifique os logs
docker-compose logs -f
```

### 5.2 Acesso Inicial ao n8n

1. Acesse: `http://seu-ip:5678`
2. Crie sua conta admin (primeira vez)
3. Configure credenciais básicas

---

## 6. Configuração do Redis

### 6.1 Teste de Conexão

```bash
# Entre no container Redis
docker exec -it redis redis-cli -a sua_senha_redis

# Teste comandos básicos
SET test "Hello World"
GET test
DEL test
```

### 6.2 Configure Persistência

O Redis já está configurado com `appendonly yes` no docker-compose.

---

## 7. Configuração de HTTPS

### 7.1 Instalar Nginx

```bash
apt install nginx -y
systemctl enable nginx
```

### 7.2 Configurar Nginx para Evolution API

```bash
# Crie configuração
cat > /etc/nginx/sites-available/evolution-api << 'EOF'
server {
    listen 80;
    server_name api.seu-dominio.com.br;

    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

# Habilite o site
ln -s /etc/nginx/sites-available/evolution-api /etc/nginx/sites-enabled/
```

### 7.3 Configurar Nginx para n8n

```bash
cat > /etc/nginx/sites-available/n8n << 'EOF'
server {
    listen 80;
    server_name n8n.seu-dominio.com.br;

    location / {
        proxy_pass http://localhost:5678;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts para webhooks longos
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }
}
EOF

ln -s /etc/nginx/sites-available/n8n /etc/nginx/sites-enabled/
```

### 7.4 Instalar Certificados SSL

```bash
# Instale Certbot
apt install certbot python3-certbot-nginx -y

# Teste configuração Nginx
nginx -t

# Recarregue Nginx
systemctl reload nginx

# Obtenha certificados SSL
certbot --nginx -d api.seu-dominio.com.br -d n8n.seu-dominio.com.br

# Configure renovação automática (já configurado por padrão)
certbot renew --dry-run
```

---

## 8. Importação de Workflows

### 8.1 Acesse n8n

Acesse: `https://n8n.seu-dominio.com.br`

### 8.2 Configure Credenciais

1. Vá em **Settings** > **Credentials**
2. Adicione as seguintes credenciais:

#### Evolution API Credential
```
Name: Evolution API Principal
Type: HTTP Request
Method: POST/GET
Authentication: Generic Credential Type
  - Header Auth
  - Header Name: apikey
  - Value: sua_chave_api_evolution
```

#### Redis Credential
```
Name: Redis State
Type: Redis
Host: redis
Port: 6379
Password: sua_senha_redis
Database: 0
```

### 8.3 Importe Workflows

1. Vá em **Workflows**
2. Clique em **Import from File**
3. Importe cada arquivo `.json` da pasta `n8n-workflows/`

---

## 9. Configuração do WhatsApp

### 9.1 Criar Instância Evolution API

```bash
# Via curl
curl -X POST https://api.seu-dominio.com.br/instance/create \
  -H "apikey: sua_chave_api" \
  -H "Content-Type: application/json" \
  -d '{
    "instanceName": "clinica-principal",
    "qrcode": true,
    "integration": "WHATSAPP-BAILEYS"
  }'
```

### 9.2 Conectar WhatsApp

1. Acesse: `https://api.seu-dominio.com.br/instance/connect/clinica-principal`
2. Escaneie o QR Code com WhatsApp
3. Aguarde confirmação

### 9.3 Configurar Webhook Global

```bash
curl -X POST https://api.seu-dominio.com.br/webhook/set/clinica-principal \
  -H "apikey: sua_chave_api" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://n8n.seu-dominio.com.br/webhook/whatsapp",
    "enabled": true,
    "events": [
      "messages.upsert",
      "messages.update",
      "connection.update"
    ]
  }'
```

---

## 10. Testes e Validação

### 10.1 Teste de Conexão Redis

```bash
# Dentro do container n8n
docker exec -it n8n npm install redis

# Teste via n8n Code Node
const Redis = require('redis');
const client = Redis.createClient({
  host: 'redis',
  port: 6379,
  password: process.env.REDIS_PASSWORD
});

await client.connect();
await client.set('test', 'Hello from n8n');
const value = await client.get('test');
console.log(value);
```

### 10.2 Teste de Webhook

```bash
# Envie mensagem de teste
curl -X POST https://n8n.seu-dominio.com.br/webhook-test/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "key": {
        "remoteJid": "5511999999999@s.whatsapp.net"
      },
      "message": {
        "conversation": "teste"
      }
    }
  }'
```

### 10.3 Checklist Final

- [ ] Docker containers rodando (`docker ps`)
- [ ] Redis respondendo (`redis-cli ping`)
- [ ] n8n acessível via HTTPS
- [ ] Evolution API acessível via HTTPS
- [ ] WhatsApp conectado e online
- [ ] Workflows importados
- [ ] Webhook configurado
- [ ] Teste de mensagem bem-sucedido
- [ ] Certificados SSL válidos
- [ ] Firewall configurado
- [ ] Backup configurado

---

## 🔧 Troubleshooting

### Problema: Container não inicia

```bash
# Veja os logs detalhados
docker-compose logs [nome-do-servico]

# Recrie os containers
docker-compose down
docker-compose up -d --force-recreate
```

### Problema: Webhook não recebe mensagens

1. Verifique logs Evolution API: `docker logs evolution-api`
2. Teste URL webhook manualmente
3. Verifique configuração de webhook
4. Confirme que n8n workflow está ativo

### Problema: Redis sem memória

```bash
# Verifique uso de memória
docker exec -it redis redis-cli -a senha INFO memory

# Configure max memory (se necessário)
docker exec -it redis redis-cli -a senha CONFIG SET maxmemory 256mb
docker exec -it redis redis-cli -a senha CONFIG SET maxmemory-policy allkeys-lru
```

---

## 📚 Próximos Passos

1. [Configure workflows específicos](workflows.md)
2. [Implemente segurança LGPD](../security/lgpd-compliance.md)
3. [Configure monitoramento](monitoring.md)
4. [Defina estratégia de backup](backup.md)

---

## 🆘 Suporte

Se encontrar problemas não cobertos aqui:

1. Consulte [Troubleshooting](troubleshooting.md)
2. Verifique logs de todos os containers
3. Consulte documentação oficial:
   - [n8n Docs](https://docs.n8n.io)
   - [Evolution API](https://evolution-api.com)
   - [Redis Docs](https://redis.io/docs)
