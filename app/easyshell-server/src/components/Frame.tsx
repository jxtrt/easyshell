import type { ReactNode } from 'react';
import terminal from '/terminal.svg';

interface FrameProps {
  children?: ReactNode;
}

export function Frame({ children }: FrameProps) {
    return (
      <div className="frame min-h-screen w-full flex flex-col p-0 box-border bg-gray-100">
        {/* Sticky top bar */}
        <div className="flex items-center space-x-2 p-3 frame-top-row sticky top-0 z-10 bg-white">
          <img src={terminal} alt="terminal icon" />
          <h1 className="text-xl font-semibold text">Easyshell</h1>
        </div>
  
        <div className="flex flex-1 items-center justify-center">
          {children}
        </div>
      </div>
    );
  }