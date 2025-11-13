import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth.jsx';

const Login = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      await login(formData);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Error al iniciar sesión');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
      {/* Efectos de fondo arcade */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-orange-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-yellow-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>

      <div className="relative z-10 w-full max-w-md">
        {/* Logo/Título */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-yellow-400 mb-2 pixel-font">
            Videogame Tournament Maker
          </h1>
          <p className="text-gray-300 text-sm">Inicia sesión para continuar</p>
        </div>

        {/* Formulario de Login */}
        <div className="bg-slate-800/80 backdrop-blur-sm border-2 border-orange-500/30 rounded-lg p-8 shadow-2xl">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Campo Usuario */}
            <div>
              <label className="block text-orange-400 text-sm font-semibold mb-2 pixel-font">
                👤 USUARIO
              </label>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-slate-700/50 border-2 border-slate-600 rounded-lg text-blue-500 placeholder-gray-400 focus:border-orange-500 focus:outline-none focus:ring-2 focus:ring-orange-500/20 transition-all duration-200"
                placeholder="Ingresa tu usuario"
                required
              />
            </div>

            {/* Campo Contraseña */}
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
                placeholder="Ingresa tu contraseña"
                required
              />
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-3 text-red-300 text-sm">
                ⚠️ {error}
              </div>
            )}

            {/* Botón Login */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-gradient-to-r from-orange-500 to-yellow-500 hover:from-orange-600 hover:to-yellow-600 text-white font-bold py-3 px-6 rounded-lg transition-all duration-200 transform hover:scale-105 hover:shadow-lg hover:shadow-orange-500/25 disabled:opacity-50 disabled:cursor-not-allowed pixel-font"
            >
              {isLoading ? '⏳ CARGANDO...' : '🚀 INICIAR SESIÓN'}
            </button>
          </form>

          {/* Separador */}
          <div className="my-6 flex items-center">
            <div className="flex-1 border-t border-slate-600"></div>
            <span className="px-4 text-gray-400 text-sm">o</span>
            <div className="flex-1 border-t border-slate-600"></div>
          </div>

          {/* Botón Registro */}
          <button
            onClick={() => navigate('/register')}
            className="w-full bg-slate-700/50 hover:bg-slate-600/50 border-2 border-slate-600 hover:border-yellow-500/50 text-gray-300 hover:text-yellow-400 font-semibold py-3 px-6 rounded-lg transition-all duration-200 pixel-font"
          >
            ✨ ¿NUEVO USUARIO? REGÍSTRATE
          </button>
        </div>

        {/* Footer */}
        <div className="text-center mt-6 text-gray-400 text-xs">
          🎮 Torneo de Videojuegos v2.0 - Gaming Community
        </div>
      </div>
    </div>
  );
};

export default Login;
