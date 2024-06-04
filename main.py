import json
from collections import defaultdict

def parse_log(log_file):
    game_number = 1
    games = []
    current_game = {
        "game": game_number,
        "status": {
            "total_kills": 0,
            "players": []
        }
    }

    for line in log_file:
        line = line.strip()

        timestamp, rest = line.split(" ", 1)
        if rest.startswith("ShutdownGame:"):
            games.append(current_game)
            game_number += 1
            current_game = {
                "game": game_number,
                "status": {
                    "total_kills": 0,
                    "players": []
                }
            }

        elif rest.startswith("ClientUserinfoChanged:"):
            parts = rest.split("\\")
            first_part = parts[0].split(" ")
            user_id = first_part[1]
            user_name = parts[1]
            
            user_data = next((p for p in current_game["status"]["players"] if p["nome"] == user_name), None)
            user_data_by_id = next((p for p in current_game["status"]["players"] if p["id"] == user_id), None)
            if user_data is None:
                if user_data_by_id is None: #de fato usuário nao existe
                    user_data = {"id": user_id,"nome": user_name, "kills": 0, "prev_names": [], "collected_items": []}
                    current_game["status"]["players"].append(user_data)
                else: #usuário mudou de nome
                    for player in current_game["status"]["players"]:
                        if player["id"] == user_id and player["nome"] != user_name:
                            player["prev_names"].append(player["nome"])
                            player["nome"] = user_name

        elif rest.startswith("Item:"):
            parts = rest.split(" ")
            user_id = parts[1]
            type_item, item = parts[2].split("_", 1)

            for player in current_game["status"]["players"]:
                if player["id"] == user_id:
                    item_data = next((p for p in player["collected_items"] if p == item), None)
                    if item_data is None:
                        player["collected_items"].append(item)
            

        elif rest.startswith("Kill:"):
            parts = rest.split(" ")

            killed_index = parts.index('killed')
            by_index = parts.index('by')

            killer = ' '.join(parts[4:killed_index])
            victim = ' '.join(parts[(killed_index + 1):by_index])

            current_game["status"]["total_kills"] += 1
            
            if killer != "<world>" and killer != victim:
                killer_data = next((p for p in current_game["status"]["players"] if p["nome"] == killer), None)
                killer_data["kills"] += 1

            elif killer == "<world>" or killer == victim:
                world_victim = next((p for p in current_game["status"]["players"] if p["nome"] == victim), None)
                world_victim["kills"] -= 1
    
    for game in games: #limpando o id do output
        for player in game["status"]["players"]:
            if "id" in player:
                del player["id"]

    return games

def main():
    with open("Quake.txt", "r") as log_file:
        games = parse_log(log_file)
        with open("output.json", "w") as output_file:
            json.dump(games, output_file, indent=2)

if __name__ == "__main__":
    main()