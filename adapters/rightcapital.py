"""
SAGEN-Sync: RightCapital Adapter (V2 Stub)
============================================

Future V2 adapter for pulling financial planning data from RightCapital.
Per the PRD: "Don't trust RightCapital that much... make that second version"
"""

class RightCapitalAdapter:
    """
    RightCapital data adapter (V2 stub).
    """
    
    def __init__(self, credentials=None):
        self.credentials = credentials
        self.base_url = "https://api.rightcapital.com"
        self.is_authenticated = False
        
    def authenticate(self):
        """Authenticate with RightCapital. V2 feature."""
        raise NotImplementedError("RightCapital integration planned for V2")
    
    def fetch_balances(self, client_id):
        """Retrieve account aggregator data. V2 feature."""
        raise NotImplementedError("RightCapital integration planned for V2")
