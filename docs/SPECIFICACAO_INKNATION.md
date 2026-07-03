# Especificação Técnica de Software: Projeto InkNation (Otimizada para IA)

## Contexto Geral

A InkNation é uma plataforma multitenant para o ecossistema de tatuagem no Brasil, funcionando como marketplace e agregador de estúdios (franquias ou individuais). Siga as instruções abaixo de forma estrita, priorizando segurança, escalabilidade e boas práticas do Django.

---

## 1. Visão Geral e Identidade Visual

- **Cores dominantes:** Preto (fundo/escuro moderno), Cinza (componentes/cards) e Vermelho (destaques, CTAs, botões).
- **Detalhes:** Branco (textos e contrastes).
- **Estilo:** Interface Dark Mode nativa, limpa e urbana utilizando Tailwind CSS.

---

## 2. Stack Tecnológica e Arquitetura de Transição

- **Backend & Frontend:** Django 5.x (monólito com Django Templates). Retorno em JSON nativo (ou Django Rest Framework leve) apenas para os endpoints do mapa.
- **Banco de Dados:** SQLite para desenvolvimento, mas utilize boas práticas de ORM (não use raw SQL específico do SQLite) visando a migração estruturada para PostgreSQL.
- **Gerenciamento de Segredos:** Utilize `python-decouple` ou `django-environ` para lidar com variáveis de ambiente (`SECRET_KEY`, `DEBUG`, credenciais futuras do Firebase). O Cursor deve criar um arquivo `.env.example`.

### Armazenamento de Arquivos (Mídia)

> ⚠️ **Regra rígida — Preparação para Firebase Storage:** O Cursor **NÃO DEVE** fazer manipulações locais de arquivos usando caminhos estáticos do sistema operacional (`os.path`). Todos os arquivos devem utilizar os fields padrão do Django (`ImageField`, `FileField`) exclusivamente através do barramento nativo de Storage do Django. Isso garantirá que a virada de chave para a produção exija apenas a instalação do `django-storages` e variáveis no `.env`, sem alterar models ou views.

- **Mapas:** Leaflet.js (OpenStreetMap) via CDN.

---

## 3. Estrutura de Apps e Sistema de Permissões (RBAC)

**Apps do Django recomendados:** `core` (usuários e views gerais), `studios` (estúdios, portfólios) e `budgets` (orçamentos).

### Grupos de Usuários (Roles) definidos em CustomUser

| Role | Descrição |
|------|-----------|
| `SYSTEM_ADMIN` | Aprova estúdios, gerencia assinaturas, acesso total ao Django Admin. |
| `STUDIO_OWNER` | Cria solicitações de estúdios, gerencia faturamento, métricas globais e funcionários de suas franquias. |
| `STUDIO_STAFF` | Vinculado a estúdios específicos. Responde orçamentos, edita portfólios, vê métricas cotidianas (sem privilégios destrutivos ou financeiros). |
| `CLIENT` | Usuário padrão. Busca estúdios, vê portfólios, solicita orçamentos. |

---

## 4. Modelagem de Dados (Models)

Todos os models devem herdar de um `BaseModel` abstrato contendo `created_at` e `updated_at` (`DateTimeField`).

### A. CustomUser (herdando de AbstractUser)

| Campo | Tipo / regra |
|-------|----------------|
| `id` | `UUIDField` (Primary Key) |
| `cpf` | `CharField(max_length=11, unique=True)` — validador customizado de CPF algorítmico no model |
| `first_name` / `last_name` | `CharField` |
| `email` | `EmailField(unique=True)` |
| `phone` | `CharField(max_length=15)` |
| `username` | `CharField(max_length=12, unique=True)` — gerado automaticamente (ex.: `INK0001`) |
| `role` | `CharField(choices, default='client')` |

### B. Studio (Estúdio / Franquia)

| Campo | Tipo / regra |
|-------|----------------|
| `id` | `UUIDField` (Primary Key) |
| `name` | `CharField(max_length=255)` |
| `cnpj` | `CharField(max_length=14, unique=True)` — validador customizado de CNPJ |
| `slug` | `SlugField(unique=True)` — autogerado via sinal `pre_save` |
| `owners` | `ManyToManyField(CustomUser, related_name='owned_studios')` |
| `staffs` | `ManyToManyField(CustomUser, related_name='assigned_studios', blank=True)` |
| Endereço | `address_street`, `address_number`, `neighborhood`, `city`, `state` (UF), `cep` |
| Geolocalização | `latitude` (`Float`, `null=True`), `longitude` (`Float`, `null=True`) |
| `is_active` | `BooleanField(default=False)` |

### C. StudioApprovalRequest

| Campo | Tipo / regra |
|-------|----------------|
| `studio` | `OneToOneField(Studio)` |
| `requested_by` | `ForeignKey(CustomUser)` |
| `status` | `CharField(choices: pending, approved, rejected, default='pending')` |

### D. TattooArtist & PortfolioItem

| Campo | Tipo / regra |
|-------|----------------|
| `studio` | `ForeignKey(Studio, related_name='artists')` |
| Dados do artista | `name`, `bio`, `instagram`, `specialties` |
| `image` | `ImageField(upload_to='portfolios/')` — abstraído via Storage |

### E. BudgetRequest (Orçamentos)

| Campo | Tipo / regra |
|-------|----------------|
| Relacionamentos | `client`, `studio`, `artist`, `description` |
| `reference_image` | `ImageField(upload_to='budgets/', blank=True, null=True)` |
| `status` | `CharField(choices: sent, in_analysis, answered, default='sent')` |

---

## 5. Regras de Negócio Cruciais e Segurança

### Lógica de Username Cronológico (INK0001) — Prevenção de Race Condition

> ⚠️ O Cursor deve sobrescrever o método `save()` do `CustomUser`. Para garantir a atomicidade ao gerar o username numérico, deve-se utilizar `transaction.atomic()` e travar a linha de verificação usando `select_for_update()` no banco de dados, buscando o último usuário cadastrado para extrair a parte numérica, somar +1 e aplicar `zfill(4)`.

### Segurança Baseada em Mixins de Permissão (Authorization)

> ⚠️ **Proibido** usar verificações soltas de `if/else` nas Views. O Cursor deve criar Mixins (ex.: `StudioOwnerRequiredMixin`, `StudioStaffOrOwnerMixin`) que avaliam `request.user.role` e interceptam o `slug` ou `id` do estúdio na URL para validar se o usuário existe nas tabelas `owners` ou `staffs` do objeto. Lançar `PermissionDenied` caso contrário.

---

## 6. Telas e Frontend (via Templates)

- **Home pública:** Layout dark contemporâneo. Mapa interativo no centro carregado via Leaflet.js. O mapa deve consumir um endpoint de leitura leve (`/api/studios/locations/`) que retorna apenas `id`, `name`, `latitude`, `longitude` e `slug`. Popups customizados no hover. Carrossel inferior.
- **Fluxo de estúdio:** Formulário para "Cadastrar meu Estúdio". O model é salvo inativo e gera um `StudioApprovalRequest`.
- **Páginas internas (estúdio):** Exibição de portfólios. Botão de orçamento abre modal dinâmico.
- **Dashboard gerencial:** Dividido entre abas/cards operacionais (visíveis para staff/owner) e gerenciais (visíveis só para owner).

---

## 7. População Automatizada (Seed Data)

Criar um management command (`python manage.py populate_ink_data`) para gerar o ambiente inicial limpo e funcional:

| Entidade | Quantidade | Detalhe |
|----------|------------|---------|
| Administrador | 1 | `SYSTEM_ADMIN` |
| Proprietários | 2 | `STUDIO_OWNER`, sendo um dono de franquia (2 estúdios) |
| Recepcionistas | 2 | `STUDIO_STAFF` alocados |
| Clientes | 3 | `CLIENT` demonstrando a lógica sequencial (`INK0001`, `INK0002`, `INK0003`) |
| Estúdios | variado | Geolocalizados (SP, RJ, BH) com dados fictícios |

---

## Notas de otimização da especificação original

As seguintes decisões foram incorporadas na redação original da spec para orientar a implementação por IA:

1. **Proteção contra concorrência (`select_for_update`):** Apenas mencionar "atômica" faz a IA usar métodos básicos que falham em alta concorrência. Especificar `transaction.atomic()` com `select_for_update()` força o Cursor a implementar um lock real no banco no momento do cadastro do ID `INK`.
2. **Variáveis de ambiente (`.env`):** Exigência do `python-decouple`/`django-environ`, evitando que o Cursor escreva a `SECRET_KEY` direto no `settings.py`.
3. **Sugestão de apps:** Separar em `core`, `studios` e `budgets` ajuda a IA a não colocar todo o código em um único e imenso `models.py` ou `views.py`.
4. **Otimização do endpoint do mapa:** Restringir os dados retornados no endpoint do mapa para ser um payload leve (apenas coords e id/nome), para que a tela de home não fique pesada carregando imagens e textos inteiros de todos os estúdios do Brasil.

---

## Decisões de implementação

Decisões confirmadas para este repositório, registradas após revisão do plano de implementação:

| Decisão | Spec original | Implementação acordada | Motivo |
|---------|---------------|------------------------|--------|
| **CSS / frontend** | Tailwind CSS | **CSS3 puro** com variáveis CSS e layout responsivo | Evitar dependência de Node/npm no MVP; dark mode com variáveis (`#0a0a0a`, `#1a1a1a`, `#e63946`) |
| **Baseline do código** | — | **Recriação greenfield** | Não restaurar o commit `ae3924c`; recriar do zero seguindo a spec estritamente (commit antigo serve apenas como referência pontual) |
| **App de autenticação** | `core` para usuários e views gerais | **`accounts`** para `CustomUser` e auth | Padrão Django (`AUTH_USER_MODEL`); evita conflito com app `core` genérico (BaseModel, mixins, validators, home) |
| **Geração de username** | `save()` + `select_for_update()` | Mantido conforme spec | Não usar tabela `UsernameSequence` nem signal `pre_save` para sequência |

### Estrutura de apps resultante

```text
InkNation/
├── core/       # BaseModel, validators, mixins, home, seed command
├── accounts/   # CustomUser, login/registro, RBAC groups
├── studios/    # Studio, aprovação, portfólio, dashboard
└── budgets/    # BudgetRequest, modal de orçamento
```

### Paleta CSS3 (substituto do Tailwind)

| Token | Valor | Uso |
|-------|-------|-----|
| Fundo | `#0a0a0a` | Background principal |
| Cards | `#1a1a1a` | Componentes e superfícies |
| Accent | `#e63946` | CTAs, destaques, botões |
| Texto | branco | Contraste e legibilidade |
