# Conformidade LGPD - Sistema de Automação WhatsApp

## 📋 Visão Geral

Este documento detalha como o sistema de automação WhatsApp atende aos requisitos da **Lei Geral de Proteção de Dados (LGPD - Lei nº 13.709/2018)**.

## 🎯 Princípios LGPD Aplicados

### 1. Finalidade
**Art. 6º, I - Finalidade específica**

✅ **Implementação:**
- Dados coletados exclusivamente para agendamento e gestão de consultas
- Propósito claro comunicado ao titular antes da coleta
- Não há uso de dados para fins não autorizados

```python
# Exemplo de consentimento explícito
CONSENT_MESSAGE = """
Para continuar, preciso do seu consentimento:

Seus dados (nome, telefone, histórico de consultas) serão 
usados APENAS para:
• Agendamento de consultas
• Envio de confirmações e lembretes
• Gestão da sua relação com a clínica

*1* - Concordo e autorizo
*2* - Não concordo

Você pode revogar este consentimento a qualquer momento.
"""
```

### 2. Adequação
**Art. 6º, II - Compatibilidade com finalidades**

✅ **Implementação:**
- Tratamento limitado ao escopo de agendamento médico
- Dados de saúde (se coletados) tratados com segurança reforçada
- Compartilhamento apenas com profissionais autorizados

### 3. Necessidade
**Art. 6º, III - Minimização**

✅ **Implementação:**
- Coleta mínima de dados: nome, telefone, data/hora preferida
- Não coleta dados desnecessários (ex: estado civil, renda)
- Exclusão automática após período de retenção

```python
# Dados coletados - Mínimo necessário
REQUIRED_DATA = {
    'phone': str,           # Obrigatório para comunicação
    'name': str,            # Obrigatório para identificação
    'preferred_date': str,  # Necessário para agendamento
    'professional_id': int  # Necessário para alocar profissional
}

# Dados NÃO coletados (desnecessários)
EXCLUDED_DATA = [
    'cpf',           # Não necessário para agendamento
    'address',       # Não necessário inicialmente
    'health_info',   # Coletado apenas presencialmente
    'payment_info'   # Não processado pelo bot
]
```

### 4. Transparência
**Art. 6º, VI - Informação clara ao titular**

✅ **Implementação:**
- Política de privacidade acessível via comando
- Informações sobre retenção de dados
- Contato do DPO (Encarregado de Proteção de Dados)

```python
PRIVACY_INFO = """
📋 *Política de Privacidade*

*O que coletamos:*
• Nome e telefone
• Histórico de consultas
• Preferências de agendamento

*Como usamos:*
• Apenas para agendamento e confirmações
• Não vendemos ou compartilhamos seus dados

*Quanto tempo guardamos:*
• Dados de consultas: 5 anos (regulamentação CFM)
• Histórico de conversa: 90 dias
• Dados de cancelamento: 30 dias

*Seus direitos:*
Digite 'meus dados' para exercer seus direitos.

*Encarregado (DPO):*
dpo@clinica.com.br
"""
```

### 5. Segurança
**Art. 6º, VII - Proteção técnica e administrativa**

✅ **Implementação:**
- Criptografia de dados em trânsito (HTTPS/TLS)
- Criptografia de dados sensíveis em repouso (Redis)
- Controle de acesso baseado em funções (RBAC)
- Logs de auditoria
- Backup seguro

```python
# Criptografia de dados sensíveis
from cryptography.fernet import Fernet

class DataEncryption:
    def __init__(self, key):
        self.cipher = Fernet(key)
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Criptografa dados sensíveis antes de armazenar"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted: str) -> str:
        """Descriptografa dados para uso autorizado"""
        return self.cipher.decrypt(encrypted.encode()).decode()

# Usar para dados como:
# - Nome completo
# - Informações de saúde (se coletadas)
# - Dados de contato alternativos
```

### 6. Prevenção
**Art. 6º, VIII - Prevenção de danos**

✅ **Implementação:**
- Validação de entrada de dados
- Sanitização de mensagens
- Rate limiting (anti-spam)
- Monitoramento de anomalias

```python
# Rate limiting para prevenir abuso
def check_rate_limit(user_phone: str) -> bool:
    """Previne spam e abuso do sistema"""
    key = f"ratelimit:{user_phone}"
    count = redis.incr(key)
    
    if count == 1:
        redis.expire(key, 60)  # 1 minuto
    
    if count > 10:
        # Log de segurança
        log_security_event(
            event_type="rate_limit_exceeded",
            user_phone=user_phone,
            count=count
        )
        return False
    
    return True
```

## 🔐 Direitos dos Titulares (Art. 18)

### Implementação dos Direitos

```python
class TitularRights:
    """Implementação dos direitos dos titulares de dados"""
    
    def handle_user_request(self, user_phone: str, request_type: str):
        """
        Processa solicitações de exercício de direitos
        
        Tipos suportados:
        - confirmacao: Confirmação de tratamento
        - acesso: Acesso aos dados
        - correcao: Correção de dados
        - anonimizacao: Anonimização
        - exclusao: Exclusão (direito ao esquecimento)
        - portabilidade: Portabilidade de dados
        - revogacao: Revogação de consentimento
        """
        
        if request_type == 'confirmacao':
            return self.confirm_data_processing(user_phone)
        
        elif request_type == 'acesso':
            return self.provide_data_access(user_phone)
        
        elif request_type == 'correcao':
            return self.request_data_correction(user_phone)
        
        elif request_type == 'exclusao':
            return self.delete_user_data(user_phone)
        
        elif request_type == 'portabilidade':
            return self.export_user_data(user_phone)
        
        elif request_type == 'revogacao':
            return self.revoke_consent(user_phone)
    
    def confirm_data_processing(self, user_phone: str) -> str:
        """Art. 18, I - Confirmação de tratamento"""
        has_data = redis.exists(f"state:{user_phone}")
        
        if has_data:
            return """
✅ Sim, processamos seus dados.

Dados tratados:
• Telefone
• Histórico de conversas (90 dias)
• Agendamentos

Para mais detalhes, digite 'meus dados'.
"""
        else:
            return "❌ Não encontramos dados seus em nosso sistema."
    
    def provide_data_access(self, user_phone: str) -> Dict:
        """Art. 18, II - Acesso aos dados"""
        # Buscar todos os dados do usuário
        user_state = redis.get(f"state:{user_phone}")
        appointments = redis.smembers(f"user_appointments:{user_phone}")
        
        data_package = {
            'phone': user_phone,
            'current_state': user_state,
            'appointments': [
                redis.get(f"appointment:{apt_id}")
                for apt_id in appointments
            ],
            'exported_at': datetime.now().isoformat()
        }
        
        # Log de auditoria
        log_audit(
            user_phone=user_phone,
            action='data_access_request',
            details={'exported': True}
        )
        
        return data_package
    
    def delete_user_data(self, user_phone: str) -> bool:
        """Art. 18, VI - Exclusão (direito ao esquecimento)"""
        
        # Verificar se há obrigações legais de retenção
        active_appointments = get_user_appointments(
            user_phone,
            status='scheduled'
        )
        
        if active_appointments:
            return {
                'success': False,
                'message': """
⚠️ Você possui consultas agendadas.

Para proteger sua saúde e cumprir regulamentação médica,
não podemos excluir seus dados enquanto houver consultas ativas.

Por favor:
1. Cancele suas consultas primeiro
2. Solicite exclusão novamente

Ou aguarde 30 dias após a última consulta.
"""
            }
        
        # Anonimizar dados mantidos por obrigação legal
        anonymize_required_data(user_phone)
        
        # Excluir dados não obrigatórios
        redis.delete(f"state:{user_phone}")
        
        # Remover de listas de espera
        remove_from_all_waiting_lists(user_phone)
        
        # Log de auditoria (obrigatório manter)
        log_audit(
            user_phone='[REDACTED]',  # Anonimizado
            action='data_deletion_request',
            details={
                'original_phone_hash': hashlib.sha256(
                    user_phone.encode()
                ).hexdigest(),
                'reason': 'user_request',
                'deleted_at': datetime.now().isoformat()
            }
        )
        
        return {
            'success': True,
            'message': """
✅ Seus dados foram excluídos.

Dados removidos:
• Histórico de conversas
• Preferências
• Listas de espera

Dados mantidos por obrigação legal (anonimizados):
• Registro de consultas realizadas (5 anos - CFM)

Você pode retornar a qualquer momento.
"""
        }
    
    def export_user_data(self, user_phone: str) -> str:
        """Art. 18, V - Portabilidade de dados"""
        data = self.provide_data_access(user_phone)
        
        # Exportar em formato estruturado (JSON)
        json_export = json.dumps(data, indent=2, ensure_ascii=False)
        
        # Enviar arquivo
        return {
            'format': 'JSON',
            'data': json_export,
            'message': """
📦 *Seus dados foram exportados*

Formato: JSON
Incluído:
• Dados pessoais
• Histórico de agendamentos
• Preferências

Você pode usar estes dados em outro sistema.
"""
        }
```

## 📊 Registro de Tratamento

### Base Legal (Art. 7º)

✅ **Consentimento (Art. 7º, I)**
- Consentimento explícito do titular
- Possibilidade de revogação a qualquer momento
- Registro do momento e forma de consentimento

```python
# Registro de consentimento
def register_consent(user_phone: str, consent_type: str) -> bool:
    """Registra consentimento do usuário"""
    consent_record = {
        'user_phone': user_phone,
        'consent_type': consent_type,
        'granted_at': datetime.now().isoformat(),
        'ip_address': get_user_ip(),  # Se aplicável
        'consent_text': CONSENT_MESSAGE,
        'version': '1.0'
    }
    
    redis.set(
        f"consent:{user_phone}",
        json.dumps(consent_record),
        ex=7 * 365 * 24 * 60 * 60  # 7 anos
    )
    
    log_audit(
        user_phone=user_phone,
        action='consent_granted',
        details=consent_record
    )
    
    return True
```

## 🔒 Segurança da Informação

### Medidas Implementadas

#### 1. Criptografia

```yaml
# Criptografia em trânsito
- HTTPS/TLS 1.3 para todas as comunicações
- Certificados SSL válidos (Let's Encrypt)
- HSTS habilitado

# Criptografia em repouso
- Redis com senha forte
- Dados sensíveis criptografados (Fernet)
- Backups criptografados (GPG)
```

#### 2. Controle de Acesso

```python
# RBAC - Role-Based Access Control
ROLES = {
    'admin': [
        'view_all_data',
        'delete_data',
        'configure_system',
        'view_logs'
    ],
    'operator': [
        'view_appointments',
        'reschedule_appointments',
        'cancel_appointments'
    ],
    'viewer': [
        'view_appointments',
        'view_metrics'
    ]
}

def check_permission(user: str, action: str) -> bool:
    """Verifica se usuário tem permissão"""
    user_role = get_user_role(user)
    return action in ROLES.get(user_role, [])
```

#### 3. Logs de Auditoria

```python
# Todos os acessos e modificações são logados
AUDIT_LOG_STRUCTURE = {
    'timestamp': 'ISO 8601',
    'user': 'username or system',
    'action': 'action type',
    'resource': 'resource affected',
    'ip_address': 'source IP',
    'user_agent': 'client info',
    'result': 'success/failure',
    'details': {}
}

# Retenção: 5 anos (Art. 37)
# Armazenamento: Imutável, criptografado
```

## ⚠️ Incidentes de Segurança

### Procedimento de Resposta

```python
def handle_security_incident(incident_type: str, details: Dict):
    """
    Procedimento para incidentes de segurança
    Art. 48 - Comunicação à ANPD
    """
    
    # 1. Conter o incidente
    contain_incident(incident_type)
    
    # 2. Avaliar impacto
    impact = assess_incident_impact(details)
    
    # 3. Notificar ANPD (se relevante)
    if impact['severity'] in ['high', 'critical']:
        notify_anpd(
            incident_type=incident_type,
            impact=impact,
            affected_users=impact['affected_count'],
            measures_taken=get_containment_measures()
        )
    
    # 4. Notificar titulares afetados
    if impact['affected_users']:
        for user in impact['affected_users']:
            notify_user_of_incident(user, incident_type, impact)
    
    # 5. Documentar incidente
    document_incident(incident_type, details, impact)
    
    # 6. Revisar e melhorar segurança
    schedule_security_review()
```

## 📝 Política de Retenção

### Prazos de Retenção

| Tipo de Dado | Prazo | Base Legal |
|--------------|-------|------------|
| Agendamentos realizados | 5 anos | CFM Resolução 1.821/2007 |
| Histórico de conversas | 90 dias | Operacional |
| Dados de cancelamento | 30 dias | Operacional |
| Logs de auditoria | 5 anos | LGPD Art. 37 |
| Registros de consentimento | 7 anos | LGPD |

```python
# Exclusão automática por TTL (Redis)
TTL_CONFIG = {
    'state': 600,              # 10 minutos (sessão)
    'appointment': 604800,     # 7 dias (agendamento futuro)
    'conversation': 7776000,   # 90 dias (histórico)
    'audit': 157680000,        # 5 anos (auditoria)
    'consent': 220752000       # 7 anos (consentimento)
}
```

## ✅ Checklist de Conformidade

### Pré-Implantação

- [ ] Realizar mapeamento de dados
- [ ] Definir base legal para tratamento
- [ ] Elaborar política de privacidade
- [ ] Implementar controles de acesso
- [ ] Configurar criptografia
- [ ] Implementar logs de auditoria
- [ ] Nomear encarregado (DPO)
- [ ] Treinar equipe em LGPD

### Operacional

- [ ] Coletar consentimento explícito
- [ ] Informar finalidade claramente
- [ ] Implementar direitos dos titulares
- [ ] Manter registros de tratamento
- [ ] Revisar segurança periodicamente
- [ ] Auditar logs regularmente
- [ ] Atualizar política de privacidade
- [ ] Testar procedimento de incidentes

### Documentação

- [ ] Política de Privacidade atualizada
- [ ] Registro de Tratamento completo
- [ ] Avaliação de Impacto (RIPD) se necessário
- [ ] Contratos com operadores (se houver)
- [ ] Procedimento de resposta a incidentes
- [ ] Documentação técnica de segurança
- [ ] Termos de consentimento

## 📞 Contatos LGPD

### Encarregado de Proteção de Dados (DPO)

```
Nome: [Seu DPO]
Email: dpo@clinica.com.br
Telefone: (11) 9999-9999

Responsabilidades:
• Orientar sobre LGPD
• Receber comunicações da ANPD
• Atender solicitações de titulares
• Coordenar resposta a incidentes
```

### ANPD - Autoridade Nacional

```
Site: https://www.gov.br/anpd
Ouvidoria: https://www.gov.br/anpd/pt-br/canais_atendimento
Telefone: Não disponível publicado
```

## 📚 Referências

- Lei nº 13.709/2018 (LGPD)
- Resolução CFM nº 1.821/2007 (Prontuários)
- ISO 27001 (Segurança da Informação)
- OWASP Top 10 (Segurança de Aplicações)

---

**Última atualização:** Dezembro 2024
**Versão:** 1.0
**Responsável:** [Seu Nome/Empresa]
