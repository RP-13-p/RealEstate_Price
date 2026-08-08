def apply_ascenseur(price_estime: float, ascenseur: bool) -> float:
    """Pénalise l'absence d'ascenseur. La pénalité décroît avec le prix (courbe
    logistique centrée sur p0) : un bien cher est moins sensible à ce critère
    qu'un petit bien, où l'ascenseur pèse proportionnellement plus."""
    if ascenseur:
        return price_estime

    c = 0.025       # pénalité plancher
    a = 0.095       # amplitude maximale
    p0 = 550_000    # prix pivot
    k = 1.7         # raideur

    penalty = c + a / (1 + (price_estime / p0) ** k)
    return price_estime * (1 - penalty)


def apply_renovation(price: float, etat: str) -> float:
    """Ajuste le prix selon l'état de rénovation, avec la même courbe logistique
    que apply_ascenseur (l'effet de l'état du bien s'atténue aux prix élevés)."""
    p0 = 600_000
    k = 1.6

    params = {
        "tout_a_refaire":      (-0.18, -0.05),
        "rafraichissement":    (-0.10, -0.03),
        "standard":            ( 0.00,  0.00),
        "refait_a_neuf":       ( 0.12,  0.04),
    }

    a, c = params[etat]
    delta = c + a / (1 + (price / p0) ** k)
    return price * (1 + delta)


def adjust_price(price_ml: float, ascenseur: bool = True, etat_renovation: str = "standard") -> float:
    """Applique les corrections métier (ascenseur puis rénovation) à la valeur
    brute renvoyée par le modèle ML."""
    if price_ml <= 0:
        raise ValueError(f"Le prix ML doit être strictement positif (reçu: {price_ml})")

    price_after_ascenseur = apply_ascenseur(price_ml, ascenseur)
    price_final = apply_renovation(price_after_ascenseur, etat_renovation)

    return price_final


VALID_RENOVATION_STATES = [
    "tout_a_refaire",
    "rafraichissement",
    "standard",
    "refait_a_neuf"
]

