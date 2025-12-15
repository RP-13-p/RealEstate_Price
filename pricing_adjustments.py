def apply_ascenseur(price_estime: float, ascenseur: bool) -> float:
    if ascenseur:
        return price_estime

    c = 0.025       # pénalité plancher
    a = 0.095       # amplitude maximale
    p0 = 550_000    # prix pivot
    k = 1.7         # raideur

    penalty = c + a / (1 + (price_estime / p0) ** k)
    return price_estime * (1 - penalty)


def apply_renovation(price: float, etat: str) -> float:
    
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


def adjust_price(price_ml: float,ascenseur: bool = True,etat_renovation: str = "standard"):

    if price_ml <= 0:
        raise ValueError(f"Le prix ML doit être strictement positif (reçu: {price_ml})")
    
    # Étape 1 : Correction ascenseur
    price_after_ascenseur = apply_ascenseur(price_ml, ascenseur)
    
    # Étape 2 : Correction rénovation
    price_final = apply_renovation(price_after_ascenseur, etat_renovation)
    
    return price_final


# États de rénovation valides (pour validation externe)
VALID_RENOVATION_STATES = [
    "tout_a_refaire",
    "rafraichissement",
    "standard",
    "refait_a_neuf"
]


if __name__ == "__main__":
    # Tests rapides pour vérifier le bon fonctionnement
    print("=" * 70)
    print("Tests du module pricing_adjustments")
    print("=" * 70)
    
    test_cases = [
        (500_000, True, "standard"),
        (500_000, False, "standard"),
        (500_000, True, "refait_a_neuf"),
        (500_000, False, "tout_a_refaire"),
        (300_000, False, "rafraichissement"),
        (1_000_000, False, "refait_a_neuf"),
    ]
    
    for price, asc, etat in test_cases:
        price_final = adjust_price(price, asc, etat)
        variation = ((price_final - price) / price) * 100
        print(f"\nPrix ML: {price:>12,} € | Ascenseur: {str(asc):>5} | État: {etat}")
        print(f"  → Prix final: {price_final:>12,.2f} € ({variation:+.2f}%)")
    
    print("\n" + "=" * 70)
