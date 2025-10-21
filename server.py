

import asyncio
import websockets
import json
from datetime import datetime
from urllib.parse import urlparse, parse_qs

import os
from dotenv import load_dotenv


load_dotenv()

if not (SECRET_TOKEN := os.getenv('SECRET_TOKEN')):
    raise ValueError("SECRET_TOKEN is not set")

connected_clients = set()

async def handler(websocket):
    """Gestion d'une connexion WebSocket"""
    
    parsed = urlparse(websocket.request.path)
    params = parse_qs(parsed.query)
    token = params.get("token", [None])[0]

    if token != SECRET_TOKEN:
        await websocket.close(1008, 'Unauthorized')
        return

    # Connexion validée
    connected_clients.add(websocket)
    print(f"✅ Nouvelle connexion (total: {len(connected_clients)})")

    # TODO : Broadcast notification user_joined (nécessite stocker username)
    u

    try:
        async for message in websocket:
            print(f"📩 Message reçu: {message}")
            data = json.loads(message)

            if data['type'] == 'message':
                # TODO : Broadcast à tous les clients
                # Ajouter timestamp
                # Format : {"type": "message", "username": "...", "text": "...", "timestamp": "..."}

                broadcast_data = {
                    'type': 'message',
                    'username': data['username'],
                    'text': data['text'],
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }

                # Broadcast à tous les clients connectés
                websockets.broadcast(connected_clients, json.dumps(broadcast_data))

    except websockets.ConnectionClosed:
        print("❌ Connexion fermée")
    finally:
        connected_clients.remove(websocket)
        print(f"📉 Client déconnecté (total: {len(connected_clients)})")

        # TODO : Broadcast notification user_left

async def main():
    print("🚀 Serveur WebSocket démarré sur ws://localhost:8080")
    async with websockets.serve(handler, "0.0.0.0", 8080):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
