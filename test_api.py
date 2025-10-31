#!/usr/bin/env python3
"""
Script de prueba para verificar que todos los endpoints de la API funcionen correctamente.
Ejecutar con: python test_api.py
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000/api"

def test_endpoint(method, endpoint, data=None, files=None):
    """Probar un endpoint específico"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            if files:
                response = requests.post(url, data=data, files=files)
            else:
                response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        print(f"✅ {method} {endpoint} - Status: {response.status_code}")
        
        if response.status_code >= 400:
            print(f"   ❌ Error: {response.text}")
            return None
        
        return response.json() if response.content else None
        
    except requests.exceptions.ConnectionError:
        print(f"❌ {method} {endpoint} - Error: No se puede conectar al servidor")
        print("   💡 Asegúrate de que el servidor esté ejecutándose: python manage.py runserver")
        return None
    except Exception as e:
        print(f"❌ {method} {endpoint} - Error: {str(e)}")
        return None

def main():
    print("🎮 Probando API del Torneo de Videojuegos")
    print("=" * 50)
    
    # 1. Probar endpoints de torneos
    print("\n🏆 PROBANDO TOURNAMENTS")
    tournaments = test_endpoint("GET", "/tournaments/")
    
    if tournaments and len(tournaments) > 0:
        tournament_id = tournaments[0]['id']
        print(f"   📊 Torneo encontrado: {tournaments[0]['name']} (ID: {tournament_id})")
        
        # Detalles del torneo
        test_endpoint("GET", f"/tournaments/{tournament_id}/")
        
        # Estadísticas
        test_endpoint("GET", f"/tournaments/{tournament_id}/stats/")
    
    # 2. Probar endpoints de equipos
    print("\n👥 PROBANDO TEAMS")
    teams = test_endpoint("GET", "/teams/")
    
    if teams and len(teams) > 0:
        team_id = teams[0]['id']
        print(f"   👥 Equipo encontrado: {teams[0]['name']} (ID: {team_id})")
        
        # Jugadores del equipo
        test_endpoint("GET", f"/teams/{team_id}/players/")
    
    # 3. Probar endpoints de juegos
    print("\n🎮 PROBANDO GAMES")
    games = test_endpoint("GET", "/games/")
    test_endpoint("GET", "/games/predefined/")
    
    # 4. Probar endpoints de partidas
    print("\n🏅 PROBANDO MATCHES")
    matches = test_endpoint("GET", "/matches/")
    
    if tournaments and len(tournaments) > 0:
        tournament_id = tournaments[0]['id']
        test_endpoint("GET", f"/matches/visualization/?tournament_id={tournament_id}")
        test_endpoint("GET", f"/matches/next-matches/?tournament_id={tournament_id}")
    
    # 5. Probar endpoints de chat
    print("\n💬 PROBANDO CHAT")
    messages = test_endpoint("GET", "/messages/")
    
    if tournaments and len(tournaments) > 0:
        tournament_id = tournaments[0]['id']
        test_endpoint("GET", f"/rooms/by-tournament/?tournament_id={tournament_id}")
        test_endpoint("GET", f"/messages/recent/?tournament_id={tournament_id}")
    
    # 6. Probar creación de datos
    print("\n🆕 PROBANDO CREACIÓN DE DATOS")
    
    # Crear torneo de prueba
    new_tournament_data = {
        "name": "Torneo API Test",
        "description": "Torneo creado desde el script de prueba",
        "tournament_type": "single",
        "max_teams": 4,
        "points_per_win": 3,
        "points_per_participation": 1
    }
    
    new_tournament = test_endpoint("POST", "/tournaments/", new_tournament_data)
    
    if new_tournament:
        new_tournament_id = new_tournament['id']
        print(f"   ✅ Nuevo torneo creado: ID {new_tournament_id}")
        
        # Crear equipo de prueba
        new_team_data = {
            "tournament": new_tournament_id,
            "name": "Equipo API Test",
            "players": [
                {"name": "Test Player 1", "is_captain": True},
                {"name": "Test Player 2", "is_captain": False}
            ]
        }
        
        new_team = test_endpoint("POST", "/teams/", new_team_data)
        
        if new_team:
            print(f"   ✅ Nuevo equipo creado: {new_team['name']}")
        
        # Crear mensaje de chat
        chat_message_data = {
            "tournament": new_tournament_id,
            "username": "Test User",
            "message": "¡Mensaje de prueba desde la API!"
        }
        
        test_endpoint("POST", "/messages/", chat_message_data)
    
    print("\n" + "=" * 50)
    print("🎉 Pruebas completadas!")
    print("\n💡 Para más detalles, consulta API_DOCUMENTATION.md")
    print("🚀 Para iniciar el servidor: python manage.py runserver")

if __name__ == "__main__":
    main()
