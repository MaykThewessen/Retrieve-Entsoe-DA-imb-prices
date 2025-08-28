# ENTSO-E Day-Ahead and Imbalance Price Retrieval

A comprehensive Python toolkit for retrieving, analyzing, and visualizing European electricity market data from ENTSO-E (European Network of Transmission System Operators for Electricity).

## 🎯 Project Overview

This repository contains scripts and tools for:
- **Day-Ahead (DA) Price Retrieval**: Historical and real-time electricity prices from EPEX and other European exchanges
- **Imbalance (IMB) Price Analysis**: System imbalance prices for grid stability
- **Data Visualization**: Interactive dashboards and charts for price analysis
- **Automated Data Collection**: Scripts for continuous data retrieval and storage

## 🔧 Features

### Core Functionality
- **Multi-year data retrieval** (2019-2025) with automatic chunking
- **API integration** with ENTSO-E using official Python client
- **Data persistence** with local CSV storage and caching
- **Error handling** and retry mechanisms for robust data collection

### Analysis Tools
- **Price distribution analysis** with histograms and statistical summaries
- **Time series visualization** for trend analysis
- **Monthly and annual price comparisons**
- **Interactive HTML dashboards** for data exploration

### Data Sources
- **Day-Ahead Prices**: Hourly electricity prices from European exchanges
- **Imbalance Prices**: 15-minute resolution system imbalance data
- **Geographic Coverage**: Netherlands (NL) with extensible country support

## 📁 Repository Structure

```
├── data/                           # Historical price data (CSV files)
│   ├── DA_prices_2019.csv         # Day-ahead prices by year
│   ├── DA_prices_2020.csv
│   └── ...
├── EPEX_hourly_avg_prices_v*.py   # Main price retrieval scripts
├── Retrieve_prices_v*.py           # Data processing and analysis scripts
├── Entsoe_aFRR_FCR_retrieval_v1.py # Ancillary services data retrieval
├── *.html                          # Interactive dashboards
├── *.pdf                           # Generated reports and visualizations
└── .gitignore                      # Prevents sensitive files from being committed
```

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- ENTSO-E API key (required for data retrieval)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/MaykThewessen/Retrieve-Entsoe-DA-imb-prices.git
   cd Retrieve-Entsoe-DA-imb-prices
   ```

2. Install required packages:
   ```bash
   pip install pandas numpy entsoe-python-client python-dotenv
   ```

3. Set up your API key:
   - Create a `.env` file in the root directory
   - Add your ENTSO-E API key: `ENTSOE_API_KEY=your_api_key_here`

### Usage
1. **Retrieve Day-Ahead Prices**:
   ```bash
   python EPEX_hourly_avg_prices_v5.py
   ```

2. **Generate Analysis Reports**:
   ```bash
   python Retrieve_prices_v10_histogram_loop.py
   ```

3. **View Interactive Dashboards**:
   - Open `EPEX_Prices_Analysis_v5.html` in your web browser
   - Navigate through different analysis views

## 📊 Data Outputs

### CSV Files
- **Day-Ahead Prices**: Hourly resolution with timestamp and price columns
- **Imbalance Prices**: 15-minute resolution for detailed grid analysis
- **Combined Datasets**: Multi-year consolidated data for trend analysis

### Visualizations
- **Price Histograms**: Distribution analysis by time periods
- **Time Series Charts**: Price evolution over time
- **Monthly/Annual Comparisons**: Seasonal and yearly price patterns
- **Interactive Dashboards**: Zoom-in capabilities for detailed analysis

## 🔒 Security & Privacy

**Recent Security Improvements**:
- ✅ **Removed all `.env` files** from Git history (privacy issue resolved)
- ✅ **Eliminated `.DS_Store` files** from repository (cleanup completed)
- ✅ **Added comprehensive `.gitignore`** to prevent future sensitive file commits
- ✅ **Repository history rewritten** to ensure complete data privacy

**Best Practices**:
- Never commit API keys or sensitive credentials
- Use `.env` files for local configuration (already in `.gitignore`)
- Regular security audits of repository contents

## 📈 Analysis Capabilities

### Statistical Analysis
- **Price Distribution**: Histograms and percentiles
- **Trend Analysis**: Moving averages and seasonal patterns
- **Volatility Assessment**: Price variation and stability metrics

### Market Insights
- **Peak/Off-peak Analysis**: Price patterns by time of day
- **Seasonal Trends**: Monthly and yearly price variations
- **Grid Stability**: Imbalance price analysis for system health

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure no sensitive files are included
5. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 🔗 Related Resources

- [ENTSO-E Official Website](https://www.entsoe.eu/)
- [ENTSO-E Transparency Platform](https://transparency.entsoe.eu/)
- [EPEX Spot](https://www.epexspot.com/) - European Power Exchange

## 📞 Support

For questions or issues:
- Check existing issues in the repository
- Review the analysis outputs and documentation
- Ensure your API key is properly configured

---

**Last Updated**: January 2025  
**Repository Status**: ✅ Secure, Clean, and Production Ready
