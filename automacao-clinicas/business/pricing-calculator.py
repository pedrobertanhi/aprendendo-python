"""
Calculadora de Precificação - Automações WhatsApp para Clínicas
Auxilia na definição de preços baseado em complexidade e valor
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum
import json


class ComplexityLevel(Enum):
    """Níveis de complexidade de implementação"""
    BASIC = "basic"           # Setup básico, 1 profissional, agendamento simples
    INTERMEDIATE = "intermediate"  # Múltiplos profissionais, remarcação, confirmação
    ADVANCED = "advanced"     # Multi-unidades, integrações externas, IA
    ENTERPRISE = "enterprise"  # White-label, múltiplos clientes, SLA alto


class IntegrationType(Enum):
    """Tipos de integração"""
    GOOGLE_CALENDAR = "google_calendar"
    DATABASE = "database"
    ERP_MEDICAL = "erp_medical"  # Tasy, MV, Philips, etc
    PAYMENT_GATEWAY = "payment_gateway"
    CRM = "crm"
    ANALYTICS = "analytics"


@dataclass
class PricingFactors:
    """Fatores que influenciam precificação"""
    complexity: ComplexityLevel
    num_professionals: int
    num_units: int  # Unidades/filiais
    monthly_messages: int  # Estimativa de mensagens/mês
    integrations: List[IntegrationType]
    custom_workflows: int  # Número de workflows customizados
    sla_required: bool  # Necessidade de SLA
    white_label: bool  # Revenda white-label
    multi_tenant: bool  # Suporte multi-tenant


class PricingCalculator:
    """Calculadora de preços para automações"""
    
    # Preços base
    BASE_SETUP_PRICES = {
        ComplexityLevel.BASIC: 1500,
        ComplexityLevel.INTERMEDIATE: 3500,
        ComplexityLevel.ADVANCED: 7000,
        ComplexityLevel.ENTERPRISE: 15000
    }
    
    BASE_MONTHLY_PRICES = {
        ComplexityLevel.BASIC: 197,
        ComplexityLevel.INTERMEDIATE: 497,
        ComplexityLevel.ADVANCED: 997,
        ComplexityLevel.ENTERPRISE: 2500
    }
    
    # Custos adicionais
    COST_PER_PROFESSIONAL = 50  # Por profissional/mês além do primeiro
    COST_PER_UNIT = 100  # Por unidade/mês além da primeira
    COST_PER_1000_MESSAGES = 50  # Por 1000 mensagens além do incluído
    
    INTEGRATION_COSTS = {
        IntegrationType.GOOGLE_CALENDAR: 200,  # Setup único
        IntegrationType.DATABASE: 500,
        IntegrationType.ERP_MEDICAL: 2000,
        IntegrationType.PAYMENT_GATEWAY: 800,
        IntegrationType.CRM: 600,
        IntegrationType.ANALYTICS: 400
    }
    
    INTEGRATION_MONTHLY = {
        IntegrationType.GOOGLE_CALENDAR: 0,
        IntegrationType.DATABASE: 50,
        IntegrationType.ERP_MEDICAL: 300,
        IntegrationType.PAYMENT_GATEWAY: 100,
        IntegrationType.CRM: 80,
        IntegrationType.ANALYTICS: 50
    }
    
    # Mensagens incluídas por plano
    INCLUDED_MESSAGES = {
        ComplexityLevel.BASIC: 1000,
        ComplexityLevel.INTERMEDIATE: 3000,
        ComplexityLevel.ADVANCED: 10000,
        ComplexityLevel.ENTERPRISE: 50000
    }
    
    def __init__(self):
        """Inicializa calculadora"""
        self.infrastructure_cost = 60  # VPS + domínio
        self.support_cost_percentage = 0.15  # 15% para suporte
    
    def calculate_setup_cost(self, factors: PricingFactors) -> Dict[str, Any]:
        """
        Calcula custo de setup inicial
        
        Args:
            factors: Fatores de precificação
        
        Returns:
            Breakdown detalhado do custo de setup
        """
        # Custo base
        base_cost = self.BASE_SETUP_PRICES[factors.complexity]
        
        # Custos de integrações
        integration_cost = sum(
            self.INTEGRATION_COSTS[integration]
            for integration in factors.integrations
        )
        
        # Workflows customizados (R$ 500 por workflow além dos padrões)
        standard_workflows = 5  # Agendamento, confirmação, remarcação, cancelamento, lista espera
        custom_workflow_cost = max(0, factors.custom_workflows - standard_workflows) * 500
        
        # SLA com garantia
        sla_cost = 1000 if factors.sla_required else 0
        
        # White-label (licenciamento)
        white_label_cost = 10000 if factors.white_label else 0
        
        # Multi-tenant (arquitetura mais complexa)
        multi_tenant_cost = 3000 if factors.multi_tenant else 0
        
        total_setup = (
            base_cost +
            integration_cost +
            custom_workflow_cost +
            sla_cost +
            white_label_cost +
            multi_tenant_cost
        )
        
        return {
            'base_cost': base_cost,
            'integration_cost': integration_cost,
            'custom_workflow_cost': custom_workflow_cost,
            'sla_cost': sla_cost,
            'white_label_cost': white_label_cost,
            'multi_tenant_cost': multi_tenant_cost,
            'total_setup': total_setup,
            'breakdown': {
                'Base setup': base_cost,
                'Integrações': integration_cost,
                'Workflows customizados': custom_workflow_cost,
                'SLA garantido': sla_cost,
                'Licença white-label': white_label_cost,
                'Arquitetura multi-tenant': multi_tenant_cost
            }
        }
    
    def calculate_monthly_cost(self, factors: PricingFactors) -> Dict[str, Any]:
        """
        Calcula custo mensal recorrente
        
        Args:
            factors: Fatores de precificação
        
        Returns:
            Breakdown detalhado do custo mensal
        """
        # Custo base
        base_monthly = self.BASE_MONTHLY_PRICES[factors.complexity]
        
        # Profissionais adicionais
        additional_professionals = max(0, factors.num_professionals - 1)
        professional_cost = additional_professionals * self.COST_PER_PROFESSIONAL
        
        # Unidades adicionais
        additional_units = max(0, factors.num_units - 1)
        unit_cost = additional_units * self.COST_PER_UNIT
        
        # Mensagens excedentes
        included_messages = self.INCLUDED_MESSAGES[factors.complexity]
        excess_messages = max(0, factors.monthly_messages - included_messages)
        message_cost = (excess_messages / 1000) * self.COST_PER_1000_MESSAGES
        
        # Integrações (custo mensal)
        integration_monthly = sum(
            self.INTEGRATION_MONTHLY[integration]
            for integration in factors.integrations
        )
        
        # Infraestrutura
        infrastructure_cost = self.infrastructure_cost
        
        # Suporte premium (se SLA)
        support_cost = base_monthly * self.support_cost_percentage if factors.sla_required else 0
        
        total_monthly = (
            base_monthly +
            professional_cost +
            unit_cost +
            message_cost +
            integration_monthly +
            infrastructure_cost +
            support_cost
        )
        
        return {
            'base_monthly': base_monthly,
            'professional_cost': professional_cost,
            'unit_cost': unit_cost,
            'message_cost': message_cost,
            'integration_monthly': integration_monthly,
            'infrastructure_cost': infrastructure_cost,
            'support_cost': support_cost,
            'total_monthly': total_monthly,
            'breakdown': {
                'Plano base': base_monthly,
                'Profissionais adicionais': professional_cost,
                'Unidades adicionais': unit_cost,
                'Mensagens excedentes': message_cost,
                'Integrações': integration_monthly,
                'Infraestrutura (VPS+SSL)': infrastructure_cost,
                'Suporte premium': support_cost
            },
            'included_messages': self.INCLUDED_MESSAGES[factors.complexity],
            'used_messages': factors.monthly_messages
        }
    
    def calculate_roi(self, monthly_cost: float, clinic_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcula ROI esperado para a clínica
        
        Args:
            monthly_cost: Custo mensal do sistema
            clinic_data: Dados da clínica (consultas/dia, valor médio, etc)
        
        Returns:
            Análise de ROI
        """
        # Dados da clínica
        consultations_per_day = clinic_data.get('consultations_per_day', 50)
        avg_consultation_value = clinic_data.get('avg_consultation_value', 200)
        working_days_month = clinic_data.get('working_days_month', 22)
        
        # Cálculos
        monthly_consultations = consultations_per_day * working_days_month
        monthly_revenue = monthly_consultations * avg_consultation_value
        
        # Benefícios estimados
        no_show_reduction = 0.20  # 20% redução de no-show
        no_show_current = clinic_data.get('no_show_rate', 0.15)  # 15% atual
        no_show_prevented = monthly_consultations * no_show_current * no_show_reduction
        
        revenue_from_no_show = no_show_prevented * avg_consultation_value
        
        # Economia de tempo
        hours_saved_per_week = clinic_data.get('admin_hours_per_week', 10)
        hourly_rate = clinic_data.get('admin_hourly_rate', 50)
        monthly_time_savings = hours_saved_per_week * 4 * hourly_rate
        
        # Aumento de agendamentos (agenda otimizada)
        capacity_increase = 0.10  # 10% mais eficiente
        additional_consultations = monthly_consultations * capacity_increase
        revenue_from_increase = additional_consultations * avg_consultation_value
        
        # Total de benefícios
        total_monthly_benefit = (
            revenue_from_no_show +
            monthly_time_savings +
            revenue_from_increase
        )
        
        # ROI
        net_benefit = total_monthly_benefit - monthly_cost
        roi_percentage = (net_benefit / monthly_cost) * 100 if monthly_cost > 0 else 0
        payback_months = monthly_cost / net_benefit if net_benefit > 0 else None  # None indica que não há retorno
        
        return {
            'monthly_cost': monthly_cost,
            'monthly_benefit': total_monthly_benefit,
            'net_benefit': net_benefit,
            'roi_percentage': roi_percentage,
            'payback_months': payback_months,
            'breakdown': {
                'Redução de no-show': revenue_from_no_show,
                'Economia de tempo administrativo': monthly_time_savings,
                'Aumento de capacidade': revenue_from_increase
            },
            'annual_benefit': total_monthly_benefit * 12,
            'annual_cost': monthly_cost * 12
        }
    
    def generate_proposal(self, factors: PricingFactors, 
                         clinic_data: Dict[str, Any]) -> str:
        """
        Gera proposta comercial formatada
        
        Args:
            factors: Fatores de precificação
            clinic_data: Dados da clínica
        
        Returns:
            Proposta formatada em texto
        """
        setup = self.calculate_setup_cost(factors)
        monthly = self.calculate_monthly_cost(factors)
        roi = self.calculate_roi(monthly['total_monthly'], clinic_data)
        
        proposal = f"""
═══════════════════════════════════════════════════════
    PROPOSTA COMERCIAL - AUTOMAÇÃO WHATSAPP
═══════════════════════════════════════════════════════

📋 RESUMO DA SOLUÇÃO
───────────────────────────────────────────────────────
• Complexidade: {factors.complexity.value.upper()}
• Profissionais: {factors.num_professionals}
• Unidades: {factors.num_units}
• Mensagens/mês: {factors.monthly_messages:,}
• Integrações: {len(factors.integrations)}

💰 INVESTIMENTO
───────────────────────────────────────────────────────

SETUP INICIAL (uma vez):
"""
        
        for item, value in setup['breakdown'].items():
            if value > 0:
                proposal += f"  • {item}: R$ {value:,.2f}\n"
        
        proposal += f"\n  ➤ TOTAL SETUP: R$ {setup['total_setup']:,.2f}\n"
        
        proposal += f"""
MENSALIDADE RECORRENTE:
"""
        
        for item, value in monthly['breakdown'].items():
            if value > 0:
                proposal += f"  • {item}: R$ {value:,.2f}\n"
        
        proposal += f"\n  ➤ TOTAL MENSAL: R$ {monthly['total_monthly']:,.2f}\n"
        
        proposal += f"""
📊 ANÁLISE DE RETORNO (ROI)
───────────────────────────────────────────────────────

BENEFÍCIOS MENSAIS ESTIMADOS:
"""
        
        for item, value in roi['breakdown'].items():
            proposal += f"  • {item}: R$ {value:,.2f}\n"
        
        proposal += f"""
  ➤ TOTAL BENEFÍCIO/MÊS: R$ {roi['monthly_benefit']:,.2f}

RESULTADO:
  • Benefício líquido/mês: R$ {roi['net_benefit']:,.2f}
  • ROI: {roi['roi_percentage']:.1f}%
  • Payback: {roi['payback_months']:.1f} meses
  
  • Benefício anual: R$ {roi['annual_benefit']:,.2f}
  • Investimento anual: R$ {roi['annual_cost']:,.2f}

✅ INCLUSO NA SOLUÇÃO
───────────────────────────────────────────────────────
  ✓ Infraestrutura completa (n8n + Evolution API + Redis)
  ✓ Workflows de agendamento, confirmação e remarcação
  ✓ Gerenciamento de estado conversacional
  ✓ Dashboard de métricas e relatórios
  ✓ Compliance LGPD
  ✓ Backup automático diário
  ✓ Monitoramento 24/7
  ✓ Documentação técnica completa
  ✓ Treinamento da equipe (2h)
"""
        
        if factors.sla_required:
            proposal += """
  ✓ SLA 99.5% uptime garantido
  ✓ Suporte prioritário
  ✓ Resposta em até 2h úteis
"""
        
        proposal += """
⚠️ CONDIÇÕES
───────────────────────────────────────────────────────
  • Setup: 50% na assinatura, 50% na entrega
  • Mensalidade: Pagamento antecipado mensal
  • Prazo de implementação: 7-15 dias úteis
  • Validade da proposta: 15 dias

═══════════════════════════════════════════════════════
        """
        
        return proposal


# Exemplo de uso
if __name__ == "__main__":
    # Configurar calculadora
    calculator = PricingCalculator()
    
    # Exemplo 1: Clínica pequena
    print("=" * 60)
    print("EXEMPLO 1: CLÍNICA PEQUENA")
    print("=" * 60)
    
    factors_small = PricingFactors(
        complexity=ComplexityLevel.BASIC,
        num_professionals=2,
        num_units=1,
        monthly_messages=800,
        integrations=[IntegrationType.GOOGLE_CALENDAR],
        custom_workflows=5,
        sla_required=False,
        white_label=False,
        multi_tenant=False
    )
    
    clinic_data_small = {
        'consultations_per_day': 20,
        'avg_consultation_value': 150,
        'working_days_month': 22,
        'no_show_rate': 0.15,
        'admin_hours_per_week': 8,
        'admin_hourly_rate': 40
    }
    
    proposal_small = calculator.generate_proposal(factors_small, clinic_data_small)
    print(proposal_small)
    
    # Exemplo 2: Clínica grande
    print("\n" + "=" * 60)
    print("EXEMPLO 2: CLÍNICA GRANDE COM MÚLTIPLAS UNIDADES")
    print("=" * 60)
    
    factors_large = PricingFactors(
        complexity=ComplexityLevel.ADVANCED,
        num_professionals=15,
        num_units=3,
        monthly_messages=8000,
        integrations=[
            IntegrationType.GOOGLE_CALENDAR,
            IntegrationType.DATABASE,
            IntegrationType.ERP_MEDICAL,
            IntegrationType.ANALYTICS
        ],
        custom_workflows=10,
        sla_required=True,
        white_label=False,
        multi_tenant=False
    )
    
    clinic_data_large = {
        'consultations_per_day': 80,
        'avg_consultation_value': 250,
        'working_days_month': 22,
        'no_show_rate': 0.12,
        'admin_hours_per_week': 20,
        'admin_hourly_rate': 60
    }
    
    proposal_large = calculator.generate_proposal(factors_large, clinic_data_large)
    print(proposal_large)
    
    # Exemplo 3: White-label para revenda
    print("\n" + "=" * 60)
    print("EXEMPLO 3: WHITE-LABEL PARA REVENDA")
    print("=" * 60)
    
    factors_whitelabel = PricingFactors(
        complexity=ComplexityLevel.ENTERPRISE,
        num_professionals=0,  # Não aplicável
        num_units=0,
        monthly_messages=0,
        integrations=[],
        custom_workflows=15,
        sla_required=True,
        white_label=True,
        multi_tenant=True
    )
    
    setup_wl = calculator.calculate_setup_cost(factors_whitelabel)
    monthly_wl = calculator.calculate_monthly_cost(factors_whitelabel)
    
    print(f"""
Licença White-Label:
  • Setup único: R$ {setup_wl['total_setup']:,.2f}
  • Mensalidade base: R$ {monthly_wl['total_monthly']:,.2f}
  
Modelo de revenda sugerido:
  • Markup: 50-100%
  • Preço revenda (setup): R$ {setup_wl['total_setup'] * 1.5:,.2f} - R$ {setup_wl['total_setup'] * 2:,.2f}
  • Preço revenda (mensal): R$ {monthly_wl['total_monthly'] * 1.5:,.2f} - R$ {monthly_wl['total_monthly'] * 2:,.2f}
  • Margem líquida estimada: 40-60%
    """)
