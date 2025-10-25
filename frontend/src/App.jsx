
import React, {useEffect, useState} from 'react';
import UploadPage from './pages/UploadPage';
import ReportPage from './pages/ReportPage';

export default function App(){
  const [config, setConfig] = useState({API_BASE: 'http://localhost:8000'});
  useEffect(()=>{
    fetch('/config.json').then(r=>r.json()).then(setConfig).catch(()=>{});
  },[]);
  return (
    <div style={{fontFamily:'sans-serif',padding:24}}>
      <h1>AI Dermatologist Assistant (Frontend scaffold)</h1>
      <p>Connected backend: {config.API_BASE}</p>
      <UploadPage apiBase={config.API_BASE}/>
      <hr/>
      <ReportPage />
    </div>
  );
}
