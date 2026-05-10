
from django.db import models
from django.urls import reverse

class Evento(models.Model):
    codigo = models.CharField('Evento', max_length=8, unique=True, db_index=True)
    classe = models.CharField(max_length=2, db_index=True)
    tipo_utilizacao = models.CharField(max_length=1, db_index=True)
    sequencial = models.CharField(max_length=3, db_index=True)
    estorno = models.CharField(max_length=1, blank=True)
    especificacao = models.TextField(blank=True)
    fonte = models.CharField(max_length=100, default='Tabela de Eventos SIAFI 2025')

    class Meta:
        ordering = ['codigo']
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'

    def __str__(self):
        return f'{self.codigo} - {self.especificacao[:80]}'

    def get_absolute_url(self):
        return reverse('eventos:evento_detail', args=[self.id])

class LancamentoConta(models.Model):
    UGE_CHOICES = [('UGE1', 'UGE 1'), ('UGE2', 'UGE 2')]
    DC_CHOICES = [('D', 'Débito'), ('C', 'Crédito')]
    evento = models.ForeignKey(Evento, related_name='lancamentos', on_delete=models.CASCADE)
    uge = models.CharField(max_length=4, choices=UGE_CHOICES)
    natureza = models.CharField(max_length=1, choices=DC_CHOICES)
    conta = models.CharField(max_length=30, db_index=True)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['evento__codigo', 'ordem', 'uge', 'natureza']
        indexes = [models.Index(fields=['conta'])]

    def __str__(self):
        return f'{self.evento.codigo} {self.uge} {self.natureza} {self.conta}'

class Situacao(models.Model):
    codigo = models.CharField(max_length=10, unique=True, db_index=True)
    titulo = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    tipo_documento_habil = models.CharField(max_length=20, blank=True, help_text='Ex.: PA, NP, FL etc.')
    origem = models.CharField(max_length=255, blank=True)
    observacao = models.TextField(blank=True)

    class Meta:
        ordering = ['codigo']
        verbose_name = 'Situação'
        verbose_name_plural = 'Situações'

    def __str__(self):
        return f'{self.codigo} - {self.titulo}'

class SituacaoEvento(models.Model):
    situacao = models.ForeignKey(Situacao, related_name='eventos_relacionados', on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento, related_name='situacoes_relacionadas', on_delete=models.CASCADE)
    tipo_evento = models.CharField(max_length=50, blank=True, help_text='Tipo de Evento parametrizado no CONSIT, quando conhecido.')
    confianca = models.CharField(max_length=20, default='inferida', choices=[('oficial','Oficial/CONSIT'),('inferida','Inferida por contas e descrição'),('manual','Manual do usuário')])
    justificativa = models.TextField(blank=True)

    class Meta:
        unique_together = [('situacao', 'evento', 'tipo_evento')]
        verbose_name = 'Associação Situação x Evento'
        verbose_name_plural = 'Associações Situação x Evento'

    def __str__(self):
        return f'{self.situacao.codigo} -> {self.evento.codigo}'
