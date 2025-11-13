from django.core.management.base import BaseCommand
from users.models import User, UserTournamentAssignment
from tournaments.models import Tournament

class Command(BaseCommand):
    help = 'Asigna jugadores a torneos de prueba'

    def handle(self, *args, **options):
        # Obtener admin y jugadores
        admin = User.objects.get(username='admin')
        
        # Crear un torneo de prueba si no existe
        tournament, created = Tournament.objects.get_or_create(
            name='Torneo de Prueba',
            defaults={
                'description': 'Torneo para probar asignaciones',
                'max_teams': 8,
                'tournament_type': 'single_elimination',
                'status': 'registration'
            }
        )
        
        if created:
            self.stdout.write(f'✅ Torneo creado: {tournament.name}')
        
        # Asignar jugadores al torneo
        players = User.objects.filter(user_type='player')
        
        for player in players:
            assignment, created = UserTournamentAssignment.objects.get_or_create(
                user=player,
                tournament=tournament,
                defaults={
                    'status': 'confirmed',
                    'assigned_by': admin
                }
            )
            
            if created:
                self.stdout.write(f'✅ {player.username} asignado a {tournament.name}')
            else:
                self.stdout.write(f'ℹ️ {player.username} ya estaba asignado')
        
        self.stdout.write(
            self.style.SUCCESS('🎮 Asignaciones completadas')
        )
