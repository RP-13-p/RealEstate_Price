import { useState } from 'react'
import axios from 'axios'
import './App.css'

// Set via VITE_API_URL in production, defaults to localhost in dev
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [address, setAddress] = useState({
    numero: '',
    rue: '',
    ville: '',
    codePostal: ''
  })

  const [property, setProperty] = useState({
    codeTypeLocal: '',
    nombrePieces: '',
    surface: '',
    ascenseur: true,
    etatRenovation: 'standard'
  })

  const [prediction, setPrediction] = useState(null)

  const [loadingPredict, setLoadingPredict] = useState(false)
  const [message, setMessage] = useState({ text: '', type: '' })

  const [expandedSections, setExpandedSections] = useState({
    address: true,
    characteristics: false,
    condition: false
  })

  const isAddressComplete = address.rue && address.ville && address.codePostal

  const isCharacteristicsComplete = property.codeTypeLocal && property.nombrePieces && property.surface

  const handleAddressChange = (e) => {
    const newAddress = { ...address, [e.target.name]: e.target.value }
    setAddress(newAddress)
    
    // Auto-expand the next section once the address is complete
    if (newAddress.rue && newAddress.ville && newAddress.codePostal) {
      setTimeout(() => {
        setExpandedSections(prev => ({ ...prev, characteristics: true }))
      }, 300)
    }
  }

  const handlePropertyChange = (e) => {
    const newProperty = { ...property, [e.target.name]: e.target.value }
    setProperty(newProperty)
    
    // Auto-expand the next section once the characteristics are complete
    if (newProperty.codeTypeLocal && newProperty.nombrePieces && newProperty.surface) {
      setTimeout(() => {
        setExpandedSections(prev => ({ ...prev, condition: true }))
      }, 300)
    }
  }

  const showMessage = (text, type = 'info') => {
    setMessage({ text, type })
    if (type === 'success') {
      setTimeout(() => setMessage({ text: '', type: '' }), 5000)
    }
  }

  const handlePredict = async (e) => {
    e.preventDefault()

    const requiredFields = [
      address.rue, address.ville, address.codePostal,
      property.codeTypeLocal, property.nombrePieces, property.surface
    ]
    
    if (requiredFields.some(field => !field)) {
      showMessage('Veuillez remplir tous les champs', 'warning')
      return
    }

    setLoadingPredict(true)
    setMessage({ text: '', type: '' })
    setPrediction(null)

    try {
      const geocodeResponse = await axios.post(`${API_URL}/api/geocode`, {
        numero: address.numero,
        rue: address.rue,
        ville: address.ville,
        pays: 'France'
      })

      if (!geocodeResponse.data.success) {
        showMessage('Impossible de géolocaliser cette adresse', 'error')
        setLoadingPredict(false)
        return
      }

      const { longitude, latitude } = geocodeResponse.data

      const response = await axios.post(`${API_URL}/api/predict`, {
        longitude: longitude,
        latitude: latitude,
        code_postal: parseInt(address.codePostal),
        code_type_local: parseInt(property.codeTypeLocal),
        lot1_surface_carrez: parseFloat(property.surface),
        nombre_pieces_principales: parseInt(property.nombrePieces),
        ascenseur: property.ascenseur,
        etat_renovation: property.etatRenovation
      })

      if (response.data.success) {
        setPrediction(response.data)
        showMessage('Estimation calculée avec succès', 'success')

        setTimeout(() => {
          document.getElementById('result')?.scrollIntoView({
            behavior: 'smooth',
            block: 'nearest'
          })
        }, 100)
      }

    } catch (error) {
      const isNetworkError = !error.response || error.code === 'ERR_NETWORK'
      const errorMsg = isNetworkError
        ? 'Le serveur démarre... Cliquez sur "Réessayer" dans quelques secondes.'
        : error.response?.data?.detail || 'Erreur lors de la prédiction'
      showMessage(errorMsg, 'error')
    } finally {
      setLoadingPredict(false)
    }
  }

  const handleRetry = () => {
    setMessage({ text: '', type: '' })
    handlePredict({ preventDefault: () => {} })
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Estimation Immobilière</h1>
        <p className="subtitle">Estimez la valeur de votre bien en quelques clics</p>
      </header>

      <div className="container">
        <section className="card">
          <h2>Informations du bien</h2>
          <form onSubmit={handlePredict}>
            <div className="form-section">
              <div 
                className="section-header"
                onClick={() => setExpandedSections(prev => ({ ...prev, address: !prev.address }))}
              >
                <h3 className="section-title-expand">
                  Adresse
                </h3>
                <span className={`expand-icon ${expandedSections.address ? 'expanded' : ''}`}>▼</span>
              </div>
              
              <div className={`section-content ${expandedSections.address ? 'expanded' : ''}`}>
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
              </div>
            </div>

            <div className="form-section">
              <div 
                className="section-header"
                onClick={() => isAddressComplete && setExpandedSections(prev => ({ ...prev, characteristics: !prev.characteristics }))}
                style={{ cursor: isAddressComplete ? 'pointer' : 'not-allowed', opacity: isAddressComplete ? 1 : 0.5 }}
              >
                <h3 className="section-title-expand">
                  Caractéristiques
                </h3>
                <span className={`expand-icon ${expandedSections.characteristics ? 'expanded' : ''}`}>▼</span>
              </div>
              
              <div className={`section-content ${expandedSections.characteristics ? 'expanded' : ''}`}>
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
                  <div className="form-group">
                    <label>Ascenseur</label>
                    <select
                      name="ascenseur"
                      value={property.ascenseur}
                      onChange={(e) => setProperty({...property, ascenseur: e.target.value === 'true'})}
                    >
                      <option value="true">Oui</option>
                      <option value="false">Non</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            <div className="form-section">
              <div 
                className="section-header"
                onClick={() => isCharacteristicsComplete && setExpandedSections(prev => ({ ...prev, condition: !prev.condition }))}
                style={{ cursor: isCharacteristicsComplete ? 'pointer' : 'not-allowed', opacity: isCharacteristicsComplete ? 1 : 0.5 }}
              >
                <h3 className="section-title-expand">
                  État du bien
                </h3>
                <span className={`expand-icon ${expandedSections.condition ? 'expanded' : ''}`}>▼</span>
              </div>
              
              <div className={`section-content ${expandedSections.condition ? 'expanded' : ''}`}>
                <div className="form-row">
                  <div className="form-group">
                    <label>État de rénovation</label>
                    <select
                      name="etatRenovation"
                      value={property.etatRenovation}
                      onChange={handlePropertyChange}
                    >
                      <option value="tout_a_refaire">À rénover entièrement</option>
                      <option value="rafraichissement">À rafraîchir</option>
                      <option value="standard">État standard</option>
                      <option value="refait_a_neuf">Refait à neuf</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              disabled={loadingPredict}
            >
              {loadingPredict ? 'Calcul en cours...' : 'Estimer la valeur'}
            </button>
          </form>
        </section>

        {message.text && (
          <div className={`message-box ${message.type}`}>
            {message.text}
            {message.type === 'error' && (
              <button
                className="retry-button"
                onClick={handleRetry}
                disabled={loadingPredict}
              >
                Réessayer
              </button>
            )}
          </div>
        )}

        {prediction && (
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
        )}
      </div>

      <footer>
        <p>
          © 2025 RealEstate Price - Modèle developpé par{' '}
          <a href="https://portfolio-partouche-pi.vercel.app/" target="_blank" rel="noopener noreferrer">
            Raphael Partouche
          </a>
        </p>
      </footer>
    </div>
  )
}

export default App
