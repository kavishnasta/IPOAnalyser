import React, { useState } from 'react';
import { motion } from 'framer-motion';
import './QueryForm.css';

function QueryForm({ onQuery, loading }) {
  const [formData, setFormData] = useState({
    companyName: '',
    symbol: '',
    sector: '',
    drhpUrl: ''
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await onQuery(formData);
      setFormData({
        companyName: '',
        symbol: '',
        sector: '',
        drhpUrl: ''
      });
    } catch (error) {
      alert('Error querying IPO. Please try again.');
    }
  };

  return (
    <motion.div 
      className="card query-form"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      <motion.h2
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.2 }}
      >
        🔍 Analyze New IPO
      </motion.h2>
      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          <motion.div 
            className="form-group"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <label htmlFor="companyName">
              <span className="label-icon">🏢</span>
              Company Name *
            </label>
            <input
              type="text"
              id="companyName"
              name="companyName"
              value={formData.companyName}
              onChange={handleChange}
              required
              placeholder="e.g., Paytm"
              className="glow-input"
            />
          </motion.div>

          <motion.div 
            className="form-group"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <label htmlFor="symbol">
              <span className="label-icon">📊</span>
              Symbol *
            </label>
            <input
              type="text"
              id="symbol"
              name="symbol"
              value={formData.symbol}
              onChange={handleChange}
              required
              placeholder="e.g., PAYTM"
              className="glow-input"
            />
          </motion.div>

          <motion.div 
            className="form-group"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <label htmlFor="sector">
              <span className="label-icon">🏭</span>
              Sector
            </label>
            <input
              type="text"
              id="sector"
              name="sector"
              value={formData.sector}
              onChange={handleChange}
              placeholder="e.g., FinTech"
              className="glow-input"
            />
          </motion.div>

          <motion.div 
            className="form-group"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            <label htmlFor="drhpUrl">
              <span className="label-icon">📄</span>
              DRHP PDF URL
            </label>
            <input
              type="url"
              id="drhpUrl"
              name="drhpUrl"
              value={formData.drhpUrl}
              onChange={handleChange}
              placeholder="https://example.com/drhp.pdf"
              className="glow-input"
            />
          </motion.div>
        </div>

        <motion.button 
          type="submit" 
          className="submit-btn" 
          disabled={loading}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
        >
          {loading ? (
            <>
              <span className="spinner"></span>
              Analyzing...
            </>
          ) : (
            <>
              <span>🚀</span>
              Analyze IPO
            </>
          )}
        </motion.button>
      </form>
    </motion.div>
  );
}

export default QueryForm;
