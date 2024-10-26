import React, { useState } from 'react';
import api from '../services/api';
import './CreateRuleForm.css';

const CreateRuleForm = () => {
  const [name, setName] = useState('');
  const [ruleString, setRuleString] = useState('');
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    try {
      const response = await api.post('/rules/create_rule/', { name, rule_string: ruleString });
      alert(`Rule Created: ${response.data.id}`);
      setName('');
      setRuleString('');
    } catch (err) {
      setError('Invalid rule syntax. Please check your input.');
    }
  };

  return (
    <div className="form-container">
      <h3>Create Rule</h3>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={name}
          placeholder="Rule Name"
          onChange={(e) => setName(e.target.value)}
        />
        <textarea
          value={ruleString}
          placeholder="Enter rule string (e.g., (age > 30 AND department = 'Sales'))"
          onChange={(e) => setRuleString(e.target.value)}
        />
        <button type="submit">Create Rule</button>
        {error && <p className="error">{error}</p>}
      </form>
    </div>
  );
};

export default CreateRuleForm;
