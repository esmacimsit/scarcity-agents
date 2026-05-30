import React, { useState, useEffect } from 'react';
import './ScenarioSelector.css';

const ScenarioSelector = ({ selectedScenario, onScenarioChange }) => {
  const [manifest, setManifest] = useState(null);
  const [scarcity, setScarcity] = useState('');
  const [agentType, setAgentType] = useState('');
  const [llmType, setLlmType] = useState('');
  const [policy, setPolicy] = useState('');

  // Format display names
  const formatName = (name) => {
    if (name === 'llm') return 'LLM';
    return name.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join('-');
  };

  // Load manifest
  useEffect(() => {
    fetch('/logs/manifest.json')
      .then(res => res.json())
      .then(data => setManifest(data))
      .catch(err => console.error('Error loading manifest:', err));
  }, []);

  // Get unique scarcity levels
  const getScarcityLevels = () => {
    if (!manifest) return [];
    const levels = new Set();
    manifest.available_scenarios.forEach(scenario => {
      if (scenario.startsWith('default_') && !scenario.includes('moderate') && !scenario.includes('scarcity_')) {
        levels.add('default');
      } else if (scenario.startsWith('moderate_scarcity_')) {
        levels.add('moderate_scarcity');
      } else if (scenario.startsWith('scarcity_')) {
        levels.add('scarcity');
      }
    });
    return Array.from(levels).sort();
  };

  // Get agent types for selected scarcity
  const getAgentTypes = () => {
    if (!manifest || !scarcity) return [];
    const types = new Set();
    
    manifest.available_scenarios.forEach(scenario => {
      let matchesScarcity = false;
      if (scarcity === 'default' && scenario.startsWith('default_') && !scenario.includes('moderate') && !scenario.includes('scarcity_')) {
        matchesScarcity = true;
      } else if (scarcity === 'moderate_scarcity' && scenario.startsWith('moderate_scarcity_')) {
        matchesScarcity = true;
      } else if (scarcity === 'scarcity' && scenario.startsWith('scarcity_')) {
        matchesScarcity = true;
      }
      
      if (matchesScarcity) {
        // Extract agent type - only 3 main types
        if (scenario.includes('_random_')) types.add('random');
        if (scenario.includes('_rule_')) types.add('rule-based');
        // LLM includes fine-tuned and few-shot scenarios
        if (scenario.includes('_llm_') || scenario.includes('_finetuned_') || scenario.includes('_few_shot_')) {
          types.add('llm');
        }
      }
    });
    
    return Array.from(types).sort();
  };

  // Get LLM types for LLM agent type
  const getLlmTypes = () => {
    if (!manifest || agentType !== 'llm') return [];
    const types = new Set();
    
    manifest.available_scenarios.forEach(scenario => {
      let matchesScarcity = false;
      if (scarcity === 'default' && scenario.startsWith('default_') && !scenario.includes('moderate') && !scenario.includes('scarcity_')) {
        matchesScarcity = true;
      } else if (scarcity === 'moderate_scarcity' && scenario.startsWith('moderate_scarcity_')) {
        matchesScarcity = true;
      } else if (scarcity === 'scarcity' && scenario.startsWith('scarcity_')) {
        matchesScarcity = true;
      }
      
      if (matchesScarcity) {
        if (scenario.includes('_finetuned_')) types.add('fine-tuned');
        if (scenario.includes('_few_shot_')) types.add('few-shot');
        if (scenario.includes('_zero_shot_')) types.add('zero-shot');
      }
    });
    
    return Array.from(types).sort();
  };

  // Get policies for current selection
  const getPolicies = () => {
    if (!manifest || !scarcity || !agentType) return [];
    
    // If LLM is selected but no LLM subtype chosen, return empty
    if (agentType === 'llm' && !llmType) return [];
    
    const policies = new Set();
    manifest.available_scenarios.forEach(scenario => {
      let matchesScarcity = false;
      let matchesType = false;
      
      // Check scarcity
      if (scarcity === 'default' && scenario.startsWith('default_') && !scenario.includes('moderate') && !scenario.includes('scarcity_')) {
        matchesScarcity = true;
      } else if (scarcity === 'moderate_scarcity' && scenario.startsWith('moderate_scarcity_')) {
        matchesScarcity = true;
      } else if (scarcity === 'scarcity' && scenario.startsWith('scarcity_')) {
        matchesScarcity = true;
      }
      
      // Check agent type
      if (agentType === 'random' && scenario.includes('_random_')) {
        matchesType = true;
      } else if (agentType === 'rule-based' && scenario.includes('_rule_')) {
        matchesType = true;
      } else if (agentType === 'llm' && llmType) {
        if (llmType === 'fine-tuned' && scenario.includes('_finetuned_')) matchesType = true;
        if (llmType === 'few-shot' && scenario.includes('_few_shot_')) matchesType = true;
        if (llmType === 'zero-shot' && scenario.includes('_zero_shot_')) matchesType = true;
      }
      
      if (matchesScarcity && matchesType) {
        if (scenario.includes('_social_welfare_')) policies.add('social_welfare');
        if (scenario.includes('_survival_')) policies.add('survival');
        if (scenario.includes('_wealth_maximizing_')) policies.add('wealth_maximizing');
      }
    });
    
    return Array.from(policies).sort();
  };

  // Find and select scenario based on all filters
  useEffect(() => {
    if (!manifest || !scarcity || !agentType || !policy) return;

    let typeForFilename = agentType.replace('-', '_');
    let methodForFilename = '';
    
    if (agentType === 'llm' && llmType) {
      // LLM methods: "llm" + "_{policy}_{method}"
      // Fine-tuned uses old format without "llm": "finetuned_{policy}"
      // Few-shot and zero-shot use new format: "llm_{policy}_{method}"
      if (llmType === 'fine-tuned') {
        typeForFilename = 'finetuned';
      } else {
        typeForFilename = 'llm';
        methodForFilename = `_${llmType.replace('-', '_')}`;
      }
    }

    // Convert dash to underscore for filename
    const policyForFilename = policy.replace('-', '_');

    // Build scenario name
    let scenario = '';
    
    if (scarcity === 'default') {
      scenario = `default_${typeForFilename}_${policyForFilename}${methodForFilename}_seed_1`;
    } else if (scarcity === 'moderate_scarcity') {
      scenario = `moderate_scarcity_${typeForFilename}_${policyForFilename}${methodForFilename}_seed_1`;
    } else if (scarcity === 'scarcity') {
      scenario = `scarcity_${typeForFilename}_${policyForFilename}${methodForFilename}_seed_1`;
    }

    // Check if scenario exists
    if (manifest.available_scenarios.includes(scenario)) {
      onScenarioChange(scenario);
    }
  }, [scarcity, agentType, llmType, policy, manifest, onScenarioChange]);

  // Reset dependent selections
  useEffect(() => {
    setAgentType('');
    setLlmType('');
    setPolicy('');
  }, [scarcity]);

  useEffect(() => {
    setLlmType('');
    setPolicy('');
  }, [agentType]);

  useEffect(() => {
    setPolicy('');
  }, [llmType]);

  if (!manifest) {
    return <div className="scenario-selector">Loading...</div>;
  }

  const scarcityLevels = getScarcityLevels();
  const agentTypes = getAgentTypes();
  const llmTypes = getLlmTypes();
  const policies = getPolicies();

  return (
    <div className="scenario-selector-container">
      <div className="selector-group">
        <label>Scarcity Level</label>
        <select value={scarcity} onChange={(e) => setScarcity(e.target.value)} className="selector-dropdown">
          <option value="">-- Select --</option>
          {scarcityLevels.map(level => (
            <option key={level} value={level}>
              {level === 'default' ? 'No Scarcity' : level === 'moderate_scarcity' ? 'Moderate Scarcity' : 'High Scarcity'}
            </option>
          ))}
        </select>
      </div>

      <div className="selector-group">
        <label>Agent Type</label>
        <select value={agentType} onChange={(e) => setAgentType(e.target.value)} className="selector-dropdown" disabled={!scarcity}>
          <option value="">-- Select --</option>
          {agentTypes.map(type => (
            <option key={type} value={type}>
              {formatName(type)}
            </option>
          ))}
        </select>
      </div>

      {agentType === 'llm' && (
        <div className="selector-group">
          <label>LLM Type</label>
          <select value={llmType} onChange={(e) => setLlmType(e.target.value)} className="selector-dropdown">
            <option value="">-- Select --</option>
            {llmTypes.map(type => (
              <option key={type} value={type}>
                {formatName(type)}
              </option>
            ))}
          </select>
        </div>
      )}

      <div className="selector-group">
        <label>Policy</label>
        <select value={policy} onChange={(e) => setPolicy(e.target.value)} className="selector-dropdown" disabled={!agentType || (agentType === 'llm' && !llmType)}>
          <option value="">-- Select --</option>
          {policies.map(pol => (
            <option key={pol} value={pol}>
              {pol.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
            </option>
          ))}
        </select>
      </div>

      <div className="selection-status">
        {selectedScenario && <span>📍 {selectedScenario.replace(/^default_/, '')}</span>}
      </div>
    </div>
  );
};

export default ScenarioSelector;
