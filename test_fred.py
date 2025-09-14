"""Test script for FRED API integration."""
import logging
import os
from dotenv import load_dotenv
from data_sources.fred import FREDClient

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('fred_test.log')
    ]
)
logger = logging.getLogger(__name__)

def test_fred_integration():
    """Test the FRED API integration."""
    # Load environment variables
    load_dotenv()
    
    # Initialize client
    try:
        client = FREDClient()
        logger.info("Successfully initialized FRED client")
        
        # Test series availability
        logger.info("Testing series availability...")
        available_series = client.get_available_series(days=30)
        
        if not available_series:
            logger.error("No available series found. Check your API key and internet connection.")
            return False
            
        logger.info(f"Found {len(available_series)} available series:")
        for series in available_series:
            logger.info(f"- {series['name']} ({series['id']}): {series['title']}")
        
        # Test data download
        logger.info("\nTesting data download...")
        data = client.get_swap_rates(days=30)
        
        if not data:
            logger.error("No data was downloaded.")
            return False
            
        logger.info(f"Successfully downloaded {len(data)} series:")
        for name, df in data.items():
            logger.info(f"- {name}: {len(df)} data points")
            logger.info(f"  Latest data: {df.iloc[-1].to_dict()}")
        
        # Test summary
        logger.info("\nTesting summary generation...")
        summary = client.get_swap_rate_summary(days=30)
        
        if not summary.empty:
            logger.info("\nInterest Rate Summary:")
            print(summary[['name', 'current_rate', 'units', 'change_pct', 'last_updated']].to_string())
            return True
        else:
            logger.error("Failed to generate summary")
            return False
            
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    if test_fred_integration():
        logger.info("\n✅ FRED integration test completed successfully!")
    else:
        logger.error("\n❌ FRED integration test failed. Check the logs for details.")
        exit(1)
