#!/usr/bin/env python3
"""Fetch public Roblox visit/player counts for the portfolio's games."""

from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


GAMES = {
    "123720558354386": 10765012427,  # Build the Pyramid
    "125723653259639": 7204130482,  # Drill Digging Simulator
    "509062192": 197306872,  # Project Realism
    "7845941294": 3036768570,  # Reign of Royales
    "885450884": 368327886,  # The Red Cell
    "4475184011": 1427426011,  # Royal Marines
    "16315665693": 5628599217,  # Dragonborn PMC
    "5361853069": 1879297957,  # Snow Core
}
OUTPUT = Path(__file__).resolve().parents[1] / "stats.json"


def get_json(url: str) -> dict:
    request = Request(url, headers={"User-Agent": "JaydenPortfolioStats/1.0"})
    with urlopen(request, timeout=25) as response:
        return json.load(response)


def main() -> None:
    universe_ids = ",".join(map(str, GAMES.values()))
    response = get_json(f"https://games.roblox.com/v1/games?universeIds={universe_ids}")
    records = {str(game["rootPlaceId"]): game for game in response.get("data", [])}

    missing = set(GAMES) - set(records)
    if missing:
        raise RuntimeError(f"Roblox did not return stats for place IDs: {', '.join(sorted(missing))}")

    payload = {
        "updatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "games": {
            place_id: {
                "universeId": GAMES[place_id],
                "name": game["name"],
                "visits": game["visits"],
                "playing": game["playing"],
            }
            for place_id, game in records.items()
        },
    }

    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Updated Roblox stats for {len(payload['games'])} games at {payload['updatedAt']}")


if __name__ == "__main__":
    try:
        main()
    except (HTTPError, URLError, TimeoutError) as error:
        raise SystemExit(f"Could not fetch Roblox game stats: {error}") from error
