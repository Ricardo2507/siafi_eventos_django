
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from eventos.models import Evento, LancamentoConta
from eventos.parser import parse_tabela_eventos

class Command(BaseCommand):
    help = 'Importa a Tabela de Eventos SIAFI em TXT de largura fixa.'

    def add_arguments(self, parser):
        parser.add_argument('arquivo', help='Caminho para TABELE_DE_EVENTOS_2025.txt')
        parser.add_argument('--limpar', action='store_true', help='Remove eventos e lançamentos antes de importar')

    @transaction.atomic
    def handle(self, *args, **opts):
        try:
            parsed = parse_tabela_eventos(opts['arquivo'])
        except FileNotFoundError as exc:
            raise CommandError(str(exc))
        if opts['limpar']:
            LancamentoConta.objects.all().delete()
            Evento.objects.all().delete()
        total_contas = 0
        for item in parsed:
            classe, tipo, sequencial = item.codigo.split('.')
            evento, _ = Evento.objects.update_or_create(
                codigo=item.codigo,
                defaults={'classe': classe, 'tipo_utilizacao': tipo, 'sequencial': sequencial, 'estorno': item.estorno, 'especificacao': item.especificacao},
            )
            evento.lancamentos.all().delete()
            LancamentoConta.objects.bulk_create([LancamentoConta(evento=evento, **conta) for conta in item.contas])
            total_contas += len(item.contas)
        self.stdout.write(self.style.SUCCESS(f'Importados {len(parsed)} eventos e {total_contas} lançamentos/contas.'))
