"""
Algoritmo complejo para distribución equitativa de juegos en torneos
Asegura que todos los juegos se asignen de forma cíclica y balanceada
"""
import random
from typing import List, Dict, Any
from games.models import Game

class GameDistributor:
    """
    Distribuidor inteligente de juegos para partidas de torneo
    
    Algoritmo:
    1. Obtiene todos los juegos activos de la BD
    2. Crea un pool cíclico que se repite infinitamente
    3. Distribuye equitativamente asegurando que todos los juegos se usen
    4. Cuando se agotan todos, reinicia el ciclo con orden aleatorio diferente
    """
    
    def __init__(self, tournament_id: int):
        self.tournament_id = tournament_id
        self.available_games = list(Game.objects.filter(is_active=True))
        self.game_pool = []
        self.current_index = 0
        self.cycle_count = 0
        
        # Estadísticas para debugging
        self.distribution_stats = {}
        
        if not self.available_games:
            raise ValueError("No hay juegos activos disponibles para el torneo")
        
        # Inicializar primer ciclo
        self._initialize_new_cycle()
    
    def _initialize_new_cycle(self):
        """Inicializar un nuevo ciclo de distribución de juegos"""
        self.cycle_count += 1
        
        # Crear copia de juegos y mezclar aleatoriamente
        cycle_games = self.available_games.copy()
        random.shuffle(cycle_games)
        
        # Agregar al pool
        self.game_pool.extend(cycle_games)
        
        print(f"🎮 Ciclo {self.cycle_count} iniciado con {len(cycle_games)} juegos")
        print(f"📊 Pool actual: {len(self.game_pool)} juegos disponibles")
    
    def get_next_game(self) -> Game:
        """
        Obtener el siguiente juego en la distribución cíclica
        
        Returns:
            Game: Siguiente juego a asignar
        """
        # Si llegamos al final del pool, crear nuevo ciclo
        if self.current_index >= len(self.game_pool):
            self._initialize_new_cycle()
        
        # Obtener juego actual
        game = self.game_pool[self.current_index]
        self.current_index += 1
        
        # Actualizar estadísticas
        game_name = game.name
        if game_name not in self.distribution_stats:
            self.distribution_stats[game_name] = 0
        self.distribution_stats[game_name] += 1
        
        print(f"🎯 Asignado: {game.name} (uso #{self.distribution_stats[game_name]})")
        
        return game
    
    def get_multiple_games(self, count: int) -> List[Game]:
        """
        Obtener múltiples juegos de forma secuencial
        
        Args:
            count: Número de juegos a obtener
            
        Returns:
            List[Game]: Lista de juegos asignados
        """
        games = []
        for _ in range(count):
            games.append(self.get_next_game())
        return games
    
    def get_distribution_report(self) -> Dict[str, Any]:
        """
        Generar reporte de distribución de juegos
        
        Returns:
            Dict: Estadísticas de uso de juegos
        """
        total_assigned = sum(self.distribution_stats.values())
        
        report = {
            'total_games_assigned': total_assigned,
            'unique_games_available': len(self.available_games),
            'cycles_completed': self.cycle_count,
            'current_cycle_progress': f"{self.current_index}/{len(self.game_pool) if self.game_pool else 0}",
            'distribution_by_game': {},
            'balance_analysis': {}
        }
        
        # Análisis por juego
        for game_name, usage_count in self.distribution_stats.items():
            percentage = (usage_count / total_assigned * 100) if total_assigned > 0 else 0
            report['distribution_by_game'][game_name] = {
                'usage_count': usage_count,
                'percentage': round(percentage, 2)
            }
        
        # Análisis de balance
        if self.distribution_stats:
            usage_counts = list(self.distribution_stats.values())
            min_usage = min(usage_counts)
            max_usage = max(usage_counts)
            
            report['balance_analysis'] = {
                'min_usage': min_usage,
                'max_usage': max_usage,
                'usage_difference': max_usage - min_usage,
                'is_balanced': (max_usage - min_usage) <= 1,  # Diferencia máxima de 1
                'balance_score': round((1 - (max_usage - min_usage) / max_usage) * 100, 2) if max_usage > 0 else 100
            }
        
        return report
    
    def reset_distribution(self):
        """Reiniciar completamente la distribución"""
        self.game_pool = []
        self.current_index = 0
        self.cycle_count = 0
        self.distribution_stats = {}
        self._initialize_new_cycle()
        print("🔄 Distribución de juegos reiniciada")
    
    @classmethod
    def create_for_tournament(cls, tournament_id: int) -> 'GameDistributor':
        """
        Factory method para crear distribuidor para un torneo específico
        
        Args:
            tournament_id: ID del torneo
            
        Returns:
            GameDistributor: Instancia configurada para el torneo
        """
        return cls(tournament_id)
    
    def preview_next_games(self, count: int = 5) -> List[str]:
        """
        Previsualizar los próximos juegos sin consumirlos
        
        Args:
            count: Número de juegos a previsualizar
            
        Returns:
            List[str]: Nombres de los próximos juegos
        """
        preview = []
        temp_index = self.current_index
        temp_pool = self.game_pool.copy()
        
        for i in range(count):
            # Si necesitamos más juegos, simular nuevo ciclo
            if temp_index >= len(temp_pool):
                cycle_games = self.available_games.copy()
                random.shuffle(cycle_games)
                temp_pool.extend(cycle_games)
            
            if temp_index < len(temp_pool):
                preview.append(temp_pool[temp_index].name)
                temp_index += 1
        
        return preview

class AdvancedGameDistributor(GameDistributor):
    """
    Versión avanzada del distribuidor con funcionalidades adicionales
    """
    
    def __init__(self, tournament_id: int, distribution_strategy: str = 'balanced'):
        super().__init__(tournament_id)
        self.distribution_strategy = distribution_strategy
        self.game_weights = {}
        self.forbidden_sequences = []
        
        # Inicializar pesos según estrategia
        self._initialize_strategy()
    
    def _initialize_strategy(self):
        """Inicializar estrategia de distribución"""
        if self.distribution_strategy == 'weighted':
            # Asignar pesos basados en popularidad o preferencias
            for game in self.available_games:
                # Peso base 1, se puede ajustar según criterios
                self.game_weights[game.id] = 1
        
        elif self.distribution_strategy == 'variety_focused':
            # Evitar repeticiones consecutivas del mismo juego
            self.forbidden_sequences = ['same_game_consecutive']
    
    def get_next_game_advanced(self, previous_games: List[Game] = None) -> Game:
        """
        Obtener siguiente juego con lógica avanzada
        
        Args:
            previous_games: Lista de juegos anteriores para evitar repeticiones
            
        Returns:
            Game: Siguiente juego optimizado
        """
        if self.distribution_strategy == 'variety_focused' and previous_games:
            # Evitar repetir el último juego si es posible
            last_game = previous_games[-1] if previous_games else None
            
            # Intentar obtener un juego diferente
            attempts = 0
            max_attempts = len(self.available_games) * 2
            
            while attempts < max_attempts:
                candidate_game = self.get_next_game()
                
                if not last_game or candidate_game.id != last_game.id:
                    return candidate_game
                
                # Si es el mismo juego, intentar con el siguiente
                attempts += 1
            
            # Si no se puede evitar repetición, usar el candidato
            return candidate_game
        
        # Estrategia estándar
        return self.get_next_game()
    
    def optimize_for_tournament_size(self, total_matches: int):
        """
        Optimizar distribución basada en el tamaño del torneo
        
        Args:
            total_matches: Número total de partidas esperadas
        """
        games_count = len(self.available_games)
        
        if total_matches <= games_count:
            # Torneo pequeño: usar cada juego una vez
            print(f"🎯 Torneo pequeño: {total_matches} partidas, {games_count} juegos")
            print("📋 Estrategia: Un juego por partida sin repetición")
        
        elif total_matches <= games_count * 2:
            # Torneo mediano: máximo 2 usos por juego
            print(f"🎯 Torneo mediano: {total_matches} partidas, {games_count} juegos")
            print("📋 Estrategia: Máximo 2 usos por juego")
        
        else:
            # Torneo grande: distribución cíclica completa
            cycles_needed = (total_matches // games_count) + 1
            print(f"🎯 Torneo grande: {total_matches} partidas, {games_count} juegos")
            print(f"📋 Estrategia: {cycles_needed} ciclos completos necesarios")
