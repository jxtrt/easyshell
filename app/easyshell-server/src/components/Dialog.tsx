import { validate as validateUUID } from 'uuid';

export function Dialog({ onConnect, remotes, refreshRemotes }: {
  onConnect: (data: { remoteId: string; otpCode: string }) => void;
  remotes?: Array<{ id: string; name: string }>;
  refreshRemotes?: () => void;
}) {

  let onButtonClick = (e: React.MouseEvent) => {
    e.preventDefault();
    const remoteId = (document.getElementById('remoteId') as HTMLSelectElement).value;
    const otpCode = (document.getElementById('otpCode') as HTMLInputElement).value;

    if (!validateUUID(remoteId)) {
      alert('Invalid Remote ID. Please select a valid UUID.');
      return;
    }

    if (!/^\d{6}$/.test(otpCode)) {
      alert('Invalid OTP Code. Please enter a 6-digit number.');
      return;
    }

    onConnect({ remoteId, otpCode });
  };

  const hasRemotes = remotes && remotes.length > 0;

  return (
    <div className="flex items-center justify-center">
      <form className="bg-white p-6 shadow-md max-w-lg">
        <h2 className="text-xl font-semibold mb-4 text">Connect to remote</h2>

        <label htmlFor="remoteId" className="block text-sm font-medium text mb-1">Remote ID</label>
        <div className="flex items-center gap-2 mb-4">
          <select id="remoteId" className="w-full px-3 py-2 border accent-input" disabled={!hasRemotes}>
            {hasRemotes ? (
              remotes.map(remote => (
                <option key={remote.id} value={remote.id}>{remote.id}</option>
              ))
            ) : (
              <option value="">No remotes available</option>
            )}
          </select>
          {refreshRemotes && (
            <button type="button" className="px-3 py-2 accent text-white rounded-md" onClick={refreshRemotes}>Refresh</button>
          )}
        </div>

        <label htmlFor="otpCode" className="block text-sm font-medium text mb-1">OTP Code</label>
        <input type="text" id="otpCode" className="w-full px-3 py-2 border accent-input mb-4" disabled={!hasRemotes} />

        <button type="submit" className="w-full accent text-white py-2 px-4 rounded-md" onClick={onButtonClick} disabled={!hasRemotes}>Connect</button>
      </form>
    </div>
  );
}
