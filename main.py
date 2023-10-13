# This is a sample Python script.
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
import paho.mqtt.publish as mqtt_publish
from starlette.middleware.cors import CORSMiddleware
from typing import Set

# Press the green button in the gutter to run the script.

app = FastAPI()
allowed_origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],  # You can specify HTTP methods (e.g., ["GET", "POST"])
    allow_headers=["*"],  # You can specify allowed headers
)
@app.get("/items")
def user_list():
    return {"message": "Welcome to BINGO"}

websocket_connections: Set[WebSocket] = set()  # Set to store WebSocket connections

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websocket_connections.add(websocket)  # Add the WebSocket connection to the set
    print("websocket_connections", websocket_connections)
    try:
        while True:
            data = await websocket.receive_json()
            # print('Received message:', data)  # Add this line for debugging
            # Handle the received data (simulating MQTT-like behavior)
            # Publish the received message to MQTT
            # mqtt_publish.single("square", payload=str(data), hostname="localhost", port=8000)
            # for connection in websocket_connections:

    except WebSocketDisconnect:
        # Remove the WebSocket connection from the set when disconnected
        websocket_connections.remove(websocket)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/

def find_next_element(players, name):
    next_object = None

    for i, obj in enumerate(players):
        if obj["name"] == name:
            next_index = (i + 1) % len(players)
            next_object = players[next_index]
            break
    if next_object is None and players:
        next_object = players[0]  # If the list is not empty, return the first object

    return next_object

@app.post("/publish")
async def publish_message(message: dict):
    # Broadcast the message to all connected clients
    if(message["topic"] == "square"):
        print(message["code"])
        print(active_games[message["code"]])
        players = active_games[message["code"]]
        next_player = find_next_element(players, message["name"])
        if(next_player):
            message["nextPlayer"] = next_player["name"]
    elif(message["topic"] == "startTheGame"):
        message["nextPlayer"] = message["name"]
    for connection in websocket_connections:
        await connection.send_json({'message': message})
    return {"message": "Message published"}


# Data structures to store games and players
active_games = {}

# Endpoint to host a game
@app.post("/host-game")
def host_game(data: dict):
    # Generate a unique game code (you can use your own method)
    game_code = generate_random_code()
    input_data = data
    game = []
    game.append({"name": input_data["name"]})

    # Store the game and player data
    active_games[game_code] = game
    return {"game_code": game_code}


# Endpoint to join a game
@app.post("/join-game")
async def join_game(data: dict):
    # Check if the game exists
    input_data = data
    if input_data["code"] not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")

    # Add the player to the game
    active_games[input_data["code"]].append({"name": input_data["name"]})
    for connection in websocket_connections:
        await connection.send_json({'message': {'topic': 'joinedGame', 'code': input_data["code"]}})

    return {"game_code": input_data["code"], "name": input_data["name"]}

@app.post("/players-list")
async def publish_message(data: dict):
    input_data = data
    return active_games[input_data["code"]]

    return {"message": "Message published"}


# Helper function to generate a random game code (you can customize this)
def generate_random_code():
    import random
    import string
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

