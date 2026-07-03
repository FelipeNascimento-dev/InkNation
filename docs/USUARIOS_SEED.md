# Usuários de demonstração (seed)

Credenciais criadas pelo comando:

```bash
python manage.py populate_ink_data
```

## Senha padrão

Todos os usuários abaixo usam a mesma senha de demonstração:

| Campo   | Valor           |
|---------|-----------------|
| Senha   | `inknation123`  |

> **Atenção:** use apenas em ambiente local/desenvolvimento. Não utilize esta senha em produção.

## Login

O sistema autentica pelo **e-mail** (não pelo username). Na tela de login, informe o e-mail e a senha acima.

## Listagem de usuários

| Username esperado | E-mail                     | Senha          | Perfil (role)   | CPF         | Telefone     |
|-------------------|----------------------------|----------------|-----------------|-------------|--------------|
| `INK0001`         | `cliente1@inknation.local` | `inknation123` | `CLIENT`        | 87748248800 | 11988880001  |
| `INK0002`         | `cliente2@inknation.local` | `inknation123` | `CLIENT`        | 28625587887 | 11988880002  |
| `INK0003`         | `cliente3@inknation.local` | `inknation123` | `CLIENT`        | 71428793860 | 11988880003  |
| `INK0004`         | `admin@inknation.local`    | `inknation123` | `SYSTEM_ADMIN`  | 52998224725 | 11999990001  |
| `INK0005`         | `franchise@inknation.local`| `inknation123` | `STUDIO_OWNER`  | 39053344705 | 11999990002  |
| `INK0006`         | `rio@inknation.local`      | `inknation123` | `STUDIO_OWNER`  | 15350946056 | 21999990003  |
| `INK0007`         | `staff.sp@inknation.local` | `inknation123` | `STUDIO_STAFF`  | 11144477735 | 11999990004  |
| `INK0008`         | `staff.rj@inknation.local` | `inknation123` | `STUDIO_STAFF`  | 12345678909 | 21999990005  |

## Usernames (`INK0001`, `INK0002`, …)

Os usernames são gerados automaticamente na ordem de criação, com `zfill(4)` (ex.: `INK0001`).

A tabela acima assume um **banco vazio** antes de rodar o seed. Se já existirem usuários no banco, os novos cadastros receberão o próximo número disponível na sequência.

## Papéis e vínculos no cenário de demo

| Usuário                    | Descrição resumida                                      |
|----------------------------|---------------------------------------------------------|
| `admin@inknation.local`    | Superusuário + Django Admin; aprova estúdios            |
| `franchise@inknation.local`| Dono de franquia (2 estúdios em SP)                     |
| `rio@inknation.local`      | Dono de estúdios no RJ e BH                             |
| `staff.sp@inknation.local` | Recepcionista alocada nos estúdios SP da franquia       |
| `staff.rj@inknation.local` | Recepcionista alocada no estúdio RJ                     |
| `cliente1@inknation.local` | Cliente — orçamento enviado                             |
| `cliente2@inknation.local` | Cliente — orçamento em análise                          |
| `cliente3@inknation.local` | Cliente — orçamento respondido                          |

## Referência no código

Definição dos usuários: `core/management/commands/populate_ink_data.py` (`SEED_USERS`, `SEED_PASSWORD`).
