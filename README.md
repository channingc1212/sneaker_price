# Sneaker Price Comparison Tool

A web scraping tool that compares sneaker prices across major retail websites using AI-powered search and data aggregation.

## Features
- AI-powered sneaker identification
- Multi-website price comparison
- User-friendly Streamlit interface
- Detailed product information and direct links
- Customizable search parameters

## Project Structure
```
sneaker_price/
├── src/               # Source code
├── tests/             # Test files
├── data/              # Data storage
├── config/            # Configuration files
├── ui/                # Streamlit UI components
├── requirements.txt   # Project dependencies
└── README.md         # Project documentation
```

## Setup Instructions
1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   - Create a `.env` file
   - Add your OpenAI API key: `OPENAI_API_KEY=your_key_here`

## Usage
Run the Streamlit app:
```bash
streamlit run src/main.py
```

## Development
- Use `pytest` for running tests
- Follow PEP 8 style guide
- Use `black` for code formatting
- Use `flake8` for linting 