"""Comando para popular dados de demonstração no app exemplo."""

from datetime import date, timedelta
from decimal import Decimal
import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.exemplo.models import CategoriaChoices, ItemExemplo, StatusChoices

Usuario = get_user_model()

EXEMPLOS_TITULOS = [
    ("Aquisição de estações de trabalho de alto desempenho", "Renovação do parque computacional para analistas de dados.", CategoriaChoices.OPERACIONAL, StatusChoices.CONCLUIDO, Decimal("185400.00"), 30),
    ("Modernização da infraestrutura de backup em nuvem", "Contratação de armazenamento redundante com criptografia ponta a ponta.", CategoriaChoices.ESTRATEGICO, StatusChoices.EM_ANDAMENTO, Decimal("94300.50"), 45),
    ("Consultoria em conformidade e segurança da informação", "Auditoria de processos internos e adequação às normas vigentes.", CategoriaChoices.ADMINISTRATIVO, StatusChoices.EM_ANDAMENTO, Decimal("62000.00"), 60),
    ("Assinatura de plataforma corporativa de BI e analytics", "Licenciamento anual de ferramentas de visualização e apoio à decisão.", CategoriaChoices.FINANCEIRO, StatusChoices.CONCLUIDO, Decimal("48750.00"), -15),
    ("Capacitação da equipe em governança e gestão pública", "Treinamento especializado para servidores e gestores de projetos.", CategoriaChoices.ADMINISTRATIVO, StatusChoices.RASCUNHO, Decimal("18200.00"), 90),
    ("Desenvolvimento do portal integrado de serviços", "Mapeamento e digitalização dos fluxos de atendimento ao cidadão.", CategoriaChoices.ESTRATEGICO, StatusChoices.EM_ANDAMENTO, Decimal("210000.00"), 120),
    ("Reforma ergonômica dos postos de atendimento", "Substituição de mobiliário e adequação às normas regulamentadoras.", CategoriaChoices.OPERACIONAL, StatusChoices.CONCLUIDO, Decimal("35400.00"), -40),
    ("Auditoria contábil independente do exercício anterior", "Contratação de empresa de auditoria para emissão de parecer sobre as demonstrações.", CategoriaChoices.FINANCEIRO, StatusChoices.CONCLUIDO, Decimal("78000.00"), -10),
    ("Implantação do sistema de protocolo digital e tramitação", "Eliminação de processos em papel e integração com o barramento do governo.", CategoriaChoices.ESTRATEGICO, StatusChoices.RASCUNHO, Decimal("145000.00"), 180),
    ("Aquisição de licenças de software de produtividade", "Renovação anual do pacote de aplicativos de escritório para colaboradores.", CategoriaChoices.OPERACIONAL, StatusChoices.CANCELADO, Decimal("42900.00"), 15),
    ("Contratação de link dedicado redundante de internet", "Garantia de alta disponibilidade para os serviços web e portais públicos.", CategoriaChoices.OPERACIONAL, StatusChoices.CONCLUIDO, Decimal("28800.00"), -60),
    ("Revisão do planejamento estratégico institucional", "Facilitação de oficinas de trabalho e consolidação dos indicadores de desempenho.", CategoriaChoices.ESTRATEGICO, StatusChoices.EM_ANDAMENTO, Decimal("55000.00"), 75),
    ("Manutenção preventiva e corretiva de nobreaks e geradores", "Contrato continuado de engenharia elétrica para o datacenter.", CategoriaChoices.OPERACIONAL, StatusChoices.EM_ANDAMENTO, Decimal("39600.00"), 30),
    ("Elaboração do relatório de gestão e sustentabilidade", "Diagramação, revisão técnica e publicação do balanço social e financeiro.", CategoriaChoices.ADMINISTRATIVO, StatusChoices.CONCLUIDO, Decimal("24500.00"), -5),
    ("Aquisição de switches gerenciáveis de borda", "Atualização da infraestrutura de rede local com suporte a PoE+ e 10GbE.", CategoriaChoices.OPERACIONAL, StatusChoices.RASCUNHO, Decimal("86200.00"), 105),
    ("Contratação de solução de endpoint detection and response (EDR)", "Proteção avançada contra ameaças cibernéticas e monitoramento contínuo.", CategoriaChoices.ESTRATEGICO, StatusChoices.EM_ANDAMENTO, Decimal("112000.00"), 45),
    ("Campanha institucional de conscientização em cibersegurança", "Workshops interativos, simulações de phishing e materiais educativos.", CategoriaChoices.ADMINISTRATIVO, StatusChoices.CONCLUIDO, Decimal("15000.00"), -20),
    ("Serviços de tradução e revisão de publicações técnicas", "Versão bilíngue de manuais e pronunciamentos contábeis internacionais.", CategoriaChoices.FINANCEIRO, StatusChoices.CANCELADO, Decimal("19800.00"), -30),
    ("Contratação de cofre de senhas corporativo com auditoria", "Gestão centralizada de credenciais privilegiadas e segredos de infraestrutura.", CategoriaChoices.ESTRATEGICO, StatusChoices.RASCUNHO, Decimal("37500.00"), 150),
    ("Aquisição de servidores rack para virtualização de ambientes", "Expansão da capacidade de processamento do cluster de produção.", CategoriaChoices.OPERACIONAL, StatusChoices.EM_ANDAMENTO, Decimal("230000.00"), 60),
    ("Consultoria para implementação de LGPD e privacidade", "Mapeamento de inventário de dados pessoais e elaboração de RIPD.", CategoriaChoices.ADMINISTRATIVO, StatusChoices.CONCLUIDO, Decimal("68000.00"), -90),
    ("Renovação da apólice de seguro patrimonial", "Cobertura de equipamentos de TI, instalações e responsabilidade civil.", CategoriaChoices.FINANCEIRO, StatusChoices.CONCLUIDO, Decimal("52000.00"), -15),
    ("Contratação de plataforma de envio massivo de notificações", "Comunicação tempestiva com profissionais registrados via e-mail e SMS.", CategoriaChoices.OPERACIONAL, StatusChoices.RASCUNHO, Decimal("26400.00"), 135),
    ("Estudo de viabilidade para eficiência energética predial", "Diagnóstico de consumo elétrico e projeto de geração fotovoltaica.", CategoriaChoices.ESTRATEGICO, StatusChoices.RASCUNHO, Decimal("41000.00"), 210),
    ("Serviços de gravação e transmissão de sessões plenárias", "Equipamentos audiovisuais e equipe técnica para transmissões ao vivo.", CategoriaChoices.ADMINISTRATIVO, StatusChoices.EM_ANDAMENTO, Decimal("88000.00"), 40),
]


class Command(BaseCommand):
    help = "Popula dados de exemplo realistas para o app apps/exemplo"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limpar",
            action="store_true",
            help="Remove todos os itens de exemplo existentes antes de popular",
        )
        parser.add_argument(
            "--quantidade",
            type=int,
            default=25,
            help="Quantidade de itens a serem criados (padrão: 25)",
        )

    def handle(self, *args, **options):
        limpar = options.get("limpar", False)
        quantidade = options.get("quantidade", 25)

        if limpar:
            qtd_removida, _ = ItemExemplo.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f"Removidos {qtd_removida} registros existentes do ItemExemplo.")
            )

        usuario_padrao = Usuario.objects.filter(is_superuser=True).first() or Usuario.objects.first()

        criados = 0
        hoje = date.today()

        # Cicla pelos dados base enriquecidos
        for i in range(quantidade):
            indice = i % len(EXEMPLOS_TITULOS)
            titulo_base, desc_base, cat, stat, valor_base, dias_prazo = EXEMPLOS_TITULOS[indice]

            # Se passar da lista básica, adiciona sufixo numérico para variar
            if i >= len(EXEMPLOS_TITULOS):
                sufixo = f" (Lote {(i // len(EXEMPLOS_TITULOS)) + 1} - #{i + 1})"
                titulo = f"{titulo_base}{sufixo}"
                # Varia o valor em ±15%
                fator = Decimal(str(round(0.85 + (0.30 * random.random()), 2)))
                valor = (valor_base * fator).quantize(Decimal("0.01"))
            else:
                titulo = titulo_base
                valor = valor_base

            prazo = hoje + timedelta(days=dias_prazo) if dias_prazo is not None else None

            item = ItemExemplo.objects.create(
                titulo=titulo,
                descricao=desc_base,
                categoria=cat,
                status=stat,
                valor=valor,
                prazo=prazo,
                ativo=True,
                criado_por=usuario_padrao,
            )
            criados += 1

        self.stdout.write(
            self.style.SUCCESS(f"Sucesso: {criados} itens de exemplo foram criados com sucesso!")
        )
