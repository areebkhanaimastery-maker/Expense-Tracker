import { useState } from 'react';
import { DashboardLayout, type PageId } from './layouts/DashboardLayout';
import { Dashboard } from './pages/Dashboard';
import { Expenses } from './pages/Expenses';
import { Analytics } from './pages/Analytics';
import { Intelligence } from './pages/Intelligence';
import { Predictions } from './pages/Predictions';
import { Anomalies } from './pages/Anomalies';
import { AI } from './pages/AI';
import { SettingsPage } from './pages/Settings';

export function App() {
  const [activePage, setActivePage] = useState<PageId>('dashboard');

  const renderPage = () => {
    switch (activePage) {
      case 'dashboard':
        return <Dashboard onNavigate={(page) => setActivePage(page)} />;
      case 'expenses':
        return <Expenses />;
      case 'analytics':
        return <Analytics />;
      case 'intelligence':
        return <Intelligence />;
      case 'predictions':
        return <Predictions />;
      case 'anomalies':
        return <Anomalies />;
      case 'ai':
        return <AI />;
      case 'settings':
        return <SettingsPage />;
      default:
        return <Dashboard onNavigate={(page) => setActivePage(page)} />;
    }
  };

  return (
    <DashboardLayout activePage={activePage} onSelectPage={setActivePage}>
      {renderPage()}
    </DashboardLayout>
  );
}

export default App;
