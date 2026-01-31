import React, { useState, useMemo } from 'react';
import { AppView } from '../types';
import { getPlanillaById, getOfertaById } from '../data/planillas';
import { ShieldCheck, ChevronLeft, CheckCircle, CreditCard, User, Mail, Loader2, FileText } from 'lucide-react';

/**
 * ============================================================================
 * CHECKOUT PAGE - MERCADO PAGO INTEGRATION
 * ============================================================================
 * 
 * Flujo seguro de pago con registro de usuario en metadata de MP (stateless).
 * Soporta compra de planillas individuales y ofertas/packs.
 * 
 * PRODUCCIÓN: Usa init_point de Mercado Pago
 * DESARROLLO: Usa sandbox_init_point
 * 
 * ============================================================================
 */

// API URL dinámico según el entorno
// En producción (Vercel), VITE_API_URL debería estar configurado
// En desarrollo local, usa el backend de Railway o localhost
const API_URL = import.meta.env.VITE_API_URL ||
  (import.meta.env.PROD
    ? 'https://alexcel-backend-production.up.railway.app'  // PRODUCCIÓN
    : 'http://localhost:8000');  // DESARROLLO LOCAL

interface CheckoutPageProps {
  setView: (view: AppView) => void;
  planillaId?: string | null;
  ofertaId?: string | null;
}

const CheckoutPage: React.FC<CheckoutPageProps> = ({ setView, planillaId, ofertaId }) => {
  // Form state
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [document, setDocument] = useState('');
  const [email, setEmail] = useState('');

  // UI state
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Determinar qué producto se está comprando
  const productData = useMemo(() => {
    if (ofertaId) {
      const oferta = getOfertaById(ofertaId);
      if (oferta) {
        return {
          id: oferta.id,
          title: oferta.title,
          description: oferta.description,
          originalPrice: oferta.originalPrice,
          finalPrice: oferta.price,
          discount: oferta.savings,
          type: 'oferta' as const,
        };
      }
    }

    if (planillaId) {
      const planilla = getPlanillaById(planillaId);
      if (planilla) {
        const discount = Math.round((1 - planilla.price / planilla.originalPrice) * 100);
        return {
          id: planilla.id,
          title: planilla.title,
          description: planilla.shortDescription,
          originalPrice: planilla.originalPrice,
          finalPrice: planilla.price,
          discount,
          type: 'planilla' as const,
        };
      }
    }

    // Fallback
    return {
      id: 'tracker-habitos',
      title: 'Tracker de Hábitos',
      description: 'Planilla Excel Premium',
      originalPrice: 15,
      finalPrice: 1,
      discount: 93,
      type: 'planilla' as const,
    };
  }, [planillaId, ofertaId]);

  // Validación del formulario
  const isFormValid = () => {
    return (
      firstName.trim().length >= 2 &&
      lastName.trim().length >= 2 &&
      document.trim().length >= 7 &&
      email.trim().length > 0 &&
      email.includes('@') &&
      email.includes('.')
    );
  };

  // Formatear DNI mientras escribe
  const handleDocumentChange = (value: string) => {
    const cleaned = value.replace(/[^\d.]/g, '');
    setDocument(cleaned);
  };

  // Handle Mercado Pago checkout
  const handleMercadoPagoCheckout = async () => {
    if (!isFormValid()) {
      setError('Por favor, completá todos los campos correctamente.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      console.log(`[Checkout] Enviando a ${API_URL}/api/payments/create-preference/`);

      const response = await fetch(`${API_URL}/api/payments/create-preference/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          first_name: firstName.trim(),
          last_name: lastName.trim(),
          document: document.trim(),
          email: email.trim().toLowerCase(),
          course_id: productData.id,
          title: productData.title,
          price: productData.finalPrice,
          quantity: 1,
        }),
      });

      const data = await response.json();
      console.log('[Checkout] Respuesta:', data);

      if (data.success && data.init_point) {
        // PRODUCCIÓN: El backend ya envía el init_point correcto según el entorno
        console.log('[Checkout] Redirigiendo a Mercado Pago...', data.init_point);
        window.location.href = data.init_point;
      } else {
        setError(data.error || 'Error al crear la preferencia de pago');
        setIsLoading(false);
      }
    } catch (err) {
      console.error('[Checkout] Error:', err);
      setError('Error de conexión. Por favor intentá de nuevo.');
      setIsLoading(false);
    }
  };

  const handleGoBack = () => {
    if (ofertaId) {
      setView(AppView.OFERTAS);
    } else if (planillaId) {
      setView(AppView.PLANILLA_DETAIL);
    } else {
      setView(AppView.PLANILLAS);
    }
  };

  return (
    <div className="animate-in zoom-in duration-500 max-w-5xl mx-auto py-12">
      <button
        onClick={handleGoBack}
        className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-8 group"
      >
        <ChevronLeft size={20} className="group-hover:-translate-x-1 transition-transform" />
        Volver
      </button>

      <h1 className="text-4xl font-extrabold mb-12">Finalizar Compra</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-start">
        {/* Left Column - User Form */}
        <div className="space-y-8">
          {/* User Information Form */}
          <div className="glass p-8 rounded-[2rem] border-white/10 space-y-6">
            <h2 className="text-xl font-bold text-white flex items-center gap-3">
              <div className="w-8 h-8 bg-green-500/20 rounded-lg flex items-center justify-center">
                <User size={18} className="text-green-500" />
              </div>
              Tus Datos
            </h2>

            <p className="text-sm text-gray-400">
              Ingresá tus datos para recibir el archivo.
            </p>

            <div className="space-y-5">
              {/* Row: Nombre + Apellido */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label htmlFor="firstName" className="block text-sm font-medium text-gray-300">
                    Nombre
                  </label>
                  <input
                    id="firstName"
                    type="text"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    placeholder="Juan"
                    disabled={isLoading}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl 
                             text-white placeholder-gray-500 
                             focus:border-green-500 focus:ring-2 focus:ring-green-500/20 
                             transition-all outline-none disabled:opacity-50"
                  />
                </div>

                <div className="space-y-2">
                  <label htmlFor="lastName" className="block text-sm font-medium text-gray-300">
                    Apellido
                  </label>
                  <input
                    id="lastName"
                    type="text"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    placeholder="Pérez"
                    disabled={isLoading}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl 
                             text-white placeholder-gray-500 
                             focus:border-green-500 focus:ring-2 focus:ring-green-500/20 
                             transition-all outline-none disabled:opacity-50"
                  />
                </div>
              </div>

              {/* DNI/CUIT */}
              <div className="space-y-2">
                <label htmlFor="document" className="block text-sm font-medium text-gray-300">
                  DNI / CUIT
                </label>
                <div className="relative">
                  <FileText size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" />
                  <input
                    id="document"
                    type="text"
                    value={document}
                    onChange={(e) => handleDocumentChange(e.target.value)}
                    placeholder="12.345.678"
                    disabled={isLoading}
                    maxLength={14}
                    className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl 
                             text-white placeholder-gray-500 
                             focus:border-green-500 focus:ring-2 focus:ring-green-500/20 
                             transition-all outline-none disabled:opacity-50"
                  />
                </div>
              </div>

              {/* Email */}
              <div className="space-y-2">
                <label htmlFor="email" className="block text-sm font-medium text-gray-300">
                  Email
                </label>
                <div className="relative">
                  <Mail size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" />
                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="tu@email.com"
                    disabled={isLoading}
                    className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl 
                             text-white placeholder-gray-500 
                             focus:border-green-500 focus:ring-2 focus:ring-green-500/20 
                             transition-all outline-none disabled:opacity-50"
                  />
                </div>
                <p className="text-xs text-gray-500">
                  Recibirás el link de descarga en este email.
                </p>
              </div>
            </div>
          </div>

          {/* Payment Method Info */}
          <div className="glass p-6 rounded-2xl border border-white/10 space-y-4">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-[#009EE3] rounded-xl flex items-center justify-center shrink-0">
                <CreditCard className="text-white" size={28} />
              </div>
              <div>
                <h3 className="font-bold text-lg">Mercado Pago</h3>
                <p className="text-sm text-gray-400">Pagá como quieras, 100% seguro</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs text-gray-400">
              <div className="flex items-center gap-2">
                <CheckCircle size={14} className="text-green-500 shrink-0" />
                <span>Tarjetas de crédito</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle size={14} className="text-green-500 shrink-0" />
                <span>Tarjetas de débito</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle size={14} className="text-green-500 shrink-0" />
                <span>Pago Fácil / Rapipago</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle size={14} className="text-green-500 shrink-0" />
                <span>Dinero en cuenta MP</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Summary & Payment */}
        <div className="space-y-6">
          {/* Order Summary */}
          <div className="glass p-8 rounded-[2rem] border-white/10 space-y-6">
            <h2 className="text-xl font-bold text-gray-400">Resumen del Pedido</h2>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <div>
                  <p className="font-semibold">{productData.title}</p>
                  <p className="text-xs text-gray-500">{productData.description}</p>
                </div>
                <span className="font-bold text-gray-400 line-through">${productData.originalPrice.toFixed(2)}</span>
              </div>
              <div className="flex justify-between items-center text-green-500">
                <p className="font-medium">Descuento Especial ({productData.discount}%)</p>
                <span className="font-bold">-${(productData.originalPrice - productData.finalPrice).toFixed(2)}</span>
              </div>
              <div className="pt-4 border-t border-white/10 flex justify-between items-center">
                <span className="text-lg font-bold">Total a pagar:</span>
                <span className="text-3xl font-black text-green-500 neon-text">${productData.finalPrice.toFixed(2)}</span>
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

          {/* Error Message */}
          {error && (
            <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
              ⚠️ {error}
            </div>
          )}

          {/* Mercado Pago Button */}
          <button
            onClick={handleMercadoPagoCheckout}
            disabled={isLoading || !isFormValid()}
            className={`
              w-full py-5 bg-[#009EE3] text-white font-bold rounded-2xl text-lg 
              flex items-center justify-center gap-3 transition-all
              ${isLoading || !isFormValid()
                ? 'opacity-50 cursor-not-allowed'
                : 'hover:bg-[#0087cc] hover:scale-[1.02]'
              }
            `}
          >
            {isLoading ? (
              <>
                <Loader2 size={24} className="animate-spin" />
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

          {/* Form validation hint */}
          {!isFormValid() && !isLoading && (
            <p className="text-center text-xs text-gray-500">
              Completá todos los campos para continuar
            </p>
          )}

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
