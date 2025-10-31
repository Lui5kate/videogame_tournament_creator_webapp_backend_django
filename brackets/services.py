import random
from .models import Match
from games.models import Game

class BracketGenerator:
    """Generador mejorado de brackets para torneos"""
    
    @staticmethod
    def generate_single_elimination(tournament):
        """Generar bracket de eliminación simple"""
        teams = list(tournament.teams.all())
        if len(teams) < 2:
            return False
        
        # Mezclar equipos aleatoriamente
        random.shuffle(teams)
        
        # Obtener juegos disponibles
        available_games = list(Game.objects.filter(is_active=True))
        
        round_number = 1
        current_teams = teams[:]
        
        # Generar todas las rondas
        while len(current_teams) > 1:
            next_round_teams = []
            match_number = 1
            
            # Crear partidas para la ronda actual
            for i in range(0, len(current_teams), 2):
                if i + 1 < len(current_teams):
                    # Partida normal
                    team1 = current_teams[i]
                    team2 = current_teams[i + 1]
                else:
                    # Equipo pasa automáticamente (bye)
                    team1 = current_teams[i]
                    team2 = None
                
                # Asignar juego aleatoriamente
                game = random.choice(available_games) if available_games else None
                
                match = Match.objects.create(
                    tournament=tournament,
                    team1=team1,
                    team2=team2,
                    bracket_type='winners',
                    round_number=round_number,
                    match_number=match_number,
                    game=game
                )
                
                # Si no hay team2, team1 avanza automáticamente
                if team2 is None:
                    match.winner = team1
                    match.status = 'completed'
                    match.save()
                    team1.add_victory()
                
                # El ganador (o team1 si hay bye) avanza
                next_round_teams.append(team1 if team2 is None else None)
                match_number += 1
            
            # Preparar para siguiente ronda
            current_teams = [team for team in next_round_teams if team is not None]
            round_number += 1
        
        # El último equipo es el campeón
        if current_teams:
            champion = current_teams[0]
            champion.bracket_status = 'champion'
            champion.save()
        
        return True
    
    @staticmethod
    def generate_double_elimination(tournament):
        """Generar bracket de eliminación doble"""
        teams = list(tournament.teams.all())
        if len(teams) < 2:
            return False
        
        # Por ahora, generar eliminación simple
        # TODO: Implementar lógica completa de eliminación doble
        return BracketGenerator.generate_single_elimination(tournament)
    
    @staticmethod
    def advance_winner(match, winner):
        """Avanzar ganador al siguiente round"""
        if winner not in [match.team1, match.team2]:
            raise ValueError("El equipo ganador debe ser uno de los participantes")
        
        loser = match.team2 if winner == match.team1 else match.team1
        
        # Actualizar estadísticas
        winner.add_victory()
        loser.add_loss()
        
        # Buscar siguiente partida para el ganador
        next_match = Match.objects.filter(
            tournament=match.tournament,
            bracket_type=match.bracket_type,
            round_number=match.round_number + 1,
            team1__isnull=True
        ).first()
        
        if next_match:
            next_match.team1 = winner
            next_match.save()
        else:
            # Buscar partida donde team2 esté vacío
            next_match = Match.objects.filter(
                tournament=match.tournament,
                bracket_type=match.bracket_type,
                round_number=match.round_number + 1,
                team2__isnull=True
            ).first()
            
            if next_match:
                next_match.team2 = winner
                next_match.save()
        
        # Si no hay más partidas, es el campeón
        if not next_match:
            winner.bracket_status = 'champion'
            winner.save()
            
            # Finalizar torneo
            match.tournament.status = 'completed'
            match.tournament.save()
        
        return True

class MatchService:
    """Servicio para gestión de partidas"""
    
    @staticmethod
    def declare_winner(match, winner):
        """Declarar ganador de una partida"""
        if match.status == 'completed':
            raise ValueError("La partida ya está completada")
        
        if winner not in [match.team1, match.team2]:
            raise ValueError("El equipo ganador debe ser uno de los participantes")
        
        # Actualizar partida
        match.winner = winner
        match.status = 'completed'
        match.save()
        
        # Avanzar ganador
        BracketGenerator.advance_winner(match, winner)
        
        return True
    
    @staticmethod
    def get_next_matches(tournament, limit=5):
        """Obtener próximas partidas a jugar"""
        return Match.objects.filter(
            tournament=tournament,
            status='pending',
            team1__isnull=False,
            team2__isnull=False
        ).order_by('bracket_type', 'round_number', 'match_number')[:limit]
    
    @staticmethod
    def get_bracket_visualization(tournament):
        """Obtener datos para visualización del bracket"""
        matches = Match.objects.filter(tournament=tournament)
        
        bracket_data = {
            'winners': matches.filter(bracket_type='winners').order_by('round_number', 'match_number'),
            'losers': matches.filter(bracket_type='losers').order_by('round_number', 'match_number'),
            'finals': matches.filter(bracket_type__in=['grand_final', 'final_reset']).order_by('bracket_type')
        }
        
        return bracket_data
