# IPO Sentiment Analyzer

## Installation

**Backend:**
```bash
cd backend
pip install -r requirements.txt
pip install -r python/requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

## Supabase Setup

1. Go to https://supabase.com
2. Create free account and project
3. Copy Project URL and anon key
4. Create `.env` file in `backend/` folder:
```
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
PORT=5000
```
5. Run SQL script in Supabase SQL Editor (see SQL below)

## Running

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

- Backend: http://localhost:5000
- Frontend: http://localhost:3000

## SQL Script for Supabase

Run this in Supabase SQL Editor:

```sql
CREATE TABLE IF NOT EXISTS ipos (
  id BIGSERIAL PRIMARY KEY,
  company_name VARCHAR(255) NOT NULL,
  symbol VARCHAR(50) UNIQUE NOT NULL,
  issue_date TIMESTAMP NOT NULL,
  issue_size DECIMAL(15, 2) NOT NULL,
  qib_subscription DECIMAL(10, 2) NOT NULL,
  hni_subscription DECIMAL(10, 2) NOT NULL,
  retail_subscription DECIMAL(10, 2) NOT NULL,
  pe_ratio DECIMAL(10, 2) NOT NULL,
  ofs_percentage DECIMAL(5, 4) NOT NULL,
  gmp_listing_day DECIMAL(10, 2) DEFAULT 0,
  positive_listing_gain BOOLEAN NOT NULL,
  listing_gain_percentage DECIMAL(10, 2) DEFAULT 0,
  sector VARCHAR(100),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS live_queries (
  id BIGSERIAL PRIMARY KEY,
  company_name VARCHAR(255) NOT NULL,
  symbol VARCHAR(50) NOT NULL,
  sector VARCHAR(100),
  query_date TIMESTAMP DEFAULT NOW(),
  drhp_data JSONB,
  sentiment_data JSONB,
  ml_prediction JSONB,
  risk_flags JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sector_averages (
  id BIGSERIAL PRIMARY KEY,
  sector VARCHAR(100) UNIQUE NOT NULL,
  average_ofs_ratio DECIMAL(5, 4) NOT NULL,
  average_sentiment_score DECIMAL(10, 4) NOT NULL,
  last_updated TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ipos_symbol ON ipos(symbol);
CREATE INDEX IF NOT EXISTS idx_live_queries_symbol ON live_queries(symbol);
CREATE INDEX IF NOT EXISTS idx_sector_averages_sector ON sector_averages(sector);
```
