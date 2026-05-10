
import re
from dataclasses import dataclass, field
from pathlib import Path

EVENT_RE = re.compile(r'^(?P<codigo>\d{2}\.\d\.\d{3})\|(?P<est>.?)\s*\|(?P<spec>.{0,54})\|(?P<d1>[^|]*)\|(?P<c1>[^|]*)\|(?P<d2>[^|]*)\|(?P<c2>[^|]*)')
CONT_RE = re.compile(r'^\s{8}\|\s*\|(?P<spec>.{0,54})\|(?P<d1>[^|]*)\|(?P<c1>[^|]*)\|(?P<d2>[^|]*)\|(?P<c2>[^|]*)')
ACCOUNT_RE = re.compile(r'^[1-9XYWK]\.[0-9XWYKN]\.[0-9XWYKN]\.[0-9XWYKN]\.[0-9XWYKN]\.[0-9XWYKN]{1,2}\.[0-9XYWK]{1,2}$')

@dataclass
class ParsedEvento:
    codigo: str
    estorno: str = ''
    especificacao: str = ''
    contas: list = field(default_factory=list)


def _clean(text: str) -> str:
    return ' '.join((text or '').replace('|', ' ').split())


def _add_account(evento, conta, uge, natureza, ordem):
    conta = _clean(conta)
    if conta and ACCOUNT_RE.match(conta):
        evento.contas.append({'uge': uge, 'natureza': natureza, 'conta': conta, 'ordem': ordem})


def parse_tabela_eventos(path):
    eventos = []
    current = None
    ordem = 0
    for raw in Path(path).read_text(encoding='utf-8', errors='ignore').splitlines():
        m = EVENT_RE.match(raw)
        if m:
            if current:
                current.especificacao = _clean(current.especificacao)
                eventos.append(current)
            codigo = m.group('codigo')
            current = ParsedEvento(codigo=codigo, estorno=_clean(m.group('est')), especificacao=_clean(m.group('spec')))
            ordem = 0
            for field, uge, nat in [('d1','UGE1','D'),('c1','UGE1','C'),('d2','UGE2','D'),('c2','UGE2','C')]:
                _add_account(current, m.group(field), uge, nat, ordem); ordem += 1
            continue
        m = CONT_RE.match(raw)
        if current and m:
            spec = _clean(m.group('spec'))
            if spec:
                current.especificacao += ' ' + spec
            for field, uge, nat in [('d1','UGE1','D'),('c1','UGE1','C'),('d2','UGE2','D'),('c2','UGE2','C')]:
                _add_account(current, m.group(field), uge, nat, ordem); ordem += 1
    if current:
        current.especificacao = _clean(current.especificacao)
        eventos.append(current)
    return eventos
