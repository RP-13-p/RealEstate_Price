def apply_ascenseur(price_estime: float, ascenseur: bool) -> float:
    """Penalizes the absence of an elevator. The penalty decays with price
    (logistic curve centered on p0): expensive properties are less sensitive
    to this factor than cheaper ones, where it weighs proportionally more."""
    if ascenseur:
        return price_estime

    c = 0.025       # floor penalty
    a = 0.095       # max amplitude
    p0 = 550_000    # pivot price
    k = 1.7         # steepness

    penalty = c + a / (1 + (price_estime / p0) ** k)
    return price_estime * (1 - penalty)


def apply_renovation(price: float, etat: str) -> float:
    """Adjusts price by renovation state, using the same logistic curve as
    apply_ascenseur (the effect fades out at higher prices)."""
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
