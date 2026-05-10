from pathlib import Path

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import get_valid_filename

from .models import Evento, LancamentoConta, Situacao, SituacaoEvento
from .parser import parse_tabela_eventos


def _is_admin(user):
    return user.is_authenticated and user.is_superuser


@login_required
def home(request):
    total_eventos = Evento.objects.count()
    total_situacoes = Situacao.objects.count()
    eventos_parametrizados = Evento.objects.filter(
        situacoes_relacionadas__isnull=False
    ).distinct().count()

    contexto = {
        'total_eventos': total_eventos,
        'total_situacoes': total_situacoes,
        'eventos_parametrizados': eventos_parametrizados,
        'eventos_pendentes': max(0, total_eventos - eventos_parametrizados),
    }
    return render(request, 'eventos/home.html', contexto)


@login_required
def eventos_ajax(request):
    def as_int(value, default):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    draw = as_int(request.GET.get('draw'), 1)
    start = max(0, as_int(request.GET.get('start'), 0))
    length = min(max(1, as_int(request.GET.get('length'), 10)), 100)
    search_value = request.GET.get('search[value]', '').strip()

    queryset = Evento.objects.all()
    records_total = queryset.count()

    if search_value:
        queryset = queryset.filter(
            Q(codigo__icontains=search_value)
            | Q(especificacao__icontains=search_value)
            | Q(situacoes_relacionadas__situacao__codigo__icontains=search_value)
        ).distinct()

    records_filtered = queryset.count()
    eventos_pagina = queryset.prefetch_related(
        Prefetch('lancamentos'),
        Prefetch('situacoes_relacionadas', queryset=SituacaoEvento.objects.select_related('situacao')),
    )[start:start + length]

    data = []
    for evento in eventos_pagina:
        lancamentos = '<br>'.join(
            f'{lancamento.uge} {lancamento.natureza} {lancamento.conta}'
            for lancamento in evento.lancamentos.all()
        ) or 'Nenhum'
        situacoes = '<br>'.join(
            relacao.situacao.codigo for relacao in evento.situacoes_relacionadas.all()
        ) or 'Nenhuma'

        acoes = f'''
        <div style="display: flex; gap: 0.35rem; justify-content: center;">
            <button type="button" onclick="abrirDetalhe({evento.id})" class="btn btn-info" style="padding: 0.3rem 0.6rem; font-size: 0.85rem;" title="Ver detalhes">
                &#128065;
            </button>'''

        if request.user.is_superuser:
            acoes += f'''
            <button type="button" onclick="abrirEditar({evento.id})" class="btn btn-warning" style="padding: 0.3rem 0.6rem; font-size: 0.85rem;" title="Editar situações">
                &#9998;
            </button>'''

        acoes += '</div>'

        data.append({
            'codigo': evento.codigo,
            'especificacao': evento.especificacao,
            'fonte': evento.fonte,
            'lancamentos': lancamentos,
            'situacoes': situacoes,
            'acoes': acoes,
        })

    return JsonResponse({
        'draw': draw,
        'recordsTotal': records_total,
        'recordsFiltered': records_filtered,
        'data': data,
    })


@login_required
def evento_detail_modal(request, evento_id):
    evento = get_object_or_404(
        Evento.objects.prefetch_related(
            Prefetch('lancamentos'),
            Prefetch('situacoes_relacionadas', queryset=SituacaoEvento.objects.select_related('situacao')),
        ),
        id=evento_id,
    )
    return render(request, 'eventos/detalhe_modal_corpo.html', {'evento': evento})


@login_required
def evento_detail(request, evento_id):
    evento = get_object_or_404(
        Evento.objects.prefetch_related(
            Prefetch('lancamentos'),
            Prefetch('situacoes_relacionadas', queryset=SituacaoEvento.objects.select_related('situacao')),
        ),
        id=evento_id,
    )
    return render(request, 'eventos/evento_detail.html', {
        'evento': evento,
        'lancamentos': evento.lancamentos.all(),
        'situacoes': evento.situacoes_relacionadas.all(),
    })


@user_passes_test(_is_admin, login_url='eventos:login')
def atualizar_situacoes(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    situacoes = SituacaoEvento.objects.filter(evento=evento).select_related('situacao')
    todas_situacoes = Situacao.objects.all()

    if request.method == 'POST':
        with transaction.atomic():
            for relacao in situacoes:
                relacao.tipo_evento = request.POST.get(f'tipo_evento_{relacao.id}', '')
                relacao.confianca = request.POST.get(f'confianca_{relacao.id}', 'manual')
                relacao.justificativa = request.POST.get(f'justificativa_{relacao.id}', '')
                relacao.save()

            nova_situacao_id = request.POST.get('nova_situacao')
            if nova_situacao_id:
                SituacaoEvento.objects.get_or_create(
                    evento=evento,
                    situacao_id=nova_situacao_id,
                    tipo_evento=request.POST.get('nova_tipo_evento', ''),
                    defaults={
                        'confianca': request.POST.get('nova_confianca', 'manual'),
                        'justificativa': request.POST.get('nova_justificativa', ''),
                    },
                )

            nova_codigo = request.POST.get('nova_situacao_manual_codigo', '').strip().upper()
            novo_titulo = request.POST.get('nova_situacao_manual_titulo', '').strip()
            if nova_codigo and novo_titulo:
                nova_situacao, _ = Situacao.objects.get_or_create(
                    codigo=nova_codigo,
                    defaults={'titulo': novo_titulo},
                )
                SituacaoEvento.objects.get_or_create(
                    evento=evento,
                    situacao=nova_situacao,
                    tipo_evento=request.POST.get('nova_tipo_evento', ''),
                    defaults={
                        'confianca': request.POST.get('nova_confianca', 'manual'),
                        'justificativa': request.POST.get('nova_justificativa', ''),
                    },
                )

        return JsonResponse({'status': 'success', 'message': 'Alterações gravadas com sucesso!'})

    return render(request, 'eventos/atualizar_situacoes.html', {
        'evento': evento,
        'situacoes': situacoes,
        'todas_situacoes': todas_situacoes,
    })


@user_passes_test(_is_admin, login_url='eventos:login')
def importar_tabela_view(request):
    contexto = {'status': None, 'mensagem': None}

    if request.method == 'POST' and request.FILES.get('arquivo_txt'):
        arquivo_upload = request.FILES['arquivo_txt']
        nome_arquivo = get_valid_filename(arquivo_upload.name)

        if not nome_arquivo.lower().endswith('.txt'):
            contexto.update({'status': 'error', 'mensagem': 'Extensão inválida. Forneça um arquivo .txt do SIAFI.'})
            return render(request, 'eventos/importar_tabela.html', contexto)

        caminho_temporario = Path('data') / f'temp_{nome_arquivo}'

        try:
            caminho_temporario.parent.mkdir(exist_ok=True)
            with caminho_temporario.open('wb+') as destino:
                for fragmento in arquivo_upload.chunks():
                    destino.write(fragmento)

            parsed_eventos = parse_tabela_eventos(caminho_temporario)

            with transaction.atomic():
                for parsed in parsed_eventos:
                    classe, tipo_utilizacao, sequencial = parsed.codigo.split('.')
                    evento, _ = Evento.objects.update_or_create(
                        codigo=parsed.codigo,
                        defaults={
                            'classe': classe,
                            'tipo_utilizacao': tipo_utilizacao,
                            'sequencial': sequencial,
                            'estorno': parsed.estorno,
                            'especificacao': parsed.especificacao,
                            'fonte': f'Upload manual via web por {request.user.username}',
                        },
                    )
                    LancamentoConta.objects.filter(evento=evento).delete()
                    LancamentoConta.objects.bulk_create([
                        LancamentoConta(
                            evento=evento,
                            uge=conta['uge'],
                            natureza=conta['natureza'],
                            conta=conta['conta'],
                            ordem=conta['ordem'],
                        )
                        for conta in parsed.contas
                    ])

            contexto.update({
                'status': 'success',
                'mensagem': f'Sucesso! Foram processados {len(parsed_eventos)} eventos mantendo as parametrizações existentes.',
            })
        except Exception as erro:
            contexto.update({'status': 'error', 'mensagem': f'Falha crítica no processamento: {erro}'})
        finally:
            caminho_temporario.unlink(missing_ok=True)

    return render(request, 'eventos/importar_tabela.html', contexto)
