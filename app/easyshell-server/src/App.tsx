import React, { useEffect, useRef, useState } from 'react';
import { Frame } from './components/Frame';
import { Terminal } from './components/Terminal';
import { Dialog } from './components/Dialog';

function App() {
  //state: "initial" or "terminal"
  const [state, setState] = React.useState<'initial' | 'terminal'>('initial');

  const [remoteId, setRemoteId] = React.useState('');
  const [mfaCode, setMfaCode] = React.useState('');

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