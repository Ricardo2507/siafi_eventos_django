# SIAFI Eventos - Django

Projeto Django para consultar eventos SIAFI, contas debitadas/creditadas e situações associadas.

## Base conceitual

- A Tabela de Eventos transforma atos e fatos administrativos rotineiros em registros contábeis automáticos no SIAFI.
- O código do evento possui classe, tipo de utilização e sequencial.
- Registros do Novo SIAFI/CPR e PF ocorrem por eventos parametrizados em tabelas de situações, consultáveis por CONSITDOC/CONSITPF.
- No Manual SIAFI, a Situação representa o ato/fato contábil registrado por meio do Documento Hábil; no CONSIT há uma tabela de associação entre Tipo de Evento e Evento do SIAFI.

## Como rodar

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py importar_tabela_eventos data/TABELE_DE_EVENTOS_2025.txt --limpar
python manage.py carregar_situacoes_seed
python manage.py createsuperuser
python manage.py runserver
```

Abra `http://127.0.0.1:8000/` e pesquise por `IMB061` ou `54.0.508`.

## Associação inicial IMB061

A situação `IMB061` foi carregada como associação **inferida** com o evento `54.0.508`, porque o procedimento público indica bens móveis `12311.XX.YY` e VPA doação `45901.01.00`, e a Tabela de Eventos 2025 contém `54.0.508 - Entrada de bens móveis por recebimento em doação`, debitando `1.2.3.1.1.XX.XX` e creditando `4.5.9.1.1.01.00`. Há diferença entre a VPA indicada no procedimento consultado (`45901.01.00`) e a conta de crédito do evento em 2025 (`4.5.9.1.1.01.00`), então a associação foi marcada como inferida, não oficial.

Também foi cadastrada `54.0.442` como alternativa similar para conferência.

> Atenção: em produção, confirme a associação oficial na transação/tela CONSIT/CONSITDOC, porque a tabela de eventos não contém, sozinha, todas as parametrizações de situação.

## Como ampliar

1. Exporte ou digite as situações oficiais do CONSIT/CONSITDOC.
2. Cadastre/importe em `Situacao` e `SituacaoEvento`.
3. Marque `confianca='oficial'` quando a associação vier diretamente da consulta oficial.

## Estrutura principal

- `Evento`: código, classe, tipo, sequencial, estorno e especificação.
- `LancamentoConta`: conta debitada/creditada por UGE 1/UGE 2.
- `Situacao`: situação do Documento Hábil, como `IMB061`.
- `SituacaoEvento`: associação entre situação e evento, incluindo tipo de evento e justificativa.
