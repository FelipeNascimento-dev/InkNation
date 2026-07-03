# InkNation

Plataforma Django para marketplace de estúdios de tatuagem no Brasil — mapa interativo, cadastro de estúdios com aprovação administrativa, portfólios e solicitações de orçamento.

## Stack

- Django 5.x (templates + JSON leve para o mapa)
- SQLite em desenvolvimento (PostgreSQL preparado via ORM)
- CSS3 puro com dark mode (`static/css/inknation.css`)
- Leaflet.js para mapa na home
- Pillow para upload de imagens
- `python-decouple` para variáveis de ambiente

## Estrutura

```text
InkNation/
├── config/          # settings, urls, wsgi/asgi
├── core/            # BaseModel, validators, mixins, home
├── accounts/        # CustomUser, auth (login/registro)
├── studios/         # estúdios, artistas, portfólio, aprovação
├── budgets/         # solicitações de orçamento
├── static/          # CSS e JS
└── docs/            # especificação e guias Cursor
```

## Setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env       # ajuste SECRET_KEY se necessário
python manage.py migrate
python manage.py populate_ink_data
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/` e o admin em `http://127.0.0.1:8000/admin/`.

## Dados de demonstração

O comando `populate_ink_data` cria usuários, estúdios em SP/RJ/BH, artistas, portfólio e orçamentos de exemplo.

| Tipo | E-mail | Senha |
|------|--------|-------|
| Admin | admin@inknation.local | inknation123 |
| Dono (franquia) | franchise@inknation.local | inknation123 |
| Dono (RJ) | rio@inknation.local | inknation123 |
| Cliente | cliente1@inknation.local | inknation123 |

Clientes seed recebem usernames `INK0001`, `INK0002` e `INK0003` em banco vazio.

```bash
python manage.py populate_ink_data --flush --no-input   # limpa e recria
```

## Roles (RBAC)

| Role | Descrição |
|------|-----------|
| `SYSTEM_ADMIN` | Aprova estúdios no Django Admin |
| `STUDIO_OWNER` | Cadastra e gerencia estúdios |
| `STUDIO_STAFF` | Opera portfólio e orçamentos do estúdio |
| `CLIENT` | Busca estúdios e solicita orçamentos |

Permissões de views usam `CustomUser.role` e mixins em `core/mixins.py`.

## Rotas principais

| Rota | Descrição |
|------|-----------|
| `/` | Home com mapa Leaflet |
| `/api/studios/locations/` | JSON leve para markers (id, name, lat, lng, slug) |
| `/accounts/login/` | Login |
| `/accounts/register/` | Cadastro de cliente |
| `/studios/cadastrar/` | Cadastro de estúdio (owner) |
| `/studios/<slug>/` | Detalhe do estúdio |
| `/studios/<slug>/dashboard/` | Dashboard (owner/staff) |
| `/admin/` | Django Admin — ação "Aprovar estúdio" |

## Testes

```bash
python manage.py test
```

## Documentação

- [Especificação do projeto](docs/SPECIFICACAO_INKNATION.md)
- [Guia Cursor](docs/cursor/README.md)
- [AGENTS.md](AGENTS.md) — instruções para agentes de IA

## Alterações recentes

| Data | Tipo | Módulo/Pasta | Alteração | Impacto |
| ---- | ---- | --- | --- | ---- |
| 2026-07-02 | feature | core/management | Comando `populate_ink_data` | Dados de demo para desenvolvimento |
| 2026-07-02 | docs | README, AGENTS | Documentação InkNation | Onboarding do projeto |
