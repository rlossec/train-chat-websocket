

import asyncio
import websockets
import json
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs
from websockets.asyncio.server import ServerConnection

from config import Config
from logger import logger

connected_clients: dict[ServerConnection, str] = {}


async def handler(websocket: ServerConnection):
    """Handle WebSocket connection."""
    client_ip = websocket.remote_address[0] if websocket.remote_address else "unknown"
    logger.info(f"[CONNECTION] New connection from {client_ip}")
    
    parsed = urlparse(websocket.request.path)
    params = parse_qs(parsed.query)
    token = params.get("token", [None])[0]

    # Token validation
    if not token:
        logger.warning(f"[SECURITY] Missing token from {client_ip}")
        await websocket.close(1008, 'Missing token')
        return
    
    if len(token) < 8:
        logger.warning(f"[SECURITY] Token too short from {client_ip}")
        await websocket.close(1008, 'Invalid token')
        return
    
    if token != Config.SECRET_TOKEN:
        logger.warning(f"[SECURITY] Invalid token from {client_ip}")
        await websocket.close(1008, 'Invalid token')
        return
    
    current_username = "Anonyme"
    if connected_clients.get(websocket) != "Anonyme":
        current_username = connected_clients.get(websocket)
    else:
        connected_clients[websocket] = "Anonyme"
    
    logger.info(f"[AUTH] Authenticated for {current_username} (total clients: {len(connected_clients)})")

    broadcast_data = {
        'type': 'user_joined',
        'username': current_username
    }
    for client in connected_clients:
        await client.send(json.dumps(broadcast_data))
    logger.debug(f"[BROADCAST] Connection message sent for {current_username}")

    try:
        async for message in websocket:
            logger.debug(f"[MESSAGE] Received message: {message}")
            try:
                data = json.loads(message)
            except json.JSONDecodeError as e:
                logger.error(f"[ERROR] JSON parsing error: {e}")
                continue

            # Validate received data
            if not isinstance(data, dict) or 'type' not in data:
                logger.warning(f"[VALIDATION] Invalid message received: {data}")
                continue

            if data['type'] == 'message':
                username = data.get('username', 'Anonyme')
                if connected_clients.get(websocket) != username:
                    connected_clients[websocket] = username
                text = data.get('text', '')
                
                # Message length validation
                if len(text) > Config.MAX_MESSAGE_LENGTH:
                    logger.warning(f"[VALIDATION] Message too long for {username} ({len(text)} chars)")
                    continue
                
                if not text.strip():
                    logger.warning(f"[VALIDATION] Empty message for {username}")
                    continue
                
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
                logger.info(f"[JOIN] {username} joined the chat")
                if connected_clients.get(websocket) != username:
                    connected_clients[websocket] = username
                broadcast_data = {
                    'type': 'user_joined',
                    'username': username
                }
                for client in connected_clients:
                    await client.send(json.dumps(broadcast_data))
                logger.debug(f"[BROADCAST] Connection message sent for {username}")
    
    except websockets.ConnectionClosed:
        logger.info("[DISCONNECTION] Connection closed by client")
    except Exception as e:
        logger.error(f"[ERROR] Unexpected error in WebSocket handler: {e}", exc_info=True)
    finally:
        if websocket in connected_clients:
            username_to_broadcast = connected_clients.pop(websocket)
            logger.info(f"[LEAVE] {username_to_broadcast} left the chat (total clients: {len(connected_clients)})")
            broadcast_data = {
                'type': 'user_left',
                'username': username_to_broadcast
            }
            for client in connected_clients:
                await client.send(json.dumps(broadcast_data))
        else:
            logger.warning("[WARNING] Attempt to disconnect an unregistered client")


async def main():
    logger.info(f"[STARTUP] Starting WebSocket server on {Config.HOST}:{Config.PORT}")
    logger.info(f"[CONFIG] Authentication token configured: {'*' * len(Config.SECRET_TOKEN)}")
    
    async with websockets.serve(handler, Config.HOST, Config.PORT):
        logger.info(f"[READY] WebSocket server ready on ws://{Config.HOST}:{Config.PORT}")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
