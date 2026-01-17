
import React from 'react';
import { AppView } from '../types';
import { Mail, Lock, Eye, EyeOff } from 'lucide-react';

interface LoginPageProps {
  onLogin: () => void;
  setView: (view: AppView) => void;
}

const LoginPage: React.FC<LoginPageProps> = ({ onLogin, setView }) => {
  return (
    <div className="animate-in fade-in zoom-in duration-500 flex items-center justify-center min-h-[70vh]">
      <div className="w-full max-w-md glass p-10 rounded-[2.5rem] border-white/10 space-y-8 text-center relative overflow-hidden">
        {/* Glow effect inside card */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-48 h-1 bg-green-500/50 blur-xl"></div>

        <div className="space-y-2">
          <div className="w-12 h-12 bg-green-500 rounded-xl mx-auto flex items-center justify-center neon-glow mb-4">
            <span className="text-black font-black text-lg">AI</span>
          </div>
          <h1 className="text-2xl font-bold">Campus Authentication</h1>
          <p className="text-sm text-gray-400">Ingresa tus credenciales para acceder a tus cursos</p>
        </div>

        <div className="space-y-4 text-left">
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-gray-500 ml-1">Correo electrónico</label>
            <div className="relative">
              <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-600" size={18} />
              <input type="email" placeholder="email@ejemplo.com" className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-12 pr-4 focus:border-green-500 outline-none transition-all" />
            </div>
          </div>
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-gray-500 ml-1">Contraseña</label>
            <div className="relative">
              <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-600" size={18} />
              <input type="password" placeholder="••••••••" className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-12 pr-12 focus:border-green-500 outline-none transition-all" />
              <button className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-600 hover:text-white transition-colors">
                <EyeOff size={18} />
              </button>
            </div>
          </div>
        </div>

        <button 
          onClick={onLogin}
          className="w-full py-4 bg-green-500 text-black font-bold rounded-2xl hover:scale-[1.02] transition-all neon-glow text-lg"
        >
          Entrar al Campus
        </button>

        <div className="space-y-2">
          <button className="text-xs text-gray-500 hover:text-green-400 transition-colors">¿Olvidaste tu contraseña?</button>
          <div className="text-xs text-gray-500">
            ¿No tienes cuenta? <button onClick={() => setView(AppView.LANDING)} className="text-green-500 font-bold hover:underline">Regístrate</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
