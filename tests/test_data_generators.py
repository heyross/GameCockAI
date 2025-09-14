"""
Test Data Generators for GameCock AI Vector Embeddings Testing
Generates realistic financial data for comprehensive testing
"""

import random
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import uuid

class FinancialTestDataGenerator:
    """Generates realistic financial test data for vector embeddings testing"""
    
    def __init__(self):
        self.companies = [
            {"name": "Apple Inc.", "ticker": "AAPL", "cik": "0000320193", "sector": "Technology"},
            {"name": "JPMorgan Chase & Co.", "ticker": "JPM", "cik": "0000019617", "sector": "Financial Services"},
            {"name": "Tesla Inc.", "ticker": "TSLA", "cik": "0001318605", "sector": "Automotive"},
            {"name": "Microsoft Corporation", "ticker": "MSFT", "cik": "0000789019", "sector": "Technology"},
            {"name": "Goldman Sachs Group Inc.", "ticker": "GS", "cik": "0000886982", "sector": "Financial Services"},
            {"name": "Amazon.com Inc.", "ticker": "AMZN", "cik": "0001018724", "sector": "E-commerce"},
            {"name": "Berkshire Hathaway Inc.", "ticker": "BRK.A", "cik": "0001067983", "sector": "Conglomerate"},
            {"name": "Bank of America Corp.", "ticker": "BAC", "cik": "0000070858", "sector": "Financial Services"}
        ]
        
        self.risk_factors = [
            "Market volatility may impact trading revenues",
            "Credit risk from counterparty defaults",
            "Regulatory changes affecting compliance costs",
            "Cybersecurity threats to data systems",
            "Interest rate fluctuations affecting portfolio value",
            "Liquidity risk in stressed market conditions",
            "Operational risk from system failures",
            "Concentration risk in specific market segments",
            "Foreign exchange rate volatility",
            "Economic downturn impacting business operations"
        ]
        
        self.business_descriptions = [
            "operates as a diversified financial services company",
            "develops and manufactures consumer electronics and software",
            "provides investment banking and asset management services",
            "designs and manufactures electric vehicles and energy systems",
            "offers cloud computing and technology services",
            "operates e-commerce and digital advertising platforms",
            "provides insurance and diversified investment services",
            "operates retail banking and commercial lending business"
        ]
        
        self.financial_keywords = [
            "revenue", "earnings", "EBITDA", "cash flow", "assets", "liabilities",
            "equity", "debt", "capital", "investment", "dividend", "acquisition",
            "merger", "IPO", "bonds", "securities", "derivatives", "hedging",
            "risk management", "compliance", "regulatory", "Basel III", "Dodd-Frank",
            "stress testing", "liquidity", "credit risk", "market risk", "operational risk"
        ]
    
    def generate_financial_text_corpus(self, num_documents: int = 100) -> List[Dict[str, Any]]:
        """Generate realistic financial text documents"""
        documents = []
        
        for i in range(num_documents):
            company = random.choice(self.companies)
            doc_type = random.choice(["10-K", "8-K", "13F", "earnings_call", "analyst_report"])
            
            if doc_type == "10-K":
                content = self._generate_10k_content(company)
            elif doc_type == "8-K":
                content = self._generate_8k_content(company)
            elif doc_type == "13F":
                content = self._generate_13f_content(company)
            elif doc_type == "earnings_call":
                content = self._generate_earnings_call_content(company)
            else:
                content = self._generate_analyst_report_content(company)
            
            document = {
                "id": f"doc_{i:04d}",
                "company": company,
                "document_type": doc_type,
                "content": content,
                "filing_date": self._generate_random_date(),
                "metadata": {
                    "word_count": len(content.split()),
                    "section": random.choice(["business", "risk_factors", "financial_data", "management_discussion"]),
                    "importance_score": random.uniform(0.1, 1.0)
                }
            }
            
            documents.append(document)
        
        return documents
    
    def _generate_10k_content(self, company: Dict[str, str]) -> str:
        """Generate realistic 10-K filing content"""
        templates = [
            f"{company['name']} {random.choice(self.business_descriptions)}. During fiscal year 2023, the company reported revenue of ${random.randint(10, 500)} billion, representing a {random.randint(-15, 25)}% change from the prior year. {random.choice(self.risk_factors)}.",
            
            f"Risk Factors: The following risk factors may materially affect {company['name']}'s business operations: {random.choice(self.risk_factors)}. Additionally, {random.choice(self.risk_factors)}. Management believes these risks are adequately addressed through comprehensive risk management frameworks.",
            
            f"Management's Discussion and Analysis: {company['name']} experienced significant changes in market conditions during the reporting period. Key performance indicators include: {random.choice(self.financial_keywords)} growth of {random.randint(-20, 40)}%, improved {random.choice(self.financial_keywords)} metrics, and strategic investments in {random.choice(['technology', 'human capital', 'market expansion', 'regulatory compliance'])}.",
            
            f"Business Overview: {company['name']} operates in the {company.get('sector', 'Financial Services')} sector, with primary business activities including {random.choice(self.business_descriptions)}. The company maintains a diversified portfolio of {random.choice(self.financial_keywords)} and focuses on {random.choice(['sustainable growth', 'shareholder value', 'market leadership', 'innovation'])}."
        ]
        
        return random.choice(templates)
    
    def _generate_8k_content(self, company: Dict[str, str]) -> str:
        """Generate realistic 8-K filing content"""
        event_types = [
            "earnings_announcement",
            "executive_appointment", 
            "acquisition_announcement",
            "dividend_declaration",
            "material_agreement",
            "regulatory_filing"
        ]
        
        event = random.choice(event_types)
        
        templates = {
            "earnings_announcement": f"{company['name']} announced quarterly earnings results showing {random.choice(self.financial_keywords)} of ${random.randint(1, 50)} billion, {random.choice(['exceeding', 'meeting', 'falling short of'])} analyst expectations. Management provided guidance for the next quarter indicating {random.choice(['strong', 'moderate', 'cautious'])} outlook.",
            
            "executive_appointment": f"{company['name']} announced the appointment of a new {random.choice(['Chief Executive Officer', 'Chief Financial Officer', 'Chief Risk Officer', 'Head of Operations'])}. The appointment is effective immediately and is expected to {random.choice(['strengthen leadership', 'drive strategic initiatives', 'enhance operational excellence', 'improve risk management'])}.",
            
            "acquisition_announcement": f"{company['name']} entered into a definitive agreement to acquire {random.choice(['a technology company', 'a financial services firm', 'strategic assets', 'a competitor'])} for approximately ${random.randint(1, 10)} billion. The transaction is expected to {random.choice(['enhance market position', 'expand capabilities', 'create synergies', 'drive growth'])}.",
            
            "dividend_declaration": f"{company['name']} declared a quarterly dividend of ${random.uniform(0.1, 2.0):.2f} per share, {random.choice(['maintaining', 'increasing', 'adjusting'])} the dividend rate from the previous quarter. The dividend will be paid to shareholders of record.",
            
            "material_agreement": f"{company['name']} entered into a material agreement with {random.choice(['a major customer', 'a strategic partner', 'a government entity', 'an industry consortium'])} valued at approximately ${random.randint(10, 500)} million over {random.randint(2, 10)} years.",
            
            "regulatory_filing": f"{company['name']} submitted required regulatory filings related to {random.choice(['capital adequacy', 'stress testing', 'compliance requirements', 'risk management'])}. The filing demonstrates the company's commitment to {random.choice(['regulatory compliance', 'sound risk management', 'operational excellence', 'stakeholder protection'])}."
        }
        
        return templates[event]
    
    def _generate_13f_content(self, company: Dict[str, str]) -> str:
        """Generate realistic 13F filing content"""
        holdings = []
        for _ in range(random.randint(5, 20)):
            holding_company = random.choice(self.companies)
            if holding_company != company:
                holdings.append({
                    "security": holding_company["name"],
                    "ticker": holding_company["ticker"],
                    "shares": random.randint(100000, 10000000),
                    "value": random.randint(10, 1000) * 1000000
                })
        
        total_value = sum(h["value"] for h in holdings)
        
        content = f"{company['name']} 13F Holdings Report: Total portfolio value of ${total_value/1000000:.0f} million across {len(holdings)} positions. "
        content += f"Top holdings include {holdings[0]['security']} (${holdings[0]['value']/1000000:.0f}M), "
        content += f"{holdings[1]['security'] if len(holdings) > 1 else 'N/A'} (${holdings[1]['value']/1000000:.0f}M). "
        content += f"Portfolio demonstrates {random.choice(['diversification', 'focus on growth', 'value orientation', 'sector concentration'])} strategy."
        
        return content
    
    def _generate_earnings_call_content(self, company: Dict[str, str]) -> str:
        """Generate realistic earnings call transcript content"""
        metrics = {
            "revenue": random.randint(10, 100) * 1000000000,
            "net_income": random.randint(1, 20) * 1000000000,
            "eps": random.uniform(0.5, 10.0),
            "growth_rate": random.uniform(-10, 30)
        }
        
        content = f"{company['name']} Q{random.randint(1,4)} 2023 Earnings Call Transcript: "
        content += f"CEO: We delivered strong results with revenue of ${metrics['revenue']/1000000000:.1f} billion, "
        content += f"representing {metrics['growth_rate']:.1f}% growth year-over-year. "
        content += f"Net income was ${metrics['net_income']/1000000000:.1f} billion, and earnings per share of ${metrics['eps']:.2f}. "
        content += f"Looking ahead, we remain focused on {random.choice(['operational excellence', 'strategic growth', 'market expansion', 'innovation', 'cost optimization'])}. "
        content += f"CFO: Our {random.choice(self.financial_keywords)} position remains strong with adequate {random.choice(['liquidity', 'capital', 'reserves'])}."
        
        return content
    
    def _generate_analyst_report_content(self, company: Dict[str, str]) -> str:
        """Generate realistic analyst report content"""
        rating = random.choice(["Buy", "Hold", "Sell", "Outperform", "Underperform"])
        price_target = random.randint(50, 500)
        
        content = f"Analyst Report: {company['name']} ({company['ticker']}) - {rating} Rating with ${price_target} price target. "
        content += f"We believe {company['name']} is well-positioned in the {company['sector']} sector due to "
        content += f"{random.choice(['strong fundamentals', 'market leadership', 'innovative products', 'operational efficiency'])}. "
        content += f"Key catalysts include {random.choice(['earnings growth', 'market expansion', 'cost reduction', 'new products', 'regulatory changes'])}. "
        content += f"Risk factors include {random.choice(self.risk_factors)}."
        
        return content
    
    def generate_sec_10k_document(self, company: Dict[str, str]) -> str:
        """Generate a realistic SEC 10-K document content"""
        return self._generate_10k_content(company)
    
    def generate_test_embeddings(self, dimension: int, count: int) -> List[List[float]]:
        """Generate random test embeddings for performance testing"""
        import numpy as np
        return np.random.random((count, dimension)).tolist()
    
    def generate_cftc_swap_data(self, num_records: int = 500) -> List[Dict[str, Any]]:
        """Generate realistic CFTC swap data"""
        asset_classes = ["Equity", "Interest Rate", "Credit", "Commodity", "FX"]
        currencies = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF"]
        
        swap_data = []
        
        for i in range(num_records):
            record = {
                "trade_id": f"SWAP_{i:06d}",
                "execution_timestamp": self._generate_random_datetime(),
                "asset_class": random.choice(asset_classes),
                "notional_amount": random.randint(1000000, 1000000000),
                "currency": random.choice(currencies),
                "maturity_date": self._generate_future_date(),
                "counterparty_1": f"DEALER_{random.randint(1, 50):02d}",
                "counterparty_2": f"CLIENT_{random.randint(1, 200):03d}",
                "product_type": random.choice(["Vanilla", "Structured", "Exotic"]),
                "clearing_status": random.choice(["Cleared", "Uncleared"]),
                "price": random.uniform(95.0, 105.0),
                "spread": random.uniform(0.1, 5.0),
                "risk_metrics": {
                    "delta": random.uniform(-1.0, 1.0),
                    "gamma": random.uniform(0.0, 0.1),
                    "vega": random.uniform(0.0, 10.0),
                    "theta": random.uniform(-5.0, 0.0)
                }
            }
            
            swap_data.append(record)
        
        return swap_data
    
    def generate_insider_transactions(self, num_transactions: int = 200) -> List[Dict[str, Any]]:
        """Generate realistic insider transaction data"""
        transaction_types = ["Purchase", "Sale", "Grant", "Exercise", "Gift"]
        relationship_types = ["Officer", "Director", "10% Owner", "Other"]
        
        transactions = []
        
        for i in range(num_transactions):
            company = random.choice(self.companies)
            
            transaction = {
                "transaction_id": f"INSIDER_{i:06d}",
                "company": company,
                "insider_name": f"Insider_{random.randint(1, 100):03d}",
                "relationship": random.choice(relationship_types),
                "transaction_date": self._generate_random_date(),
                "transaction_type": random.choice(transaction_types),
                "shares": random.randint(100, 100000),
                "price_per_share": random.uniform(10.0, 500.0),
                "total_value": 0,  # Will be calculated
                "remaining_holdings": random.randint(0, 1000000),
                "form_type": random.choice(["Form 4", "Form 5", "Form 3"])
            }
            
            transaction["total_value"] = transaction["shares"] * transaction["price_per_share"]
            transactions.append(transaction)
        
        return transactions
    
    def generate_form_13f_holdings(self, num_holdings: int = 300) -> List[Dict[str, Any]]:
        """Generate realistic Form 13F holdings data"""
        holdings = []
        
        institutional_investors = [
            "BlackRock Inc", "Vanguard Group", "State Street Corp", "Fidelity Investments",
            "Berkshire Hathaway", "Capital Research", "T. Rowe Price", "Wellington Management"
        ]
        
        for i in range(num_holdings):
            company = random.choice(self.companies)
            investor = random.choice(institutional_investors)
            
            holding = {
                "holding_id": f"13F_{i:06d}",
                "investor_name": investor,
                "investor_cik": f"{random.randint(1000000, 9999999):07d}",
                "security": company["name"],
                "ticker": company["ticker"],
                "cusip": f"{random.randint(100000000, 999999999):09d}",
                "shares_held": random.randint(10000, 50000000),
                "market_value": random.randint(1000000, 10000000000),
                "percent_of_portfolio": random.uniform(0.1, 25.0),
                "reporting_period": self._generate_quarter_end_date(),
                "change_from_prior_period": random.uniform(-50.0, 100.0),
                "investment_discretion": random.choice(["Sole", "Shared", "None"])
            }
            
            holdings.append(holding)
        
        return holdings
    
    def generate_market_events(self, num_events: int = 50) -> List[Dict[str, Any]]:
        """Generate realistic market event data"""
        event_types = [
            "Earnings Announcement", "FDA Approval", "Merger Announcement", 
            "Dividend Declaration", "Credit Rating Change", "Regulatory Action",
            "Product Launch", "Executive Change", "Lawsuit Settlement",
            "Economic Data Release"
        ]
        
        events = []
        
        for i in range(num_events):
            company = random.choice(self.companies)
            
            event = {
                "event_id": f"EVENT_{i:06d}",
                "company": company,
                "event_type": random.choice(event_types),
                "event_date": self._generate_random_date(),
                "description": self._generate_event_description(company),
                "market_impact": random.choice(["Positive", "Negative", "Neutral"]),
                "volatility_impact": random.uniform(0.1, 5.0),
                "analyst_sentiment": random.choice(["Bullish", "Bearish", "Neutral"]),
                "media_mentions": random.randint(1, 100),
                "social_sentiment_score": random.uniform(-1.0, 1.0)
            }
            
            events.append(event)
        
        return events
    
    def _generate_event_description(self, company: Dict[str, str]) -> str:
        """Generate event description"""
        templates = [
            f"{company['name']} announced better than expected quarterly results",
            f"Regulatory approval received for {company['name']} new product line",
            f"{company['name']} completed acquisition of strategic technology assets", 
            f"Credit rating agency upgraded {company['name']} outlook to positive",
            f"{company['name']} launched innovative solution in {company['sector']} market"
        ]
        
        return random.choice(templates)
    
    def _generate_random_date(self) -> str:
        """Generate random date in the past 2 years"""
        start_date = datetime.now() - timedelta(days=730)
        end_date = datetime.now()
        
        random_date = start_date + timedelta(
            days=random.randint(0, (end_date - start_date).days)
        )
        
        return random_date.strftime("%Y-%m-%d")
    
    def _generate_random_datetime(self) -> str:
        """Generate random datetime in the past year"""
        start_date = datetime.now() - timedelta(days=365)
        end_date = datetime.now()
        
        random_datetime = start_date + timedelta(
            seconds=random.randint(0, int((end_date - start_date).total_seconds()))
        )
        
        return random_datetime.isoformat()
    
    def _generate_future_date(self) -> str:
        """Generate future date for maturity/expiration"""
        start_date = datetime.now() + timedelta(days=30)
        end_date = datetime.now() + timedelta(days=3650)  # 10 years
        
        random_date = start_date + timedelta(
            days=random.randint(0, (end_date - start_date).days)
        )
        
        return random_date.strftime("%Y-%m-%d")
    
    def _generate_quarter_end_date(self) -> str:
        """Generate quarter end date"""
        year = random.randint(2021, 2023)
        quarter_ends = [
            f"{year}-03-31",
            f"{year}-06-30", 
            f"{year}-09-30",
            f"{year}-12-31"
        ]
        
        return random.choice(quarter_ends)
    
    def save_test_data_to_files(self, output_dir: str):
        """Save all generated test data to files"""
        from pathlib import Path
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Generate all data types
        datasets = {
            "financial_documents": self.generate_financial_text_corpus(100),
            "cftc_swaps": self.generate_cftc_swap_data(500),
            "insider_transactions": self.generate_insider_transactions(200),
            "form_13f_holdings": self.generate_form_13f_holdings(300),
            "market_events": self.generate_market_events(50)
        }
        
        # Save to JSON files
        for dataset_name, data in datasets.items():
            file_path = output_path / f"{dataset_name}.json"
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            print(f"✅ Saved {len(data)} {dataset_name} records to {file_path}")
        
        # Create summary
        summary = {
            "generation_timestamp": datetime.now().isoformat(),
            "datasets": {name: len(data) for name, data in datasets.items()},
            "total_records": sum(len(data) for data in datasets.values())
        }
        
        summary_path = output_path / "test_data_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"📊 Generated {summary['total_records']} total test records")
        print(f"📁 Test data saved to: {output_path}")
        
        return datasets


def create_test_vector_collection(embeddings_data: List[Dict] = None, collection_name: str = "test_collection"):
    """Create a test vector collection for testing purposes"""
    try:
        import chromadb
        
        # Generate default test data if none provided
        if embeddings_data is None:
            generator = FinancialTestDataGenerator()
            embeddings_data = generator.generate_financial_text_corpus(100)
        
        # Create ChromaDB client using new configuration
        import tempfile
        temp_dir = tempfile.mkdtemp()
        client = chromadb.PersistentClient(path=temp_dir)
        
        collection = client.create_collection(name=collection_name)
        
        # Add embeddings to collection
        documents = []
        metadatas = []
        ids = []
        
        for i, item in enumerate(embeddings_data):
            documents.append(item.get("content", ""))
            metadatas.append({
                "document_type": item.get("document_type", "unknown"),
                "company": item.get("company", {}).get("name", "unknown"),
                "importance_score": item.get("metadata", {}).get("importance_score", 0.5)
            })
            ids.append(f"test_doc_{i}")
        
        # Generate fake embeddings (for testing without actual models)
        import numpy as np
        fake_embeddings = np.random.random((len(documents), 768)).tolist()
        
        # Return data dictionary for performance tests
        return {
            "documents": documents,
            "metadatas": metadatas,
            "ids": ids,
            "embeddings": fake_embeddings,
            "collection": collection  # Include collection for tests that need it
        }
        
    except ImportError:
        print("ChromaDB not available - returning mock data")
        # Return mock data when ChromaDB is not available
        return {
            "documents": [f"Mock document {i}" for i in range(100)],
            "metadatas": [{"type": "mock", "id": i} for i in range(100)],
            "ids": [f"mock_{i}" for i in range(100)],
            "embeddings": [[0.1] * 768 for _ in range(100)],
            "collection": None
        }


def generate_test_database():
    """Generate a complete test database with realistic financial data"""
    generator = FinancialTestDataGenerator()
    
    # Generate comprehensive test dataset
    test_data = {
        "companies": generator.companies,
        "financial_documents": generator.generate_financial_text_corpus(200),
        "cftc_swaps": generator.generate_cftc_swap_data(1000),
        "insider_transactions": generator.generate_insider_transactions(500),
        "form_13f_holdings": generator.generate_form_13f_holdings(600),
        "market_events": generator.generate_market_events(100)
    }
    
    print(f"🎲 Generated comprehensive test database:")
    for dataset_name, data in test_data.items():
        if isinstance(data, list):
            print(f"  📊 {dataset_name}: {len(data)} records")
        else:
            print(f"  📊 {dataset_name}: {data}")
    
    return test_data


if __name__ == "__main__":
    """Generate test data when run directly"""
    print("🎲 GameCock AI Test Data Generator")
    print("=" * 50)
    
    generator = FinancialTestDataGenerator()
    
    # Generate and save test data
    output_directory = "./test_data"
    datasets = generator.save_test_data_to_files(output_directory)
    
    print(f"\n✅ Test data generation complete!")
    print(f"📁 Files saved to: {output_directory}")
    print(f"📊 Total records: {sum(len(data) for data in datasets.values())}")
