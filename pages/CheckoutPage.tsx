
import React from 'react';
import { AppView } from '../types';
import { CreditCard, Calendar, Lock, ShieldCheck, ChevronLeft } from 'lucide-react';

interface CheckoutPageProps {
  setView: (view: AppView) => void;
}

const CheckoutPage: React.FC<CheckoutPageProps> = ({ setView }) => {
  return (
    <div className="animate-in zoom-in duration-500 max-w-5xl mx-auto py-12">
      <button 
        onClick={() => setView(AppView.COURSE)}
        className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-8 group"
      >
        <ChevronLeft size={20} className="group-hover:-translate-x-1 transition-transform" />
        Volver al curso
      </button>

      <h1 className="text-4xl font-extrabold mb-12">Secure Checkout</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-start">
        {/* Summary */}
        <div className="glass p-8 rounded-[2rem] border-white/10 space-y-6">
          <h2 className="text-xl font-bold text-gray-400">Resumen del Pedido</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <div>
                <p className="font-semibold">Excel para Principiantes</p>
                <p className="text-xs text-gray-500">Acceso Completo + Certificado</p>
              </div>
              <span className="font-bold">$49.00</span>
            </div>
            <div className="flex justify-between items-center text-green-500">
              <p className="font-medium">Cupón: BIENVENIDA (50%)</p>
              <span className="font-bold">-$24.50</span>
            </div>
            <div className="pt-4 border-t border-white/10 flex justify-between items-center">
              <span className="text-lg font-bold">Total a pagar:</span>
              <span className="text-3xl font-black text-green-500 neon-text">$24.50</span>
            </div>
          </div>
        </div>

        {/* Payment Form */}
        <div className="space-y-8">
          <div className="space-y-4">
            <h2 className="text-xl font-bold">Detalles de Pago</h2>
            <div className="space-y-3">
              <div className="relative">
                <CreditCard className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
                <input type="text" placeholder="Número de Tarjeta" className="w-full glass bg-white/5 border border-white/10 rounded-xl py-4 pl-12 pr-4 focus:border-green-500 outline-none transition-all" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="relative">
                  <Calendar className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
                  <input type="text" placeholder="MM/YY" className="w-full glass bg-white/5 border border-white/10 rounded-xl py-4 pl-12 pr-4 focus:border-green-500 outline-none transition-all" />
                </div>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
                  <input type="text" placeholder="CVC" className="w-full glass bg-white/5 border border-white/10 rounded-xl py-4 pl-12 pr-4 focus:border-green-500 outline-none transition-all" />
                </div>
              </div>
              <input type="text" placeholder="Nombre en la Tarjeta" className="w-full glass bg-white/5 border border-white/10 rounded-xl py-4 px-4 focus:border-green-500 outline-none transition-all" />
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-white/5 border border-white/5 flex items-start gap-4">
            <ShieldCheck className="text-green-500 shrink-0 mt-1" size={24} />
            <div>
              <p className="text-sm font-bold">Pago Seguro SSL</p>
              <p className="text-xs text-gray-500">Tus datos están protegidos y encriptados bajo estándares internacionales de seguridad.</p>
            </div>
          </div>

          <button 
            onClick={() => setView(AppView.DASHBOARD)}
            className="w-full py-5 bg-green-500 text-black font-bold rounded-2xl hover:scale-[1.02] transition-all neon-glow text-lg"
          >
            Finalizar Compra
          </button>
          <p className="text-center text-[10px] text-gray-500">Al hacer clic, aceptas nuestros Términos de Servicio y Privacidad.</p>
        </div>
      </div>
    </div>
  );
};

export default CheckoutPage;
