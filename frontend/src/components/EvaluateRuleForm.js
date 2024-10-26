import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './EvaluateRuleForm.css';

const EvaluateRuleForm = () => {
  const [rules, setRules] = useState([]);
  const [selectedRuleId, setSelectedRuleId] = useState('');
  const [ruleString, setRuleString] = useState('');
  const [data, setData] = useState({});
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  useEffect(() => {
    const fetchRules = async () => {
      try {
        const response = await api.get('/rules/get/');
        setRules(response.data);
      } catch (err) {
        setError('Failed to load rules.');
      }
    };
  
    fetchRules();

    const intervalId = setInterval(fetchRules, 1000);

    return () => clearInterval(intervalId);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setResult(null);

    try {
      const response = await api.post('/rules/evaluate_rule/', { rule_id: selectedRuleId, data });
      setResult(response.data.result ? 'User eligible' : 'User not eligible');
    } catch (err) {
      setError('Evaluation failed. Check data input.');
    }
  };

  const handleDataChange = (e) => {
    const { name, value } = e.target;
    setData((prevData) => ({ ...prevData, [name]: value }));
  };

  const handleRuleChange = async (ruleId) => {
    setSelectedRuleId(ruleId);
    if (ruleId) {
      try {
        const response = await api.get(`/rules/${ruleId}/`);
        setRuleString(response.data.rule_string);
      } catch (err) {
        setError('Failed to load rule details.');
      }
    } else {
      setRuleString('');
    }
  };

  
  return (
    <div className="form-container">
      <h3>Evaluate Rule</h3>
      <form onSubmit={handleSubmit}>
      <select value={selectedRuleId} onChange={(e) => handleRuleChange(e.target.value)}>
          <option value="">Select Rule</option>
          {rules.map((rule) => (
            <option key={rule.id} value={rule.id}>{rule.name}</option>
          ))}
        </select>
        {ruleString && <p className="rule-string">{ruleString}</p>}
        {selectedRuleId && (
          <>
            <input type="number" name="age" placeholder="Age" onChange={handleDataChange} />
            <input type="text" name="department" placeholder="Department" onChange={handleDataChange} />
            <input type="number" name="salary" placeholder="Salary" onChange={handleDataChange} />
            <input type="number" name="experience" placeholder="Experience" onChange={handleDataChange} />
          </>
        )}
        <button type="submit">Evaluate</button>
        {result && <p className="result">{result}</p>}
        {error && <p className="error">{error}</p>}
      </form>
    </div>
  );
};

export default EvaluateRuleForm;
