# Claude Assistant Instructions

## Project Overview
Stock management and price analysis project for Hyundai and Kia vehicles.

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

# Pricing
python -m src.pricing.pricing_unified

# Export
python -m src.utils.export_cleansing_results
```

### Testing
```bash
# No specific test commands defined yet
```

### Linting/Type Checking
```bash
# No specific lint/typecheck commands defined yet
```

## Project Structure
- `src/cleansing/` - Data cleansing modules
- `src/pricing/` - Price calculation modules  
- `src/listing/` - Listing generation modules
- `src/image/` - Image management modules
- `src/utils/` - Utility functions
- `data/raw/` - Raw input data
- `data/reference/` - Reference data
- `data/export/` - Output files

## Important Notes
- Virtual environment (`venv/`) is excluded from Git
- Data files in `data/raw/` need to be managed separately
- All results are saved to `data/export/` folder