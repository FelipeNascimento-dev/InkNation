# AGENTS.md — InkNation

Projeto Django greenfield para marketplace de estúdios de tatuagem.

## Regras principais

- Views enxutas; regras complexas em `services/` ou helpers.
- Models representam dados e relacionamentos; forms validam entrada.
- Templates não carregam regra de negócio pesada.
- Permissões via `CustomUser.role` e mixins em `core/mixins.py`.
- Upload de mídia apenas com `ImageField`/`FileField` — sem paths OS manuais.
- Não versionar secrets (usar `.env` e `python-decouple`).
- Ao descobrir regra de negócio recorrente, registrar em `.cursor/business-rules/` e propor rule em `.cursor/rules/2xx-business-<dominio>-auto.mdc`.

## Apps

| App | Responsabilidade |
|-----|------------------|
| `core` | BaseModel, validators (CPF/CNPJ), mixins, home |
| `accounts` | CustomUser, auth, username sequencial `INK0001` |
| `studios` | Estúdios, aprovação, artistas, portfólio |
| `budgets` | Solicitações de orçamento |

## RBAC

Roles: `SYSTEM_ADMIN`, `STUDIO_OWNER`, `STUDIO_STAFF`, `CLIENT`.

- Estúdio inativo até aprovação no Django Admin.
- Owner cadastra estúdio; admin usa ação "Aprovar estúdio".
- Dashboard e portfólio: owner ou staff vinculado ao estúdio.
- Orçamento: apenas `CLIENT` autenticado.

## Comandos úteis

```bash
python manage.py migrate
python manage.py populate_ink_data
python manage.py test
python manage.py runserver
```

## Referências

- [Especificação](docs/SPECIFICACAO_INKNATION.md)
- [README](README.md)
