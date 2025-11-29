import requests
from typing import Tuple, Optional
import time


class GeocodeurAdresse:
    """
    Classe pour convertir une adresse en coordonnées GPS (longitude, latitude).
    Utilise l'API Nominatim d'OpenStreetMap.
    """
    
    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org/search"
        self.headers = {
            'User-Agent': 'RealEstate_Price_App/1.0'
        }
    
    def obtenir_coordonnees(self, numero: str = "", rue: str = "", ville: str = "", 
                           pays: str = "France") -> Optional[Tuple[float, float]]:
        """
        Convertit une adresse en coordonnées GPS.
        
        Args:
            numero: Numéro de rue
            rue: Nom de la rue
            ville: Nom de la ville
            pays: Pays (par défaut "France")
        
        Returns:
            Tuple (longitude, latitude) ou None si l'adresse n'est pas trouvée
        
        Exemple:
            >>> geocodeur = GeocodeurAdresse()
            >>> coords = geocodeur.obtenir_coordonnees("1", "Avenue des Champs-Élysées", "Paris")
            >>> print(coords)
            (2.3069, 48.8698)
        """
        # Construction de l'adresse complète
        adresse_parts = [p for p in [numero, rue, ville, pays] if p]
        adresse_complete = ", ".join(adresse_parts)
        
        if not adresse_complete:
            raise ValueError("Au moins un élément d'adresse doit être fourni")
        
        # Paramètres de la requête
        params = {
            'q': adresse_complete,
            'format': 'json',
            'limit': 1
        }
        
        try:
            # Respect du rate limit (1 requête par seconde max pour Nominatim)
            time.sleep(1)
            
            response = requests.get(self.base_url, params=params, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            
            if data and len(data) > 0:
                longitude = float(data[0]['lon'])
                latitude = float(data[0]['lat'])
                return (longitude, latitude)
            else:
                print(f"Aucune coordonnée trouvée pour l'adresse: {adresse_complete}")
                return None
                
        except requests.RequestException as e:
            print(f"Erreur lors de la requête: {e}")
            return None
        except (KeyError, ValueError, IndexError) as e:
            print(f"Erreur lors du traitement de la réponse: {e}")
            return None


def adresse_vers_coordonnees(numero: str = "", rue: str = "", ville: str = "", 
                             pays: str = "France") -> Optional[Tuple[float, float]]:
    """
    Fonction simple pour convertir une adresse en coordonnées GPS.
    
    Args:
        numero: Numéro de rue
        rue: Nom de la rue
        ville: Nom de la ville
        pays: Pays (par défaut "France")
    
    Returns:
        Tuple (longitude, latitude) ou None si l'adresse n'est pas trouvée
    
    Exemple:
        >>> coords = adresse_vers_coordonnees("10", "Rue de Rivoli", "Paris")
        >>> print(coords)
        (2.3522, 48.8566)
    """
    geocodeur = GeocodeurAdresse()
    return geocodeur.obtenir_coordonnees(numero, rue, ville, pays)


# Exemple d'utilisation
if __name__ == "__main__":
    # Test avec la classe
    geocodeur = GeocodeurAdresse()
    
    # Exemple 1: Adresse complète
    coords = geocodeur.obtenir_coordonnees("13", "rue lasson", "Paris")
    print(f"Coordonnées Champs-Élysées: {coords}")
   
