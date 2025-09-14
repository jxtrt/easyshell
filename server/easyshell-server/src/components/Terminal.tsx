import React, { useEffect, useRef, useState } from 'react';
import type { ReactNode } from 'react';

interface TerminalProps {
  children?: ReactNode;
  initialLines?: string[];
}

export function Terminal({ children, initialLines = [] }: TerminalProps) {
  // grab simple string/number children as initial text if provided
  const childrenText = React.Children.toArray(children)
    .filter((c): c is string | number => typeof c === 'string' || typeof c === 'number')
    .map(String);

  const [lines, setLines] = useState<string[]>(() => [...initialLines, ...childrenText]);
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

  useEffect(() => {
    const id = setInterval(() => {
      counterRef.current += 1;
      setLines(prev => [...prev, counterRef.current.toString()]);
    }, 100);
    return () => clearInterval(id);
  }, []);

  let goToBottom = () => {
    const el = containerRef.current;
    if (!el) return;
    el.scrollTop = el.scrollHeight;
    autoScrollRef.current = true;
  }

  return (
    <div className="relative bg-slate-900 border text-white w-[90%] h-[70vh] max-w-[80vw] max-h-[80vh]">
      {/* Scrollable container */}
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
  );
}
