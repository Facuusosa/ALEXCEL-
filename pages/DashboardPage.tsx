
import React from 'react';
import { AppView } from '../types';
import { Play, TrendingUp, Clock, Book, User as UserIcon, Star, ArrowRight } from 'lucide-react';

interface DashboardPageProps {
  setView: (view: AppView) => void;
}

const DashboardPage: React.FC<DashboardPageProps> = ({ setView }) => {
  const myCourses = [
    { title: "Excel para Principiantes", progress: 15, color: "from-green-500 to-green-700", img: "https://picsum.photos/seed/c1/400/250" },
    { title: "Introducción a Datos", progress: 0, color: "from-blue-500 to-blue-700", img: "https://picsum.photos/seed/c2/400/250" },
  ];

  const recommended = [
    { title: "Dashboard Masterclass", instructor: "Muntker Nonera", time: "1h 10m", img: "https://picsum.photos/seed/r1/400/250" },
    { title: "Excel para Finanzas", instructor: "Danatar Revn", time: "45 min", img: "https://picsum.photos/seed/r2/400/250" },
    { title: "Automatización Básica", instructor: "Cichial Birason", time: "25 min", img: "https://picsum.photos/seed/r3/400/250" },
  ];

  return (
    <div className="animate-in fade-in slide-in-from-right-4 duration-500 space-y-12 py-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <h1 className="text-5xl font-extrabold tracking-tight mb-2">Welcome back, <span className="text-green-500">Alex</span>.</h1>
          <p className="text-gray-400">Es un buen día para aprender algo nuevo.</p>
        </div>
        
        {/* Active Session Highlight */}
        <div className="glass p-6 rounded-3xl border-white/10 flex items-center gap-6 max-w-lg group hover:border-green-500/30 transition-all cursor-pointer">
           <div className="relative w-32 h-20 rounded-xl overflow-hidden shrink-0">
             <img src="https://picsum.photos/seed/resume/300/200" className="w-full h-full object-cover" alt="Current" />
             <div className="absolute inset-0 flex items-center justify-center bg-black/40 group-hover:bg-black/20 transition-all">
               <Play size={24} className="text-white drop-shadow-lg" />
             </div>
           </div>
           <div className="flex-1 space-y-2">
             <h3 className="text-sm font-bold leading-tight">Excel para Principiantes: Módulo 1</h3>
             <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
               <div className="bg-green-500 h-full w-[15%]"></div>
             </div>
             <div className="flex items-center justify-between text-[10px] text-gray-500">
               <span>15% Completado</span>
               <span className="text-green-500 font-bold">Continuar</span>
             </div>
           </div>
        </div>
      </div>

      {/* Your Courses Grid */}
      <section className="space-y-6">
        <h2 className="text-2xl font-bold flex items-center gap-2"><Book size={24} className="text-green-500" /> Mis Cursos</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {myCourses.map((course, i) => (
            <div key={i} className="glass rounded-[1.5rem] border-white/10 p-5 space-y-4 hover:-translate-y-1 transition-transform group">
              <div className="aspect-video rounded-xl overflow-hidden relative">
                <img src={course.img} alt={course.title} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" />
                <div className={`absolute bottom-0 left-0 h-1 bg-gradient-to-r ${course.color}`} style={{ width: `${course.progress}%` }}></div>
              </div>
              <div className="space-y-1">
                <h3 className="font-bold text-sm leading-tight">{course.title}</h3>
                <p className="text-[10px] text-gray-500 flex items-center gap-1"><Clock size={10} /> Último acceso: hace 2 días</p>
              </div>
              <div className="flex items-center justify-between pt-2">
                <span className="text-xs font-bold text-green-500">{course.progress}%</span>
                <button className="text-[10px] bg-white/5 px-2 py-1 rounded-full border border-white/10 hover:bg-white/10 transition-colors">Seguir</button>
              </div>
            </div>
          ))}
          {/* Add Course Card Placeholder */}
          <div className="border-2 border-dashed border-white/10 rounded-[1.5rem] flex flex-col items-center justify-center p-8 space-y-3 opacity-50 hover:opacity-100 transition-opacity cursor-pointer group" onClick={() => setView(AppView.LANDING)}>
            <div className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center group-hover:scale-110 transition-transform">
              <ArrowRight size={20} className="text-gray-400 group-hover:text-green-500 transition-colors" />
            </div>
            <span className="text-sm font-medium">Ver más cursos</span>
          </div>
        </div>
      </section>

      {/* Recommended Grid */}
      <section className="space-y-6 pb-8">
        <h2 className="text-2xl font-bold flex items-center gap-2"><Star size={24} className="text-green-500" /> Recomendado para ti</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6">
          {recommended.map((course, i) => (
            <div key={i} className="glass rounded-[1.5rem] border-white/10 overflow-hidden flex flex-col hover:border-green-500/20 transition-all group">
              <div className="aspect-[4/5] relative">
                 <img src={course.img} className="w-full h-full object-cover grayscale-[20%] group-hover:grayscale-0 transition-all" alt={course.title} />
                 <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent"></div>
                 <div className="absolute bottom-4 left-4 right-4">
                    <h3 className="font-bold text-sm mb-1">{course.title}</h3>
                    <div className="flex items-center gap-2 mb-3">
                      <img src={`https://i.pravatar.cc/150?u=${i}`} className="w-5 h-5 rounded-full border border-green-500" alt="Inst" />
                      <span className="text-[10px] text-gray-300">{course.instructor}</span>
                    </div>
                    <button className="w-full py-2 bg-green-500 text-black text-[10px] font-black rounded-lg uppercase tracking-widest hover:scale-[1.05] transition-transform">Inscribirme</button>
                 </div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default DashboardPage;
