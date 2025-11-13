#!/usr/bin/env python3
"""
Script de prueba para el sistema de autenticación
"""

import requests
import json

BASE_URL = 'http://localhost:8000/api'

def test_auth_system():
    print("🎮 Probando Sistema de Autenticación")
    print("=" * 50)
    
    # 1. Probar login de administrador
    print("\n1. 🔐 Login Administrador")
    admin_login = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=admin_login)
    if response.status_code == 200:
        admin_data = response.json()
        admin_token = admin_data['tokens']['access']
        print(f"✅ Login exitoso: {admin_data['user']['username']} ({admin_data['user']['user_type']})")
    else:
        print(f"❌ Error en login: {response.text}")
        return
    
    # 2. Probar login de jugador
    print("\n2. 🎯 Login Jugador")
    player_login = {
        "username": "player1",
        "password": "player123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=player_login)
    if response.status_code == 200:
        player_data = response.json()
        player_token = player_data['tokens']['access']
        print(f"✅ Login exitoso: {player_data['user']['username']} ({player_data['user']['user_type']})")
        print(f"   Perfil: {player_data['user']['profile']['first_name']} {player_data['user']['profile']['last_name']}")
    else:
        print(f"❌ Error en login: {response.text}")
        return
    
    # 3. Probar registro de nuevo jugador
    print("\n3. ✨ Registro Nuevo Jugador")
    new_player = {
        "username": "testplayer",
        "password": "test123",
        "attuid": "ATT999",
        "first_name": "Test",
        "last_name": "Player",
        "has_played_games": True,
        "favorite_game_types": ["fighting", "arcade"]
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=new_player)
    if response.status_code == 201:
        new_user_data = response.json()
        print(f"✅ Registro exitoso: {new_user_data['user']['username']}")
        print(f"   ATTUID: {new_user_data['user']['attuid']}")
    else:
        print(f"❌ Error en registro: {response.text}")
    
    # 4. Probar tipos de juegos
    print("\n4. 🎮 Tipos de Juegos Disponibles")
    response = requests.get(f"{BASE_URL}/auth/game-types/")
    if response.status_code == 200:
        game_types = response.json()['game_types']
        print("✅ Tipos de juegos:")
        for game_type in game_types[:5]:  # Mostrar solo los primeros 5
            print(f"   - {game_type['label']}")
    else:
        print(f"❌ Error obteniendo tipos: {response.text}")
    
    # 5. Probar acceso protegido con token de admin
    print("\n5. 🛡️ Acceso Protegido (Admin)")
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = requests.get(f"{BASE_URL}/tournaments/", headers=headers)
    print(f"✅ Acceso a torneos: {response.status_code}")
    
    # 6. Probar acceso protegido con token de jugador
    print("\n6. 🛡️ Acceso Protegido (Jugador)")
    headers = {'Authorization': f'Bearer {player_token}'}
    response = requests.get(f"{BASE_URL}/tournaments/", headers=headers)
    print(f"✅ Acceso a torneos: {response.status_code}")
    
    # 7. Probar acceso sin token
    print("\n7. 🚫 Acceso Sin Token")
    response = requests.get(f"{BASE_URL}/tournaments/")
    print(f"❌ Acceso denegado: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("🎉 Pruebas de autenticación completadas")

if __name__ == "__main__":
    try:
        test_auth_system()
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor Django")
        print("   Asegúrate de que el servidor esté ejecutándose en http://localhost:8000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
