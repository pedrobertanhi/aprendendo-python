# Documentação de Workflows n8n - Sistema de Automação

## 📋 Índice

1. [Visão Geral dos Workflows](#visão-geral-dos-workflows)
2. [Workflow: Agendamento](#workflow-agendamento)
3. [Workflow: Confirmação](#workflow-confirmação)
4. [Workflow: Remarcação](#workflow-remarcação)
5. [Workflow: Cancelamento](#workflow-cancelamento)
6. [Workflow: Lista de Espera](#workflow-lista-de-espera)
7. [Workflow: Error Handling](#workflow-error-handling)
8. [Boas Práticas](#boas-práticas)

---

## Visão Geral dos Workflows

### Arquitetura de Comunicação

```
WhatsApp Message
      ↓
Evolution API Webhook
      ↓
n8n Webhook Trigger
      ↓
Redis State Check → [State Machine]
      ↓
Business Logic → [Validation, Calendar, DB]
      ↓
Redis State Update
      ↓
WhatsApp Response (Evolution API)
```

### Fluxo de Estados (State Machine)

```
IDLE → MENU_PRINCIPAL
    ↓
    ├→ AGENDAMENTO_INICIO
    │   ├→ AGENDAMENTO_SELECAO_PROFISSIONAL
    │   ├→ AGENDAMENTO_SELECAO_DATA
    │   ├→ AGENDAMENTO_SELECAO_HORA
    │   └→ AGENDAMENTO_CONFIRMACAO → IDLE
    │
    ├→ REMARCACAO_INICIO
    │   ├→ REMARCACAO_BUSCA_CONSULTA
    │   ├→ REMARCACAO_NOVA_DATA
    │   └→ REMARCACAO_CONFIRMACAO → IDLE
    │
    └→ CANCELAMENTO_INICIO
        ├→ CANCELAMENTO_BUSCA_CONSULTA
        ├→ CANCELAMENTO_MOTIVO
        └→ CANCELAMENTO_CONFIRMACAO → IDLE
```

---

## Workflow: Agendamento

### Objetivo
Permitir que pacientes agendem consultas via WhatsApp de forma conversacional.

### Trigger
- **Type**: Webhook
- **Path**: `/webhook/whatsapp`
- **Method**: POST

### Nós Principais

#### 1. Webhook Trigger
```javascript
// Recebe payload do Evolution API
{
  "data": {
    "key": {
      "remoteJid": "5511999999999@s.whatsapp.net",
      "fromMe": false
    },
    "message": {
      "conversation": "texto da mensagem"
    },
    "messageTimestamp": "1234567890"
  }
}
```

#### 2. Extract User Info
```javascript
// Code Node - Extrai informações do usuário
const data = $input.item.json;
const userPhone = data.data.key.remoteJid.split('@')[0];
const message = data.data.message.conversation || 
                data.data.message.extendedTextMessage?.text || '';

return {
  json: {
    userPhone: userPhone,
    message: message.trim(),
    timestamp: data.data.messageTimestamp
  }
};
```

#### 3. Get Current State (Redis)
```javascript
// Redis Get Node
// Key: `state:${userPhone}`
// Returns: { state: 'IDLE', context: {} }
```

#### 4. State Machine Router
```javascript
// Switch Node baseado no estado atual
const currentState = $json.state || 'IDLE';
const message = $json.message.toLowerCase();

// Rotas diferentes baseadas no estado
switch(currentState) {
  case 'IDLE':
    return [0]; // Mostra menu principal
  case 'MENU_PRINCIPAL':
    return [1]; // Processa escolha do menu
  case 'AGENDAMENTO_SELECAO_PROFISSIONAL':
    return [2]; // Processa seleção profissional
  // ... outros estados
}
```

#### 5. Menu Principal
```javascript
// Function Node - Prepara menu
const menuMessage = `👋 Olá! Bem-vindo à *Clínica Saúde Total*

Como posso ajudar você hoje?

*1* - 📅 Agendar consulta
*2* - 🔄 Remarcar consulta
*3* - ❌ Cancelar consulta
*4* - 📞 Falar com atendente

_Digite o número da opção desejada_`;

return {
  json: {
    message: menuMessage,
    nextState: 'MENU_PRINCIPAL'
  }
};
```

#### 6. Processar Escolha Menu
```javascript
// Code Node
const choice = $json.message;

let nextState, responseMessage;

switch(choice) {
  case '1':
    nextState = 'AGENDAMENTO_SELECAO_PROFISSIONAL';
    responseMessage = `📋 *Agendamento de Consulta*

Escolha o profissional:

*1* - Dr. João Silva - Cardiologista
*2* - Dra. Maria Santos - Dermatologista
*3* - Dr. Pedro Costa - Ortopedista
*4* - Dra. Ana Oliveira - Pediatra

_Digite o número do profissional_`;
    break;
    
  case '2':
    nextState = 'REMARCACAO_INICIO';
    // ... mensagem de remarcação
    break;
    
  case '3':
    nextState = 'CANCELAMENTO_INICIO';
    // ... mensagem de cancelamento
    break;
    
  default:
    nextState = 'MENU_PRINCIPAL';
    responseMessage = '❌ Opção inválida. Por favor, escolha uma opção de 1 a 4.';
}

return {
  json: {
    message: responseMessage,
    nextState: nextState
  }
};
```

#### 7. Seleção de Profissional
```javascript
// Code Node
const professionals = {
  '1': { id: 1, name: 'Dr. João Silva', specialty: 'Cardiologista' },
  '2': { id: 2, name: 'Dra. Maria Santos', specialty: 'Dermatologista' },
  '3': { id: 3, name: 'Dr. Pedro Costa', specialty: 'Ortopedista' },
  '4': { id: 4, name: 'Dra. Ana Oliveira', specialty: 'Pediatra' }
};

const choice = $json.message;
const professional = professionals[choice];

if (!professional) {
  return {
    json: {
      message: '❌ Profissional inválido. Digite um número de 1 a 4.',
      nextState: 'AGENDAMENTO_SELECAO_PROFISSIONAL'
    }
  };
}

// Calcular próximos dias disponíveis
const today = new Date();
const availableDates = [];
for (let i = 1; i <= 7; i++) {
  const date = new Date(today);
  date.setDate(date.getDate() + i);
  if (date.getDay() !== 0 && date.getDay() !== 6) { // Não incluir finais de semana
    availableDates.push(date);
  }
}

const dateOptions = availableDates
  .map((d, i) => `*${i+1}* - ${d.toLocaleDateString('pt-BR', { weekday: 'long', day: '2-digit', month: 'long' })}`)
  .join('\n');

return {
  json: {
    message: `✅ Você selecionou: *${professional.name}* - ${professional.specialty}

📅 *Escolha a data:*

${dateOptions}

_Digite o número da data desejada_`,
    nextState: 'AGENDAMENTO_SELECAO_DATA',
    context: {
      professional: professional
    }
  }
};
```

#### 8. Seleção de Data
```javascript
// Code Node - Similar ao anterior
// Busca horários disponíveis no calendário
// Retorna lista de horários
```

#### 9. Google Calendar Integration
```javascript
// HTTP Request Node
// GET https://www.googleapis.com/calendar/v3/calendars/${calendarId}/events/list
// Params: timeMin, timeMax, singleEvents=true
// Auth: OAuth2
```

#### 10. Seleção de Horário
```javascript
// Code Node
// Valida horário escolhido
// Prepara confirmação
```

#### 11. Confirmação e Criação no Calendar
```javascript
// HTTP Request - POST to Google Calendar
{
  "summary": "Consulta - Paciente",
  "description": "Consulta agendada via WhatsApp",
  "start": {
    "dateTime": "2024-01-15T10:00:00-03:00",
    "timeZone": "America/Sao_Paulo"
  },
  "end": {
    "dateTime": "2024-01-15T10:30:00-03:00",
    "timeZone": "America/Sao_Paulo"
  },
  "attendees": [
    {
      "email": "paciente@email.com"
    }
  ]
}
```

#### 12. Save State (Redis)
```javascript
// Redis Set Node
// Key: `state:${userPhone}`
// Value: { state: 'IDLE', lastAction: 'agendamento', timestamp }
// TTL: 3600 (1 hora)

// Também salvar consulta
// Key: `appointment:${appointmentId}`
// Value: { professional, date, time, userPhone, status: 'scheduled' }
// TTL: 604800 (7 dias)
```

#### 13. Send WhatsApp Response
```javascript
// HTTP Request - Evolution API
// POST /message/sendText/${instanceName}
{
  "number": "5511999999999",
  "text": "✅ *Consulta agendada com sucesso!*\n\n📋 Detalhes:\n👨‍⚕️ Profissional: Dr. João Silva\n📅 Data: 15/01/2024\n🕐 Horário: 10:00\n\n📍 Endereço: Rua Exemplo, 123\n\n⚠️ *Importante:*\n- Chegue 10 minutos antes\n- Traga documentos e exames\n- Em caso de atraso, avise\n\n_Enviaremos uma confirmação 24h antes da consulta._"
}
```

---

## Workflow: Confirmação

### Objetivo
Enviar confirmação automática 24h antes da consulta.

### Trigger
- **Type**: Cron
- **Expression**: `0 10 * * *` (Todo dia às 10h)

### Lógica Principal

```javascript
// 1. Buscar consultas para amanhã (Redis Scan)
const tomorrow = new Date();
tomorrow.setDate(tomorrow.getDate() + 1);

// 2. Para cada consulta, enviar confirmação
const message = `🔔 *Lembrete de Consulta*

Você tem uma consulta agendada para *amanhã*:

👨‍⚕️ Profissional: ${appointment.professional}
📅 Data: ${appointment.date}
🕐 Horário: ${appointment.time}

*Por favor, confirme sua presença:*

*1* - ✅ Confirmo presença
*2* - ❌ Preciso remarcar
*3* - 📞 Falar com atendente

_Digite o número da opção desejada_`;

// 3. Atualizar estado no Redis
// state: CONFIRMACAO_AGUARDANDO_RESPOSTA
```

---

## Workflow: Remarcação

### Estados
```
REMARCACAO_INICIO
  ↓
REMARCACAO_BUSCA_CONSULTA (por telefone)
  ↓
REMARCACAO_EXIBIR_CONSULTAS
  ↓
REMARCACAO_SELECAO_CONSULTA
  ↓
REMARCACAO_NOVA_DATA
  ↓
REMARCACAO_NOVO_HORARIO
  ↓
REMARCACAO_CONFIRMACAO
  ↓
IDLE
```

### Lógica de Busca

```javascript
// Redis - Buscar consultas do usuário
// Pattern: `appointment:*`
// Filter: appointments where userPhone matches

const userAppointments = await redis.keys('appointment:*');
const appointments = [];

for (const key of userAppointments) {
  const apt = await redis.get(key);
  if (apt.userPhone === currentUserPhone && apt.status === 'scheduled') {
    appointments.push(apt);
  }
}

// Exibir lista
const message = appointments.map((apt, i) => 
  `*${i+1}* - ${apt.date} às ${apt.time} - ${apt.professional}`
).join('\n');
```

---

## Workflow: Cancelamento

### Lógica com Lista de Espera

```javascript
// 1. Identificar consulta a cancelar
// 2. Confirmar cancelamento
// 3. Liberar horário
// 4. Verificar lista de espera

// Buscar lista de espera para aquele profissional/horário
const waitingListKey = `waiting:${professional.id}:${date}`;
const waitingList = await redis.lrange(waitingListKey, 0, -1);

if (waitingList.length > 0) {
  // Notificar primeira pessoa da lista
  const firstInLine = waitingList[0];
  
  const notificationMessage = `🎉 *Boa notícia!*

Uma vaga foi aberta para:

👨‍⚕️ Profissional: ${professional.name}
📅 Data: ${date}
🕐 Horário: ${time}

*Você tem interesse neste horário?*

*1* - ✅ Sim, quero agendar
*2* - ❌ Não tenho interesse

⏰ _Você tem 30 minutos para responder_`;

  // Enviar notificação
  // Aguardar resposta com timeout
}
```

---

## Workflow: Error Handling

### Estratégia Global

```javascript
// Error Trigger - Captura erros de qualquer workflow

// 1. Log do erro
const errorLog = {
  timestamp: new Date().toISOString(),
  workflow: $workflow.name,
  node: $node.name,
  error: $json.error,
  input: $input,
  userPhone: $json.userPhone
};

// Salvar no Redis
await redis.lpush('errors:log', JSON.stringify(errorLog));

// 2. Notificar admin (Telegram/Email)
// 3. Enviar mensagem amigável ao usuário

const userMessage = `😔 Desculpe, encontramos um problema temporário.

Nossa equipe foi notificada e já está trabalhando na solução.

Por favor, tente novamente em alguns minutos ou entre em contato:
📞 (11) 99999-9999

_Pedimos desculpas pelo inconveniente._`;

// 4. Resetar estado do usuário
await redis.set(`state:${userPhone}`, JSON.stringify({ state: 'IDLE' }));

// 5. Retry com backoff exponencial (se aplicável)
```

---

## Boas Práticas

### 1. Validação de Entrada

```javascript
// Sempre validar input do usuário
function validateInput(input, type) {
  switch(type) {
    case 'phone':
      return /^55\d{10,11}$/.test(input);
    case 'number':
      return /^\d+$/.test(input);
    case 'date':
      // Validar data
      return true;
  }
}
```

### 2. Timeout de Sessão

```javascript
// Redis TTL para estados
// Após X minutos sem interação, retornar ao IDLE
const SESSION_TIMEOUT = 600; // 10 minutos

await redis.set(
  `state:${userPhone}`,
  JSON.stringify(state),
  'EX',
  SESSION_TIMEOUT
);
```

### 3. Rate Limiting

```javascript
// Evitar spam
const rateLimitKey = `ratelimit:${userPhone}`;
const messageCount = await redis.incr(rateLimitKey);

if (messageCount === 1) {
  await redis.expire(rateLimitKey, 60); // 1 minuto
}

if (messageCount > 10) {
  return {
    json: {
      message: '⚠️ Você está enviando mensagens muito rapidamente. Por favor, aguarde um momento.'
    }
  };
}
```

### 4. Logging e Auditoria

```javascript
// Log todas as interações para auditoria LGPD
const auditLog = {
  timestamp: new Date().toISOString(),
  userPhone: userPhone,
  action: 'agendamento_criado',
  details: {
    professional: professional.name,
    date: date,
    time: time
  }
};

await redis.lpush('audit:logs', JSON.stringify(auditLog));
await redis.ltrim('audit:logs', 0, 9999); // Manter últimas 10k entradas
```

### 5. Retry Logic

```javascript
// Para chamadas externas (Calendar, DB)
const MAX_RETRIES = 3;
let retries = 0;

while (retries < MAX_RETRIES) {
  try {
    const result = await externalApiCall();
    return result;
  } catch (error) {
    retries++;
    if (retries >= MAX_RETRIES) {
      throw error;
    }
    // Backoff exponencial
    await sleep(Math.pow(2, retries) * 1000);
  }
}
```

---

## 📊 Métricas e Monitoramento

### KPIs para Monitorar

```javascript
// Salvar métricas no Redis
const metrics = {
  'total_messages': counter,
  'total_appointments': counter,
  'conversion_rate': gauge,
  'average_response_time': histogram,
  'error_rate': gauge
};

// Incrementar métricas
await redis.incr('metrics:total_messages');
await redis.incr(`metrics:appointments:${date}`);
```

---

## 🔍 Debugging

### Como Testar Workflows

1. **Teste Manual via n8n**
   - Execute workflow manualmente
   - Forneça JSON de teste
   - Verifique cada nó

2. **Webhook Test**
   ```bash
   curl -X POST https://n8n.seu-dominio.com.br/webhook-test/whatsapp \
     -H "Content-Type: application/json" \
     -d @test-payload.json
   ```

3. **Redis Inspection**
   ```bash
   # Ver todos os estados ativos
   redis-cli -a senha KEYS "state:*"
   
   # Ver estado específico
   redis-cli -a senha GET "state:5511999999999"
   ```

4. **Logs do n8n**
   ```bash
   docker logs -f n8n
   ```

---

## 📚 Referências

- [n8n Documentation](https://docs.n8n.io)
- [Evolution API Docs](https://evolution-api.com)
- [Redis Commands](https://redis.io/commands)
- [Google Calendar API](https://developers.google.com/calendar)

---

**Próximo**: [Implementar workflows no n8n](../n8n-workflows/)
