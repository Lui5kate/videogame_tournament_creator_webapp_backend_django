import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth.jsx';
import api from '../../services/api';

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    attuid: '',
    first_name: '',
    last_name: '',
    has_played_games: false,
    favorite_game_types: []
  });
  const [gameTypes, setGameTypes] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { register } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchGameTypes = async () => {
      try {
        const response = await api.get('/auth/game-types/');
        setGameTypes(response.data.game_types);
      } catch (err) {
        console.error('Error fetching game types:', err);
      }
    };
    fetchGameTypes();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      await register(formData);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Error al registrarse');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleGameTypeChange = (gameType) => {
    const updatedTypes = formData.favorite_game_types.includes(gameType)
      ? formData.favorite_game_types.filter(type => type !== gameType)
      : [...formData.favorite_game_types, gameType];
    
    setFormData({
      ...formData,
      favorite_game_types: updatedTypes
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
      {/* Efectos de fondo */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-orange-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-yellow-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>

      <div className="relative z-10 w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-yellow-400 mb-2 pixel-font">
            ✨ REGISTRO
          </h1>
          <p className="text-gray-300 text-sm">Únete a la comunidad gaming</p>
        </div>

        {/* Formulario */}
        <div className="bg-slate-800/80 backdrop-blur-sm border-2 border-orange-500/30 rounded-lg p-8 shadow-2xl">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Datos básicos */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-orange-400 text-sm font-semibold mb-2 pixel-font">
                  👤 NOMBRE
                </label>
                <input
                  type="text"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-slate-700/50 border-2 border-slate-600 rounded-lg text-blue-500 placeholder-gray-400 focus:border-orange-500 focus:outline-none focus:ring-2 focus:ring-orange-500/20 transition-all duration-200"
                  placeholder="Tu nombre"
                  required
                />
              </div>
              
              <div>
                <label className="block text-orange-400 text-sm font-semibold mb-2 pixel-font">
                  👤 APELLIDO
                </label>
                <input
                  type="text"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-slate-700/50 border-2 border-slate-600 rounded-lg text-blue-500 placeholder-gray-400 focus:border-orange-500 focus:outline-none focus:ring-2 focus:ring-orange-500/20 transition-all duration-200"
                  placeholder="Tu apellido"
                  required
                />
              </div>
            </div>

            {/* Usuario y ATTUID */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-orange-400 text-sm font-semibold mb-2 pixel-font">
                  🎮 USUARIO
                </label>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-slate-700/50 border-2 border-slate-600 rounded-lg text-blue-500 placeholder-gray-400 focus:border-orange-500 focus:outline-none focus:ring-2 focus:ring-orange-500/20 transition-all duration-200"
                  placeholder="Nombre de usuario"
                  required
                />
              </div>
              
              <div>
                <label className="block text-orange-400 text-sm font-semibold mb-2 pixel-font">
                  🆔 ATTUID
                </label>
                <input
                  type="text"
                  name="attuid"
                  value={formData.attuid}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-slate-700/50 border-2 border-slate-600 rounded-lg text-blue-500 placeholder-gray-400 focus:border-orange-500 focus:outline-none focus:ring-2 focus:ring-orange-500/20 transition-all duration-200"
                  placeholder="Código alfanumérico"
                  required
                />
              </div>
            </div>

            {/* Contraseña */}
            <div>
              <label className="block text-orange-400 text-sm font-semibold mb-2 pixel-font">
                🔒 CONTRASEÑA
              </label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-slate-700/50 border-2 border-slate-600 rounded-lg text-blue-500 placeholder-gray-400 focus:border-orange-500 focus:outline-none focus:ring-2 focus:ring-orange-500/20 transition-all duration-200"
                placeholder="Mínimo 6 caracteres"
                required
                minLength={6}
              />
            </div>

            {/* Experiencia gaming */}
            <div>
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  name="has_played_games"
                  checked={formData.has_played_games}
                  onChange={handleChange}
                  className="w-5 h-5 text-orange-500 bg-slate-700 border-slate-600 rounded focus:ring-orange-500 focus:ring-2"
                />
                <span className="text-yellow-400 font-semibold pixel-font">
                  🎯 ¿Has jugado videojuegos antes?
                </span>
              </label>
            </div>

            {/* Tipos de juegos favoritos */}
            {formData.has_played_games && (
              <div>
                <label className="block text-orange-400 text-sm font-semibold mb-3 pixel-font">
                  🎮 TIPOS DE JUEGOS FAVORITOS
                </label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {gameTypes.map((gameType) => (
                    <label
                      key={gameType.value}
                      className={`flex items-center space-x-2 p-3 rounded-lg border-2 cursor-pointer transition-all duration-200 ${
                        formData.favorite_game_types.includes(gameType.value)
                          ? 'bg-orange-500/20 border-orange-500 text-orange-300'
                          : 'bg-slate-700/30 border-slate-600 text-gray-300 hover:border-yellow-500/50'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={formData.favorite_game_types.includes(gameType.value)}
                        onChange={() => handleGameTypeChange(gameType.value)}
                        className="sr-only"
                      />
                      <span className="text-sm font-medium">{gameType.label}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-3 text-red-300 text-sm">
                ⚠️ {error}
              </div>
            )}

            {/* Botones */}
            <div className="flex flex-col space-y-3">
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-gradient-to-r from-orange-500 to-yellow-500 hover:from-orange-600 hover:to-yellow-600 text-white font-bold py-3 px-6 rounded-lg transition-all duration-200 transform hover:scale-105 hover:shadow-lg hover:shadow-orange-500/25 disabled:opacity-50 disabled:cursor-not-allowed pixel-font"
              >
                {isLoading ? '⏳ REGISTRANDO...' : '🚀 CREAR CUENTA'}
              </button>
              
              <button
                type="button"
                onClick={() => navigate('/login')}
                className="w-full bg-slate-700/50 hover:bg-slate-600/50 border-2 border-slate-600 hover:border-yellow-500/50 text-gray-300 hover:text-yellow-400 font-semibold py-3 px-6 rounded-lg transition-all duration-200 pixel-font"
              >
                ← YA TENGO CUENTA
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Register;
