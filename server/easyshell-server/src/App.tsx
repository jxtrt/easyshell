import { Frame } from './components/Frame';
import { Terminal } from './components/Terminal';

function App() {
  return (
    <Frame>
      <Terminal initialLines={['Welcome to Easyshell']}></Terminal>
    </Frame>
  );
}

export default App;
