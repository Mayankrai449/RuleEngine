import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './CombineRulesForm.css';

const CombineRulesForm = () => {
  const [rules, setRules] = useState([]);
  const [combinedName, setCombinedName] = useState('');
  const [operator, setOperator] = useState('AND');
  const [selectedRules, setSelectedRules] = useState([]);
  const [ruleStrings, setRuleStrings] = useState({});
  const [error, setError] = useState(null);

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
  
    try {
      await api.post('/rules/combine_rules/', {
        name: combinedName,
        operator,
        rule_ids: selectedRules,
      });
      alert('Rules combined successfully');
      setCombinedName('');
      setOperator('AND');
      setSelectedRules([]);
    } catch (err) {
      setError('Failed to combine rules.');
    }
  };

  const handleAddRule = () => {
    setSelectedRules([...selectedRules, '']);
  };

  const handleRuleChange = async (index, ruleId) => {
    const newRules = [...selectedRules];
    newRules[index] = ruleId;
    setSelectedRules(newRules);
  
    if (ruleId) {
      try {
        const response = await api.get(`/rules/${ruleId}/`);
        setRuleStrings((prevStrings) => ({
          ...prevStrings,
          [index]: response.data.rule_string,
        }));
      } catch (err) {
        setError('Failed to load rule details.');
      }
    } else {
      setRuleStrings((prevStrings) => ({
        ...prevStrings,
        [index]: '',
      }));
    }
  };

  return (
    <div className="form-container">
      <h3>Combine Rules</h3>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={combinedName}
          placeholder="Combined Rule Name"
          onChange={(e) => setCombinedName(e.target.value)}
        />
        <select value={operator} onChange={(e) => setOperator(e.target.value)}>
          <option value="AND">AND</option>
          <option value="OR">OR</option>
        </select>
        {selectedRules.map((ruleId, index) => (
          <div key={index}>
            <select value={ruleId} onChange={(e) => handleRuleChange(index, e.target.value)}>
              <option value="">Select Rule</option>
              {rules.map((rule) => (
                <option key={rule.id} value={rule.id}>{rule.name}</option>
              ))}
            </select>
            {ruleStrings[index] && <p className="rule-string">{ruleStrings[index]}</p>}
          </div>
        ))}
        <button type="button" onClick={handleAddRule}>Add Rule</button>
        <button type="submit">Combine Rules</button>
        {error && <p className="error">{error}</p>}
      </form>
    </div>
  );
};

export default CombineRulesForm;
