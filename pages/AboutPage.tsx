
import React from 'react';
import { AppView } from '../types';
import { Target, Users, Zap, Award, BarChart3, Rocket } from 'lucide-react';

interface AboutPageProps {
  setView: (view: AppView) => void;
}

const AboutPage: React.FC<AboutPageProps> = ({ setView }) => {
  const team = [
    { name: "Ana Martínez", role: "Directora de Currículo", img: "https://i.pravatar.cc/150?u=ana" },
    { name: "Carlos Ruiz", role: "Instructor Principal", img: "https://i.pravatar.cc/150?u=carlos" },
    { name: "Sofia Patel", role: "Experta en Datos", img: "https://i.pravatar.cc/150?u=sofia" },
    { name: "David Lee", role: "Desarrollo", img: "https://i.pravatar.cc/150?u=david" },
    { name: "Elena Gómez", role: "Soporte Estudiante", img: "https://i.pravatar.cc/150?u=elena" },
  ];

  return (
    <div className="animate-in fade-in zoom-in duration-500 py-12 space-y-24">
      {/* Mission */}
      <section className="text-center space-y-6 max-w-3xl mx-auto">
        <h1 className="text-5xl font-black mb-6">Nuestra Misión</h1>
        <p className="text-lg text-gray-400 leading-relaxed">
          En AIExcel, empoderamos a profesionales principiantes con habilidades esenciales de Excel y análisis de datos 
          para que puedan sobresalir en un mundo impulsado por la información. Creemos en la educación práctica 
          y el aprendizaje continuo como base del éxito profesional.
        </p>
      </section>

      {/* Team */}
      <section className="space-y-12">
        <h2 className="text-3xl font-bold text-center">Nuestro Equipo</h2>
        <div className="flex flex-wrap justify-center gap-12">
          {team.map((member, i) => (
            <div key={i} className="text-center group">
              <div className="w-28 h-28 mx-auto mb-4 relative">
                <div className="absolute inset-0 bg-green-500 rounded-full blur opacity-0 group-hover:opacity-40 transition-opacity"></div>
                <img src={member.img} className="w-full h-full rounded-full border-4 border-white/10 group-hover:border-green-500 transition-all relative z-10" alt={member.name} />
              </div>
              <h3 className="font-bold text-sm">{member.name}</h3>
              <p className="text-[10px] text-gray-500 uppercase tracking-widest mt-1">{member.role}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Values */}
      <section className="space-y-12">
        <h2 className="text-3xl font-bold text-center">Nuestros Valores</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="glass p-8 rounded-3xl border-white/10 text-center space-y-4 hover:border-green-500/30 transition-all group">
            <div className="w-14 h-14 bg-green-500/10 rounded-2xl flex items-center justify-center mx-auto text-green-500 group-hover:scale-110 transition-transform">
              <Award size={28} />
            </div>
            <h3 className="text-xl font-bold">Excelencia</h3>
            <p className="text-sm text-gray-400">Nos esforzamos por la máxima calidad en cada curso y recurso que creamos.</p>
          </div>
          <div className="glass p-8 rounded-3xl border-white/10 text-center space-y-4 hover:border-green-500/30 transition-all group">
            <div className="w-14 h-14 bg-green-500/10 rounded-2xl flex items-center justify-center mx-auto text-green-500 group-hover:scale-110 transition-transform">
              <Users size={28} />
            </div>
            <h3 className="text-xl font-bold">Comunidad</h3>
            <p className="text-sm text-gray-400">Fomentamos la colaboración y el apoyo mutuo entre nuestros estudiantes.</p>
          </div>
          <div className="glass p-8 rounded-3xl border-white/10 text-center space-y-4 hover:border-green-500/30 transition-all group">
            <div className="w-14 h-14 bg-green-500/10 rounded-2xl flex items-center justify-center mx-auto text-green-500 group-hover:scale-110 transition-transform">
              <Rocket size={28} />
            </div>
            <h3 className="text-xl font-bold">Innovación</h3>
            <p className="text-sm text-gray-400">Nos mantenemos a la vanguardia de las herramientas y técnicas de datos.</p>
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="glass p-12 rounded-[3rem] border-white/10 text-center space-y-8 relative overflow-hidden neon-glow">
        <div className="absolute top-0 right-0 w-64 h-64 bg-green-500/5 blur-[80px] rounded-full"></div>
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-green-500/5 blur-[80px] rounded-full"></div>
        <h2 className="text-3xl font-bold relative z-10">¿Listo para llevar tus habilidades al siguiente nivel?</h2>
        <button 
          onClick={() => setView(AppView.LANDING)}
          className="px-10 py-4 bg-green-500 text-black font-bold rounded-2xl hover:scale-105 transition-transform neon-glow relative z-10"
        >
          Únete a la Comunidad
        </button>
      </section>
    </div>
  );
};

export default AboutPage;
