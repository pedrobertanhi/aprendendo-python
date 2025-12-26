"""
Redis State Machine Manager para Automação WhatsApp
Gerencia estados conversacionais e contexto de usuários
"""

import redis
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class UserState:
    """Representa o estado atual de um usuário"""
    state: str
    context: Dict[str, Any]
    last_update: str
    session_start: str


@dataclass
class Appointment:
    """Representa um agendamento"""
    id: str
    user_phone: str
    professional_id: int
    professional_name: str
    date: str
    time: str
    status: str  # scheduled, confirmed, cancelled, completed
    created_at: str
    notes: Optional[str] = None


class RedisStateManager:
    """Gerenciador de estado conversacional com Redis"""
    
    # Estados possíveis
    STATE_IDLE = 'IDLE'
    STATE_MENU = 'MENU_PRINCIPAL'
    STATE_APPOINTMENT_START = 'AGENDAMENTO_INICIO'
    STATE_APPOINTMENT_PROFESSIONAL = 'AGENDAMENTO_SELECAO_PROFISSIONAL'
    STATE_APPOINTMENT_DATE = 'AGENDAMENTO_SELECAO_DATA'
    STATE_APPOINTMENT_TIME = 'AGENDAMENTO_SELECAO_HORA'
    STATE_APPOINTMENT_CONFIRM = 'AGENDAMENTO_CONFIRMACAO'
    STATE_RESCHEDULE_START = 'REMARCACAO_INICIO'
    STATE_CANCEL_START = 'CANCELAMENTO_INICIO'
    STATE_CONFIRMATION_WAITING = 'CONFIRMACAO_AGUARDANDO_RESPOSTA'
    
    # TTLs
    SESSION_TTL = 600  # 10 minutos
    APPOINTMENT_TTL = 604800  # 7 dias
    RATE_LIMIT_TTL = 60  # 1 minuto
    
    def __init__(self, host: str = 'localhost', port: int = 6379, 
                 password: Optional[str] = None, db: int = 0):
        """
        Inicializa conexão com Redis
        
        Args:
            host: Host do Redis
            port: Porta do Redis
            password: Senha do Redis (opcional)
            db: Número do database (0-15)
        """
        self.client = redis.Redis(
            host=host,
            port=port,
            password=password,
            db=db,
            decode_responses=True
        )
        logger.info(f"Conectado ao Redis em {host}:{port}")
    
    def get_user_state(self, user_phone: str) -> UserState:
        """
        Busca o estado atual de um usuário
        
        Args:
            user_phone: Telefone do usuário (formato: 5511999999999)
        
        Returns:
            UserState com estado atual ou IDLE se não existir
        """
        key = f"state:{user_phone}"
        data = self.client.get(key)
        
        if not data:
            # Criar novo estado IDLE
            now = datetime.now().isoformat()
            return UserState(
                state=self.STATE_IDLE,
                context={},
                last_update=now,
                session_start=now
            )
        
        state_dict = json.loads(data)
        return UserState(**state_dict)
    
    def set_user_state(self, user_phone: str, state: str, 
                       context: Dict[str, Any] = None) -> bool:
        """
        Atualiza o estado de um usuário
        
        Args:
            user_phone: Telefone do usuário
            state: Novo estado
            context: Contexto adicional (opcional)
        
        Returns:
            True se sucesso
        """
        key = f"state:{user_phone}"
        
        # Buscar estado existente para manter session_start
        current = self.get_user_state(user_phone)
        
        user_state = UserState(
            state=state,
            context=context or current.context,
            last_update=datetime.now().isoformat(),
            session_start=current.session_start
        )
        
        self.client.setex(
            key,
            self.SESSION_TTL,
            json.dumps(asdict(user_state))
        )
        
        logger.info(f"Estado atualizado: {user_phone} -> {state}")
        return True
    
    def update_context(self, user_phone: str, context_update: Dict[str, Any]) -> bool:
        """
        Atualiza apenas o contexto mantendo o estado atual
        
        Args:
            user_phone: Telefone do usuário
            context_update: Dados para atualizar no contexto
        
        Returns:
            True se sucesso
        """
        current = self.get_user_state(user_phone)
        current.context.update(context_update)
        
        return self.set_user_state(
            user_phone,
            current.state,
            current.context
        )
    
    def reset_user_state(self, user_phone: str) -> bool:
        """
        Reseta o estado do usuário para IDLE
        
        Args:
            user_phone: Telefone do usuário
        
        Returns:
            True se sucesso
        """
        return self.set_user_state(user_phone, self.STATE_IDLE, {})
    
    def check_rate_limit(self, user_phone: str, max_messages: int = 10) -> bool:
        """
        Verifica se usuário está dentro do rate limit
        
        Args:
            user_phone: Telefone do usuário
            max_messages: Máximo de mensagens por minuto
        
        Returns:
            True se dentro do limite, False se excedido
        """
        key = f"ratelimit:{user_phone}"
        count = self.client.incr(key)
        
        if count == 1:
            self.client.expire(key, self.RATE_LIMIT_TTL)
        
        return count <= max_messages
    
    def save_appointment(self, appointment: Appointment) -> bool:
        """
        Salva um agendamento
        
        Args:
            appointment: Objeto Appointment
        
        Returns:
            True se sucesso
        """
        key = f"appointment:{appointment.id}"
        
        self.client.setex(
            key,
            self.APPOINTMENT_TTL,
            json.dumps(asdict(appointment))
        )
        
        # Indexar por usuário para busca rápida
        user_index_key = f"user_appointments:{appointment.user_phone}"
        self.client.sadd(user_index_key, appointment.id)
        self.client.expire(user_index_key, self.APPOINTMENT_TTL)
        
        logger.info(f"Agendamento salvo: {appointment.id}")
        return True
    
    def get_appointment(self, appointment_id: str) -> Optional[Appointment]:
        """
        Busca um agendamento por ID
        
        Args:
            appointment_id: ID do agendamento
        
        Returns:
            Appointment ou None se não encontrado
        """
        key = f"appointment:{appointment_id}"
        data = self.client.get(key)
        
        if not data:
            return None
        
        apt_dict = json.loads(data)
        return Appointment(**apt_dict)
    
    def get_user_appointments(self, user_phone: str, 
                            status: Optional[str] = None) -> List[Appointment]:
        """
        Busca todos os agendamentos de um usuário
        
        Args:
            user_phone: Telefone do usuário
            status: Filtrar por status (opcional)
        
        Returns:
            Lista de Appointments
        """
        user_index_key = f"user_appointments:{user_phone}"
        appointment_ids = self.client.smembers(user_index_key)
        
        appointments = []
        for apt_id in appointment_ids:
            appointment = self.get_appointment(apt_id)
            if appointment:
                if status is None or appointment.status == status:
                    appointments.append(appointment)
        
        return appointments
    
    def update_appointment_status(self, appointment_id: str, 
                                 new_status: str) -> bool:
        """
        Atualiza o status de um agendamento
        
        Args:
            appointment_id: ID do agendamento
            new_status: Novo status
        
        Returns:
            True se sucesso
        """
        appointment = self.get_appointment(appointment_id)
        if not appointment:
            logger.warning(f"Agendamento não encontrado: {appointment_id}")
            return False
        
        appointment.status = new_status
        return self.save_appointment(appointment)
    
    def add_to_waiting_list(self, professional_id: int, date: str, 
                           time: str, user_phone: str) -> int:
        """
        Adiciona usuário à lista de espera
        
        Args:
            professional_id: ID do profissional
            date: Data desejada
            time: Horário desejado
            user_phone: Telefone do usuário
        
        Returns:
            Posição na fila
        """
        key = f"waiting:{professional_id}:{date}:{time}"
        
        waiting_data = {
            'user_phone': user_phone,
            'added_at': datetime.now().isoformat()
        }
        
        position = self.client.rpush(key, json.dumps(waiting_data))
        self.client.expire(key, self.APPOINTMENT_TTL)
        
        logger.info(f"Adicionado à lista de espera: {user_phone} - Posição {position}")
        return position
    
    def get_waiting_list(self, professional_id: int, date: str, 
                        time: str) -> List[Dict[str, Any]]:
        """
        Busca lista de espera para um horário
        
        Args:
            professional_id: ID do profissional
            date: Data
            time: Horário
        
        Returns:
            Lista de usuários esperando
        """
        key = f"waiting:{professional_id}:{date}:{time}"
        waiting_list = self.client.lrange(key, 0, -1)
        
        return [json.loads(item) for item in waiting_list]
    
    def remove_from_waiting_list(self, professional_id: int, date: str,
                                 time: str, user_phone: str) -> bool:
        """
        Remove usuário da lista de espera
        
        Args:
            professional_id: ID do profissional
            date: Data
            time: Horário
            user_phone: Telefone do usuário
        
        Returns:
            True se removido
        """
        key = f"waiting:{professional_id}:{date}:{time}"
        waiting_list = self.get_waiting_list(professional_id, date, time)
        
        for item in waiting_list:
            if item['user_phone'] == user_phone:
                self.client.lrem(key, 1, json.dumps(item))
                logger.info(f"Removido da lista de espera: {user_phone}")
                return True
        
        return False
    
    def log_audit(self, user_phone: str, action: str, 
                  details: Dict[str, Any]) -> bool:
        """
        Registra ação para auditoria LGPD
        
        Args:
            user_phone: Telefone do usuário
            action: Tipo de ação
            details: Detalhes da ação
        
        Returns:
            True se sucesso
        """
        audit_log = {
            'timestamp': datetime.now().isoformat(),
            'user_phone': user_phone,
            'action': action,
            'details': details
        }
        
        self.client.lpush('audit:logs', json.dumps(audit_log))
        self.client.ltrim('audit:logs', 0, 9999)  # Manter últimas 10k
        
        return True
    
    def get_metrics(self, date: Optional[str] = None) -> Dict[str, int]:
        """
        Busca métricas do sistema
        
        Args:
            date: Data específica (YYYY-MM-DD) ou None para total
        
        Returns:
            Dicionário com métricas
        """
        if date:
            key_suffix = f":{date}"
        else:
            key_suffix = ""
        
        metrics = {
            'total_messages': int(self.client.get(f'metrics:total_messages{key_suffix}') or 0),
            'total_appointments': int(self.client.get(f'metrics:total_appointments{key_suffix}') or 0),
            'total_cancellations': int(self.client.get(f'metrics:total_cancellations{key_suffix}') or 0),
            'total_reschedules': int(self.client.get(f'metrics:total_reschedules{key_suffix}') or 0),
        }
        
        return metrics
    
    def increment_metric(self, metric_name: str, date: Optional[str] = None) -> int:
        """
        Incrementa uma métrica
        
        Args:
            metric_name: Nome da métrica
            date: Data específica (opcional)
        
        Returns:
            Novo valor da métrica
        """
        if date:
            key = f'metrics:{metric_name}:{date}'
        else:
            key = f'metrics:{metric_name}'
        
        new_value = self.client.incr(key)
        
        # Manter métricas por 90 dias
        if date:
            self.client.expire(key, 90 * 24 * 60 * 60)
        
        return new_value
    
    def delete_user_data(self, user_phone: str) -> bool:
        """
        Remove todos os dados de um usuário (LGPD - Direito ao esquecimento)
        
        Args:
            user_phone: Telefone do usuário
        
        Returns:
            True se sucesso
        """
        # Remover estado
        self.client.delete(f"state:{user_phone}")
        
        # Remover agendamentos
        appointment_ids = self.client.smembers(f"user_appointments:{user_phone}")
        for apt_id in appointment_ids:
            self.client.delete(f"appointment:{apt_id}")
        self.client.delete(f"user_appointments:{user_phone}")
        
        # Log de auditoria
        self.log_audit(
            user_phone,
            'data_deletion',
            {'reason': 'user_request', 'gdpr_compliance': True}
        )
        
        logger.info(f"Dados removidos para usuário: {user_phone}")
        return True
    
    def health_check(self) -> Dict[str, Any]:
        """
        Verifica saúde da conexão Redis
        
        Returns:
            Status e informações do Redis
        """
        try:
            info = self.client.info()
            
            return {
                'status': 'healthy',
                'connected': True,
                'version': info['redis_version'],
                'uptime_days': info['uptime_in_days'],
                'used_memory_human': info['used_memory_human'],
                'connected_clients': info['connected_clients'],
            }
        except Exception as e:
            logger.error(f"Health check falhou: {str(e)}")
            return {
                'status': 'unhealthy',
                'connected': False,
                'error': str(e)
            }


# Exemplo de uso
if __name__ == "__main__":
    # Inicializar
    manager = RedisStateManager(
        host='localhost',
        port=6379,
        password='sua_senha_aqui'
    )
    
    # Health check
    health = manager.health_check()
    print(f"Redis Status: {health}")
    
    # Testar fluxo
    user_phone = "5511999999999"
    
    # 1. Verificar estado inicial
    state = manager.get_user_state(user_phone)
    print(f"Estado inicial: {state.state}")
    
    # 2. Iniciar agendamento
    manager.set_user_state(user_phone, manager.STATE_APPOINTMENT_PROFESSIONAL)
    
    # 3. Atualizar contexto
    manager.update_context(user_phone, {
        'professional_id': 1,
        'professional_name': 'Dr. João Silva'
    })
    
    # 4. Criar agendamento
    appointment = Appointment(
        id='apt_123456',
        user_phone=user_phone,
        professional_id=1,
        professional_name='Dr. João Silva',
        date='2024-01-15',
        time='10:00',
        status='scheduled',
        created_at=datetime.now().isoformat()
    )
    manager.save_appointment(appointment)
    
    # 5. Buscar agendamentos do usuário
    user_appointments = manager.get_user_appointments(user_phone)
    print(f"Agendamentos: {len(user_appointments)}")
    
    # 6. Resetar estado
    manager.reset_user_state(user_phone)
    
    print("Teste concluído com sucesso!")
