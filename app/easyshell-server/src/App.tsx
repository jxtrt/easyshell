import React, { useEffect, useRef, useState } from 'react';
import { Frame } from './components/Frame';
import { Terminal } from './components/Terminal';
import { Dialog } from './components/Dialog';

function App() {
  //state: "initial" or "terminal"
  const [state, setState] = React.useState<'initial' | 'terminal'>('initial');

  const [remoteId, setRemoteId] = React.useState('');
  const [mfaCode, setMfaCode] = React.useState('');

  useEffect(() => {
    const fetchDevices = async () => {
      let host = import.meta.env.VITE_SERVER_HOST || 'localhost';
      let port = import.meta.env.VITE_SERVER_PORT || '3000';
      
      console.log(`Fetching devices from http://${host}:${port}/devices`);

      try {
        const response = await fetch(`http://${host}:${port}/devices`);
        const data = await response.json();
        console.log('Devices:', data.devices);
      } catch (error) {
        console.error('Error fetching devices:', error);
      }
    };

    const interval = setInterval(fetchDevices, 5000);
    return () => clearInterval(interval);
  }, []);

  let onConnect = ({ remoteId, mfaCode }: { remoteId: string; mfaCode: string }) => {
    setRemoteId(remoteId);
    setMfaCode(mfaCode);
    
    setState('terminal');
  };

  let onDisconnect = () => {
    setState('initial');
    setRemoteId('');
    setMfaCode('');
  }

  return (
    <Frame>
      {state === 'initial' ? (
        <Dialog onConnect={onConnect}/>
      ) : (
        <Terminal remoteId={remoteId} onDisconnect={onDisconnect}/>
      )}
    </Frame>
  );
}

export default App;