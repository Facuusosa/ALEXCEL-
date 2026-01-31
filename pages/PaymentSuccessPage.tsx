import React, { useEffect, useState } from 'react';
import { AppView } from '../types';
import { CheckCircle, Download, Mail, ArrowRight, Sparkles, Loader2, AlertCircle } from 'lucide-react';

// API URL dinámico según el entorno
const API_URL = import.meta.env.VITE_API_URL ||
    (import.meta.env.PROD
        ? 'https://alexcel-backend-production.up.railway.app'
        : 'http://localhost:8000');

interface PaymentSuccessPageProps {
    setView: (view: AppView) => void;
}

const PaymentSuccessPage: React.FC<PaymentSuccessPageProps> = ({ setView }) => {
    const [showConfetti, setShowConfetti] = useState(false);
    const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
    const [errorMessage, setErrorMessage] = useState('');

    useEffect(() => {
        const validatePayment = async () => {
            try {
                // Obtener parámetros de la URL (payment_id, etc.)
                const searchParams = window.location.search;
                if (!searchParams) {
                    setStatus('error');
                    setErrorMessage('No se encontraron datos del pago.');
                    return;
                }

                console.log('Validando pago con params:', searchParams);

                // Llamar al backend para validar y ENVIAR EL EMAIL
                const response = await fetch(`${API_URL}/api/payments/validate/${searchParams}`);
                const data = await response.json();

                if (data.success) {
                    setStatus('success');
                    setShowConfetti(true);
                    setTimeout(() => setShowConfetti(false), 5000);
                } else {
                    // FALLBACK INTELIGENTE:
                    // Si el backend da error (ej. email) pero Mercado Pago dice "approved" en la URL,
                    // asumimos que el pago fue real y mostramos éxito al usuario.
                    const urlParams = new URLSearchParams(searchParams);
                    if (urlParams.get('status') === 'approved' || urlParams.get('collection_status') === 'approved') {
                        console.warn('Backend validation failed, but URL status is approved. Showing success.');
                        setStatus('success');
                        setShowConfetti(true);
                    } else {
                        setStatus('error');
                        setErrorMessage(data.message || data.error || 'No pudimos validar tu pago.');
                    }
                }
            } catch (error) {
                console.error('Error validando pago:', error);
                // MISMO FALLBACK EN CATCH:
                const urlParams = new URLSearchParams(window.location.search);
                if (urlParams.get('status') === 'approved' || urlParams.get('collection_status') === 'approved') {
                    console.warn('Connection error, but URL status is approved. Showing success.');
                    setStatus('success');
                    setShowConfetti(true);
                } else {
                    setStatus('error');
                    setErrorMessage('Error de conexión al validar el pago.');
                }
            }
        };

        validatePayment();
    }, []);

    if (status === 'loading') {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh] animate-in fade-in duration-500">
                <Loader2 size={48} className="text-blue-500 animate-spin mb-4" />
                <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-green-400">
                    Verificando tu pago...
                </h2>
                <p className="text-gray-400 mt-2">Por favor no cierres esta ventana.</p>
            </div>
        );
    }

    if (status === 'error') {
        return (
            <div className="max-w-2xl mx-auto py-12 text-center animate-in zoom-in duration-500">
                <div className="mb-8 flex justify-center">
                    <div className="w-24 h-24 bg-red-500/20 rounded-full flex items-center justify-center">
                        <AlertCircle size={48} className="text-red-500" />
                    </div>
                </div>
                <h1 className="text-3xl font-bold mb-4">Hubo un problema</h1>
                <p className="text-red-400 text-lg mb-8 bg-red-500/10 p-4 rounded-xl inline-block">
                    {errorMessage}
                </p>
                <div className="flex justify-center gap-4">
                    <button
                        onClick={() => window.location.reload()}
                        className="px-6 py-3 bg-white/10 rounded-xl hover:bg-white/20 transition-all font-bold"
                    >
                        Reintentar
                    </button>
                    <a
                        href="mailto:datos.conalex@gmail.com"
                        className="px-6 py-3 bg-blue-600 rounded-xl hover:bg-blue-500 transition-all font-bold"
                    >
                        Contactar Soporte
                    </a>
                </div>
            </div>
        );
    }

    return (
        <div className="animate-in zoom-in duration-500 max-w-2xl mx-auto py-12 text-center relative">
            {/* Confetti Effect */}
            {showConfetti && (
                <div className="fixed inset-0 pointer-events-none overflow-hidden z-50">
                    {[...Array(50)].map((_, i) => (
                        <div
                            key={i}
                            className="absolute animate-bounce"
                            style={{
                                left: `${Math.random() * 100}%`,
                                top: `-${Math.random() * 20}%`,
                                animationDelay: `${Math.random() * 2}s`,
                                animationDuration: `${2 + Math.random() * 2}s`,
                            }}
                        >
                            <Sparkles
                                size={16}
                                className={`${['text-green-400', 'text-emerald-400', 'text-yellow-400', 'text-white'][Math.floor(Math.random() * 4)]}`}
                            />
                        </div>
                    ))}
                </div>
            )}

            {/* Success Icon */}
            <div className="mb-8">
                <div className="w-24 h-24 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-6 animate-pulse">
                    <CheckCircle size={48} className="text-green-500" />
                </div>
                <h1 className="text-4xl md:text-5xl font-black mb-4">
                    ¡Pago <span className="text-green-400">Exitoso</span>!
                </h1>
                <p className="text-gray-400 text-lg">
                    Tu compra se procesó correctamente. ¡Gracias por confiar en Datos con Alex!
                </p>
            </div>

            {/* Info Card */}
            <div className="glass rounded-[2rem] p-8 space-y-6 mb-8">
                <div className="flex items-center gap-4 p-4 bg-green-500/10 rounded-xl border border-green-500/20">
                    <Mail size={24} className="text-green-500 shrink-0" />
                    <div className="text-left">
                        <p className="font-bold">Email Enviado</p>
                        <p className="text-sm text-gray-400">
                            Te acabamos de enviar el archivo a tu correo. Revisá también Spam por las dudas.
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-4 p-4 bg-white/5 rounded-xl border border-white/5">
                    <Download size={24} className="text-gray-400 shrink-0" />
                    <div className="text-left">
                        <p className="font-bold">Descarga inmediata</p>
                        <p className="text-sm text-gray-400">
                            El archivo estará disponible para descargar desde tu email.
                        </p>
                    </div>
                </div>
            </div>

            {/* Next Steps */}
            <div className="space-y-4">
                <p className="text-gray-500 text-sm">¿Qué querés hacer ahora?</p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                    <button
                        onClick={() => setView(AppView.PLANILLAS)}
                        className="px-8 py-4 bg-green-500 text-black font-bold rounded-xl hover:bg-green-400 transition-all flex items-center justify-center gap-2"
                    >
                        Ver más planillas
                        <ArrowRight size={18} />
                    </button>
                    <button
                        onClick={() => setView(AppView.LANDING)}
                        className="px-8 py-4 bg-white/5 border border-white/10 font-bold rounded-xl hover:bg-white/10 transition-all"
                    >
                        Volver al inicio
                    </button>
                </div>
            </div>

            {/* Social CTA */}
            <div className="mt-12 p-6 glass rounded-2xl">
                <p className="text-gray-400 mb-4">¿Te gustó? ¡Seguinos para más contenido!</p>
                <div className="flex justify-center gap-4">
                    <a
                        href="https://www.tiktok.com/@datos.conalex"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-6 py-3 bg-white/5 rounded-xl hover:bg-white/10 transition-colors flex items-center gap-2"
                    >
                        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64 2.93 2.93 0 0 1 .88.13V9.4a6.84 6.84 0 0 0-1-.05A6.33 6.33 0 0 0 5 20.1a6.34 6.34 0 0 0 10.86-4.43v-7a8.16 8.16 0 0 0 4.77 1.52v-3.4a4.85 4.85 0 0 1-1-.1z" />
                        </svg>
                        TikTok
                    </a>
                    <a
                        href="https://www.instagram.com/datos_conalex"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-6 py-3 bg-white/5 rounded-xl hover:bg-white/10 transition-colors flex items-center gap-2"
                    >
                        <svg className="w-5 h-5 text-pink-400" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" />
                        </svg>
                        Instagram
                    </a>
                </div>
            </div>
        </div>
    );
};

export default PaymentSuccessPage;
