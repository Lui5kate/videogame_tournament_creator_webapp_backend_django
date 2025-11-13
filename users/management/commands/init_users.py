from django.core.management.base import BaseCommand
from users.models import User, PlayerProfile

class Command(BaseCommand):
    help = 'Inicializa usuarios de prueba'

    def handle(self, *args, **options):
        # Crear usuario administrador
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_user(
                username='admin',
                password='admin123',
                user_type='admin'
            )
            self.stdout.write(
                self.style.SUCCESS(f'✅ Usuario administrador creado: admin/admin123')
            )
        
        # Crear usuario jugador de prueba
        if not User.objects.filter(username='player1').exists():
            player_user = User.objects.create_user(
                username='player1',
                password='player123',
                user_type='player',
                attuid='ATT001'
            )
            
            PlayerProfile.objects.create(
                user=player_user,
                first_name='Juan',
                last_name='Pérez',
                has_played_games=True,
                favorite_game_types=['fighting', 'racing', 'arcade']
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Usuario jugador creado: player1/player123')
            )
        
        self.stdout.write(
            self.style.SUCCESS('🎮 Usuarios de prueba inicializados correctamente')
        )
