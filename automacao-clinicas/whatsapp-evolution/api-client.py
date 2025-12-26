"""
Evolution API Client - Cliente Python para WhatsApp Evolution API
Facilita integração com WhatsApp Business via Evolution API
"""

import requests
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Tipos de mensagem suportados"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    BUTTONS = "buttons"
    LIST = "list"


@dataclass
class ButtonOption:
    """Opção de botão"""
    id: str
    text: str


@dataclass
class ListSection:
    """Seção de lista"""
    title: str
    rows: List[Dict[str, str]]


class EvolutionAPIClient:
    """Cliente para Evolution API - WhatsApp Integration"""
    
    def __init__(self, base_url: str, api_key: str, instance_name: str):
        """
        Inicializa cliente Evolution API
        
        Args:
            base_url: URL base da API (ex: https://api.seu-dominio.com.br)
            api_key: Chave de API
            instance_name: Nome da instância WhatsApp
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.instance_name = instance_name
        self.headers = {
            'apikey': api_key,
            'Content-Type': 'application/json'
        }
        logger.info(f"Evolution API Client inicializado: {instance_name}")
    
    def _make_request(self, method: str, endpoint: str, 
                     data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Faz requisição HTTP para API
        
        Args:
            method: Método HTTP (GET, POST, etc)
            endpoint: Endpoint da API
            data: Dados para enviar (opcional)
        
        Returns:
            Resposta da API
        
        Raises:
            requests.exceptions.RequestException: Erro na requisição
        """
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers, timeout=30)
            elif method == 'POST':
                response = requests.post(
                    url, 
                    headers=self.headers, 
                    json=data,
                    timeout=30
                )
            elif method == 'PUT':
                response = requests.put(
                    url,
                    headers=self.headers,
                    json=data,
                    timeout=30
                )
            elif method == 'DELETE':
                response = requests.delete(url, headers=self.headers, timeout=30)
            else:
                raise ValueError(f"Método HTTP inválido: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(
                f"Erro na requisição: {str(e)} | "
                f"Method: {method} | "
                f"URL: {url} | "
                f"Data: {data}"
            )
            raise
    
    def send_text(self, number: str, text: str, 
                  delay: Optional[int] = None) -> Dict[str, Any]:
        """
        Envia mensagem de texto
        
        Args:
            number: Número do destinatário (formato: 5511999999999)
            text: Texto da mensagem
            delay: Delay em milissegundos (opcional)
        
        Returns:
            Resposta da API com messageId
        """
        endpoint = f"message/sendText/{self.instance_name}"
        
        payload = {
            "number": number,
            "text": text
        }
        
        if delay:
            payload["delay"] = delay
        
        logger.info(f"Enviando mensagem de texto para {number}")
        return self._make_request('POST', endpoint, payload)
    
    def send_buttons(self, number: str, text: str, 
                    buttons: List[ButtonOption],
                    footer: Optional[str] = None) -> Dict[str, Any]:
        """
        Envia mensagem com botões interativos
        
        Args:
            number: Número do destinatário
            text: Texto da mensagem
            buttons: Lista de botões (máximo 3)
            footer: Texto do rodapé (opcional)
        
        Returns:
            Resposta da API
        """
        if len(buttons) > 3:
            raise ValueError("Máximo de 3 botões permitidos")
        
        endpoint = f"message/sendButtons/{self.instance_name}"
        
        payload = {
            "number": number,
            "text": text,
            "buttons": [
                {"id": btn.id, "text": btn.text}
                for btn in buttons
            ]
        }
        
        if footer:
            payload["footer"] = footer
        
        logger.info(f"Enviando mensagem com botões para {number}")
        return self._make_request('POST', endpoint, payload)
    
    def send_list(self, number: str, title: str, description: str,
                 button_text: str, sections: List[ListSection]) -> Dict[str, Any]:
        """
        Envia mensagem com lista interativa
        
        Args:
            number: Número do destinatário
            title: Título da mensagem
            description: Descrição da mensagem
            button_text: Texto do botão para abrir lista
            sections: Seções da lista
        
        Returns:
            Resposta da API
        """
        endpoint = f"message/sendList/{self.instance_name}"
        
        payload = {
            "number": number,
            "title": title,
            "description": description,
            "buttonText": button_text,
            "sections": [
                {
                    "title": section.title,
                    "rows": section.rows
                }
                for section in sections
            ]
        }
        
        logger.info(f"Enviando lista interativa para {number}")
        return self._make_request('POST', endpoint, payload)
    
    def send_media(self, number: str, media_type: MessageType,
                  media_url: str, caption: Optional[str] = None) -> Dict[str, Any]:
        """
        Envia mensagem com mídia (imagem, vídeo, áudio, documento)
        
        Args:
            number: Número do destinatário
            media_type: Tipo de mídia
            media_url: URL da mídia
            caption: Legenda (opcional)
        
        Returns:
            Resposta da API
        """
        if media_type == MessageType.TEXT:
            raise ValueError("Use send_text() para mensagens de texto")
        
        endpoint = f"message/send{media_type.value.capitalize()}/{self.instance_name}"
        
        payload = {
            "number": number,
            f"{media_type.value}": media_url
        }
        
        if caption and media_type in [MessageType.IMAGE, MessageType.VIDEO]:
            payload["caption"] = caption
        
        logger.info(f"Enviando {media_type.value} para {number}")
        return self._make_request('POST', endpoint, payload)
    
    def get_instance_status(self) -> Dict[str, Any]:
        """
        Verifica status da instância WhatsApp
        
        Returns:
            Status da instância (connected, disconnected, etc)
        """
        endpoint = f"instance/connectionState/{self.instance_name}"
        return self._make_request('GET', endpoint)
    
    def get_instance_info(self) -> Dict[str, Any]:
        """
        Busca informações da instância
        
        Returns:
            Informações detalhadas da instância
        """
        endpoint = f"instance/fetchInstances?instanceName={self.instance_name}"
        return self._make_request('GET', endpoint)
    
    def set_webhook(self, webhook_url: str, 
                   events: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Configura webhook para receber eventos
        
        Args:
            webhook_url: URL do webhook
            events: Lista de eventos para escutar (opcional)
        
        Returns:
            Confirmação da configuração
        """
        if events is None:
            events = [
                "messages.upsert",
                "messages.update",
                "connection.update"
            ]
        
        endpoint = f"webhook/set/{self.instance_name}"
        
        payload = {
            "url": webhook_url,
            "enabled": True,
            "events": events
        }
        
        logger.info(f"Configurando webhook: {webhook_url}")
        return self._make_request('POST', endpoint, payload)
    
    def check_number(self, number: str) -> Dict[str, Any]:
        """
        Verifica se número está registrado no WhatsApp
        
        Args:
            number: Número para verificar
        
        Returns:
            Informações sobre o número
        """
        endpoint = f"chat/checkNumberStatus/{self.instance_name}"
        
        payload = {
            "number": number
        }
        
        return self._make_request('POST', endpoint, payload)
    
    def mark_as_read(self, message_id: str) -> Dict[str, Any]:
        """
        Marca mensagem como lida
        
        Args:
            message_id: ID da mensagem
        
        Returns:
            Confirmação
        """
        endpoint = f"chat/markMessageAsRead/{self.instance_name}"
        
        payload = {
            "messageId": message_id
        }
        
        return self._make_request('POST', endpoint, payload)
    
    def send_presence(self, number: str, presence: str = "composing") -> Dict[str, Any]:
        """
        Envia status de presença (digitando, gravando áudio, etc)
        
        Args:
            number: Número do destinatário
            presence: Tipo de presença (composing, recording, available)
        
        Returns:
            Confirmação
        """
        endpoint = f"chat/sendPresence/{self.instance_name}"
        
        payload = {
            "number": number,
            "presence": presence,
            "delay": 3000  # 3 segundos
        }
        
        return self._make_request('POST', endpoint, payload)
    
    def get_profile_picture(self, number: str) -> Dict[str, Any]:
        """
        Busca foto de perfil de um número
        
        Args:
            number: Número do usuário
        
        Returns:
            URL da foto de perfil
        """
        endpoint = f"chat/getProfilePicture/{self.instance_name}"
        
        payload = {
            "number": number
        }
        
        return self._make_request('POST', endpoint, payload)


class MessageTemplates:
    """Templates de mensagens pré-formatadas para clínicas"""
    
    @staticmethod
    def welcome_message() -> str:
        """Mensagem de boas-vindas"""
        return """👋 Olá! Bem-vindo à *Clínica Saúde Total*

Como posso ajudar você hoje?

*1* - 📅 Agendar consulta
*2* - 🔄 Remarcar consulta  
*3* - ❌ Cancelar consulta
*4* - 📞 Falar com atendente

_Digite o número da opção desejada_"""
    
    @staticmethod
    def appointment_confirmation(professional: str, date: str, 
                               time: str, address: str) -> str:
        """Confirmação de agendamento"""
        return f"""✅ *Consulta agendada com sucesso!*

📋 *Detalhes da consulta:*
👨‍⚕️ Profissional: {professional}
📅 Data: {date}
🕐 Horário: {time}

📍 *Endereço:*
{address}

⚠️ *Importante:*
• Chegue 10 minutos antes
• Traga documentos e exames anteriores
• Em caso de atraso, avise pelo WhatsApp

💚 _Enviaremos uma confirmação 24h antes da consulta._"""
    
    @staticmethod
    def reminder_24h(professional: str, date: str, time: str) -> str:
        """Lembrete 24h antes"""
        return f"""🔔 *Lembrete de Consulta*

Você tem uma consulta agendada para *amanhã*:

👨‍⚕️ Profissional: {professional}
📅 Data: {date}
🕐 Horário: {time}

*Por favor, confirme sua presença:*

*1* - ✅ Confirmo presença
*2* - ❌ Preciso remarcar
*3* - 📞 Falar com atendente

_Aguardamos sua resposta._"""
    
    @staticmethod
    def cancellation_confirmation(professional: str, date: str, time: str) -> str:
        """Confirmação de cancelamento"""
        return f"""✅ *Consulta cancelada com sucesso*

📋 Consulta cancelada:
👨‍⚕️ Profissional: {professional}
📅 Data: {date}
🕐 Horário: {time}

Se precisar agendar novamente, é só me chamar! 😊"""
    
    @staticmethod
    def waiting_list_notification(professional: str, date: str, time: str) -> str:
        """Notificação de vaga na lista de espera"""
        return f"""🎉 *Boa notícia!*

Uma vaga foi aberta para:

👨‍⚕️ Profissional: {professional}
📅 Data: {date}
🕐 Horário: {time}

*Você tem interesse neste horário?*

*1* - ✅ Sim, quero agendar
*2* - ❌ Não tenho interesse

⏰ _Você tem 30 minutos para responder_"""
    
    @staticmethod
    def error_message() -> str:
        """Mensagem de erro genérica"""
        return """😔 Desculpe, encontramos um problema temporário.

Nossa equipe foi notificada e já está trabalhando na solução.

Por favor, tente novamente em alguns minutos ou entre em contato:
📞 (11) 99999-9999

_Pedimos desculpas pelo inconveniente._"""
    
    @staticmethod
    def rate_limit_exceeded() -> str:
        """Mensagem quando usuário excede rate limit"""
        return """⚠️ Você está enviando mensagens muito rapidamente.

Por favor, aguarde um momento e tente novamente.

_Obrigado pela compreensão!_ 😊"""
    
    @staticmethod
    def invalid_option() -> str:
        """Mensagem para opção inválida"""
        return """❌ Opção inválida.

Por favor, escolha uma das opções apresentadas.

_Digite o número correspondente à opção desejada._"""
    
    @staticmethod
    def session_timeout() -> str:
        """Mensagem quando sessão expira"""
        return """⏰ Sua sessão expirou por inatividade.

Não se preocupe! Digite qualquer mensagem para começarmos novamente.

_Estou aqui para ajudar!_ 😊"""


# Exemplo de uso
if __name__ == "__main__":
    # Configurar cliente
    client = EvolutionAPIClient(
        base_url="https://api.seu-dominio.com.br",
        api_key="sua_chave_api_aqui",
        instance_name="clinica-principal"
    )
    
    # Verificar status da instância
    try:
        status = client.get_instance_status()
        print(f"Status da instância: {status}")
        
        # Enviar mensagem de teste
        test_number = "5511999999999"
        
        # Mensagem de texto simples
        response = client.send_text(
            number=test_number,
            text=MessageTemplates.welcome_message()
        )
        print(f"Mensagem enviada: {response}")
        
        # Enviar botões
        buttons = [
            ButtonOption(id="1", text="Agendar"),
            ButtonOption(id="2", text="Remarcar"),
            ButtonOption(id="3", text="Cancelar")
        ]
        
        response = client.send_buttons(
            number=test_number,
            text="Como posso ajudar?",
            buttons=buttons,
            footer="Clínica Saúde Total"
        )
        print(f"Botões enviados: {response}")
        
    except Exception as e:
        print(f"Erro: {str(e)}")
