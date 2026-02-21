import sys
import subprocess
from pathlib import Path

def main():
    print("=" * 70)
    print("IPO Data Scraper & Model Trainer")
    print("=" * 70)
    
    print("\nStep 1: Scraping IPO data from multiple sources...")
    print("-" * 70)
    
    scripts_to_try = ['scrape_ipo_comprehensive.py', 'scrape_ipo_enhanced.py', 'scrape_ipo_data.py']
    success = False
    
    for script in scripts_to_try:
        script_path = Path(script)
        if script_path.exists():
            try:
                result = subprocess.run(
                    [sys.executable, script],
                    capture_output=True,
                    text=True,
                    timeout=1800
                )
                print(result.stdout)
                if result.stderr:
                    print("Warnings/Errors:", result.stderr)
                success = True
                break
            except subprocess.TimeoutExpired:
                print(f"{script} took too long. Trying next script...")
                continue
            except Exception as e:
                print(f"Error with {script}: {e}. Trying next script...")
                continue
    
    if not success:
        print("All scraping scripts failed. Please check your internet connection.")
        return
    
    csv_file = Path('indian_ipo_data.csv')
    if not csv_file.exists():
        print("\nError: CSV file not generated. Please check scraping script.")
        return
    
    print(f"\nStep 2: Training ML model on scraped data...")
    print("-" * 70)
    
    try:
        result = subprocess.run(
            [sys.executable, 'train_model.py', str(csv_file)],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print("Warnings/Errors:", result.stderr)
        
        model_file = Path('ml_model.pkl')
        if model_file.exists():
            print(f"\n{'=' * 70}")
            print("SUCCESS! Model trained and saved.")
            print(f"{'=' * 70}")
        else:
            print("\nWarning: Model file not found after training.")
    except Exception as e:
        print(f"Error during training: {e}")

if __name__ == '__main__':
    main()
