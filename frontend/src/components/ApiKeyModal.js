import React, { useState, useEffect } from 'react';
import './ApiKeyModal.css';
import { getKieApiKey, updateKieApiKey } from '../services/api';

function ApiKeyModal({ onClose }) {
  const [apiKey, setApiKey] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Load current API key on mount
  useEffect(() => {
    const loadApiKey = async () => {
      try {
        const data = await getKieApiKey();
        if (data.api_key) {
          setApiKey(data.api_key);
        }
      } catch (error) {
        console.error('Failed to load API key:', error);
      } finally {
        setLoading(false);
      }
    };

    loadApiKey();
  }, []);

  const handleSave = async () => {
    if (apiKey.trim()) {
      setSaving(true);
      try {
        await updateKieApiKey(apiKey.trim());
        alert('API Key saved successfully to .env file!');
        onClose();
      } catch (error) {
        console.error('Failed to save API key:', error);
        alert('Failed to save API key: ' + error.message);
      } finally {
        setSaving(false);
      }
    } else {
      alert('Please enter a valid API key');
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>API Key Settings</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          <label>
            Kie.ai API Key
            <input
              type="text"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="Enter your Kie.ai API key"
              autoFocus
              disabled={loading}
            />
          </label>
          <p className="modal-hint">
            Get your API key from <a href="https://kie.ai" target="_blank" rel="noopener noreferrer">kie.ai</a>
          </p>
        </div>

        <div className="modal-footer">
          <button className="modal-btn modal-btn-cancel" onClick={onClose} disabled={saving}>
            Cancel
          </button>
          <button className="modal-btn modal-btn-save" onClick={handleSave} disabled={loading || saving}>
            {saving ? 'Saving...' : 'Save to .env'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ApiKeyModal;
