#!/usr/bin/env python3
"""
Script de prueba para el algoritmo de distribución equitativa de juegos
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tournament_manager.settings')
django.setup()

from tournaments.models import Tournament
from teams.models import Team
from games.models import Game
from brackets.models import Match
from brackets.services import BracketGenerator
from brackets.game_distributor import GameDistributor, AdvancedGameDistributor

def test_game_distribution():
    """Probar la distribución equitativa de juegos"""
    print("🎮 INICIANDO PRUEBA DE DISTRIBUCIÓN DE JUEGOS")
    print("=" * 60)
    
    # 1. Crear torneo de prueba
    tournament = Tournament.objects.create(
        name="Test Distribución Juegos",
        tournament_type="double",
        max_teams=8,
        status="registration"
    )
    print(f"✅ Torneo creado: {tournament.name}")
    
    # 2. Crear equipos
    team_names = ["Alpha", "Beta", "Gamma", "Delta", "Echo", "Foxtrot"]
    teams = []
    for name in team_names:
        team = Team.objects.create(
            name=f"Team {name}",
            tournament=tournament
        )
        teams.append(team)
    print(f"✅ {len(teams)} equipos creados")
    
    # 3. Verificar juegos disponibles
    games = Game.objects.filter(is_active=True)
    print(f"✅ {games.count()} juegos activos disponibles:")
    for game in games:
        print(f"   - {game.name}")
    
    if games.count() == 0:
        print("❌ No hay juegos activos. Creando juegos de prueba...")
        test_games = [
            "Mario Kart 8", "Super Smash Bros", "Street Fighter 6", 
            "Tekken 8", "FIFA 24", "Rocket League"
        ]
        for game_name in test_games:
            Game.objects.create(name=game_name, is_active=True)
        games = Game.objects.filter(is_active=True)
        print(f"✅ {games.count()} juegos de prueba creados")
    
    # 4. Probar distribuidor básico
    print("\n🔧 PROBANDO DISTRIBUIDOR BÁSICO")
    print("-" * 40)
    
    try:
        distributor = GameDistributor.create_for_tournament(tournament.id)
        
        # Obtener 15 juegos para simular un torneo
        test_games = distributor.get_multiple_games(15)
        
        print("📊 Juegos asignados:")
        for i, game in enumerate(test_games, 1):
            print(f"   Partida {i:2d}: {game.name}")
        
        # Mostrar reporte
        report = distributor.get_distribution_report()
        print(f"\n📈 REPORTE DE DISTRIBUCIÓN:")
        print(f"   Total asignado: {report['total_games_assigned']}")
        print(f"   Ciclos completados: {report['cycles_completed']}")
        print(f"   Balance score: {report['balance_analysis'].get('balance_score', 0)}%")
        
        print("\n📋 Distribución por juego:")
        for game_name, stats in report['distribution_by_game'].items():
            print(f"   {game_name}: {stats['usage_count']} usos ({stats['percentage']}%)")
        
    except Exception as e:
        print(f"❌ Error en distribuidor básico: {e}")
    
    # 5. Probar distribuidor avanzado
    print("\n🚀 PROBANDO DISTRIBUIDOR AVANZADO")
    print("-" * 40)
    
    try:
        advanced_distributor = AdvancedGameDistributor(tournament.id, 'variety_focused')
        
        # Simular asignación con variedad
        previous_games = []
        assigned_games = []
        
        for i in range(12):
            game = advanced_distributor.get_next_game_advanced(previous_games[-2:])
            assigned_games.append(game)
            previous_games.append(game)
        
        print("📊 Juegos con variedad:")
        for i, game in enumerate(assigned_games, 1):
            print(f"   Partida {i:2d}: {game.name}")
        
        # Verificar que no hay repeticiones consecutivas
        consecutive_repeats = 0
        for i in range(1, len(assigned_games)):
            if assigned_games[i].id == assigned_games[i-1].id:
                consecutive_repeats += 1
        
        print(f"\n🎯 Repeticiones consecutivas: {consecutive_repeats}")
        
        # Previsualizar próximos juegos
        preview = advanced_distributor.preview_next_games(5)
        print(f"🔮 Próximos 5 juegos: {', '.join(preview)}")
        
    except Exception as e:
        print(f"❌ Error en distribuidor avanzado: {e}")
    
    # 6. Probar generación completa de brackets
    print("\n🏆 PROBANDO GENERACIÓN COMPLETA DE BRACKETS")
    print("-" * 50)
    
    try:
        # Cambiar estado del torneo
        tournament.status = "active"
        tournament.save()
        
        # Generar brackets con el nuevo algoritmo
        success = BracketGenerator.generate_double_elimination(tournament)
        
        if success:
            print("✅ Brackets generados exitosamente")
            
            # Analizar distribución de juegos en las partidas
            matches = Match.objects.filter(tournament=tournament)
            game_usage = {}
            
            for match in matches:
                if match.game:
                    game_name = match.game.name
                    if game_name not in game_usage:
                        game_usage[game_name] = 0
                    game_usage[game_name] += 1
            
            print(f"\n📊 DISTRIBUCIÓN EN BRACKETS REALES:")
            print(f"   Total partidas creadas: {matches.count()}")
            print(f"   Partidas con juego asignado: {matches.filter(game__isnull=False).count()}")
            
            print("\n📋 Uso por juego en brackets:")
            for game_name, count in sorted(game_usage.items()):
                percentage = (count / matches.count() * 100) if matches.count() > 0 else 0
                print(f"   {game_name}: {count} usos ({percentage:.1f}%)")
            
            # Verificar balance
            if game_usage:
                min_usage = min(game_usage.values())
                max_usage = max(game_usage.values())
                balance_score = (1 - (max_usage - min_usage) / max_usage) * 100 if max_usage > 0 else 100
                
                print(f"\n🎯 ANÁLISIS DE BALANCE:")
                print(f"   Uso mínimo: {min_usage}")
                print(f"   Uso máximo: {max_usage}")
                print(f"   Diferencia: {max_usage - min_usage}")
                print(f"   Score de balance: {balance_score:.1f}%")
                
                if balance_score >= 80:
                    print("   ✅ Distribución EXCELENTE")
                elif balance_score >= 60:
                    print("   ⚠️ Distribución BUENA")
                else:
                    print("   ❌ Distribución MEJORABLE")
        else:
            print("❌ Error al generar brackets")
            
    except Exception as e:
        print(f"❌ Error en generación de brackets: {e}")
        import traceback
        traceback.print_exc()
    
    # 7. Limpiar datos de prueba
    print(f"\n🧹 LIMPIANDO DATOS DE PRUEBA")
    tournament.delete()
    print("✅ Torneo de prueba eliminado")
    
    print("\n🎉 PRUEBA COMPLETADA")
    print("=" * 60)

if __name__ == "__main__":
    test_game_distribution()
