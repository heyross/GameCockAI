"""
Data Sources Package
Provides access to all data source modules
"""

# Import all data source modules
try:
    from . import cftc
    from . import sec  
    from . import fred
    from . import dtcc
    from . import exchange
    
    __all__ = ['cftc', 'sec', 'fred', 'dtcc', 'exchange']
    
except ImportError as e:
    # Graceful fallback for missing modules
    import logging
    logging.warning(f"Some data source modules not available: {e}")
    
    # Create dummy modules to prevent crashes
    class DummyModule:
        def __getattr__(self, name):
            def dummy_function(*args, **kwargs):
                return None
            return dummy_function
    
    cftc = sec = fred = dtcc = exchange = DummyModule()
    __all__ = ['cftc', 'sec', 'fred', 'dtcc', 'exchange']