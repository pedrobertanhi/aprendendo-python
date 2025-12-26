# Sistema de Automação WhatsApp para Clínicas e Consultórios

## 🎯 Visão Geral

Sistema profissional de automação conversacional via WhatsApp para clínicas e consultórios, construído com arquitetura moderna e escalável.

### Stack Tecnológica

- **n8n**: Orquestração de workflows e automações
- **Evolution API**: Integração WhatsApp Business
- **Redis**: Gerenciamento de estado e sessões
- **Docker**: Containerização e deploy
- **Hostinger VPS**: Infraestrutura self-hosted

## 🏗️ Arquitetura

```
┌─────────────────┐
│   WhatsApp      │
│   Cliente       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Evolution API  │◄── Webhooks
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│      n8n        │◄── Workflows
│   (Orquestrador)│
└────┬───────┬────┘
     │       │
     ▼       ▼
┌────────┐ ┌──────────────┐
│ Redis  │ │  Integrações │
│ State  │ │  (Calendar,  │
│ Machine│ │   DB, etc)   │
└────────┘ └──────────────┘
```

## 📁 Estrutura do Projeto

```
automacao-clinicas/
├── n8n-workflows/          # Templates de workflows n8n
│   ├── agendamento.json
│   ├── confirmacao.json
│   ├── remarcacao.json
│   ├── cancelamento.json
│   ├── lista-espera.json
│   └── error-handling.json
├── whatsapp-evolution/     # Configurações e utilitários Evolution API
│   ├── message-templates/
│   ├── webhook-handlers/
│   └── api-client.py
├── redis-state/            # Gerenciamento de estado conversacional
│   ├── state-machine.py
│   ├── session-manager.py
│   └── schemas/
├── infrastructure/         # Configurações de infraestrutura
│   ├── docker-compose.yml
│   ├── nginx/
│   ├── backup/
│   └── monitoring/
├── security/              # Segurança e LGPD
│   ├── lgpd-compliance.md
│   ├── data-retention.py
│   └── encryption/
├── business/              # Modelos de negócio e precificação
│   ├── pricing-models.md
│   ├── pricing-calculator.py
│   └── proposal-templates/
├── utils/                 # Utilitários compartilhados
│   ├── validators.py
│   ├── formatters.py
│   └── multi-tenant.py
├── examples/             # Exemplos e demos
│   └── clinic-complete-setup/
└── docs/                 # Documentação detalhada
    ├── setup-guide.md
    ├── workflows.md
    └── troubleshooting.md
```

## 🚀 Funcionalidades Principais

### 1. **Agendamento Automatizado**
- Verificação de disponibilidade em tempo real
- Múltiplos profissionais e unidades
- Confirmação automática por WhatsApp
- Integração com Google Calendar

### 2. **Gestão de Consultas**
- Remarcação inteligente
- Cancelamento com lista de espera
- Confirmação 24h antes
- Lembretes personalizados

### 3. **Estado Conversacional**
- Máquina de estados com Redis
- Controle de sessão (TTL configurável)
- Contexto de conversa preservado
- Idempotência garantida

### 4. **Multi-tenant**
- Isolamento por cliente
- Configurações independentes
- Billing separado
- LGPD compliance

## 📋 Pré-requisitos

- VPS Hostinger (mínimo 2GB RAM, 2 vCPU)
- Domínio com HTTPS configurado
- Docker e Docker Compose
- Número WhatsApp Business
- Conhecimento básico de n8n

## ⚙️ Instalação Rápida

### 1. Clone o repositório
```bash
git clone <repository-url>
cd automacao-clinicas
```

### 2. Configure as variáveis de ambiente
```bash
cp infrastructure/.env.example infrastructure/.env
# Edite o arquivo .env com suas configurações
```

### 3. Inicie os serviços
```bash
cd infrastructure
docker-compose up -d
```

### 4. Acesse o n8n
```
https://seu-dominio.com:5678
```

### 5. Importe os workflows
- Acesse n8n
- Vá em "Workflows" > "Import"
- Selecione os arquivos em `n8n-workflows/`

## 🔐 Segurança e LGPD

Este sistema foi projetado com foco em segurança e conformidade com a LGPD:

- ✅ **Minimização de dados**: Coleta apenas o necessário
- ✅ **Consentimento**: Opt-in explícito obrigatório
- ✅ **Retenção controlada**: TTL configurável no Redis
- ✅ **Criptografia**: Dados sensíveis criptografados
- ✅ **Direito ao esquecimento**: Exclusão automática sob demanda
- ✅ **Logs auditáveis**: Rastreabilidade completa
- ✅ **Isolamento por tenant**: Separação de dados por cliente

Veja mais em: [security/lgpd-compliance.md](security/lgpd-compliance.md)

## 💰 Modelos de Precificação

### Modelo 1: Setup + Mensalidade
- **Setup inicial**: R$ 2.500 - R$ 5.000
- **Mensalidade**: R$ 297 - R$ 997/mês
- **Inclui**: Até 5.000 mensagens/mês

### Modelo 2: Por Volume
- **Setup**: R$ 1.500
- **Por mensagem**: R$ 0,10 - R$ 0,15
- **Mínimo**: R$ 200/mês

### Modelo 3: White Label
- **Licença**: R$ 10.000 - R$ 25.000
- **Suporte**: R$ 1.500/mês
- **Margem**: 40-60% para revenda

Calcule seu preço: [business/pricing-calculator.py](business/pricing-calculator.py)

## 📊 ROI Esperado

Para uma clínica média (50 consultas/dia):

- **Redução de no-show**: 15-25% (R$ 3.000-5.000/mês)
- **Economia de tempo**: 10h/semana (R$ 2.000/mês)
- **Aumento de agendamentos**: 10-15% (R$ 5.000-8.000/mês)

**ROI típico**: 3-6 meses

## 🎓 Fluxos de Conversa

### Exemplo: Agendamento
```
Bot: Olá! Sou o assistente da Clínica XYZ. Como posso ajudar?
[1] Agendar consulta
[2] Remarcar consulta
[3] Cancelar consulta

Usuário: 1

Bot: Com qual profissional deseja agendar?
[1] Dr. João - Cardiologista
[2] Dra. Maria - Dermatologista

Usuário: 1

Bot: Escolha a data:
[Hoje] [Amanhã] [Esta semana]

... (fluxo continua no Redis state machine)
```

## 🛠️ Manutenção e Monitoramento

### Logs
```bash
# n8n logs
docker logs -f n8n

# Evolution API logs
docker logs -f evolution-api

# Redis logs
docker logs -f redis
```

### Backups
Backup automático diário configurado em `infrastructure/backup/`

### Alertas
- Webhook down: Telegram/Email
- Redis memory > 80%: Email
- Taxa de erro > 5%: Telegram

## 📚 Documentação Completa

- [Guia de Setup](docs/setup-guide.md)
- [Documentação de Workflows](docs/workflows.md)
- [Troubleshooting](docs/troubleshooting.md)
- [API Reference](docs/api-reference.md)

## 🤝 Contribuindo

Melhorias são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📞 Suporte

- **Documentação**: `/docs`
- **Issues**: GitHub Issues
- **Email**: suporte@exemplo.com

## ⚠️ Importante

### Limitações Conhecidas
- WhatsApp API tem janela de 24h para mensagens ativas
- Rate limits da Evolution API devem ser respeitados
- Redis requer backup regular para dados críticos

### Boas Práticas Anti-Bloqueio
- ✅ Respeitar janela de 24h
- ✅ Não enviar spam
- ✅ Usar templates aprovados
- ✅ Implementar backoff exponencial
- ✅ Monitorar qualidade de mensagens

## 📝 Licença

Este projeto é fornecido para fins educacionais e comerciais.

## 🎯 Roadmap

- [ ] Integração com Telegram
- [ ] Dashboard analytics
- [ ] IA para triagem inteligente
- [ ] App mobile complementar
- [ ] Integração com sistemas médicos (Tasy, MV, etc)

---

**Desenvolvido com foco em produção, escalabilidade e negócio recorrente.**

Para começar, veja: [docs/setup-guide.md](docs/setup-guide.md)
