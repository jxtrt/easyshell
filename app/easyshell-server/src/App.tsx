import { useEffect, useRef, useState } from 'react';
import { Frame } from './components/Frame';
import { Terminal } from './components/Terminal';
import { Dialog } from './components/Dialog';

function App() {
  //state: "initial" or "terminal"
  const [state, setState] = useState<'initial' | 'terminal'>('initial');
  const [remoteId, setRemoteId] = useState('');
  const [OTPCode, setOTPCode] = useState('');
  const [remotes, setRemotes] = useState<Array<{ id: string; name: string }>>([]);
  const [terminalLines, setTerminalLines] = useState<string[]>([]);

  // WebSocket reference
  const websocketRef = useRef<WebSocket | null>(null);

  //create a clientId (uuid) on app startup.
  const clientIdRef = useRef<string>('');
  if (!clientIdRef.current) {
    clientIdRef.current = crypto.randomUUID();
  }
  const clientId = clientIdRef.current;

  const host = import.meta.env.VITE_SERVER_HOST || 'localhost';
  const port = import.meta.env.VITE_SERVER_PORT || '3000';

  const refreshRemotes = async () => {    
    console.log(`Fetching devices from http://${host}:${port}/devices`);

    try {
      const response = await fetch(`http://${host}:${port}/devices`);
      const data = await response.json();
      setRemotes(data.devices);
    } catch (error) {
    }
  };

  let onConnect = async ({ remoteId, otpCode }: { remoteId: string; otpCode: string }) => {
    // POST request to /session with { clientId, remoteId, authType="otp", otpCode }
    setRemoteId(remoteId);
    setOTPCode(otpCode);

    let response = await fetch(`http://${host}:${port}/session`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        client_id: clientId,
        remote_id: remoteId,
        auth_type: 'otp',
        auth_value: otpCode,
      }),
    });
    
    console.log('Session request response status:', response.status);
    if (!response.ok) {
      let errorData = await response.json();
      alert(`Failed to create session: ${errorData.error || response.statusText}`);
      return;
    }

    const { websocket_url } = await response.json();
    const websocket = new WebSocket(websocket_url);
    websocketRef.current = websocket;

    websocket.onmessage = (event) => {
      setTerminalLines((prevLines) => [...prevLines, event.data]);
    };

    websocket.onclose = () => {
      console.log('WebSocket connection closed.');
      onDisconnect();
    };

    setState('terminal');
  };

  let onDisconnect = () => {
    setState('initial');
    setRemoteId('');
    setOTPCode('');
    setTerminalLines([]);

    if (websocketRef.current) {
      websocketRef.current.close();
      websocketRef.current = null;
    }
  };

  useEffect(() => {
    refreshRemotes();
  }, []);

  return (
    <Frame>
      {state === 'initial' ? (
        <Dialog onConnect={onConnect} remotes={remotes} refreshRemotes={refreshRemotes}/>
      ) : (
        <Terminal remoteId={remoteId} onDisconnect={onDisconnect} lines={terminalLines} />
      )}
    </Frame>
  );
}

export default App;