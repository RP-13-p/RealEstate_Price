import { useState } from 'react'
import axios from 'axios'
import './App.css'

// URL backend depuis Vercel / .env local
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  // État pour l'adresse
  const [address, setAddress] = useState({
    numero: '',
    rue: '',
    ville: '',
    codePostal: ''
  })

  // État pour les caractéristiques du bien
  const [property, setProperty] = useState({
    codeTypeLocal: '',
    nombrePieces: '',
    surface: ''
  })

  // État pour le résultat
  const [prediction, setPrediction] = useState(null)

  // États de chargement et messages
  const [loadingPredict, setLoadingPredict] = useState(false)
  const [message, setMessage] = useState({ text: '', type: '' })

  // Gérer les changements d'adresse
  const handleAddressChange = (e) => {
    setAddress({ ...address, [e.target.name]: e.target.value })
  }

  // Gérer les changements de propriété
  const handlePropertyChange = (e) => {
    setProperty({ ...property, [e.target.name]: e.target.value })
  }

  // Afficher un message
  const showMessage = (text, type = 'info') => {
    setMessage({ text, type })
    if (type === 'success') {
      setTimeout(() => setMessage({ text: '', type: '' }), 5000)
    }
  }

  // Faire la prédiction
  const handlePredict = async (e) => {
    e.preventDefault()

    const requiredFields = [
      address.rue, address.ville, address.codePostal,
      property.codeTypeLocal, property.nombrePieces, property.surface
    ]
    
    if (requiredFields.some(field => !field)) {
      showMessage('⚠️ Veuillez remplir tous les champs', 'warning')
      return
    }

    setLoadingPredict(true)
    setMessage({ text: '', type: '' })
    setPrediction(null)

    try {
      // Géolocaliser d'abord l'adresse automatiquement
      const geocodeResponse = await axios.post(`${API_URL}/api/geocode`, {
        numero: address.numero,
        rue: address.rue,
        ville: address.ville,
        pays: 'France'
      })

      if (!geocodeResponse.data.success) {
        showMessage('❌ Impossible de géolocaliser cette adresse', 'error')
        setLoadingPredict(false)
        return
      }

      const { longitude, latitude } = geocodeResponse.data

      // Puis faire la prédiction
      const response = await axios.post(`${API_URL}/api/predict`, {
        longitude: longitude,
        latitude: latitude,
        code_postal: parseInt(address.codePostal),
        code_type_local: parseInt(property.codeTypeLocal),
        lot1_surface_carrez: parseFloat(property.surface),
        nombre_pieces_principales: parseInt(property.nombrePieces)
      })

      if (response.data.success) {
        setPrediction(response.data)
        showMessage('✓ Estimation calculée avec succès !', 'success')

        setTimeout(() => {
          document.getElementById('result')?.scrollIntoView({
            behavior: 'smooth',
            block: 'nearest'
          })
        }, 100)
      }

    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Erreur lors de la prédiction'
      showMessage('❌ ' + errorMsg, 'error')
    } finally {
      setLoadingPredict(false)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Estimation Immobilière</h1>
        <p className="subtitle">Estimez la valeur de votre bien en quelques clics</p>
      </header>

      <div className="container">
        {/* Section Formulaire complet */}
        <section className="card">
          <h2>📍 Informations du bien</h2>
          <form onSubmit={handlePredict}>
            <h3 className="section-title">Adresse</h3>
            <div className="form-row">
              <div className="form-group small">
                <label>Numéro</label>
                <input
                  type="text"
                  name="numero"
                  value={address.numero}
                  onChange={handleAddressChange}
                  placeholder="112"
                />
              </div>
              <div className="form-group grow">
                <label>Rue *</label>
                <input
                  type="text"
                  name="rue"
                  value={address.rue}
                  onChange={handleAddressChange}
                  placeholder="Avenue des Champs Elysées"
                  required
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group grow">
                <label>Ville *</label>
                <input
                  type="text"
                  name="ville"
                  value={address.ville}
                  onChange={handleAddressChange}
                  placeholder="Paris"
                  required
                />
              </div>
              <div className="form-group">
                <label>Code Postal *</label>
                <input
                  type="text"
                  name="codePostal"
                  value={address.codePostal}
                  onChange={handleAddressChange}
                  placeholder="75008"
                  maxLength="5"
                  required
                />
              </div>
            </div>

            <h3 className="section-title">Caractéristiques</h3>
            <div className="form-row">
              <div className="form-group">
                <label>Type de local *</label>
                <select
                  name="codeTypeLocal"
                  value={property.codeTypeLocal}
                  onChange={handlePropertyChange}
                  required
                >
                  <option value="">Sélectionnez...</option>
                  <option value="1">Maison</option>
                  <option value="2">Appartement</option>
                  <option value="3">Dépendance</option>
                  <option value="4">Local industriel/commercial</option>
                </select>
              </div>
              <div className="form-group">
                <label>Nombre de pièces *</label>
                <input
                  type="number"
                  name="nombrePieces"
                  value={property.nombrePieces}
                  onChange={handlePropertyChange}
                  min="1"
                  max="20"
                  placeholder="3"
                  required
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Surface Carré (m²) *</label>
                <input
                  type="number"
                  name="surface"
                  value={property.surface}
                  onChange={handlePropertyChange}
                  min="1"
                  step="0.01"
                  placeholder="45.5"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              disabled={loadingPredict}
            >
              {loadingPredict ? '⏳ Calcul en cours...' : ' Estimer la valeur'}
            </button>
          </form>
        </section>

        {/* Messages */}
        {message.text && (
          <div className={`message-box ${message.type}`}>
            {message.text}
          </div>
        )}

        {/* Résultat */}
        {prediction && (
          <>
            <section className="card result-card" id="result">
              <h2>Estimation</h2>
              <div className="result-content">
                <div className="result-value">
                  <span className="result-label">Valeur estimée:</span>
                  <span className="result-price">{prediction.prediction_formatted}</span>
                </div>
                {prediction.prix_m2_formatted && (
                  <div className="result-m2">
                    <span className="result-m2-label">Prix au m²:</span>
                    <span className="result-m2-price">{prediction.prix_m2_formatted}</span>
                  </div>
                )}
                <p className="result-info">
                  Cette estimation est basée sur les données historiques et les caractéristiques du bien.
                </p>
              </div>
            </section>

            {/* Graphique des prix */}
            {prediction.price_history && prediction.price_history.length > 0 && (
              <section className="card chart-card">
                <h2>Évolution des prix au m² - Arrondissement {prediction.code_postal}</h2>
                <div className="chart-container">
                  <svg viewBox="0 0 800 400" className="price-chart">
                    {/* Grille horizontale */}
                    {[0, 1, 2, 3, 4, 5].map(i => (
                      <line
                        key={`grid-${i}`}
                        x1="80"
                        y1={50 + i * 60}
                        x2="750"
                        y2={50 + i * 60}
                        stroke="#e2e8f0"
                        strokeWidth="1"
                        strokeDasharray="5,5"
                      />
                    ))}
                    
                    {/* Axes */}
                    <line x1="80" y1="350" x2="750" y2="350" stroke="#64748b" strokeWidth="2" />
                    <line x1="80" y1="50" x2="80" y2="350" stroke="#64748b" strokeWidth="2" />
                    
                    {/* Courbe des prix */}
                    {(() => {
                      const prices = prediction.price_history.map(p => p.prix_m2);
                      const minPrice = Math.min(...prices) * 0.95;
                      const maxPrice = Math.max(...prices) * 1.05;
                      const priceRange = maxPrice - minPrice || 1;
                      const pointWidth = 670 / (prices.length - 1 || 1);
                      
                      const points = prices.map((price, i) => {
                        const x = 80 + i * pointWidth;
                        const y = 350 - ((price - minPrice) / priceRange) * 300;
                        return `${x},${y}`;
                      }).join(' ');
                      
                      // Points pour l'aire sous la courbe
                      const areaPoints = `80,350 ${points} ${80 + (prices.length - 1) * pointWidth},350`;
                      
                      return (
                        <>
                          {/* Aire sous la courbe */}
                          <polygon
                            points={areaPoints}
                            fill="url(#priceGradient)"
                            opacity="0.3"
                          />
                          
                          {/* Définition du gradient */}
                          <defs>
                            <linearGradient id="priceGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                              <stop offset="0%" stopColor="#2563eb" stopOpacity="0.8" />
                              <stop offset="100%" stopColor="#2563eb" stopOpacity="0.1" />
                            </linearGradient>
                          </defs>
                          
                          {/* Ligne de la courbe */}
                          <polyline
                            points={points}
                            fill="none"
                            stroke="#2563eb"
                            strokeWidth="3"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          />
                          
                          {/* Points sur la courbe */}
                          {prices.map((price, i) => {
                            const x = 80 + i * pointWidth;
                            const y = 350 - ((price - minPrice) / priceRange) * 300;
                            const isLast = i === prices.length - 1;
                            return (
                              <g key={`point-${i}`}>
                                <circle
                                  cx={x}
                                  cy={y}
                                  r={isLast ? "6" : "4"}
                                  fill={isLast ? "#10b981" : "#2563eb"}
                                  stroke="white"
                                  strokeWidth="2"
                                />
                                {isLast && (
                                  <text
                                    x={x}
                                    y={y - 15}
                                    textAnchor="middle"
                                    fill="#10b981"
                                    fontSize="13"
                                    fontWeight="bold"
                                  >
                                    Actuel
                                  </text>
                                )}
                              </g>
                            );
                          })}
                          
                          {/* Labels des dates */}
                          {prediction.price_history.map((item, i) => {
                            const x = 80 + i * pointWidth;
                            const shouldShow = prices.length <= 6 || i % 2 === 0 || i === prices.length - 1;
                            if (shouldShow) {
                              return (
                                <text
                                  key={`date-${i}`}
                                  x={x}
                                  y="370"
                                  textAnchor="middle"
                                  fill="#64748b"
                                  fontSize="12"
                                  transform={`rotate(-45, ${x}, 370)`}
                                >
                                  {item.date.substring(0, 7)}
                                </text>
                              );
                            }
                            return null;
                          })}
                          
                          {/* Labels des prix sur l'axe Y */}
                          {[0, 1, 2, 3, 4, 5].map(i => {
                            const price = minPrice + (priceRange * i / 5);
                            const y = 350 - (i * 60);
                            return (
                              <text
                                key={`price-${i}`}
                                x="70"
                                y={y + 5}
                                textAnchor="end"
                                fill="#64748b"
                                fontSize="12"
                                fontWeight="500"
                              >
                                {Math.round(price).toLocaleString()}€
                              </text>
                            );
                          })}
                          
                          {/* Titre axe Y */}
                          <text
                            x="20"
                            y="200"
                            textAnchor="middle"
                            fill="#64748b"
                            fontSize="13"
                            fontWeight="600"
                            transform="rotate(-90, 20, 200)"
                          >
                            Prix au m² (€)
                          </text>
                        </>
                      );
                    })()}
                  </svg>
                </div>
                <p className="chart-info">
                  💡 Évolution du prix moyen au m² dans l'arrondissement {prediction.code_postal} sur les 12 derniers mois disponibles.
                </p>
              </section>
            )}
          </>
        )}
      </div>

      <footer>
        <p>
          © 2025 RealEstate Price - Modèle developpé par{' '}
          <a href="https://portofolio-partouche-pi.vercel.app/" target="_blank" rel="noopener noreferrer">
            Raphael Partouche
          </a>
        </p>
      </footer>
    </div>
  )
}

export default App
