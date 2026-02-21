import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import Dashboard from './components/Dashboard';
import QueryForm from './components/QueryForm';
import './App.css';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

function App() {
  const [queries, setQueries] = useState([]);
  const [sectorAverages, setSectorAverages] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchQueries();
    fetchSectorAverages();
  }, []);

  const fetchQueries = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/ipo/queries`);
      setQueries(response.data);
    } catch (error) {
      console.error('Error fetching queries:', error);
    }
  };

  const fetchSectorAverages = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/ipo/sector-averages`);
      setSectorAverages(response.data);
    } catch (error) {
      console.error('Error fetching sector averages:', error);
    }
  };

  const handleQuery = async (queryData) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/ipo/query`, queryData);
      await fetchQueries();
      return response.data;
    } catch (error) {
      console.error('Error querying IPO:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <motion.header 
        className="App-header"
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
        >
          <h1 className="title-main">IPO Sentiment Analyzer</h1>
        </motion.div>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="subtitle"
        >
          Protect Your Investments from Hype-Driven Overvaluation
        </motion.p>
        <motion.div
          className="header-decoration"
          initial={{ width: 0 }}
          animate={{ width: "200px" }}
          transition={{ delay: 0.6, duration: 0.8 }}
        />
      </motion.header>

      <main className="App-main">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <QueryForm onQuery={handleQuery} loading={loading} />
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Dashboard 
            queries={queries} 
            sectorAverages={sectorAverages}
            onRefresh={fetchQueries}
          />
        </motion.div>
      </main>
    </div>
  );
}

export default App;
