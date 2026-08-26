"""Comando para popular dados de demonstração no app de diárias e passagens.

Idempotente por construção: a lista de viagens é fixa (sem sorteio) e a
inserção usa ``get_or_create`` chaveado por (servidor, destino, data de
início) — rodar o comando duas vezes não duplica registro nenhum.
"""

from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.diarias.models import StatusChoices, Viagem

# (servidor, destino, deslocamento em dias do início, duração em dias,
#  motivo, valor de diárias, valor de passagens, status)
VIAGENS_BASE = [
    ("Ana Beatriz Nogueira", "Brasília/DF", -60, 3, "Participação na reunião plenária ordinária do Conselho.", Decimal("2530.50"), Decimal("1890.00"), StatusChoices.PAGA),
    ("Carlos Eduardo Menezes", "São Paulo/SP", -45, 2, "Fiscalização de organizações contábeis na jurisdição.", Decimal("1687.00"), Decimal("1245.90"), StatusChoices.PAGA),
    ("Mariana Duarte Sales", "Belo Horizonte/MG", -30, 4, "Capacitação de fiscais no novo sistema de registro profissional.", Decimal("3374.00"), Decimal("980.45"), StatusChoices.PAGA),
    ("João Pedro Vasconcelos", "Recife/PE", -21, 2, "Auditoria de prestação de contas do conselho regional.", Decimal("1687.00"), Decimal("1560.30"), StatusChoices.PAGA),
    ("Luciana Freire Cardoso", "Porto Alegre/RS", -14, 3, "Seminário regional de educação continuada para a classe contábil.", Decimal("2530.50"), Decimal("1720.00"), StatusChoices.APROVADA),
    ("Rafael Antunes Barbosa", "Salvador/BA", -7, 2, "Reunião da comissão de tomada de contas especial.", Decimal("1687.00"), Decimal("1310.75"), StatusChoices.APROVADA),
    ("Fernanda Lopes Siqueira", "Manaus/AM", 0, 5, "Fiscalização itinerante em municípios do interior do estado.", Decimal("4217.50"), Decimal("2845.60"), StatusChoices.APROVADA),
    ("Gustavo Henrique Prado", "Curitiba/PR", 7, 2, "Plenária extraordinária sobre normas brasileiras de contabilidade.", Decimal("1687.00"), Decimal("1120.00"), StatusChoices.APROVADA),
    ("Patrícia Ramos Bittencourt", "Fortaleza/CE", 14, 3, "Capacitação em mediação e arbitragem para conselheiros.", Decimal("2530.50"), Decimal("1495.20"), StatusChoices.SOLICITADA),
    ("Tiago Almeida Rocha", "Goiânia/GO", 21, 2, "Acompanhamento do exame de suficiência na seccional.", Decimal("1687.00"), Decimal("875.40"), StatusChoices.SOLICITADA),
    ("Camila Vieira Andrade", "Belém/PA", 30, 4, "Fiscalização conjunta com a comissão de ética e disciplina.", Decimal("3374.00"), Decimal("2210.90"), StatusChoices.SOLICITADA),
    ("Rodrigo Paiva Castelo", "Florianópolis/SC", 45, 3, "Encontro nacional de coordenadores de desenvolvimento profissional.", Decimal("2530.50"), Decimal("1385.00"), StatusChoices.SOLICITADA),
    ("Helena Martins Queiroz", "Vitória/ES", 60, 2, "Plenária temática sobre contabilidade aplicada ao setor público.", Decimal("1687.00"), Decimal("990.60"), StatusChoices.SOLICITADA),
    ("Bruno César Tavares", "Cuiabá/MT", -90, 3, "Capacitação da equipe regional em fiscalização eletrônica.", Decimal("2530.50"), Decimal("1650.35"), StatusChoices.CANCELADA),
]


class Command(BaseCommand):
    help = "Popula dados de demonstração para o app de diárias e passagens (idempotente)"

    def handle(self, *args, **options):
        hoje = timezone.localdate()

        criadas = 0
        existentes = 0

        for servidor, destino, desloc, duracao, motivo, diarias, passagens, status in VIAGENS_BASE:
            data_inicio = hoje + timedelta(days=desloc)
            data_fim = data_inicio + timedelta(days=duracao)

            _, criada = Viagem.objects.get_or_create(
                servidor=servidor,
                destino=destino,
                data_inicio=data_inicio,
                defaults={
                    "data_fim": data_fim,
                    "motivo": motivo,
                    "valor_diarias": diarias,
                    "valor_passagens": passagens,
                    "status": status,
                },
            )
            if criada:
                criadas += 1
            else:
                existentes += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Sucesso: {criadas} viagens criadas, {existentes} já existiam (nada duplicado)."
            )
        )
