import { useEffect, useRef, useState } from 'react';

interface TerminalProps {
  initialLines?: string[];
  remoteId?: string;
  onDisconnect?: () => void;
}

export function Terminal({ initialLines = [], remoteId, onDisconnect}: TerminalProps) {
  const [lines, setLines] = useState<string[]>(() => [...initialLines]);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const autoScrollRef = useRef(true);
  const counterRef = useRef(0);

  // track whether the user is at the bottom; if they are, new lines auto-scroll.
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const onScroll = () => {
      autoScrollRef.current = el.scrollHeight - (el.scrollTop + el.clientHeight) < 20;
    };
    el.addEventListener('scroll', onScroll);
    onScroll();
    return () => el.removeEventListener('scroll', onScroll);
  }, []);

  // scroll-to-bottom when lines change, but only if the user was already at the bottom
  useEffect(() => {
    if (autoScrollRef.current) {
      const el = containerRef.current;
      if (!el) return;
      el.scrollTop = el.scrollHeight;
    }
  }, [lines]);

  let goToBottom = () => {
    const el = containerRef.current;
    if (!el) return;
    el.scrollTop = el.scrollHeight;
    autoScrollRef.current = true;
  }

  return (
    <div className="flex flex-col items-center w-[90%] h-[70vh] max-w-[80vw] max-h-[80vh]">
      <div className="flex flex-row justify-left w-full mb-2 gap-2">
        <p>Connected to {remoteId}.</p>
        <div className="link" onClick={() => onDisconnect && onDisconnect()}>Disconnect</div>
      </div>
      <div className="relative background text-white w-[100%] h-[100%] max-w-[80vw] max-h-[80vh] p-2 rounded-md shadow-md">
        
        <div
          ref={containerRef}
          className="overflow-y-auto w-full h-full"
        >
          <div>
            {lines.map((line, i) => (
              <div key={i} className="whitespace-pre-wrap border-t border-slate-800 p-1">
                {line}
              </div>
            ))}
          </div>
        </div>
    
        {/* Scroll to bottom button */}
        {!autoScrollRef.current && (
          <button
            className="absolute bottom-4 right-4 bg-slate-700 text-white px-3 py-1 rounded hover:bg-slate-600"
            onClick={goToBottom}
          >
            Scroll to bottom
          </button>
        )}
      </div>
    </div>
  );
}
