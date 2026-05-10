
from django.core.management.base import BaseCommand
from django.db import transaction
from eventos.models import Evento, Situacao, SituacaoEvento

SEEDS = [
    {
        'codigo': 'IMB061',
        'titulo': 'Entrada de bens móveis por doação - credor nacional/CPF',
        'descricao': 'Situação usada no Documento Hábil PA para entrada de bens móveis por doação, com conta de bens móveis 12311.XX.YY e VPA de doação 45901.01.00.',
        'tipo_documento_habil': 'PA',
        'origem': 'Manual/procedimento público de patrimônio + inferência pela Tabela de Eventos 2025',
        'eventos': [
            {
                'evento': '54.0.508',
                'tipo_evento': 'OUTROS_LANCAMENTOS',
                'confianca': 'inferida',
                'justificativa': 'A situação IMB061 informa débito em Bens Móveis 12311.XX.YY e crédito em VPA Doações 45901.01.00. Na Tabela de Eventos 2025, o evento 54.0.508 tem a especificação “Entrada de bens móveis por recebimento em doação” e lançamentos UGE1 D 1.2.3.1.1.XX.XX / C 4.5.9.1.1.01.00, compatíveis parcialmente com a conta de bens móveis 12311.XX.XX; a VPA informada no procedimento consultado é 45901.01.00, enquanto a tabela 2025 traz 4.5.9.1.1.01.00 para este evento. Por isso a associação é inferida e precisa ser validada no CONSIT/CONSITDOC antes de uso operacional.'
            },
            {
                'evento': '54.0.442',
                'tipo_evento': 'ALTERNATIVO_SIMILAR',
                'confianca': 'inferida',
                'justificativa': 'Evento similar: entrada de bens móveis no imobilizado por doação, com D 1.2.3.1.1.XX.YY e C 4.5.9.1.1.01.00. Mantido como alternativa para conferência no CONSIT.'
            }
        ]
    }
]

class Command(BaseCommand):
    help = 'Carrega associações iniciais de situações conhecidas/inferidas.'

    @transaction.atomic
    def handle(self, *args, **opts):
        count = 0
        for seed in SEEDS:
            situacao, _ = Situacao.objects.update_or_create(
                codigo=seed['codigo'],
                defaults={k: seed[k] for k in ['titulo', 'descricao', 'tipo_documento_habil', 'origem']},
            )
            for rel in seed['eventos']:
                try:
                    evento = Evento.objects.get(codigo=rel['evento'])
                except Evento.DoesNotExist:
                    self.stderr.write(f'Evento {rel["evento"]} não encontrado. Importe a tabela antes.')
                    continue
                SituacaoEvento.objects.update_or_create(
                    situacao=situacao,
                    evento=evento,
                    tipo_evento=rel['tipo_evento'],
                    defaults={'confianca': rel['confianca'], 'justificativa': rel['justificativa']},
                )
                count += 1
        self.stdout.write(self.style.SUCCESS(f'Carregadas {count} associações de situação x evento.'))
