from django.core.management.base import BaseCommand
from tournaments.models import Tournament
from teams.models import Team, Player
from games.models import Game
from chat.models import ChatRoom

class Command(BaseCommand):
    help = 'Inicializar datos de prueba para el torneo'
    
    def handle(self, *args, **options):
        self.stdout.write('Inicializando datos de prueba...')
        
        # Crear juegos predefinidos
        self.stdout.write('Creando juegos predefinidos...')
        Game.create_predefined_games()
        
        # Crear torneo de prueba
        tournament, created = Tournament.objects.get_or_create(
            name="Torneo de Prueba Gaming",
            defaults={
                'description': 'Torneo de prueba para testing de la aplicación',
                'tournament_type': 'single',
                'status': 'registration',
                'max_teams': 8,
                'points_per_win': 3,
                'points_per_participation': 1
            }
        )
        
        if created:
            self.stdout.write(f'✅ Torneo creado: {tournament.name}')
        else:
            self.stdout.write(f'ℹ️  Torneo ya existe: {tournament.name}')
        
        # Crear sala de chat
        chat_room, created = ChatRoom.objects.get_or_create(
            tournament=tournament,
            defaults={'is_active': True}
        )
        
        if created:
            self.stdout.write('✅ Sala de chat creada')
        
        # Crear equipos de prueba
        sample_teams = [
            ('Los Guerreros', ['Mario', 'Luigi']),
            ('Team Rocket', ['Ash', 'Pikachu']),
            ('Los Campeones', ['Link', 'Zelda']),
            ('Fire Squad', ['Ryu', 'Ken']),
        ]
        
        for team_name, players in sample_teams:
            team, created = Team.objects.get_or_create(
                tournament=tournament,
                name=team_name
            )
            
            if created:
                self.stdout.write(f'✅ Equipo creado: {team_name}')
                
                # Crear jugadores
                for i, player_name in enumerate(players):
                    Player.objects.create(
                        team=team,
                        name=player_name,
                        is_captain=(i == 0)  # Primer jugador es capitán
                    )
                    self.stdout.write(f'  👤 Jugador: {player_name}')
            else:
                self.stdout.write(f'ℹ️  Equipo ya existe: {team_name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Datos de prueba inicializados exitosamente!\n'
                f'📊 Torneo: {tournament.name}\n'
                f'👥 Equipos: {tournament.teams.count()}\n'
                f'🎮 Juegos disponibles: {Game.objects.filter(is_active=True).count()}\n'
                f'\n🚀 Puedes iniciar el servidor con: python manage.py runserver'
            )
        )
