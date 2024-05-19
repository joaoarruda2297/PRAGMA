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
        if rest.startswith("InitGame"):
            if current_game["status"]["total_kills"] > 0:
                games.append(current_game)
                game_number += 1
                current_game = {
                    "game": game_number,
                    "status": {
                        "total_kills": 0,
                        "players": []
                    }
                }
        elif rest.startswith("Kill:"):
            parts = rest.split(" ")

            killed_index = parts.index('killed')
            by_index = parts.index('by')

            killer = ' '.join(parts[4:killed_index])
            victim = ' '.join(parts[(killed_index + 1):by_index])

            #print(parts, len(parts), killer, victim)
            current_game["status"]["total_kills"] += 1
            
            if killer != "<world>":
                killer_data = next((p for p in current_game["status"]["players"] if p["nome"] == killer), None)
                if killer_data is None:
                    killer_data = {"nome": killer, "kills": 0}
                    current_game["status"]["players"].append(killer_data)
                killer_data["kills"] += 1

            victim_data = next((p for p in current_game["status"]["players"] if p["nome"] == victim), None)
            if victim_data is None:
                victim_data = {"nome": victim, "kills": 0}
                current_game["status"]["players"].append(victim_data)

            if killer == "<world>":
                world_victim = next((p for p in current_game["status"]["players"] if p["nome"] == victim), None)
                if world_victim["kills"] > 0:
                    world_victim["kills"] -= 1

    if current_game["status"]["total_kills"] > 0:
        games.append(current_game)

    return games

def main():
    with open("Quake.txt", "r") as log_file:
        games = parse_log(log_file)
        with open("output.json", "w") as output_file:
            json.dump(games, output_file, indent=2)

if __name__ == "__main__":
    main()