# RealEstate Price

A machine learning web application that estimates the market value of a residential property in Paris from its address and characteristics. It combines a Gradient Boosting model trained on French official property-transaction data with rule-based adjustments for factors the raw data doesn't capture well (elevator access, renovation state).

**Live demo:** [real-estate-price-nine.vercel.app](https://real-estate-price-nine.vercel.app)

## Overview

- **Input:** address, number of rooms, surface area (m²), property type, elevator, renovation state
- **Output:** estimated market value, price per m², and the 12-month price-per-m² trend for the property's postal code
- The address is geocoded on the fly (Nominatim/OpenStreetMap), so no manual coordinate lookup is needed

## How it works

```
DVF transactions ─┐
                   ├──▶ data_preprocessing.py ──▶ donnees_immobilieres.csv
Metro stations   ──┘        (cleaning, transit-proximity score,
                              outlier filtering)
                                       │
                                       ▼
                              model.py (Gradient Boosting)
                                       │
                                       ▼
                   best_model.pkl + model_features.pkl

```

1. **Data preprocessing** ([model/data_preprocessing.py](model/data_preprocessing.py)) cleans the raw [DVF](https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres/) (*Demandes de valeurs foncières*) transaction records — France's official, publicly published real-estate transaction history — deduplicates and type-casts them, and engineers a public-transport proximity score (1–5) from the nearest metro station using a `BallTree` haversine search. Transactions priced more than 150% above their postal code's average €/m² are filtered out as outliers.
2. **Model training** ([model/model.py](model/model.py)) fits a `GradientBoostingRegressor` (scikit-learn) on the cleaned dataset and persists the model and its feature list to `Training_set/`.
3. **Serving** ([app.py](app.py)) is a FastAPI app that loads the trained model once at startup, geocodes the submitted address, runs the prediction, and applies deterministic business-rule adjustments before returning the result.
4. **Frontend** ([frontend/](frontend)) is a small React app that collects the address and property details and displays the estimate.

### Model performance

Gradient Boosting (`n_estimators=200`, `learning_rate=0.1`, `max_depth=5`), evaluated on a held-out 20% test split:

| Metric | Value |
|---|---|
| R² | 0.969 |
| MAE | ≈ 86,200 € |
| RMSE | ≈ 242,400 € |

Input features: `longitude`, `latitude`, `code_postal`, `code_type_local`, `lot1_surface_carrez`, `nombre_pieces_principales`.

### Business-rule price adjustments

The ML model is trained on transaction data alone, which doesn't reliably encode elevator access or renovation state. [pricing_adjustments.py](pricing_adjustments.py) applies bounded, logistic-shaped corrections on top of the raw prediction — the adjustment shrinks as the base price grows, since these attributes matter proportionally less on higher-value properties.

## Tech stack

| Layer | Technology |
|---|---|
| Model | scikit-learn (Gradient Boosting), pandas, numpy |
| Backend | FastAPI, uvicorn |
| Geocoding | OpenStreetMap Nominatim |

## Setup

### Model

```bash
python -m venv venv
venv\Scripts\activate          # Windows; use `source venv/bin/activate` on macOS/Linux
pip install -r requirements.txt

# 1. Download a DVF export (see "Data source" below), place it at DATA/dvf.csv,
#    and place a metro-station export at DATA/metro-france.csv
# 2. Build the cleaned dataset
python model/data_preprocessing.py
# 3. Train the model (writes Training_set/best_model.pkl + model_features.pkl)
python model/model.py
# 4. Run the API
uvicorn app:app --reload
```


### Dataset 

 DVF exports are published by the French Ministry of Economy and Finance on data.gouv.fr — browse their datasets at [data.gouv.fr/organizations/ministeres-economiques-et-financiers/datasets](https://www.data.gouv.fr/organizations/ministeres-economiques-et-financiers/datasets) to find the current *Demandes de valeurs foncières* export.

## Limitations

- The model is trained exclusively on Paris apartment transactions (`code_type_local = 2`); estimates for other property types or other cities are not currently supported, though the form doesn't yet enforce this.
- Geocoding depends on OpenStreetMap Nominatim's public instance, which is rate-limited to one request per second and can occasionally fail to resolve an address.

## Author

[Raphael Partouche](https://portfolio-partouche-pi.vercel.app/)
