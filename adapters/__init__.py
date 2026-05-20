"""
SAGEN-Sync: External Data Adapters (V2 Extensibility)
======================================================

This package contains adapters for integrating with external
financial data sources. These modules are NOT used in V1 but 
are architected to be plug-and-play when V2 automation is implemented.

Adapters Planned:
    schwab:        Charles Schwab account data
    rightcapital:  Financial planning aggregator
    precisefp:     Client onboarding data
    plaid:         Bank account connectivity

Usage in V2:
    from adapters.schwab import SchwabAdapter
    
    adapter = SchwabAdapter(api_credentials)
    balances = adapter.fetch_balances(client_id)
    
Each adapter follows the same interface:
    - __init__(self, credentials): Initialize with API credentials
    - authenticate(self): Verify credentials
    - fetch_data(self, client_id): Pull data for a specific client
    - get_balances(self, account_ids): Get balances for account IDs
    - disconnect(self): Clean up session

To add a new V2 adapter:
    1. Create a new file in this folder (e.g., new_adapter.py)
    2. Implement the adapter interface
    3. Import it here
"""
