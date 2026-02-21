import sys
import json
import pdfplumber
import requests
import tempfile
import os
from pathlib import Path

def download_pdf(url):
    if not url or url.strip() == '':
        return None
    
    try:
        response = requests.get(url, timeout=30, stream=True)
        response.raise_for_status()
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        for chunk in response.iter_content(chunk_size=8192):
            temp_file.write(chunk)
        temp_file.close()
        
        return temp_file.name
    except Exception:
        return None

def extract_drhp_data(pdf_path):
    ofs_ratio = None
    fresh_issue = None
    total_issue_size = None
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ''
            for page in pdf.pages:
                full_text += page.extract_text() or ''
            
            lines = full_text.split('\n')
            in_objects_section = False
            
            for i, line in enumerate(lines):
                if 'objects of the issue' in line.lower() or 'objects of issue' in line.lower():
                    in_objects_section = True
                    continue
                
                if in_objects_section:
                    if 'offer for sale' in line.lower() or 'ofs' in line.lower():
                        for j in range(i, min(i + 10, len(lines))):
                            text = lines[j].lower()
                            if 'rs.' in text or 'crore' in text or 'lakh' in text:
                                numbers = extract_numbers(lines[j])
                                if numbers:
                                    ofs_value = numbers[0]
                                    if 'lakh' in text:
                                        ofs_value = ofs_value * 0.01
                                    break
                    
                    if 'fresh issue' in line.lower() or 'new issue' in line.lower():
                        for j in range(i, min(i + 10, len(lines))):
                            text = lines[j].lower()
                            if 'rs.' in text or 'crore' in text or 'lakh' in text:
                                numbers = extract_numbers(lines[j])
                                if numbers:
                                    fresh_value = numbers[0]
                                    if 'lakh' in text:
                                        fresh_value = fresh_value * 0.01
                                    fresh_issue = fresh_value
                                    break
                    
                    if 'total issue' in line.lower() or 'aggregate issue' in line.lower():
                        for j in range(i, min(i + 10, len(lines))):
                            text = lines[j].lower()
                            if 'rs.' in text or 'crore' in text or 'lakh' in text:
                                numbers = extract_numbers(lines[j])
                                if numbers:
                                    total_value = numbers[0]
                                    if 'lakh' in text:
                                        total_value = total_value * 0.01
                                    total_issue_size = total_value
                                    break
                    
                    if ofs_ratio is not None and fresh_issue is not None:
                        break
            
            if fresh_issue and total_issue_size:
                ofs_ratio = (total_issue_size - fresh_issue) / total_issue_size if total_issue_size > 0 else 0
            elif fresh_issue:
                ofs_ratio = 0
            else:
                ofs_ratio = 1.0 if total_issue_size else None
                
    except Exception:
        pass
    
    return {
        'ofsRatio': ofs_ratio if ofs_ratio is not None else 0.5,
        'freshIssue': fresh_issue if fresh_issue is not None else 0,
        'totalIssueSize': total_issue_size if total_issue_size is not None else 0,
        'pdfSource': pdf_path
    }

def extract_numbers(text):
    import re
    numbers = re.findall(r'[\d,]+\.?\d*', text.replace(',', ''))
    return [float(n) for n in numbers if n]

if __name__ == '__main__':
    pdf_url = sys.argv[1] if len(sys.argv) > 1 else ''
    
    pdf_path = None
    if pdf_url:
        pdf_path = download_pdf(pdf_url)
    
    if pdf_path and os.path.exists(pdf_path):
        result = extract_drhp_data(pdf_path)
        os.unlink(pdf_path)
    else:
        result = {
            'ofsRatio': 0.5,
            'freshIssue': 0,
            'totalIssueSize': 0,
            'pdfSource': None
        }
    
    print(json.dumps(result))
