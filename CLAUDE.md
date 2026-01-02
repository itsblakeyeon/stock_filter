# Claude Assistant Instructions

## Project Overview
Stock filtering project for Hyundai and Kia vehicles - simple 2-stage pipeline.

## Key Commands
한글로 대화하자.

### Environment Setup
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Main Execution
```bash
# Run main script
python run.py
```

### Individual Module Execution
```bash
# Cleansing
python -m src.cleansing.cleansing_hyundai
python -m src.cleansing.cleansing_kia
python -m src.cleansing.cleansing_unified

# Listing
python -m src.listing.listing_unified
```

## Project Structure
- `src/cleansing/` - Data cleansing modules (Hyundai, Kia, unified)
- `src/listing/` - Listing filtering module
- `src/config/` - Configuration and constants
- `data/raw/` - Raw input data (날짜별: YYMMDD 형식)
- `results/` - Output files

## Pipeline
1. **Cleansing**: Clean and merge Hyundai + Kia inventory data
2. **Listing**: Filter vehicles by criteria (wheel/tire, options, seating)
3. **Output**: Generate `stock_filtered_YYMMDD.xlsx` in `results/` folder

## Filtering Criteria
- 기본 휠&타이어만 (제네시스 18인치 포함)
- 빌트인캠 또는 무옵션만
- 싼타페 하이브리드: 5인승만
- 팰리세이드: 9인승만

## Important Notes
- Virtual environment (`venv/`) is excluded from Git
- Data files in `data/raw/` are managed per date (YYMMDD format)
- All results are saved to `results/` folder
- No pricing, subscription, or image features - pure filtering only
- Minimal dependencies: pandas, openpyxl, xlrd, requests
