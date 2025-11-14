import random
import math
from django.db import models
from .models import Match
from games.models import Game
from .game_distributor import GameDistributor, AdvancedGameDistributor

class BracketGenerator:
    """Generador mejorado de brackets para torneos"""
    
    @staticmethod
    def generate_single_elimination(tournament):
        """Generar bracket de eliminación simple con distribución equitativa de juegos"""
        teams = list(tournament.teams.all())
        if len(teams) < 2:
            return False
        
        # Mezclar equipos aleatoriamente
        random.shuffle(teams)
        
        # Inicializar distribuidor de juegos
        try:
            game_distributor = AdvancedGameDistributor(tournament.id, 'variety_focused')
            
            # Calcular total de partidas para optimización
            total_matches = BracketGenerator._calculate_single_elimination_matches(len(teams))
            game_distributor.optimize_for_tournament_size(total_matches)
            
        except ValueError as e:
            print(f"⚠️ Error al inicializar distribuidor de juegos: {e}")
            return False
        
        round_number = 1
        current_teams = teams[:]
        previous_games = []
        
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
                
                # Asignar juego usando distribuidor inteligente
                game = game_distributor.get_next_game_advanced(previous_games[-3:])  # Evitar repetir últimos 3
                previous_games.append(game)
                
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
        
        # Mostrar reporte de distribución
        report = game_distributor.get_distribution_report()
        print(f"🎮 Distribución de juegos completada:")
        print(f"📊 Total partidas: {report['total_games_assigned']}")
        print(f"🎯 Balance score: {report['balance_analysis'].get('balance_score', 0)}%")
        
        return True
    
    @staticmethod
    def generate_double_elimination(tournament):
        """Generar bracket de eliminación doble con distribución equitativa de juegos"""
        teams = list(tournament.teams.all())
        n = len(teams)
        
        # 1️⃣ CASOS BASE
        if n < 2:
            return False
        
        # Limpiar partidas existentes
        Match.objects.filter(tournament=tournament).delete()
        
        # Mezclar equipos aleatoriamente (seeding)
        random.shuffle(teams)
        
        # Inicializar distribuidor de juegos avanzado
        try:
            game_distributor = AdvancedGameDistributor(tournament.id, 'variety_focused')
            
            # Calcular total aproximado de partidas para optimización
            total_matches = BracketGenerator._calculate_double_elimination_matches(n)
            game_distributor.optimize_for_tournament_size(total_matches)
            
        except ValueError as e:
            print(f"⚠️ Error al inicializar distribuidor de juegos: {e}")
            return False
        
        if n == 2:
            return BracketGenerator._generate_two_teams(tournament, teams, game_distributor)
        
        if n == 3:
            return BracketGenerator._generate_three_teams(tournament, teams, game_distributor)
        
        # 2️⃣ CALCULAR BYES Y ESTRUCTURA BÁSICA
        next_power = 1
        while next_power < n:
            next_power *= 2
        
        byes = next_power - n
        rounds_winners = int(math.log2(next_power))
        
        # 3️⃣ DISTRIBUCIÓN DE BYES BALANCEADA
        distribution = BracketGenerator._distribute_byes(teams, byes)
        
        # 4️⃣ CONSTRUCCIÓN DE MATCHES EN WINNERS
        BracketGenerator._build_winners_bracket(tournament, distribution, rounds_winners, game_distributor)
        
        # 5️⃣ GENERAR LOSERS BRACKET
        BracketGenerator._build_losers_bracket(tournament, rounds_winners, game_distributor)
        
        # 6️⃣ CREAR ETAPA FINAL
        BracketGenerator._create_finals_structure(tournament, game_distributor)
        
        # 7️⃣ MOSTRAR REPORTE DE DISTRIBUCIÓN
        report = game_distributor.get_distribution_report()
        print(f"🎮 Distribución de juegos completada:")
        print(f"📊 Total partidas: {report['total_games_assigned']}")
        print(f"🎯 Balance score: {report['balance_analysis'].get('balance_score', 0)}%")
        print(f"🔄 Ciclos utilizados: {report['cycles_completed']}")
        
        return True
    
    @staticmethod
    def _generate_two_teams(tournament, teams, game_distributor):
        """Caso especial: 2 equipos con distribuidor de juegos"""
        # Winners R1
        Match.objects.create(
            tournament=tournament,
            team1=teams[0],
            team2=teams[1],
            bracket_type='winners',
            round_number=1,
            match_number=1,
            game=game_distributor.get_next_game()
        )
        
        # Gran Final (ganador winners vs perdedor winners)
        Match.objects.create(
            tournament=tournament,
            team1=None,  # Ganador Winners
            team2=None,  # Perdedor Winners (viene de losers)
            bracket_type='grand_final',
            round_number=1,
            match_number=1,
            game=game_distributor.get_next_game()
        )
        
        # Reset Final
        Match.objects.create(
            tournament=tournament,
            team1=None,
            team2=None,
            bracket_type='final_reset',
            round_number=1,
            match_number=1,
            game=game_distributor.get_next_game()
        )
        
        return True
    
    @staticmethod
    def _generate_three_teams(tournament, teams, game_distributor):
        """Caso especial: 3 equipos con distribuidor de juegos"""
        # 1 bye automático al último equipo
        bye_team = teams[2]
        
        # Winners R1: equipos 0 vs 1
        Match.objects.create(
            tournament=tournament,
            team1=teams[0],
            team2=teams[1],
            bracket_type='winners',
            round_number=1,
            match_number=1,
            game=game_distributor.get_next_game()
        )
        
        # Winners R2: bye_team vs ganador R1
        Match.objects.create(
            tournament=tournament,
            team1=bye_team,
            team2=None,  # Ganador R1
            bracket_type='winners',
            round_number=2,
            match_number=1,
            game=game_distributor.get_next_game()
        )
        
        # Losers R1: perdedor Winners R2 vs perdedor Winners R1
        Match.objects.create(
            tournament=tournament,
            team1=None,  # Perdedor Winners R2
            team2=None,  # Perdedor Winners R1
            bracket_type='losers',
            round_number=1,
            match_number=1,
            game=game_distributor.get_next_game()
        )
        
        # Gran Final
        Match.objects.create(
            tournament=tournament,
            team1=None,  # Ganador Winners
            team2=None,  # Ganador Losers
            bracket_type='grand_final',
            round_number=1,
            match_number=1,
            game=game_distributor.get_next_game()
        )
        
        # Reset Final
        Match.objects.create(
            tournament=tournament,
            team1=None,
            team2=None,
            bracket_type='final_reset',
            round_number=1,
            match_number=1,
            game=game_distributor.get_next_game()
        )
        
        return True
    
    @staticmethod
    def _calculate_single_elimination_matches(num_teams):
        """Calcular número total de partidas en eliminación simple"""
        return num_teams - 1
    
    @staticmethod
    def _calculate_double_elimination_matches(num_teams):
        """Calcular número aproximado de partidas en eliminación doble"""
        # Fórmula aproximada: 2n - 2 (en el peor caso)
        return (2 * num_teams) - 2
    
    @staticmethod
    def _distribute_byes(teams, byes):
        """Distribuir byes de manera balanceada - CORREGIDO"""
        # Para 5 equipos: 2 juegan en R1, 3 tienen bye a R2
        teams_in_r1 = len(teams) - byes
        
        # R1: Solo los primeros equipos sin bye
        r1_participants = teams[:teams_in_r1]
        
        # R2: Equipos con bye
        bye_teams = teams[teams_in_r1:]
        
        return {
            'r1_teams': r1_participants,
            'bye_teams': bye_teams,
            'teams_in_r1': teams_in_r1,
            'byes': byes
        }
        """Distribuir byes de manera balanceada - CORREGIDO"""
        # Para 5 equipos: 2 juegan en R1, 3 tienen bye a R2
        teams_in_r1 = len(teams) - byes
        
        # R1: Solo los primeros equipos sin bye
        r1_participants = teams[:teams_in_r1]
        
        # R2: Equipos con bye
        bye_teams = teams[teams_in_r1:]
        
        return {
            'r1_teams': r1_participants,
            'bye_teams': bye_teams,
            'teams_in_r1': teams_in_r1,
            'byes': byes
        }
    
    @staticmethod
    def _build_winners_bracket(tournament, distribution, rounds_winners, game_distributor):
        """Construir Winners Bracket completo con distribuidor de juegos"""
        
        # R1: Solo equipos sin bye
        r1_teams = distribution['r1_teams']
        bye_teams = distribution['bye_teams']
        
        # Crear partidas R1
        match_number = 1
        for i in range(0, len(r1_teams), 2):
            if i + 1 < len(r1_teams):
                Match.objects.create(
                    tournament=tournament,
                    team1=r1_teams[i],
                    team2=r1_teams[i + 1],
                    bracket_type='winners',
                    round_number=1,
                    match_number=match_number,
                    game=game_distributor.get_next_game()
                )
                match_number += 1
        
        # R2: Equipos con bye + ganadores R1
        if rounds_winners >= 2:
            match_number = 1
            bye_index = 0
            
            # Calcular partidas necesarias en R2
            winners_from_r1 = len(r1_teams) // 2
            total_in_r2 = len(bye_teams) + winners_from_r1
            matches_in_r2 = total_in_r2 // 2
            
            for i in range(matches_in_r2):
                team1 = None
                team2 = None
                
                # Asignar equipos con bye primero
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
                    game=game_distributor.get_next_game()
                )
                match_number += 1
        
        # R3+: Partidas vacías para ganadores
        for round_num in range(3, rounds_winners + 1):
            matches_in_round = 2 ** (rounds_winners - round_num)
            
            for match_number in range(1, matches_in_round + 1):
                Match.objects.create(
                    tournament=tournament,
                    team1=None,
                    team2=None,
                    bracket_type='winners',
                    round_number=round_num,
                    match_number=match_number,
                    game=game_distributor.get_next_game()
                )
    
    @staticmethod
    def _build_losers_bracket(tournament, rounds_winners, game_distributor):
        """Construir Losers Bracket - REESCRITO SIMPLE Y CORRECTO"""
        # Para 12 equipos: crear SOLO las partidas que realmente se van a usar
        # No crear partidas vacías que nunca se llenarán
        
        print(f'DEBUG: Construyendo losers bracket SIMPLE para {tournament.teams.count()} equipos')
        
        # Crear solo estructura mínima inicial
        # Losers R1: Para perdedores de Winners R1 (se crearán dinámicamente)
        # Losers R2: Para ganadores de L1 (se crearán dinámicamente)
        # etc.
        
        # NO crear partidas vacías - se crearán cuando sea necesario
        print(f'DEBUG: Losers bracket se construirá dinámicamente según avancen los equipos')
    
    @staticmethod
    def _create_finals_structure(tournament, game_distributor):
        """Crear estructura de finales con distribuidor de juegos"""
        # Gran Final
        Match.objects.create(
            tournament=tournament,
            team1=None,  # Ganador Winners
            team2=None,  # Ganador Losers
            bracket_type='grand_final',
            round_number=1,
            match_number=1,
            game=game_distributor.get_next_game()
        )
        
        # Reset Final (solo se activa si losers gana)
        Match.objects.create(
            tournament=tournament,
            team1=None,
            team2=None,
            bracket_type='final_reset',
            round_number=1,
            match_number=1,
            game=game_distributor.get_next_game()
        )
    
class MatchService:
    """Servicio para gestión de partidas"""
    
    @staticmethod
    def declare_winner(match, winner):
        """Declarar ganador de una partida con lógica de doble eliminación"""
        print(f'DEBUG: Declarando ganador {winner.name} en {match.bracket_type} R{match.round_number} M{match.match_number}')
        
        if match.status == 'completed':
            raise ValueError("La partida ya está completada")
        
        # Verificar si es una partida con BYE (solo un equipo)
        if match.team1 is None or match.team2 is None:
            # Es un BYE - el equipo presente avanza automáticamente
            present_team = match.team1 if match.team1 else match.team2
            if winner != present_team:
                raise ValueError("En una partida con BYE, solo el equipo presente puede ganar")
            
            print(f'DEBUG: Partida con BYE detectada - {winner.name} avanza automáticamente')
            
            # Actualizar partida
            match.winner = winner
            match.status = 'completed'
            match.save()
            
            # No actualizar estadísticas en BYEs
            print(f'DEBUG: Procesando avance automático por BYE...')
            
            # Lógica específica por tipo de bracket
            if match.bracket_type == 'winners':
                print(f'DEBUG: Procesando Winners bracket (BYE)')
                MatchService._handle_winners_bracket_bye(match, winner)
            elif match.bracket_type == 'losers':
                print(f'DEBUG: Procesando Losers bracket (BYE)')
                MatchService._handle_losers_bracket_bye(match, winner)
            
            print(f'DEBUG: Avance automático por BYE completado')
            return True
        
        # Partida normal con dos equipos
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
        
        print(f'DEBUG: Partida completada. Procesando lógica de bracket...')
        
        # Lógica específica por tipo de bracket
        if match.bracket_type == 'winners':
            print(f'DEBUG: Procesando Winners bracket')
            MatchService._handle_winners_bracket_result(match, winner, loser)
        elif match.bracket_type == 'losers':
            print(f'DEBUG: Procesando Losers bracket')
            MatchService._handle_losers_bracket_result(match, winner, loser)
        elif match.bracket_type == 'grand_final':
            print(f'DEBUG: Procesando Grand Final')
            MatchService._handle_grand_final_result(match, winner, loser)
        elif match.bracket_type == 'final_reset':
            print(f'DEBUG: Procesando Final Reset')
            MatchService._handle_final_reset_result(match, winner, loser)
        
        print(f'DEBUG: Lógica de bracket completada')
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
        """Colocar perdedor de Winners en losers - DINÁMICO CORREGIDO con distribuidor"""
        winners_round = winners_match.round_number
        tournament = winners_match.tournament
        
        # Determinar ronda de losers objetivo
        target_losers_round = 2 * winners_round - 1
        
        print(f'DEBUG: Colocando {loser.name} (perdedor Winners R{winners_round}) en Losers R{target_losers_round}')
        
        # Buscar si hay otro perdedor de la misma ronda de winners esperando emparejamiento
        waiting_match = Match.objects.filter(
            tournament=tournament,
            bracket_type='losers',
            round_number=target_losers_round,
            status='pending',
            team1__isnull=False,
            team2__isnull=True
        ).first()
        
        if waiting_match:
            # Hay alguien esperando - emparejar
            waiting_match.team2 = loser
            waiting_match.save()
            print(f'DEBUG: {loser.name} emparejado con {waiting_match.team1.name} en Losers R{target_losers_round} M{waiting_match.match_number}')
        else:
            # Crear nueva partida y esperar rival
            try:
                game_distributor = GameDistributor.create_for_tournament(tournament.id)
                game = game_distributor.get_next_game()
            except ValueError:
                # Fallback si no hay juegos disponibles
                available_games = list(Game.objects.filter(is_active=True))
                game = random.choice(available_games) if available_games else None
            
            existing_matches = Match.objects.filter(
                tournament=tournament,
                bracket_type='losers',
                round_number=target_losers_round
            ).count()
            
            new_match = Match.objects.create(
                tournament=tournament,
                team1=loser,
                team2=None,
                bracket_type='losers',
                round_number=target_losers_round,
                match_number=existing_matches + 1,
                game=game
            )
            print(f'DEBUG: {loser.name} esperando rival en nueva partida Losers R{target_losers_round} M{new_match.match_number}')
    
    @staticmethod
    def _handle_losers_bracket_result(match, winner, loser):
        """Manejar resultado en Losers Bracket - DINÁMICO CORREGIDO con distribuidor"""
        # Perdedor queda eliminado
        loser.bracket_status = 'eliminated'
        loser.save()
        
        # Ganador avanza en losers bracket
        current_round = match.round_number
        next_round = current_round + 1
        
        print(f'DEBUG: {winner.name} ganó Losers R{current_round}, avanzando a R{next_round}')
        
        # Buscar si hay alguien esperando en la siguiente ronda
        waiting_match = Match.objects.filter(
            tournament=match.tournament,
            bracket_type='losers',
            round_number=next_round,
            status='pending',
            team1__isnull=False,
            team2__isnull=True
        ).first()
        
        if waiting_match:
            # Hay alguien esperando - emparejar
            waiting_match.team2 = winner
            waiting_match.save()
            print(f'DEBUG: {winner.name} emparejado con {waiting_match.team1.name} en Losers R{next_round} M{waiting_match.match_number}')
        else:
            # Verificar si debe ir a Grand Final
            max_losers_round = 2 * 4 - 2  # Para 12 equipos, máximo 6 rondas losers
            if next_round > max_losers_round:
                # Va a Grand Final
                grand_final = Match.objects.filter(
                    tournament=match.tournament,
                    bracket_type='grand_final'
                ).first()
                if grand_final and grand_final.team2 is None:
                    grand_final.team2 = winner
                    grand_final.save()
                    print(f'DEBUG: {winner.name} avanza a Gran Final')
                return
            
            # Crear nueva partida y esperar rival o perdedor de winners
            try:
                game_distributor = GameDistributor.create_for_tournament(match.tournament.id)
                game = game_distributor.get_next_game()
            except ValueError:
                # Fallback si no hay juegos disponibles
                available_games = list(Game.objects.filter(is_active=True))
                game = random.choice(available_games) if available_games else None
            
            existing_matches = Match.objects.filter(
                tournament=match.tournament,
                bracket_type='losers',
                round_number=next_round
            ).count()
            
            new_match = Match.objects.create(
                tournament=match.tournament,
                team1=winner,
                team2=None,
                bracket_type='losers',
                round_number=next_round,
                match_number=existing_matches + 1,
                game=game
            )
            print(f'DEBUG: {winner.name} esperando rival en nueva partida Losers R{next_round} M{new_match.match_number}')
    
    @staticmethod
    def _handle_grand_final_result(match, winner, loser):
        """Manejar resultado de Gran Final"""
        if winner.bracket_status == 'winners':
            # Ganador de Winners gana - es campeón
            winner.bracket_status = 'champion'
            winner.save()
            loser.bracket_status = 'runner_up'
            loser.save()
            
            # Limpiar estados de equipos restantes
            MatchService._finalize_tournament_states(match.tournament)
            
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
        
        # Limpiar estados de equipos restantes
        MatchService._finalize_tournament_states(match.tournament)
        
        # Finalizar torneo
        match.tournament.status = 'completed'
        match.tournament.save()
    
    @staticmethod
    def _finalize_tournament_states(tournament):
        """Limpiar estados de equipos al finalizar torneo"""
        # Todos los equipos que no son champion o runner_up deben ser eliminated
        for team in tournament.teams.all():
            if team.bracket_status not in ['champion', 'runner_up']:
                team.bracket_status = 'eliminated'
                team.save()
        
        print(f'DEBUG: Estados de equipos finalizados para torneo {tournament.name}')
    
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
    
    @staticmethod
    def cleanup_impossible_matches(tournament):
        """Limpiar partidas imposibles y auto-avanzar equipos huérfanos - INTELIGENTE"""
        print(f'DEBUG: Iniciando limpieza inteligente para {tournament.name}')
        
        # 1. Detectar equipos huérfanos (esperando rivales que nunca llegarán)
        orphaned_teams = MatchService._detect_orphaned_teams(tournament)
        
        # 2. Auto-avanzar equipos huérfanos
        for team, match in orphaned_teams:
            print(f'DEBUG: Auto-avanzando equipo huérfano: {team.name} en {match.bracket_type} R{match.round_number}')
            MatchService._auto_advance_team(match, team)
        
        # 3. Verificar finalización
        MatchService._check_tournament_completion(tournament)
        
        return len(orphaned_teams)
    
    @staticmethod
    def _detect_orphaned_teams(tournament):
        """Detectar equipos que esperan rivales imposibles"""
        orphaned = []
        
        # Buscar partidas con un solo equipo esperando
        waiting_matches = Match.objects.filter(
            tournament=tournament,
            status='pending',
            team1__isnull=False,
            team2__isnull=True
        ).order_by('bracket_type', 'round_number')
        
        for match in waiting_matches:
            if MatchService._is_team_orphaned(tournament, match):
                orphaned.append((match.team1, match))
        
        return orphaned
    
    @staticmethod
    def _is_team_orphaned(tournament, match):
        """Verificar si un equipo está realmente huérfano"""
        bracket_type = match.bracket_type
        round_number = match.round_number
        
        if bracket_type == 'losers':
            # En losers, verificar si pueden llegar más equipos
            # Contar equipos activos en winners que podrían caer
            active_winners = tournament.teams.filter(bracket_status='winners').count()
            
            # Contar equipos en losers que podrían avanzar
            active_losers_below = Match.objects.filter(
                tournament=tournament,
                bracket_type='losers',
                round_number__lt=round_number,
                status='pending',
                team1__isnull=False,
                team2__isnull=False
            ).count()
            
            # Si no hay equipos que puedan llegar a esta ronda, está huérfano
            if active_winners == 0 and active_losers_below == 0:
                print(f'DEBUG: Equipo {match.team1.name} huérfano en Losers R{round_number} - no hay rivales posibles')
                return True
        
        elif bracket_type == 'winners':
            # En winners, verificar si hay otros equipos que puedan avanzar
            potential_opponents = Match.objects.filter(
                tournament=tournament,
                bracket_type='winners',
                round_number__lt=round_number,
                status='pending',
                team1__isnull=False,
                team2__isnull=False
            ).count()
            
            if potential_opponents == 0:
                print(f'DEBUG: Equipo {match.team1.name} huérfano en Winners R{round_number} - no hay rivales posibles')
                return True
        
        return False
    
    @staticmethod
    def _auto_advance_team(match, team):
        """Auto-avanzar equipo huérfano"""
        print(f'DEBUG: Auto-avanzando {team.name} desde {match.bracket_type} R{match.round_number}')
        
        # Marcar partida como completada con BYE
        match.winner = team
        match.status = 'completed'
        match.save()
        
        # Procesar avance según bracket
        if match.bracket_type == 'winners':
            MatchService._handle_winners_bracket_bye(match, team)
        elif match.bracket_type == 'losers':
            MatchService._handle_losers_bracket_bye(match, team)
        
        print(f'DEBUG: {team.name} auto-avanzado exitosamente')
    
    @staticmethod
    def manual_advance_team(match_id):
        """Avanzar equipo manualmente (para botón de admin)"""
        try:
            match = Match.objects.get(id=match_id)
            
            # Verificar que es una partida válida para avance manual
            if match.status != 'pending':
                raise ValueError("La partida ya está completada")
            
            if match.team1 is None:
                raise ValueError("No hay equipo para avanzar")
            
            if match.team2 is not None:
                raise ValueError("La partida tiene dos equipos, no es elegible para avance manual")
            
            team = match.team1
            print(f'DEBUG: Avance manual solicitado para {team.name} en {match.bracket_type} R{match.round_number}')
            
            # Usar la misma lógica que auto-advance
            MatchService._auto_advance_team(match, team)
            
            return True
            
        except Match.DoesNotExist:
            raise ValueError("Partida no encontrada")
    
    @staticmethod
    def get_advanceable_matches(tournament):
        """Obtener partidas elegibles para avance manual"""
        return Match.objects.filter(
            tournament=tournament,
            status='pending',
            team1__isnull=False,
            team2__isnull=True
        ).order_by('bracket_type', 'round_number', 'match_number')
    
    @staticmethod
    def _cleanup_truly_impossible_matches(tournament):
        """Eliminar solo las partidas que realmente no pueden completarse"""
        # Contar equipos activos (no eliminados)
        active_teams = tournament.teams.exclude(bracket_status='eliminated').count()
        
        # Solo eliminar TBD vs TBD si no hay suficientes equipos activos para llenarlas
        if active_teams <= 2:  # Solo quedan 2 o menos equipos activos
            impossible_matches = Match.objects.filter(
                tournament=tournament,
                team1__isnull=True,
                team2__isnull=True,
                status='pending'
            ).exclude(bracket_type__in=['grand_final', 'final_reset'])
            
            deleted_count = impossible_matches.count()
            if deleted_count > 0:
                impossible_matches.delete()
                print(f'DEBUG: Eliminadas {deleted_count} partidas verdaderamente imposibles')
        
        # Verificar si el torneo puede finalizar
        MatchService._check_tournament_completion(tournament)
    
    @staticmethod
    def _check_tournament_completion(tournament):
        """Verificar si el torneo puede finalizar automáticamente"""
        remaining_matches = Match.objects.filter(
            tournament=tournament,
            status='pending'
        ).exclude(
            team1__isnull=True,
            team2__isnull=True
        )
        
        if remaining_matches.count() == 0:
            print(f'DEBUG: No hay más partidas jugables, determinando campeón...')
            
            # Buscar el último ganador de winners bracket
            last_winners_match = Match.objects.filter(
                tournament=tournament,
                bracket_type='winners',
                status='completed'
            ).order_by('-round_number', '-match_number').first()
            
            if last_winners_match and last_winners_match.winner:
                champion = last_winners_match.winner
                champion.bracket_status = 'champion'
                champion.save()
                
                # Buscar runner-up (último ganador de losers)
                last_losers_match = Match.objects.filter(
                    tournament=tournament,
                    bracket_type='losers',
                    status='completed'
                ).order_by('-round_number', '-match_number').first()
                
                if last_losers_match and last_losers_match.winner:
                    runner_up = last_losers_match.winner
                    runner_up.bracket_status = 'runner_up'
                    runner_up.save()
                
                # Finalizar torneo
                MatchService._finalize_tournament_states(tournament)
                tournament.status = 'completed'
                tournament.save()
                
                print(f'DEBUG: Torneo finalizado automáticamente. Campeón: {champion.name}')
    
    @staticmethod
    def _handle_losers_bracket_bye(match, winner):
        """Manejar BYE en Losers Bracket"""
        # En un BYE de losers, el equipo avanza a la siguiente ronda disponible
        current_round = match.round_number
        
        # Buscar siguiente partida disponible en losers
        next_losers_match = Match.objects.filter(
            tournament=match.tournament,
            bracket_type='losers',
            round_number__gt=current_round,
            status='pending'
        ).filter(
            models.Q(team1__isnull=True) | models.Q(team2__isnull=True)
        ).order_by('round_number', 'match_number').first()
        
        if next_losers_match:
            if next_losers_match.team1 is None:
                next_losers_match.team1 = winner
            else:
                next_losers_match.team2 = winner
            next_losers_match.save()
            print(f'DEBUG: {winner.name} avanza por BYE a Losers R{next_losers_match.round_number} M{next_losers_match.match_number}')
        else:
            # No hay más partidas en losers - va a Grand Final
            grand_final = Match.objects.filter(
                tournament=match.tournament,
                bracket_type='grand_final'
            ).first()
            if grand_final and grand_final.team2 is None:
                grand_final.team2 = winner
                grand_final.save()
                print(f'DEBUG: {winner.name} avanza por BYE a Gran Final')
    
    @staticmethod
    def _handle_winners_bracket_bye(match, winner):
        """Manejar BYE en Winners Bracket"""
        # En un BYE de winners, el equipo avanza a la siguiente ronda
        current_round = match.round_number
        
        # Buscar siguiente partida en winners
        next_winners_match = Match.objects.filter(
            tournament=match.tournament,
            bracket_type='winners',
            round_number=current_round + 1,
            status='pending'
        ).filter(
            models.Q(team1__isnull=True) | models.Q(team2__isnull=True)
        ).order_by('match_number').first()
        
        if next_winners_match:
            if next_winners_match.team1 is None:
                next_winners_match.team1 = winner
            else:
                next_winners_match.team2 = winner
            next_winners_match.save()
            winner.bracket_status = 'winners'
            winner.save()
            print(f'DEBUG: {winner.name} avanza por BYE a Winners R{next_winners_match.round_number} M{next_winners_match.match_number}')
        else:
            # No hay más rondas en Winners - va a Grand Final
            grand_final = Match.objects.filter(
                tournament=match.tournament,
                bracket_type='grand_final'
            ).first()
            if grand_final and grand_final.team1 is None:
                grand_final.team1 = winner
                grand_final.save()
                print(f'DEBUG: {winner.name} avanza por BYE a Gran Final')
