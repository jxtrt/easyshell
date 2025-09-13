

import type { ReactNode } from 'react';
import terminal from '/terminal.svg'

interface FrameProps {
    children?: ReactNode;
}

export function Frame({ children }: FrameProps) {
    return (
        <div className="frame h-screen w-screen flex flex-col border border-red-200">
            <div className="flex items-center space-x-2 p-3 frame-top-row">
                <img src={terminal} alt="terminal icon" />
                <h1 className="text-xl font-semibold">Easyshell</h1>
            </div>
            <div className="flex-1 p-4 overflow-auto">
                {children}
            </div>
        </div>
    )
}