"""Popula o banco com cenário de demonstração do InkNation."""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.utils.seed_images import (
    ensure_static_default_covers,
    fetch_portfolio_image,
    is_placeholder_image,
)

from budgets.models import (
    BUDGET_STATUS_ANSWERED,
    BUDGET_STATUS_IN_ANALYSIS,
    BUDGET_STATUS_SENT,
    BudgetRequest,
)
from core.constants import CLIENT, STUDIO_OWNER, STUDIO_STAFF, SYSTEM_ADMIN
from studios.models import (
    APPROVAL_STATUS_APPROVED,
    APPROVAL_STATUS_PENDING,
    PortfolioItem,
    Studio,
    StudioApprovalRequest,
    TattooArtist,
)

User = get_user_model()

SEED_PASSWORD = 'inknation123'

SEED_USERS = [
    {
        'key': 'client1',
        'email': 'cliente1@inknation.local',
        'cpf': '87748248800',
        'phone': '11988880001',
        'role': CLIENT,
    },
    {
        'key': 'client2',
        'email': 'cliente2@inknation.local',
        'cpf': '28625587887',
        'phone': '11988880002',
        'role': CLIENT,
    },
    {
        'key': 'client3',
        'email': 'cliente3@inknation.local',
        'cpf': '71428793860',
        'phone': '11988880003',
        'role': CLIENT,
    },
    {
        'key': 'admin',
        'email': 'admin@inknation.local',
        'cpf': '52998224725',
        'phone': '11999990001',
        'role': SYSTEM_ADMIN,
        'superuser': True,
    },
    {
        'key': 'owner_franchise',
        'email': 'franchise@inknation.local',
        'cpf': '39053344705',
        'phone': '11999990002',
        'role': STUDIO_OWNER,
    },
    {
        'key': 'owner_rj',
        'email': 'rio@inknation.local',
        'cpf': '15350946056',
        'phone': '21999990003',
        'role': STUDIO_OWNER,
    },
    {
        'key': 'staff_sp',
        'email': 'staff.sp@inknation.local',
        'cpf': '11144477735',
        'phone': '11999990004',
        'role': STUDIO_STAFF,
    },
    {
        'key': 'staff_rj',
        'email': 'staff.rj@inknation.local',
        'cpf': '12345678909',
        'phone': '21999990005',
        'role': STUDIO_STAFF,
    },
]

SEED_STUDIOS = [
    {
        'key': 'sp_centro',
        'name': 'Ink Nation SP Centro',
        'cnpj': '11222333000181',
        'address_street': 'Rua Augusta',
        'address_number': '1500',
        'neighborhood': 'Consolação',
        'city': 'São Paulo',
        'state': 'SP',
        'cep': '01304-001',
        'latitude': -23.5505,
        'longitude': -46.6608,
        'is_active': True,
        'owner_key': 'owner_franchise',
        'staff_keys': ['staff_sp'],
    },
    {
        'key': 'sp_vila',
        'name': 'Ink Nation SP Vila Madalena',
        'cnpj': '11444777000161',
        'address_street': 'Rua Harmonia',
        'address_number': '420',
        'neighborhood': 'Vila Madalena',
        'city': 'São Paulo',
        'state': 'SP',
        'cep': '05435-000',
        'latitude': -23.5465,
        'longitude': -46.6890,
        'is_active': True,
        'owner_key': 'owner_franchise',
        'staff_keys': ['staff_sp'],
    },
    {
        'key': 'rj_copacabana',
        'name': 'Ink Nation RJ Copacabana',
        'cnpj': '19131243000197',
        'address_street': 'Av. Nossa Senhora de Copacabana',
        'address_number': '800',
        'neighborhood': 'Copacabana',
        'city': 'Rio de Janeiro',
        'state': 'RJ',
        'cep': '22020-001',
        'latitude': -22.9711,
        'longitude': -43.1822,
        'is_active': True,
        'owner_key': 'owner_rj',
        'staff_keys': ['staff_rj'],
    },
    {
        'key': 'bh_savassi',
        'name': 'Ink Nation BH Savassi',
        'cnpj': '34028316000103',
        'address_street': 'Rua Pernambuco',
        'address_number': '900',
        'neighborhood': 'Savassi',
        'city': 'Belo Horizonte',
        'state': 'MG',
        'cep': '30130-150',
        'latitude': -19.9378,
        'longitude': -43.9345,
        'is_active': True,
        'owner_key': 'owner_rj',
        'staff_keys': [],
    },
    {
        'key': 'sp_pending',
        'name': 'Ink Nation SP Pendente',
        'cnpj': '27865757000102',
        'address_street': 'Rua Oscar Freire',
        'address_number': '300',
        'neighborhood': 'Jardins',
        'city': 'São Paulo',
        'state': 'SP',
        'cep': '01426-001',
        'latitude': -23.5629,
        'longitude': -46.6719,
        'is_active': False,
        'owner_key': 'owner_franchise',
        'staff_keys': [],
        'approval_status': APPROVAL_STATUS_PENDING,
    },
]


class Command(BaseCommand):
    help = 'Popula o banco com usuários, estúdios, artistas e orçamentos de demonstração.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Remove dados de seed antes de popular (pede confirmação).',
        )
        parser.add_argument(
            '--no-input',
            action='store_true',
            help='Não pedir confirmação ao usar --flush.',
        )
        parser.add_argument(
            '--refresh-images',
            action='store_true',
            help='Substitui imagens de portfólio (inclui placeholders antigos).',
        )

    def handle(self, *args, **options):
        if options['flush']:
            self._confirm_flush(options['no_input'])
            self._flush_data()

        self.stdout.write('Baixando capas padrão para static/...')
        ensure_static_default_covers(stdout=self.stdout)

        with transaction.atomic():
            users = self._create_users()
            studios = self._create_studios(users)
            artists = self._create_artists(studios)
            self._create_portfolio(artists, refresh=options['refresh_images'])
            self._create_budgets(users, studios, artists)

        self.stdout.write(self.style.SUCCESS('Dados de demonstração criados com sucesso.'))
        self.stdout.write(f'Senha padrão dos usuários: {SEED_PASSWORD}')
        self.stdout.write('Clientes esperados: INK0001, INK0002, INK0003 (se banco vazio).')

    def _confirm_flush(self, no_input):
        if no_input:
            return
        answer = input(
            'Isso apagará usuários (exceto superusuários), estúdios e orçamentos. '
            'Continuar? [y/N]: '
        )
        if answer.strip().lower() not in ('y', 'yes', 's', 'sim'):
            raise CommandError('Operação cancelada.')

    def _flush_data(self):
        BudgetRequest.objects.all().delete()
        PortfolioItem.objects.all().delete()
        TattooArtist.objects.all().delete()
        StudioApprovalRequest.objects.all().delete()
        Studio.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write('Dados anteriores removidos.')

    def _create_users(self):
        users = {}
        for spec in SEED_USERS:
            if User.objects.filter(email=spec['email']).exists():
                users[spec['key']] = User.objects.get(email=spec['email'])
                self.stdout.write(f'  Usuário já existe: {spec["email"]}')
                continue

            if spec.get('superuser'):
                user = User.objects.create_superuser(
                    email=spec['email'],
                    password=SEED_PASSWORD,
                    cpf=spec['cpf'],
                    phone=spec['phone'],
                    role=spec['role'],
                )
            else:
                user = User.objects.create_user(
                    email=spec['email'],
                    password=SEED_PASSWORD,
                    cpf=spec['cpf'],
                    phone=spec['phone'],
                    role=spec['role'],
                )
            users[spec['key']] = user
            self.stdout.write(f'  Usuário criado: {user.username} ({spec["email"]})')
        return users

    def _create_studios(self, users):
        studios = {}
        for spec in SEED_STUDIOS:
            if Studio.objects.filter(cnpj=spec['cnpj']).exists():
                studio = Studio.objects.get(cnpj=spec['cnpj'])
                studios[spec['key']] = studio
                self.stdout.write(f'  Estúdio já existe: {studio.name}')
                continue

            studio = Studio.objects.create(
                name=spec['name'],
                cnpj=spec['cnpj'],
                address_street=spec['address_street'],
                address_number=spec['address_number'],
                neighborhood=spec['neighborhood'],
                city=spec['city'],
                state=spec['state'],
                cep=spec['cep'],
                latitude=spec['latitude'],
                longitude=spec['longitude'],
                is_active=spec['is_active'],
            )
            owner = users[spec['owner_key']]
            studio.owners.add(owner)
            for staff_key in spec.get('staff_keys', []):
                studio.staffs.add(users[staff_key])

            approval_status = spec.get(
                'approval_status',
                APPROVAL_STATUS_APPROVED if spec['is_active'] else APPROVAL_STATUS_PENDING,
            )
            StudioApprovalRequest.objects.create(
                studio=studio,
                requested_by=owner,
                status=approval_status,
            )
            studios[spec['key']] = studio
            self.stdout.write(f'  Estúdio criado: {studio.name} (ativo={studio.is_active})')
        return studios

    def _create_artists(self, studios):
        artist_specs = [
            ('sp_centro', 'Luna Ferreira', 'Realismo e preto e cinza', '@luna.ink'),
            ('sp_centro', 'Diego Martins', 'Old school e neo tradicional', '@diego.ink'),
            ('sp_vila', 'Ana Costa', 'Fine line e minimalista', '@ana.ink'),
            ('rj_copacabana', 'Bruno Silva', 'Oriental e blackwork', '@bruno.ink'),
            ('bh_savassi', 'Marina Souza', 'Aquarela e floral', '@marina.ink'),
        ]
        artists = []
        for studio_key, name, specialties, instagram in artist_specs:
            studio = studios[studio_key]
            artist, created = TattooArtist.objects.get_or_create(
                studio=studio,
                name=name,
                defaults={
                    'bio': f'Tatuadora/tatuador em {studio.city}.',
                    'specialties': specialties,
                    'instagram': instagram,
                },
            )
            if created:
                self.stdout.write(f'  Artista criado: {name} ({studio.name})')
            artists.append(artist)
        return artists

    def _create_portfolio(self, artists, refresh=False):
        for artist in artists:
            existing = list(artist.portfolio_items.all())
            needs_images = not existing or refresh or any(
                is_placeholder_image(item.image) for item in existing
            )

            if not needs_images:
                continue

            if existing:
                for item in existing:
                    item.image.delete(save=False)
                    item.delete()

            saved_count = 0
            for index in range(1, 4):
                content = fetch_portfolio_image(artist.name, index)
                item = PortfolioItem(artist=artist)
                item.image.save(f'{artist.pk}-{index}.jpg', content, save=True)
                saved_count += 1

            if saved_count:
                self.stdout.write(
                    f'  Portfólio com imagens criado para {artist.name} ({saved_count})',
                )

    def _create_budgets(self, users, studios, artists):
        if BudgetRequest.objects.exists():
            self.stdout.write('  Orçamentos já existem — pulando.')
            return

        client1 = users['client1']
        client2 = users['client2']
        client3 = users['client3']
        sp_centro = studios['sp_centro']
        rj = studios['rj_copacabana']

        artist_sp = next(a for a in artists if a.studio_id == sp_centro.pk)
        artist_rj = next(a for a in artists if a.studio_id == rj.pk)

        specs = [
            (client1, sp_centro, artist_sp, 'Braço completo realismo leão', BUDGET_STATUS_SENT),
            (client2, sp_centro, artist_sp, 'Costas tribal geométrico', BUDGET_STATUS_IN_ANALYSIS),
            (client3, rj, artist_rj, 'Panturrilha oriental dragão', BUDGET_STATUS_ANSWERED),
        ]
        for client, studio, artist, description, status in specs:
            BudgetRequest.objects.create(
                client=client,
                studio=studio,
                artist=artist,
                description=description,
                status=status,
            )
            self.stdout.write(
                f'  Orcamento criado: {client.username} -> {studio.name} ({status})'
            )
