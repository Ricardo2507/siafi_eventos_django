
from django.contrib import admin
from .models import Evento, LancamentoConta, Situacao, SituacaoEvento

class LancamentoInline(admin.TabularInline):
    model = LancamentoConta
    extra = 0

class SituacaoEventoInline(admin.TabularInline):
    model = SituacaoEvento
    extra = 0

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'classe', 'tipo_utilizacao', 'sequencial', 'estorno', 'resumo')
    search_fields = ('codigo', 'especificacao', 'lancamentos__conta', 'situacoes_relacionadas__codigo')
    list_filter = ('classe', 'tipo_utilizacao', 'estorno')
    inlines = [LancamentoInline, SituacaoEventoInline]
    def resumo(self, obj):
        return (obj.especificacao or '')[:120]

@admin.register(Situacao)
class SituacaoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'titulo', 'tipo_documento_habil')
    search_fields = ('codigo', 'titulo', 'descricao')
    inlines = [SituacaoEventoInline]

@admin.register(LancamentoConta)
class LancamentoContaAdmin(admin.ModelAdmin):
    list_display = ('evento', 'uge', 'natureza', 'conta', 'ordem')
    search_fields = ('evento__codigo', 'conta')
    list_filter = ('uge', 'natureza')

@admin.register(SituacaoEvento)
class SituacaoEventoAdmin(admin.ModelAdmin):
    list_display = ('situacao', 'evento', 'tipo_evento', 'confianca')
    search_fields = ('situacao__codigo', 'evento__codigo', 'justificativa')
    list_filter = ('confianca',)
