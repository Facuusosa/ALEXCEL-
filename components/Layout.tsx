
import React from 'react';
import { AppView } from '../types';
import { LayoutGrid, BookOpen, Map, Info, User as UserIcon, Bell, Search, LogIn } from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
  currentView: AppView;
  setView: (view: AppView) => void;
  isLoggedIn: boolean;
}

const Layout: React.FC<LayoutProps> = ({ children, currentView, setView, isLoggedIn }) => {
  return (
    <div className="min-h-screen flex flex-col relative">
      {/* Background Decorative Blobs */}
      <div className="fixed top-[-10%] left-[-5%] w-[40%] h-[40%] bg-green-900/10 blur-[120px] rounded-full z-[-1]" />
      <div className="fixed bottom-[-10%] right-[-5%] w-[40%] h-[40%] bg-green-800/10 blur-[120px] rounded-full z-[-1]" />

      {/* Navigation */}
      <nav className="fixed top-4 left-1/2 -translate-x-1/2 w-[90%] max-w-6xl glass rounded-2xl px-6 py-3 flex items-center justify-between z-50 transition-all hover:border-white/20">
        <div className="flex items-center gap-2 cursor-pointer group" onClick={() => setView(AppView.LANDING)}>
          <div className="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center neon-glow group-hover:scale-110 transition-transform">
             <span className="text-black font-black text-xs">AI</span>
          </div>
          <span className="text-xl font-bold tracking-tight">AIExcel</span>
        </div>

        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-gray-300">
          <button onClick={() => setView(AppView.LANDING)} className={`hover:text-green-400 transition-colors ${currentView === AppView.LANDING ? 'text-green-400' : ''}`}>Inicio</button>
          <button onClick={() => setView(AppView.DASHBOARD)} className={`hover:text-green-400 transition-colors ${currentView === AppView.DASHBOARD ? 'text-green-400' : ''}`}>Cursos</button>
          <button onClick={() => setView(AppView.ABOUT)} className={`hover:text-green-400 transition-colors ${currentView === AppView.ABOUT ? 'text-green-400' : ''}`}>Sobre Nosotros</button>
        </div>

        <div className="flex items-center gap-4">
          {isLoggedIn ? (
            <div className="flex items-center gap-4">
              <div className="hidden sm:flex bg-white/5 p-1.5 rounded-xl border border-white/10 items-center gap-2">
                <Search size={16} className="text-gray-400 ml-2" />
                <input type="text" placeholder="Buscar..." className="bg-transparent border-none outline-none text-sm w-32 focus:w-48 transition-all" />
              </div>
              <button className="relative p-2 hover:bg-white/5 rounded-full transition-colors">
                <Bell size={20} />
                <span className="absolute top-1 right-1 w-2 h-2 bg-green-500 rounded-full border-2 border-black"></span>
              </button>
              <div className="flex items-center gap-3 cursor-pointer p-1 pr-3 hover:bg-white/5 rounded-full transition-colors" onClick={() => setView(AppView.DASHBOARD)}>
                <img src="https://picsum.photos/seed/alex/100/100" className="w-8 h-8 rounded-full border border-green-500" alt="Avatar" />
                <span className="text-sm font-medium hidden lg:block">Alex Reed</span>
              </div>
            </div>
          ) : (
            <button 
              onClick={() => setView(AppView.LOGIN)}
              className="px-5 py-2 bg-green-600/20 text-green-400 border border-green-500/50 rounded-xl text-sm font-semibold hover:bg-green-600/30 transition-all flex items-center gap-2 neon-glow"
            >
              <LogIn size={16} />
              Iniciar Sesión
            </button>
          )}
        </div>
      </nav>

      <main className="flex-1 pt-24 px-4 sm:px-8 max-w-7xl mx-auto w-full pb-12">
        {children}
      </main>

      <footer className="py-8 text-center text-gray-500 text-sm border-t border-white/5 mt-12">
        <p>© 2024 AIExcel - Tu primer paso hacia el dominio de los datos.</p>
      </footer>
    </div>
  );
};

export default Layout;
