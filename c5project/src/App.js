import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import './App.css';

/* Popup */
const LoginPopup = ({ isOpen, setIsOpen, onLogin, isLoggedIn, onLogout, username }) => {
  const [inputUsername, setInputUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  
  /* Login */
  const handleLogin = (e) => {
    e.preventDefault();
    console.log('Intentando iniciar sesión con:', inputUsername, password);
    if (inputUsername === 'usuario' && password === 'contraseña') {
      onLogin(inputUsername);
      setError('');
      setInputUsername('');
      setPassword('');
    } else {
      setError('Usuario o contraseña incorrectos');
    }
  };

  return (
    <div className={`login-sidebar ${isOpen ? 'open' : ''}`}>
      <div className="login-content">
        <h2>{isLoggedIn ? 'Perfil de Usuario' : 'Iniciar Sesión'}</h2>
        {isLoggedIn ? (
          <div>
            <p>Bienvenido, {username}!</p>
            <button onClick={onLogout} className="logout-button">Cerrar Sesión</button>
          </div>
        ) : (
          <form onSubmit={handleLogin}>
            <input
              type="text"
              placeholder="Usuario"
              value={inputUsername}
              onChange={(e) => setInputUsername(e.target.value)}
              required
            />
            <input
              type="password"
              placeholder="Contraseña"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            {error && <p className="error-message">{error}</p>}
            <button type="submit">Entrar</button>
          </form>
        )}
        <button onClick={() => setIsOpen(false)} className="close-button">
          Cerrar
        </button>
      </div>
    </div>
  );
};
 /* Mapa */ 
const MapComponent = () => {
  const position = [21.87511, -102.28512]; // coordenadas

  return (
    <MapContainer center={position} zoom={13} scrollWheelZoom={false}>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
    </MapContainer>
  );
};

/* Menu */ 
const MenuBar = ({ isOpen, setIsOpen }) => {
  const openNewTab = () => {
    window.open('https://www.youtube.com/watch?v=PJp_R2YyDS8', '_blank');
  };

  return (
    <div className={`menu-bar ${isOpen ? 'open' : ''}`}>
      <button onClick={() => setIsOpen(false)} className="close-button">
        Cerrar
      </button>
      <button onClick={openNewTab} className="new-tab-button">
        Abrir Nueva Pestaña
      </button>
    </div>
  );
};

const App = () => {
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const handleLoginButtonClick = () => {
    if (isLoggedIn) {
      // Si el usuario está logueado, mostrar el sidebar con la opción de cerrar sesión
      setIsLoginOpen(true);
    } else {
      // Si el usuario no está logueado, alternar el estado del sidebar
      setIsLoginOpen(!isLoginOpen);
    }
  };

  const handleLogin = (user) => {
    setIsLoggedIn(true);
    setUsername(user);
    setIsLoginOpen(false);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setUsername('');
    setIsLoginOpen(false);
  };

  const handleSearch = (e) => {
    e.preventDefault();
    // Aquí se puede implementar la lógica de búsqueda
    console.log('Buscando:', searchQuery);
  };

  const handleMenuButtonClick = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  return (
    <div className="app-container">
      <header>
        <div className="login-container">
          <button 
            onClick={handleLoginButtonClick} 
            className="login-button"
          >
            {isLoggedIn ? username : 'Iniciar Sesión'}
          </button>
        </div>
        <div className="right-container">
          <div className="search-container">
            <form onSubmit={handleSearch}>
              <input 
                type="text" 
                placeholder="Buscar..." 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <button type="submit"></button>
            </form>
          </div>
          <button 
            onClick={handleMenuButtonClick} 
            className="menu-button"
          >
            Menú
          </button>
        </div>
      </header>
      <MapComponent />
      <LoginPopup 
        isOpen={isLoginOpen} 
        setIsOpen={setIsLoginOpen}
        onLogin={handleLogin}
        isLoggedIn={isLoggedIn}
        onLogout={handleLogout}
        username={username}
      />
      <MenuBar 
        isOpen={isMenuOpen}
        setIsOpen={setIsMenuOpen}
      />
    </div>
  );
};

export default App;