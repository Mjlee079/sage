"""
SAGEN-Sync: Charles Schwab Adapter (V2 Stub)
==============================================

Future V2 adapter for pulling investment balances from Charles Schwab.
Per the PRD, this deferred to V2 due to compliance restrictions.
"""

class SchwabAdapter:
    """
    Charles Schwab data adapter (V2 stub).
    """
    
    def __init__(self, credentials=None):
        self.credentials = credentials
        self.base_url = "https://api.schwab.com"
        self.is_authenticated = False
        
    def authenticate(self):
        """Authenticate with Schwab API. V2 feature."""
        raise NotImplementedError("Schwab API integration planned for V2")
    
    def fetch_balances(self, client_id):
        """Retrieve investment balances. V2 feature."""
        raise NotImplementedError("Schwab API integration planned for V2")
