import React from 'react';
import CreateRuleForm from './components/CreateRuleForm';
import EvaluateRuleForm from './components/EvaluateRuleForm';
import CombineRulesForm from './components/CombineRulesForm';
import './App.css';

function App() {
  return (
    <div className="App">
      <h1>Rule Engine</h1>
      <CreateRuleForm />
      <EvaluateRuleForm />
      <CombineRulesForm />
    </div>
  );
}

export default App;
