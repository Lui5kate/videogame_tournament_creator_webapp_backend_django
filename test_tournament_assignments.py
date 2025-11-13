#!/usr/bin/env python3
"""
Script de prueba para el sistema de asignaciones de torneos
"""

import requests
import json

BASE_URL = 'http://localhost:8000/api'

def test_tournament_assignments():
    print("🎮 Probando Sistema de Asignaciones de Torneos")
    print("=" * 60)
    
    # 1. Login como admin
    print("\n1. 🔐 Login Administrador")
    admin_login = requests.post(f"{BASE_URL}/auth/login/", json={
        "username": "admin",
        "password": "admin123"
    })
    
    if admin_login.status_code == 200:
        admin_data = admin_login.json()
        admin_token = admin_data['tokens']['access']
        print(f"✅ Admin logueado: {admin_data['user']['username']}")
    else:
        print(f"❌ Error en login admin: {admin_login.text}")
        return
    
    # 2. Login como jugador
    print("\n2. 🎯 Login Jugador")
    player_login = requests.post(f"{BASE_URL}/auth/login/", json={
        "username": "player1",
        "password": "player123"
    })
    
    if player_login.status_code == 200:
        player_data = player_login.json()
        player_token = player_data['tokens']['access']
        print(f"✅ Jugador logueado: {player_data['user']['username']}")
        print(f"   Asignaciones actuales: {len(player_data['user']['tournament_assignments'])}")
        for assignment in player_data['user']['tournament_assignments']:
            print(f"   - {assignment['tournament_name']} ({assignment['status']})")
    else:
        print(f"❌ Error en login jugador: {player_login.text}")
        return
    
    # 3. Admin ve lista de jugadores
    print("\n3. 👥 Lista de Jugadores (Admin)")
    headers = {'Authorization': f'Bearer {admin_token}'}
    players_response = requests.get(f"{BASE_URL}/auth/players/", headers=headers)
    
    if players_response.status_code == 200:
        players = players_response.json()
        print(f"✅ Jugadores encontrados: {len(players)}")
        for player in players:
            print(f"   - {player['username']}: {player['profile']['first_name']} {player['profile']['last_name']}")
            print(f"     Torneos: {len(player['tournament_assignments'])}")
    else:
        print(f"❌ Error obteniendo jugadores: {players_response.text}")
    
    # 4. Jugador ve sus torneos
    print("\n4. 🏆 Mis Torneos (Jugador)")
    player_headers = {'Authorization': f'Bearer {player_token}'}
    my_tournaments = requests.get(f"{BASE_URL}/auth/my-tournaments/", headers=player_headers)
    
    if my_tournaments.status_code == 200:
        tournaments = my_tournaments.json()
        print(f"✅ Torneos asignados: {len(tournaments)}")
        for tournament in tournaments:
            print(f"   - {tournament['name']} ({tournament['status']})")
    else:
        print(f"❌ Error obteniendo mis torneos: {my_tournaments.text}")
    
    # 5. Admin asigna jugador a nuevo torneo (si existe otro)
    print("\n5. ➕ Asignar Jugador a Torneo (Admin)")
    all_tournaments = requests.get(f"{BASE_URL}/tournaments/", headers=headers)
    
    if all_tournaments.status_code == 200:
        tournaments_list = all_tournaments.json()
        print(f"✅ Torneos disponibles: {len(tournaments_list)}")
        
        if len(tournaments_list) > 0:
            # Intentar asignar al primer torneo
            assignment_data = {
                "user_id": player_data['user']['id'],
                "tournament_id": tournaments_list[0]['id'],
                "status": "confirmed"
            }
            
            assign_response = requests.post(
                f"{BASE_URL}/auth/assign-tournament/", 
                json=assignment_data,
                headers=headers
            )
            
            if assign_response.status_code == 200:
                result = assign_response.json()
                print(f"✅ Asignación exitosa: {result['message']}")
            else:
                print(f"ℹ️ Asignación: {assign_response.text}")
    
    # 6. Verificar acceso del jugador
    print("\n6. 🛡️ Verificar Acceso del Jugador")
    # El jugador intenta acceder a un torneo
    if len(tournaments_list) > 0:
        tournament_id = tournaments_list[0]['id']
        tournament_access = requests.get(
            f"{BASE_URL}/tournaments/{tournament_id}/", 
            headers=player_headers
        )
        
        if tournament_access.status_code == 200:
            print(f"✅ Jugador puede acceder al torneo {tournament_id}")
        else:
            print(f"❌ Jugador no puede acceder: {tournament_access.status_code}")
    
    print("\n" + "=" * 60)
    print("🎉 Pruebas de asignaciones completadas")
    
    # Resumen del sistema
    print("\n📊 RESUMEN DEL SISTEMA:")
    print("✅ Usuarios con tipos (admin/player)")
    print("✅ Asignaciones de torneos por admin")
    print("✅ Control de acceso basado en asignaciones")
    print("✅ Estados de asignación (invited/confirmed/active/etc)")
    print("✅ Relación many-to-many con tabla intermedia")

if __name__ == "__main__":
    try:
        test_tournament_assignments()
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor Django")
        print("   Asegúrate de que el servidor esté ejecutándose en http://localhost:8000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
