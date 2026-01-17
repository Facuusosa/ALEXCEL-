
import React from 'react';
import { AppView } from '../types';
import { ChevronRight, Zap, Trophy, MousePointer2, Instagram } from 'lucide-react';

interface LandingPageProps {
  setView: (view: AppView) => void;
}

const LandingPage: React.FC<LandingPageProps> = ({ setView }) => {
  return (
    <div className="animate-in fade-in duration-1000">
      {/* Hero Section Minimalista y Potente */}
      <section className="relative py-24 flex flex-col items-center text-center space-y-10 overflow-hidden">
        <div className="absolute top-0 w-full h-full -z-10">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-green-500/10 blur-[120px] rounded-full"></div>
        </div>

        <div className="space-y-4">
          <span className="px-4 py-1.5 rounded-full bg-green-500/10 border border-green-500/20 text-green-400 text-xs font-bold uppercase tracking-widest animate-pulse">
            Academia de Excel Líder
          </span>
          <h1 className="text-6xl md:text-8xl font-black tracking-tighter leading-none">
            TU ÉXITO TIENE <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-emerald-600 uppercase">Forma de Celda</span>
          </h1>
        </div>
        
        <p className="text-gray-400 max-w-xl text-lg md:text-xl font-medium leading-relaxed">
          Domina la herramienta más poderosa del mundo laboral. Cursos diseñados para transformar principiantes en analistas expertos.
        </p>

        <div className="flex flex-col sm:flex-row gap-5 pt-4">
          <button 
            onClick={() => setView(AppView.COURSE)}
            className="group px-10 py-5 bg-white text-black font-extrabold rounded-2xl hover:bg-green-500 transition-all duration-300 flex items-center gap-3 hover:scale-105 active:scale-95 shadow-[0_0_20px_rgba(255,255,255,0.1)]"
          >
            Ver Catálogo de Cursos
            <ChevronRight size={20} className="group-hover:translate-x-1 transition-transform" />
          </button>
          <a 
            href="https://instagram.com" 
            target="_blank" 
            rel="noopener noreferrer"
            className="px-10 py-5 bg-white/5 border border-white/10 text-white font-bold rounded-2xl hover:bg-white/10 transition-all flex items-center gap-3 group"
          >
            <Instagram size={20} className="text-pink-500 group-hover:scale-110 transition-transform" />
            Síguenos en Instagram
          </a>
        </div>
      </section>

      {/* Grid de Beneficios */}
      <section className="py-24 grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="glass p-10 rounded-[2.5rem] border-white/5 space-y-4 hover:border-green-500/20 transition-all group">
          <div className="w-14 h-14 bg-green-500/20 rounded-2xl flex items-center justify-center text-green-500 group-hover:scale-110 transition-transform">
            <Zap size={28} fill="currentColor" />
          </div>
          <h3 className="text-2xl font-bold">Aprendizaje Ágil</h3>
          <p className="text-gray-500 leading-relaxed">Sin rellenos innecesarios. Vamos directo a lo que las empresas piden en sus entrevistas.</p>
        </div>

        <div className="glass p-10 rounded-[2.5rem] border-white/5 space-y-4 hover:border-green-500/20 transition-all group">
          <div className="w-14 h-14 bg-green-500/20 rounded-2xl flex items-center justify-center text-green-500 group-hover:scale-110 transition-transform">
            <Trophy size={28} />
          </div>
          <h3 className="text-2xl font-bold">Certificación Real</h3>
          <p className="text-gray-500 leading-relaxed">Obtén un diploma que valida tus habilidades y destaca en tu perfil profesional.</p>
        </div>

        <div className="glass p-10 rounded-[2.5rem] border-white/5 space-y-4 hover:border-green-500/20 transition-all group">
          <div className="w-14 h-14 bg-green-500/20 rounded-2xl flex items-center justify-center text-green-500 group-hover:scale-110 transition-transform">
            <MousePointer2 size={28} />
          </div>
          <h3 className="text-2xl font-bold">100% Práctico</h3>
          <p className="text-gray-500 leading-relaxed">Ejercicios reales desde el minuto uno. Construye tus propios reportes inteligentes.</p>
        </div>
      </section>

      {/* Social Proof */}
      <div className="py-12 border-t border-white/5 text-center">
        <p className="text-gray-600 text-sm font-bold uppercase tracking-[0.3em] mb-8">Nuestros alumnos trabajan en</p>
        <div className="flex flex-wrap justify-center gap-12 opacity-30 grayscale hover:grayscale-0 transition-all duration-500">
           <span className="text-2xl font-black italic">MICRO-CORP</span>
           <span className="text-2xl font-black italic">DATA-LOGIC</span>
           <span className="text-2xl font-black italic">FIN-FLOW</span>
           <span className="text-2xl font-black italic">TECH-WAVE</span>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
