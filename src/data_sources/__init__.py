# Data sources module initialization
try:
    from . import cftc
    from . import sec  
    from . import fred
    from . import dtcc
    from . import exchange
    
    __all__ = ['cftc', 'sec', 'fred', 'dtcc', 'exchange']
    
except ImportError as e:
    print(f"Warning: Could not import all data sources: {e}")
    # Import what we can
    try:
        from . import cftc
    except ImportError:
        cftc = None
        
    try:
        from . import sec
    except ImportError:
        sec = None
        
    try:
        from . import fred
    except ImportError:
        fred = None
        
    try:
        from . import dtcc
    except ImportError:
        dtcc = None
        
    try:
        from . import exchange
    except ImportError:
        exchange = None
