"""Geocodes a French address to (longitude, latitude) via the Nominatim/OSM API."""
import time
from typing import Optional, Tuple

import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "RealEstate_Price_App/1.0"}


def adresse_vers_coordonnees(numero: str = "", rue: str = "", ville: str = "",
                              pays: str = "France") -> Optional[Tuple[float, float]]:
    adresse = ", ".join(p for p in [numero, rue, ville, pays] if p)
    if not adresse:
        raise ValueError("Au moins un élément d'adresse doit être fourni")

    try:
        # Nominatim's usage policy caps anonymous requests at 1/s.
        time.sleep(1)
        response = requests.get(
            NOMINATIM_URL,
            params={"q": adresse, "format": "json", "limit": 1},
            headers=HEADERS,
        )
        response.raise_for_status()
        results = response.json()

        if not results:
            return None
        return (float(results[0]["lon"]), float(results[0]["lat"]))

    except (requests.RequestException, KeyError, ValueError, IndexError) as e:
        print(f"Erreur géocodage pour '{adresse}': {e}")
        return None
