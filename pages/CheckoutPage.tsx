
import React, { useState } from 'react';
import { AppView } from '../types';
import { ShieldCheck, ChevronLeft, CheckCircle, CreditCard } from 'lucide-react';

/**
 * ============================================================================
 * CHECKOUT PAGE - VERSIÓN DEMO (SIN BACKEND)
 * ============================================================================
 * 
 * Esta versión funciona sin necesidad del backend de Django.
 * El botón de "Pagar" simplemente redirige al Dashboard como demo.
 * 
 * PARA ACTIVAR MERCADO PAGO REAL:
 * 1. Descomentar el código marcado con "// MP_REAL:"
 * 2. Levantar el backend: cd backend && python manage.py runserver 8000
 * 3. Configurar el .env con tu MP_ACCESS_TOKEN
 * 
 * ============================================================================
 */

// MP_REAL: URL del backend Django (descomentar cuando uses MP real)
// const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface CheckoutPageProps {
  setView: (view: AppView) => void;
}

const CheckoutPage: React.FC<CheckoutPageProps> = ({ setView }) => {
  const [isLoading, setIsLoading] = useState(false);

  // Datos del curso (en producción vendrían de props o context)
  const courseData = {
    id: 'excel-principiantes',
    title: 'Excel para Principiantes',
    originalPrice: 49.00,
    finalPrice: 24.50,
    discount: 50,
  };

  // ============================================================================
  // VERSIÓN DEMO: Simula el pago y va al dashboard
  // ============================================================================
  const handleDemoCheckout = () => {
    setIsLoading(true);
    // Simular delay de "procesamiento"
    setTimeout(() => {
      setIsLoading(false);
      setView(AppView.DASHBOARD);
    }, 1500);
  };

  // ============================================================================
  // MP_REAL: Descomentar esta función para usar Mercado Pago real
  // ============================================================================
  /*
  const handleMercadoPagoCheckout = async () => {
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/payments/create-preference/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          course_id: courseData.id,
          title: courseData.title,
          price: courseData.finalPrice,
          quantity: 1,
        }),
      });

      const data = await response.json();

      if (data.success && data.init_point) {
        // Redirigir a Mercado Pago
        const redirectUrl = data.sandbox_init_point || data.init_point;
        window.location.href = redirectUrl;
      } else {
        console.error('Error:', data.error);
        alert('Error al crear la preferencia de pago');
      }
    } catch (err) {
      console.error('Error:', err);
      alert('Error de conexión con el backend');
    } finally {
      setIsLoading(false);
    }
  };
  */

  return (
    <div className="animate-in zoom-in duration-500 max-w-5xl mx-auto py-12">
      <button
        onClick={() => setView(AppView.COURSE)}
        className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-8 group"
      >
        <ChevronLeft size={20} className="group-hover:-translate-x-1 transition-transform" />
        Volver al curso
      </button>

      <h1 className="text-4xl font-extrabold mb-12">Finalizar Compra</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-start">
        {/* Summary */}
        <div className="glass p-8 rounded-[2rem] border-white/10 space-y-6">
          <h2 className="text-xl font-bold text-gray-400">Resumen del Pedido</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <div>
                <p className="font-semibold">{courseData.title}</p>
                <p className="text-xs text-gray-500">Acceso Completo + Certificado</p>
              </div>
              <span className="font-bold">${courseData.originalPrice.toFixed(2)}</span>
            </div>
            <div className="flex justify-between items-center text-green-500">
              <p className="font-medium">Cupón: BIENVENIDA ({courseData.discount}%)</p>
              <span className="font-bold">-${(courseData.originalPrice - courseData.finalPrice).toFixed(2)}</span>
            </div>
            <div className="pt-4 border-t border-white/10 flex justify-between items-center">
              <span className="text-lg font-bold">Total a pagar:</span>
              <span className="text-3xl font-black text-green-500 neon-text">${courseData.finalPrice.toFixed(2)}</span>
            </div>
          </div>
        </div>

        {/* Payment Section */}
        <div className="space-y-8">
          <div className="space-y-4">
            <h2 className="text-xl font-bold">Método de Pago</h2>

            {/* Mercado Pago Info Card */}
            <div className="glass p-6 rounded-2xl border border-white/10 space-y-4">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 bg-[#009EE3] rounded-xl flex items-center justify-center">
                  <CreditCard className="text-white" size={32} />
                </div>
                <div>
                  <h3 className="font-bold text-lg">Mercado Pago</h3>
                  <p className="text-sm text-gray-400">Pagá con tarjeta, efectivo o dinero en cuenta</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs text-gray-400">
                <div className="flex items-center gap-2">
                  <CheckCircle size={14} className="text-green-500" />
                  <span>Tarjetas de crédito</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle size={14} className="text-green-500" />
                  <span>Tarjetas de débito</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle size={14} className="text-green-500" />
                  <span>Pago Fácil / Rapipago</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle size={14} className="text-green-500" />
                  <span>Dinero en cuenta MP</span>
                </div>
              </div>
            </div>
          </div>

          {/* Security Badge */}
          <div className="p-4 rounded-2xl bg-white/5 border border-white/5 flex items-start gap-4">
            <ShieldCheck className="text-green-500 shrink-0 mt-1" size={24} />
            <div>
              <p className="text-sm font-bold">Pago 100% Seguro</p>
              <p className="text-xs text-gray-500">
                Procesado por Mercado Pago con la máxima seguridad y protección al comprador.
              </p>
            </div>
          </div>

          {/* Mercado Pago Button */}
          <button
            onClick={handleDemoCheckout}  // MP_REAL: Cambiar a handleMercadoPagoCheckout
            disabled={isLoading}
            className="w-full py-5 bg-[#009EE3] hover:bg-[#0087cc] text-white font-bold rounded-2xl hover:scale-[1.02] transition-all text-lg flex items-center justify-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
          >
            {isLoading ? (
              <>
                <div className="w-6 h-6 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Procesando...
              </>
            ) : (
              <>
                <svg viewBox="0 0 48 48" className="w-7 h-7" fill="currentColor">
                  <path d="M24 4C12.954 4 4 12.954 4 24s8.954 20 20 20 20-8.954 20-20S35.046 4 24 4zm0 36c-8.837 0-16-7.163-16-16S15.163 8 24 8s16 7.163 16 16-7.163 16-16 16z" />
                  <path d="M24 12c-6.627 0-12 5.373-12 12s5.373 12 12 12 12-5.373 12-12-5.373-12-12-12zm0 20c-4.411 0-8-3.589-8-8s3.589-8 8-8 8 3.589 8 8-3.589 8-8 8z" />
                </svg>
                Pagar con Mercado Pago
              </>
            )}
          </button>

          {/* Demo Notice */}
          <div className="p-3 rounded-xl bg-yellow-500/10 border border-yellow-500/20 text-yellow-400 text-xs text-center">
            🎮 MODO DEMO: El pago es simulado. Para MP real, ver comentarios en el código.
          </div>

          <p className="text-center text-[10px] text-gray-500">
            Serás redirigido a Mercado Pago para completar tu compra de forma segura.
            <br />
            Al continuar, aceptás nuestros Términos de Servicio y Privacidad.
          </p>
        </div>
      </div>
    </div>
  );
};

export default CheckoutPage;
