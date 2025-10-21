

import asyncio
import websockets
import json
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs
from websockets.asyncio.server import ServerConnection
import os
from dotenv import load_dotenv


load_dotenv()

if not (SECRET_TOKEN := os.getenv('SECRET_TOKEN')):
    raise ValueError("SECRET_TOKEN is not set")

connected_clients : dict[ServerConnection, str] = {}



async def handler(websocket : ServerConnection):
    """Gestion d'une connexion WebSocket"""
    print(f"🔗 Nouvelle connexion: {websocket}")
    parsed = urlparse(websocket.request.path)
    params = parse_qs(parsed.query)
    token = params.get("token", [None])[0]

    if token != SECRET_TOKEN:
        await websocket.close(1008, 'Unauthorized')
        return
    
    current_username = "Anonyme"
    if connected_clients.get(websocket) != "Anonyme":
        current_username = connected_clients.get(websocket)
    else:
        connected_clients[websocket] = "Anonyme"
    print(f"✅ Nouvelle connexion (total: {len(connected_clients)})")

    broadcast_data = {
        'type': 'user_joined',
        'username': current_username
    }
    for client in connected_clients:
        print("broadcast message sent")
        await client.send(json.dumps(broadcast_data))



    try:
        async for message in websocket:
            print(f"📩 Message reçu: {message}")
            data = json.loads(message)

            if data['type'] == 'message':
                username = data.get('username', 'Anonyme')
                if connected_clients.get(websocket) != username:
                    connected_clients[websocket] = username
                text = data.get('text', '')
                broadcast_data = {
                    'type': 'message',
                    'username': username,
                    'text': text,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }

                # Broadcast à tous les clients connectés
                for client in connected_clients:
                    await client.send(json.dumps(broadcast_data))

            if data['type'] == 'user_joined':
                username = data.get('username', 'Anonyme')
                print(f"username: {username}")
                if connected_clients.get(websocket) != username:
                    connected_clients[websocket] = username
                broadcast_data = {
                    'type': 'user_joined',
                    'username': username
                }
                for client in connected_clients:
                    await client.send(json.dumps(broadcast_data))
                print(f"📢 {username} a rejoint le chat")

            # if data['type'] == 'user_left':
            #     username = data.get('username', 'Anonyme')
            #     if websocket in connected_clients:
            #         del connected_clients[websocket]
            #         broadcast_data = {
            #             'type': 'user_left',
            #             'username': username
            #         }
            #         for client in connected_clients:
            #             await client.send(json.dumps(broadcast_data))
            #         print(f"📉 {username} a quitté le chat")

    
    except websockets.ConnectionClosed:
        print("❌ Connexion fermée")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
    finally:
        if websocket in connected_clients:
            username_to_broadcast = connected_clients.pop(websocket)
            broadcast_data = {
                'type': 'user_left',
                'username': username_to_broadcast
            }
            for client in connected_clients:
                await client.send(json.dumps(broadcast_data))
            print(f"📉 {username_to_broadcast} a quitté le chat (total: {len(connected_clients)})")
        else:
            print(f"❌ Une personne non trouvée dans la liste des clients connectés s'est déconnectée")


async def main():
    print("🚀 Serveur WebSocket démarré sur ws://localhost:8080")
    async with websockets.serve(handler, "0.0.0.0", 8080):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
