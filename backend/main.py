from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import subprocess
import json
from pathlib import Path
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app)

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_ANON_KEY')

supabase: Client = None
if supabase_url and supabase_key:
    supabase = create_client(supabase_url, supabase_key)
    print('✅ Supabase connected')
else:
    print('⚠️  Supabase not configured')

def execute_python_script(script_name, args=None):
    try:
        script_path = Path(__file__).parent / 'python' / script_name
        cmd = ['python', str(script_path)]
        if args:
            cmd.extend(args)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception as e:
        print(f'Python script error: {e}')
        return None

@app.route('/api/health', methods=['GET'])
def health():
    db_status = 'connected' if supabase else 'disconnected'
    return jsonify({
        'status': 'ok',
        'message': 'IPO Screener API is running',
        'database': db_status
    })

@app.route('/api/ipo/query', methods=['POST'])
def query_ipo():
    if not supabase:
        return jsonify({'error': 'Database not connected'}), 503
    
    data = request.json
    company_name = data.get('companyName')
    symbol = data.get('symbol')
    sector = data.get('sector', 'General')
    drhp_url = data.get('drhpUrl', '')
    
    if not company_name or not symbol:
        return jsonify({'error': 'Company name and symbol are required'}), 400
    
    try:
        existing = supabase.table('live_queries').select('*').eq('symbol', symbol).order('query_date', desc=True).limit(1).execute()
        if existing.data and len(existing.data) > 0:
            existing_query = existing.data[0]
            query_date_str = existing_query['query_date']
            if isinstance(query_date_str, str):
                query_date = datetime.fromisoformat(query_date_str.replace('Z', '+00:00'))
            else:
                query_date = query_date_str
            if (datetime.now().timestamp() - query_date.timestamp()) < 3600:
                return format_query_response(existing_query)
        
        query_data = {
            'company_name': company_name,
            'symbol': symbol,
            'sector': sector,
            'drhp_data': {},
            'sentiment_data': {},
            'ml_prediction': {},
            'risk_flags': {}
        }
        
        drhp_result = execute_python_script('module_b.py', [drhp_url])
        if drhp_result:
            drhp = json.loads(drhp_result)
            query_data['drhp_data'] = {
                'ofsRatio': drhp.get('ofsRatio', 0.5),
                'freshIssue': drhp.get('freshIssue', 0),
                'totalIssueSize': drhp.get('totalIssueSize', 0),
                'extractedAt': datetime.now().isoformat(),
                'pdfSource': drhp.get('pdfSource')
            }
        
        sentiment_result = execute_python_script('module_c.py', [company_name])
        if sentiment_result:
            sentiment = json.loads(sentiment_result)
            query_data['sentiment_data'] = {
                'vaderScore': sentiment.get('vaderScore', 0),
                'redditMentions': sentiment.get('redditMentions', 0),
                'newsHeadlines': sentiment.get('newsHeadlines', 0),
                'scrapedAt': datetime.now().isoformat()
            }
        
        ml_input = {
            'issueSize': query_data['drhp_data'].get('totalIssueSize', 0),
            'qibSubscription': 1.0,
            'hniSubscription': 1.0,
            'retailSubscription': 1.0,
            'peRatio': 20.0,
            'ofsPercentage': query_data['drhp_data'].get('ofsRatio', 0.5),
            'gmpListingDay': query_data['sentiment_data'].get('vaderScore', 0)
        }
        
        ml_result = execute_python_script('module_a.py', [json.dumps(ml_input)])
        if ml_result:
            ml = json.loads(ml_result)
            query_data['ml_prediction'] = {
                'successProbability': ml.get('probability', 0.5),
                'riskScore': ml.get('riskScore', 0.5),
                'predictedAt': datetime.now().isoformat()
            }
        
        sector_avg = supabase.table('sector_averages').select('*').eq('sector', sector).execute()
        if sector_avg.data and len(sector_avg.data) > 0:
            avg = sector_avg.data[0]
            drhp_data = query_data.get('drhp_data', {})
            sentiment_data = query_data.get('sentiment_data', {})
            if drhp_data.get('ofsRatio') is not None:
                query_data['risk_flags']['highOFSRatio'] = drhp_data['ofsRatio'] > avg['average_ofs_ratio']
            if sentiment_data.get('vaderScore') is not None:
                query_data['risk_flags']['highHypeScore'] = sentiment_data['vaderScore'] > avg['average_sentiment_score']
            query_data['risk_flags']['exceedsSectorAverage'] = (
                query_data['risk_flags'].get('highOFSRatio', False) and
                query_data['risk_flags'].get('highHypeScore', False)
            )
        
        result = supabase.table('live_queries').insert(query_data).execute()
        if result.data:
            return format_query_response(result.data[0])
        return jsonify({'error': 'Failed to save query'}), 500
        
    except Exception as e:
        print(f'Query error: {e}')
        return jsonify({'error': 'Failed to process IPO query'}), 500

def format_query_response(query):
    return jsonify({
        '_id': query['id'],
        'companyName': query['company_name'],
        'symbol': query['symbol'],
        'sector': query.get('sector'),
        'queryDate': query['query_date'],
        'drhpData': query.get('drhp_data', {}),
        'sentimentData': query.get('sentiment_data', {}),
        'mlPrediction': query.get('ml_prediction', {}),
        'riskFlags': query.get('risk_flags', {})
    })

@app.route('/api/ipo/queries', methods=['GET'])
def get_queries():
    if not supabase:
        return jsonify({'error': 'Database not connected'}), 503
    
    try:
        result = supabase.table('live_queries').select('*').order('query_date', desc=True).limit(50).execute()
        queries = [format_query_dict(q) for q in result.data] if result.data else []
        return jsonify(queries)
    except Exception as e:
        return jsonify({'error': 'Failed to fetch queries'}), 500

def format_query_dict(query):
    return {
        '_id': query['id'],
        'companyName': query['company_name'],
        'symbol': query['symbol'],
        'sector': query.get('sector'),
        'queryDate': query['query_date'],
        'drhpData': query.get('drhp_data', {}),
        'sentimentData': query.get('sentiment_data', {}),
        'mlPrediction': query.get('ml_prediction', {}),
        'riskFlags': query.get('risk_flags', {})
    }

@app.route('/api/ipo/sector-averages', methods=['GET'])
def get_sector_averages():
    if not supabase:
        return jsonify({'error': 'Database not connected'}), 503
    
    try:
        result = supabase.table('sector_averages').select('*').execute()
        return jsonify(result.data if result.data else [])
    except Exception as e:
        return jsonify({'error': 'Failed to fetch sector averages'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f'🚀 Server running on port {port}')
    print(f'📡 API: http://localhost:{port}/api')
    app.run(host='0.0.0.0', port=port, debug=True)
