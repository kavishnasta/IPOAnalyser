import React from 'react';
import { motion } from 'framer-motion';
import './QueryCard.css';

function QueryCard({ query, sectorAverage, onClick, expanded }) {
  const { companyName, symbol, sector, drhpData, sentimentData, mlPrediction, riskFlags, queryDate } = query;

  const formatDate = (date) => {
    return new Date(date).toLocaleString();
  };

  const getRiskLevel = () => {
    if (riskFlags?.exceedsSectorAverage) return 'high';
    if (riskFlags?.highOFSRatio || riskFlags?.highHypeScore) return 'medium';
    return 'low';
  };

  const riskLevel = getRiskLevel();

  return (
    <motion.div 
      className={`query-card ${riskLevel}-risk ${expanded ? 'expanded' : ''}`} 
      onClick={onClick}
      whileHover={{ scale: expanded ? 1 : 1.02, y: expanded ? 0 : -4 }}
      transition={{ duration: 0.2 }}
    >
      <div className="card-header">
        <h3>{companyName}</h3>
        <span className="symbol">{symbol}</span>
        {riskFlags?.exceedsSectorAverage && (
          <motion.span 
            className="risk-badge high"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 200 }}
          >
            ⚠️ HIGH RISK
          </motion.span>
        )}
      </div>

      <div className="card-body">
        <div className="info-section">
          <div className="info-item">
            <span className="label">🏭 Sector:</span>
            <span className="value">{sector || 'N/A'}</span>
          </div>
          <div className="info-item">
            <span className="label">📅 Query Date:</span>
            <span className="value">{formatDate(queryDate)}</span>
          </div>
        </div>

        {drhpData && (
          <motion.div 
            className="data-section"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
          >
            <h4>📄 DRHP Analysis</h4>
            <div className="metrics-grid">
              <div className="metric">
                <span className="metric-label">OFS Ratio</span>
                <span className="metric-value">
                  {(drhpData.ofsRatio * 100).toFixed(2)}%
                </span>
                {sectorAverage && (
                  <span className="metric-comparison">
                    Sector Avg: {(sectorAverage.averageOFSRatio * 100).toFixed(2)}%
                    {riskFlags?.highOFSRatio && ' ⚠️'}
                  </span>
                )}
              </div>
              <div className="metric">
                <span className="metric-label">Fresh Issue</span>
                <span className="metric-value">
                  ₹{drhpData.freshIssue?.toFixed(2) || 0} Cr
                </span>
              </div>
              <div className="metric">
                <span className="metric-label">Total Issue Size</span>
                <span className="metric-value">
                  ₹{drhpData.totalIssueSize?.toFixed(2) || 0} Cr
                </span>
              </div>
            </div>
          </motion.div>
        )}

        {sentimentData && (
          <motion.div 
            className="data-section"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <h4>💬 Sentiment Analysis</h4>
            <div className="metrics-grid">
              <div className="metric">
                <span className="metric-label">VADER Score</span>
                <span className="metric-value">
                  {sentimentData.vaderScore?.toFixed(4) || 0}
                </span>
                {sectorAverage && (
                  <span className="metric-comparison">
                    Sector Avg: {sectorAverage.averageSentimentScore.toFixed(4)}
                    {riskFlags?.highHypeScore && ' ⚠️'}
                  </span>
                )}
              </div>
              <div className="metric">
                <span className="metric-label">Reddit Mentions</span>
                <span className="metric-value">{sentimentData.redditMentions || 0}</span>
              </div>
              <div className="metric">
                <span className="metric-label">News Headlines</span>
                <span className="metric-value">{sentimentData.newsHeadlines || 0}</span>
              </div>
            </div>
          </motion.div>
        )}

        {mlPrediction && (
          <motion.div 
            className="data-section"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            <h4>🤖 ML Prediction</h4>
            <div className="metrics-grid">
              <div className="metric">
                <span className="metric-label">Success Probability</span>
                <span className="metric-value success">
                  {(mlPrediction.successProbability * 100).toFixed(2)}%
                </span>
              </div>
              <div className="metric">
                <span className="metric-label">Risk Score</span>
                <span className="metric-value risk">
                  {(mlPrediction.riskScore * 100).toFixed(2)}%
                </span>
              </div>
            </div>
          </motion.div>
        )}

        {expanded && (
          <motion.div 
            className="risk-flags"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <h4>⚠️ Risk Assessment</h4>
            <ul>
              <li className={riskFlags?.highOFSRatio ? 'flag-active' : ''}>
                High OFS Ratio: {riskFlags?.highOFSRatio ? 'Yes ⚠️' : 'No ✓'}
              </li>
              <li className={riskFlags?.highHypeScore ? 'flag-active' : ''}>
                High Hype Score: {riskFlags?.highHypeScore ? 'Yes ⚠️' : 'No ✓'}
              </li>
              <li className={riskFlags?.exceedsSectorAverage ? 'flag-active' : ''}>
                Exceeds Sector Average: {riskFlags?.exceedsSectorAverage ? 'Yes ⚠️' : 'No ✓'}
              </li>
            </ul>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}

export default QueryCard;
