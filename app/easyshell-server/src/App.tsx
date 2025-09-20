import React, { useEffect, useRef, useState } from 'react';
import { Frame } from './components/Frame';
import { Terminal } from './components/Terminal';
import { Dialog } from './components/Dialog';

function App() {
  //state: "initial" or "terminal"
  const [state, setState] = React.useState<'initial' | 'terminal'>('initial');

  const [remoteId, setRemoteId] = React.useState('');
  const [mfaCode, setMfaCode] = React.useState('');
  const [remotes, setRemotes] = React.useState<Array<{ id: string; name: string }>>([]);

  const refreshRemotes = async () => {
    let host = import.meta.env.VITE_SERVER_HOST || 'localhost';
    let port = import.meta.env.VITE_SERVER_PORT || '3000';
    
    console.log(`Fetching devices from http://${host}:${port}/devices`);

    try {
      const response = await fetch(`http://${host}:${port}/devices`);
      const data = await response.json();
      setRemotes(data.devices);
    } catch (error) {
    }
  };

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

  useEffect(() => {
    refreshRemotes();
  }, []);

  return (
    <Frame>
      {state === 'initial' ? (
        <Dialog onConnect={onConnect} remotes={remotes} refreshRemotes={refreshRemotes}/>
      ) : (
        <Terminal remoteId={remoteId} onDisconnect={onDisconnect}/>
      )}
    </Frame>
  );
}

export default App;