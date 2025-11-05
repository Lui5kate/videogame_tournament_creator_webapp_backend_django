import random
import math
from django.db import models
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
        """Generar bracket de eliminación doble siguiendo lógica de start.gg"""
        teams = list(tournament.teams.all())
        n = len(teams)
        if n < 2:
            return False
        
        # Limpiar partidas existentes
        Match.objects.filter(tournament=tournament).delete()
        
        # Mezclar equipos aleatoriamente
        random.shuffle(teams)
        available_games = list(Game.objects.filter(is_active=True))
        
        # Calcular k = siguiente potencia de 2 >= n
        k = 1
        while k < n:
            k *= 2
        
        byes = k - n  # Número de byes necesarios
        
        # Generar Winners Bracket
        BracketGenerator._generate_winners_with_byes(tournament, teams, k, byes, available_games)
        
        # Generar Losers Bracket
        BracketGenerator._generate_losers_structure(tournament, k, available_games)
        
        # Crear finales
        BracketGenerator._create_finals(tournament, available_games)
        
        return True
    
    @staticmethod
    def _generate_winners_with_byes(tournament, teams, k, byes, available_games):
        """Generar Winners Bracket con byes correctos"""
        rounds = int(math.log2(k))
        
        # Primera ronda: solo equipos sin bye
        teams_in_first_round = len(teams) - byes
        matches_in_first_round = teams_in_first_round // 2
        
        # Crear partidas de primera ronda
        for i in range(matches_in_first_round):
            Match.objects.create(
                tournament=tournament,
                team1=teams[i * 2],
                team2=teams[i * 2 + 1],
                bracket_type='winners',
                round_number=1,
                match_number=i + 1,
                game=random.choice(available_games) if available_games else None
            )
        
        # Crear estructura para rondas posteriores
        for round_num in range(2, rounds + 1):
            matches_in_round = k // (2 ** round_num)
            
            for match_num in range(1, matches_in_round + 1):
                # Asignar equipos con bye en segunda ronda
                team1 = None
                team2 = None
                
                if round_num == 2 and byes > 0:
                    # Asignar equipos con bye
                    bye_index = teams_in_first_round + (match_num - 1)
                    if bye_index < len(teams):
                        if match_num % 2 == 1:
                            team1 = teams[bye_index]
                        else:
                            team2 = teams[bye_index]
                
                Match.objects.create(
                    tournament=tournament,
                    team1=team1,
                    team2=team2,
                    bracket_type='winners',
                    round_number=round_num,
                    match_number=match_num,
                    game=random.choice(available_games) if available_games else None
                )
    
    @staticmethod
    def _generate_losers_structure(tournament, k, available_games):
        """Generar estructura de Losers Bracket correcta para 6 equipos"""
        winners_rounds = int(math.log2(k))
        
        # Para 6 equipos (k=8):
        # L1: 1 partida (2 perdedores de Winners R1)
        # L2: 1 partida (ganador L1 vs perdedor Winners R2)  
        # L3: 1 partida (ganador L2 vs perdedor Winners R2)
        # L4: 1 partida (ganador L3 vs perdedor Winners Finals)
        
        # Solo crear las partidas que realmente se van a usar
        losers_structure = {
            1: 1,  # L1: perdedores Winners R1
            2: 1,  # L2: ganador L1 vs perdedor Winners R2
            3: 1,  # L3: ganador L2 vs perdedor Winners R2  
            4: 1   # L4: ganador L3 vs perdedor Winners Finals
        }
        
        for round_num, matches_count in losers_structure.items():
            for match_num in range(1, matches_count + 1):
                Match.objects.create(
                    tournament=tournament,
                    team1=None,
                    team2=None,
                    bracket_type='losers',
                    round_number=round_num,
                    match_number=match_num,
                    game=random.choice(available_games) if available_games else None
                )
    
    @staticmethod
    def _create_finals(tournament, available_games):
        """Crear Gran Final y Final Reset"""
        game1 = random.choice(available_games) if available_games else None
        game2 = random.choice(available_games) if available_games else None
        
        # Gran Final
        Match.objects.create(
            tournament=tournament,
            team1=None,  # Ganador de Winners
            team2=None,  # Ganador de Losers
            bracket_type='grand_final',
            round_number=1,
            match_number=1,
            game=game1
        )
        
        # Final Reset
        Match.objects.create(
            tournament=tournament,
            team1=None,
            team2=None,
            bracket_type='final_reset',
            round_number=1,
            match_number=1,
            game=game2
        )
    
    @staticmethod
    def _generate_winners_bracket_first_round(tournament, teams, available_games):
        """Generar primera ronda del Winners Bracket con byes correctos"""
        num_teams = len(teams)
        
        # Calcular equipos que necesitan bye para llegar a potencia de 2
        next_power_of_2 = 1
        while next_power_of_2 < num_teams:
            next_power_of_2 *= 2
        
        teams_with_bye = next_power_of_2 - num_teams
        teams_in_first_round = num_teams - teams_with_bye
        
        match_number = 1
        
        # Crear partidas de primera ronda (solo para equipos sin bye)
        for i in range(0, teams_in_first_round, 2):
            team1 = teams[i]
            team2 = teams[i + 1] if i + 1 < teams_in_first_round else None
            
            game = random.choice(available_games) if available_games else None
            
            match = Match.objects.create(
                tournament=tournament,
                team1=team1,
                team2=team2,
                bracket_type='winners',
                round_number=1,
                match_number=match_number,
                game=game
            )
            
            match_number += 1
        
        # Crear partidas de segunda ronda (semifinals) con byes
        if teams_with_bye > 0:
            # Los equipos con bye van directo a R2
            bye_teams = teams[teams_in_first_round:]
            
            # Calcular partidas de R2
            winners_from_r1 = teams_in_first_round // 2
            total_teams_in_r2 = winners_from_r1 + teams_with_bye
            
            match_number = 1
            bye_index = 0
            
            for i in range(0, total_teams_in_r2, 2):
                game = random.choice(available_games) if available_games else None
                
                # Determinar equipos para R2
                team1 = None
                team2 = None
                
                if bye_index < len(bye_teams):
                    team1 = bye_teams[bye_index]
                    bye_index += 1
                
                if bye_index < len(bye_teams):
                    team2 = bye_teams[bye_index]
                    bye_index += 1
                
                Match.objects.create(
                    tournament=tournament,
                    team1=team1,
                    team2=team2,
                    bracket_type='winners',
                    round_number=2,
                    match_number=match_number,
                    game=game
                )
                
                match_number += 1
    
    @staticmethod
    def _generate_losers_bracket_structure(tournament, num_teams, available_games):
        """Generar estructura del Losers Bracket"""
        # Calcular número de rondas necesarias
        winners_rounds = math.ceil(math.log2(num_teams))
        losers_rounds = (winners_rounds - 1) * 2
        
        # Crear partidas vacías para Losers Bracket
        for round_num in range(1, losers_rounds + 1):
            # Calcular número de partidas por ronda
            if round_num % 2 == 1:  # Rondas impares: reciben perdedores de Winners
                matches_in_round = max(1, num_teams // (2 ** ((round_num + 1) // 2 + 1)))
            else:  # Rondas pares: solo ganadores de Losers
                matches_in_round = max(1, num_teams // (2 ** (round_num // 2 + 2)))
            
            for match_num in range(1, matches_in_round + 1):
                game = random.choice(available_games) if available_games else None
                
                Match.objects.create(
                    tournament=tournament,
                    team1=None,
                    team2=None,
                    bracket_type='losers',
                    round_number=round_num,
                    match_number=match_num,
                    game=game
                )
    
    @staticmethod
    def _create_grand_final(tournament, available_games):
        """Crear Gran Final"""
        game = random.choice(available_games) if available_games else None
        
        # Gran Final
        Match.objects.create(
            tournament=tournament,
            team1=None,  # Ganador de Winners
            team2=None,  # Ganador de Losers
            bracket_type='grand_final',
            round_number=1,
            match_number=1,
            game=game
        )
        
        # Final Reset (si es necesario)
        Match.objects.create(
            tournament=tournament,
            team1=None,
            team2=None,
            bracket_type='final_reset',
            round_number=1,
            match_number=1,
            game=game
        )

class MatchService:
    """Servicio para gestión de partidas"""
    
    @staticmethod
    def declare_winner(match, winner):
        """Declarar ganador de una partida con lógica de doble eliminación"""
        if match.status == 'completed':
            raise ValueError("La partida ya está completada")
        
        if winner not in [match.team1, match.team2]:
            raise ValueError("El equipo ganador debe ser uno de los participantes")
        
        loser = match.team2 if winner == match.team1 else match.team1
        
        # Actualizar partida
        match.winner = winner
        match.status = 'completed'
        match.save()
        
        # Actualizar estadísticas
        winner.add_victory()
        loser.add_loss()
        
        # Lógica específica por tipo de bracket
        if match.bracket_type == 'winners':
            MatchService._handle_winners_bracket_result(match, winner, loser)
        elif match.bracket_type == 'losers':
            MatchService._handle_losers_bracket_result(match, winner, loser)
        elif match.bracket_type == 'grand_final':
            MatchService._handle_grand_final_result(match, winner, loser)
        elif match.bracket_type == 'final_reset':
            MatchService._handle_final_reset_result(match, winner, loser)
        
        return True
    
    @staticmethod
    def _handle_winners_bracket_result(match, winner, loser):
        """Manejar resultado en Winners Bracket"""
        # Ganador avanza en Winners
        next_winners_match = Match.objects.filter(
            tournament=match.tournament,
            bracket_type='winners',
            round_number=match.round_number + 1,
            status='pending'
        ).filter(
            models.Q(team1__isnull=True) | models.Q(team2__isnull=True)
        ).order_by('match_number').first()
        
        if next_winners_match:
            # Hay una siguiente ronda en Winners
            if next_winners_match.team1 is None:
                next_winners_match.team1 = winner
            else:
                next_winners_match.team2 = winner
            next_winners_match.save()
            winner.bracket_status = 'winners'
            winner.save()
        else:
            # No hay más rondas en Winners - va a Grand Final
            grand_final = Match.objects.filter(
                tournament=match.tournament,
                bracket_type='grand_final'
            ).first()
            if grand_final:
                if grand_final.team1 is None:
                    grand_final.team1 = winner
                    grand_final.save()
        
        # Perdedor va a Losers Bracket
        loser.bracket_status = 'losers'
        loser.save()
        
        # Colocar perdedor en Losers Bracket
        MatchService._place_loser_in_losers_bracket(match, loser)
    
    @staticmethod
    def _place_loser_in_losers_bracket(winners_match, loser):
        """Colocar perdedor de Winners en la posición correcta de Losers"""
        winners_round = winners_match.round_number
        
        # Lógica de start.gg para colocación de perdedores:
        # - Perdedores de Winners R1 van a Losers R1
        # - Perdedores de Winners R2 van a Losers R2 (después de L1)
        # - Perdedores de Winners R3 van a Losers R4 (después de L3)
        # - etc.
        
        if winners_round == 1:
            target_losers_round = 1
        else:
            target_losers_round = (winners_round - 1) * 2
        
        # Buscar partida disponible en la ronda correcta de Losers
        losers_match = Match.objects.filter(
            tournament=winners_match.tournament,
            bracket_type='losers',
            round_number=target_losers_round,
            status='pending'
        ).filter(
            models.Q(team1__isnull=True) | models.Q(team2__isnull=True)
        ).order_by('match_number').first()
        
        if losers_match:
            if losers_match.team1 is None:
                losers_match.team1 = loser
            else:
                losers_match.team2 = loser
            losers_match.save()
        else:
            # Si no hay partida disponible, buscar en ronda siguiente
            next_round = target_losers_round + 1
            next_losers_match = Match.objects.filter(
                tournament=winners_match.tournament,
                bracket_type='losers',
                round_number=next_round,
                status='pending'
            ).filter(
                models.Q(team1__isnull=True) | models.Q(team2__isnull=True)
            ).order_by('match_number').first()
            
            if next_losers_match:
                if next_losers_match.team1 is None:
                    next_losers_match.team1 = loser
                else:
                    next_losers_match.team2 = loser
                next_losers_match.save()
    
    @staticmethod
    def _handle_losers_bracket_result(match, winner, loser):
        """Manejar resultado en Losers Bracket"""
        # Perdedor queda eliminado
        loser.bracket_status = 'eliminated'
        loser.save()
        
        # Determinar siguiente ronda correcta
        current_round = match.round_number
        
        # Para 6 equipos: L1 -> L3, L2 -> L3, L3 -> L4, L4 -> Grand Final
        if current_round == 1:
            next_round = 3  # L1 va a L3
        elif current_round == 2:
            next_round = 3  # L2 va a L3
        elif current_round == 3:
            next_round = 4  # L3 va a L4
        else:
            # L4 va a Grand Final
            grand_final = Match.objects.filter(
                tournament=match.tournament,
                bracket_type='grand_final'
            ).first()
            if grand_final and grand_final.team2 is None:
                grand_final.team2 = winner
                grand_final.save()
            return
        
        # Buscar partida en la siguiente ronda
        next_losers_match = Match.objects.filter(
            tournament=match.tournament,
            bracket_type='losers',
            round_number=next_round,
            status='pending'
        ).filter(
            models.Q(team1__isnull=True) | models.Q(team2__isnull=True)
        ).order_by('match_number').first()
        
        if next_losers_match:
            if next_losers_match.team1 is None:
                next_losers_match.team1 = winner
            else:
                next_losers_match.team2 = winner
            next_losers_match.save()
    
    @staticmethod
    def _handle_grand_final_result(match, winner, loser):
        """Manejar resultado de Gran Final"""
        if winner.bracket_status == 'winners':
            # Ganador de Winners gana - es campeón
            winner.bracket_status = 'champion'
            winner.save()
            loser.bracket_status = 'runner_up'
            loser.save()
            
            # Finalizar torneo
            match.tournament.status = 'completed'
            match.tournament.save()
        else:
            # Ganador de Losers gana - Bracket Reset
            final_reset = Match.objects.filter(
                tournament=match.tournament,
                bracket_type='final_reset'
            ).first()
            if final_reset:
                final_reset.team1 = winner  # Ganador de Losers
                final_reset.team2 = loser   # Perdedor de Winners
                final_reset.save()
    
    @staticmethod
    def _handle_final_reset_result(match, winner, loser):
        """Manejar resultado de Final Reset"""
        winner.bracket_status = 'champion'
        winner.save()
        loser.bracket_status = 'runner_up'
        loser.save()
        
        # Finalizar torneo
        match.tournament.status = 'completed'
        match.tournament.save()
    
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
