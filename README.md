# GCI Hackathon - Clinic Dashboard

An interactive dashboard built for the Global Clubfoot Initiative (GCI) Hackathon to visualize and analyze clinic distribution, patient data, and treatment effectiveness.

## Features

- **Interactive Map Visualization**
  - Clinic locations with Ponseti treatment availability
  - Coverage area analysis
  - Patient density heatmap
  - Detailed clinic information on hover

- **Coverage Analysis**
  - Clinic distribution by country
  - Ponseti treatment availability statistics
  - Treatment success rate analysis
  - Patient age distribution

- **Performance Optimizations**
  - Efficient data filtering
  - Caching for repeated calculations
  - Optimized geographic calculations

## Setup

1. Clone the repository:
```bash
git clone https://github.com/c4viveksharma/gci-hackathon.git
cd gci-hackathon
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the dashboard:
```bash
streamlit run clinic_dashboard.py
```

## Data Structure

The project uses several data sources:
- `Location Data/`: Clinic and patient location information
- `Treatment Data/`: Treatment cases and outcomes
- `Population Data/`: Population statistics
- `Survey Data/`: Clinic survey responses

## Contributing

Feel free to submit issues and enhancement requests!
