
import React, { useState, useEffect } from 'react';
import Layout from './components/Layout';
import LandingPage from './pages/LandingPage';
import CoursePage from './pages/CoursePage';
import CheckoutPage from './pages/CheckoutPage';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import AboutPage from './pages/AboutPage';
import { AppView } from './types';

const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<AppView>(AppView.LANDING);
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);

  // Simple scroll to top on view change
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [currentView]);

  const handleLogin = () => {
    setIsLoggedIn(true);
    setCurrentView(AppView.DASHBOARD);
  };

  const renderView = () => {
    switch (currentView) {
      case AppView.LANDING:
        return <LandingPage setView={setCurrentView} />;
      case AppView.COURSE:
        return <CoursePage setView={setCurrentView} />;
      case AppView.CHECKOUT:
        return <CheckoutPage setView={setCurrentView} />;
      case AppView.LOGIN:
        return <LoginPage onLogin={handleLogin} setView={setCurrentView} />;
      case AppView.DASHBOARD:
        return <DashboardPage setView={setCurrentView} />;
      case AppView.ABOUT:
        return <AboutPage setView={setCurrentView} />;
      default:
        return <LandingPage setView={setCurrentView} />;
    }
  };

  return (
    <Layout 
      currentView={currentView} 
      setView={setCurrentView} 
      isLoggedIn={isLoggedIn}
    >
      {renderView()}
    </Layout>
  );
};

export default App;
