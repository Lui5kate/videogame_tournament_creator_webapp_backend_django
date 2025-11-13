import { Navigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth.jsx';

const ProtectedRoute = ({ children, adminOnly = false }) => {
  const { user, loading, isAdmin } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-orange-500 border-t-transparent mx-auto mb-4"></div>
          <p className="text-orange-400 pixel-font">🎮 CARGANDO...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (adminOnly && !isAdmin()) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
        <div className="text-center bg-slate-800/80 backdrop-blur-sm border-2 border-red-500/30 rounded-lg p-8">
          <div className="text-6xl mb-4">🚫</div>
          <h2 className="text-2xl font-bold text-red-400 mb-2 pixel-font">ACCESO DENEGADO</h2>
          <p className="text-gray-300 mb-4">No tienes permisos para acceder a esta sección</p>
          <button
            onClick={() => window.history.back()}
            className="bg-gradient-to-r from-orange-500 to-yellow-500 hover:from-orange-600 hover:to-yellow-600 text-white font-bold py-2 px-4 rounded-lg transition-all duration-200 pixel-font"
          >
            ← VOLVER
          </button>
        </div>
      </div>
    );
  }

  return children;
};

export default ProtectedRoute;
