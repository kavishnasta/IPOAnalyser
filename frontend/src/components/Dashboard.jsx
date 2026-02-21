import React, { useState } from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import { motion } from 'framer-motion';
import QueryCard from './QueryCard';
import './Dashboard.css';

function Dashboard({ queries, sectorAverages, onRefresh }) {
  const [selectedQuery, setSelectedQuery] = useState(null);

  const chartData = queries
    .filter(q => q.drhpData?.ofsRatio !== null && q.sentimentData?.vaderScore !== null)
    .map(q => ({
      name: q.companyName,
      symbol: q.symbol,
      ofsRatio: q.drhpData.ofsRatio,
      vaderScore: q.sentimentData.vaderScore,
      riskFlags: q.riskFlags,
      successProbability: q.mlPrediction?.successProbability,
      queryId: q._id
    }));

  const getSectorAverage = (sector) => {
    const avg = sectorAverages.find(s => s.sector === sector);
    return avg || { averageOFSRatio: 0.5, averageSentimentScore: 0 };
  };

  const highRiskQueries = queries.filter(q => 
    q.riskFlags?.exceedsSectorAverage === true
  );

  const getPointColor = (point) => {
    if (point.riskFlags?.exceedsSectorAverage) {
      return '#ff6b6b';
    }
    if (point.riskFlags?.highOFSRatio || point.riskFlags?.highHypeScore) {
      return '#ffa500';
    }
    return '#4ecdc4';
  };

  return (
    <div className="dashboard">
      {highRiskQueries.length > 0 && (
        <motion.div 
          className="warning-banner"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ type: "spring", stiffness: 200 }}
        >
          <h3>⚠️ High Risk Alert</h3>
          <p>
            {highRiskQueries.length} IPO(s) detected with both high OFS ratio and 
            hype score exceeding sector averages. Exercise caution!
          </p>
        </motion.div>
      )}

      <motion.div 
        className="card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <div className="chart-header">
          <h2>📊 Hype vs. Reality Analysis</h2>
          <motion.button 
            onClick={onRefresh} 
            className="refresh-btn"
            whileHover={{ scale: 1.05, rotate: 180 }}
            whileTap={{ scale: 0.95 }}
            transition={{ duration: 0.3 }}
          >
            🔄 Refresh
          </motion.button>
        </div>
        <p className="chart-description">
          Scatter plot comparing OFS Ratio (promoter exit) vs. VADER Sentiment Score (social hype)
        </p>
        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={500}>
            <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.1)" />
              <XAxis 
                type="number" 
                dataKey="ofsRatio" 
                name="OFS Ratio"
                label={{ value: 'OFS Ratio (Promoter Exit)', position: 'insideBottom', offset: -5 }}
                domain={[0, 1]}
                stroke="rgba(255, 255, 255, 0.8)"
                tick={{ fill: 'rgba(255, 255, 255, 0.9)' }}
              />
              <YAxis 
                type="number" 
                dataKey="vaderScore" 
                name="VADER Score"
                label={{ value: 'VADER Sentiment Score', angle: -90, position: 'insideLeft' }}
                domain={[-1, 1]}
                stroke="rgba(255, 255, 255, 0.8)"
                tick={{ fill: 'rgba(255, 255, 255, 0.9)' }}
              />
              <Tooltip 
                cursor={{ strokeDasharray: '3 3' }}
                contentStyle={{
                  background: 'rgba(255, 255, 255, 0.95)',
                  border: 'none',
                  borderRadius: '12px',
                  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
                }}
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    return (
                      <div className="custom-tooltip">
                        <p><strong>{data.name}</strong> ({data.symbol})</p>
                        <p>OFS Ratio: {(data.ofsRatio * 100).toFixed(2)}%</p>
                        <p>Sentiment: {data.vaderScore.toFixed(4)}</p>
                        {data.successProbability && (
                          <p>Success Probability: {(data.successProbability * 100).toFixed(2)}%</p>
                        )}
                        {data.riskFlags?.exceedsSectorAverage && (
                          <p style={{ color: '#ff6b6b', fontWeight: 'bold' }}>⚠️ High Risk</p>
                        )}
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Legend wrapperStyle={{ color: 'rgba(255, 255, 255, 0.9)' }} />
              <Scatter 
                name="IPOs" 
                data={chartData} 
                fill="#8884d8"
                onClick={(data) => {
                  const query = queries.find(q => q._id === data.queryId);
                  setSelectedQuery(query);
                }}
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getPointColor(entry)} />
                ))}
              </Scatter>
            </ScatterChart>
          </ResponsiveContainer>
        ) : (
          <div className="no-data">
            <p>No IPO data available. Query an IPO to see the analysis.</p>
          </div>
        )}
      </motion.div>

      <div className="queries-list">
        <motion.h2 
          className="section-title"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
        >
          📈 Recent IPO Queries
        </motion.h2>
        {queries.length > 0 ? (
          <div className="queries-grid">
            {queries.map((query, index) => (
              <motion.div
                key={query._id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * index }}
              >
                <QueryCard 
                  query={query}
                  sectorAverage={getSectorAverage(query.sector)}
                  onClick={() => setSelectedQuery(query)}
                />
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="no-data">
            <p>No queries yet. Start by analyzing an IPO above.</p>
          </div>
        )}
      </div>

      {selectedQuery && (
        <motion.div 
          className="modal-overlay" 
          onClick={() => setSelectedQuery(null)}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <motion.div 
            className="modal-content" 
            onClick={(e) => e.stopPropagation()}
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
          >
            <button className="close-btn" onClick={() => setSelectedQuery(null)}>×</button>
            <QueryCard 
              query={selectedQuery}
              sectorAverage={getSectorAverage(selectedQuery.sector)}
              expanded={true}
            />
          </motion.div>
        </motion.div>
      )}
    </div>
  );
}

export default Dashboard;
