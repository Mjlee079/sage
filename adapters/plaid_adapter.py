"""
SAGEN-Sync: Plaid Adapter (V2+ Stub)
======================================

Future V2+ adapter for direct bank account integration via Plaid.
Replaces RightCapital as a more reliable data source.

Data Sources:
    - Pinnacle Bank (checking, savings)
    - Any bank account linked by client
    
Security:
    - Plaid handles OAuth, no credential storage
    - Authenticates via Plaid Link (user-driven)
    - Tokens are encrypted at rest
"""

class PlaidAdapter:
    """
    Plaid data adapter (V2+ stub).
    """
    
    def __init__(self, client_id, secret):
        self.client_id = client_id
        self.secret = secret
        self.base_url = "https://production.plaid.com"
        
    def create_link_token(self, client_user_id, products):
        """Create Plaid Link token for client bank authentication."""
        raise NotImplementedError("Plaid integration planned for V2+")
    
    def exchange_public_token(self, public_token):
        """Exchange Link public token for access token."""
        raise NotImplementedError("Plaid integration planned for V2+")
    
    def sync(self, access_token, cursor=None):
        """Sync transactions and balances."""
        raise NotImplementedError("Plaid integration planned for V2+")
