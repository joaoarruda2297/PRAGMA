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
            user = parts[1]
            user_data = next((p for p in current_game["status"]["players"] if p["nome"] == user), None)
            if user_data is None:
                user_data = {"nome": user, "kills": 0}
                current_game["status"]["players"].append(user_data)
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

            if killer == "<world>":
                world_victim = next((p for p in current_game["status"]["players"] if p["nome"] == victim), None)
                if world_victim["kills"] > 0:
                    world_victim["kills"] -= 1

    return games

def main():
    with open("Quake.txt", "r") as log_file:
        games = parse_log(log_file)
        with open("output.json", "w") as output_file:
            json.dump(games, output_file, indent=2)

if __name__ == "__main__":
    main()