import { useState } from 'react'
import axios from 'axios'
import './App.css'

const API_BASE = 'http://localhost:8000/api'

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

    const requiredFields = [address.rue, address.ville, address.codePostal, property.codeTypeLocal, property.nombrePieces, property.surface]
    if (requiredFields.some(field => !field)) {
      showMessage('⚠️ Veuillez remplir tous les champs', 'warning')
      return
    }

    setLoadingPredict(true)
    setMessage({ text: '', type: '' })
    setPrediction(null)

    try {
      // Géolocaliser d'abord l'adresse automatiquement
      const geocodeResponse = await axios.post(`${API_BASE}/geocode`, {
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
      const response = await axios.post(`${API_BASE}/predict`, {
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
        // Scroll vers le résultat
        setTimeout(() => {
          document.getElementById('result')?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
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
          <section className="card result-card" id="result">
            <h2>📊 Estimation</h2>
            <div className="result-content">
              <div className="result-value">
                <span className="result-label">Valeur estimée:</span>
                <span className="result-price">{prediction.prediction_formatted}</span>
              </div>
              <p className="result-info">
                Cette estimation est basée sur les données historiques et les caractéristiques du bien.
              </p>
            </div>
          </section>
        )}
      </div>

      <footer>
        <p>© 2025 RealEstate Price - Estimation basée sur machine learning</p>
      </footer>
    </div>
  )
}

export default App
