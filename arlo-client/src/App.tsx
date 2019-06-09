import React from 'react';

import { RootContainer } from './component/RootContainer';
import rootSaga from './saga/root';
import { sagaMiddleware, store } from './store';

import './screen.css'

const App: React.FC = () => {
  sagaMiddleware.run(rootSaga);
  
  return (
    <RootContainer store={ store } />
  );
}

export default App;
