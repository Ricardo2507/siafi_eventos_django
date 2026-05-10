# Modelagem e regras de negócio

## Consulta por evento

A tela de detalhe do evento mostra:

- especificação completa do evento;
- contas envolvidas, separadas por UGE 1/UGE 2 e Débito/Crédito;
- situações associadas.

## Consulta por situação

A tela de situação mostra os eventos ligados à situação e as contas envolvidas em cada evento.

## Associação situação-evento

O Manual SIAFI indica que o CONSIT possui uma tabela de associação entre Tipo de Evento e Evento do SIAFI. Por isso, o projeto trata essa relação como uma tabela própria (`SituacaoEvento`) e não tenta embuti-la no evento.

A associação pode ser:

- `oficial`: veio do CONSIT/CONSITDOC;
- `inferida`: criada por correspondência de descrição/contas;
- `manual`: cadastrada pelo usuário para operação interna.

## Limitação importante

A Tabela de Eventos informa os lançamentos contábeis de cada evento, mas não necessariamente lista todos os códigos de situação do Documento Hábil. Por isso, o projeto inclui um seed inicial e deixa pronta a camada de importação/cadastro para as situações oficiais.
