// src/App.js
import React, { useState } from 'react';
import './App.css';
import ApplianceUpload from './components/ApplianceUpload';
import ApplianceInfo from './components/ApplianceInfo';

const App = () => {
  const [activeTab, setActiveTab] = useState('upload');

  return (
    <div className="App">
      <div className="tabs">
        <button className={activeTab === 'upload' ? 'active' : ''} onClick={() => setActiveTab('upload')}>
          Upload
        </button>
        <button className={activeTab === 'info' ? 'active' : ''} onClick={() => setActiveTab('info')}>
          Appliance Info
        </button>
      </div>
      {activeTab === 'upload' ? <ApplianceUpload /> : <ApplianceInfo />}
    </div>
  );
};

export default App;
