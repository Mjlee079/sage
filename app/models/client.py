"""
SAGEN-Sync: Client Model
========================

Handles all CRUD operations for client profiles.
Clients have static information entered once during setup.

A "client" may be an individual or a married couple (Client 1 + Client 2/Spouse).
Account structures are stored as JSON for flexibility.

Usage:
    from app.models.client import Client
    
    # Create client
    client_id = Client.create(data_dict)
    
    # Retrieve
    client = Client.get_by_id(1)
    
    # Update
    Client.update(1, {\"monthly_salary\": 12000})
    
    # List all
    all_clients = Client.get_all()
"""

import json
from app.database import execute_query, get_db


class Client:
    """
    Client data model - static profile information.
    
    Each client record represents a family unit (individual or married couple).
    Static data is entered once during client setup and rarely changes.
    """
    
    # SQL column names (excluding auto-calculated 'age' and timestamp fields)
    COLUMNS = [
        "first_name", "last_name", "date_of_birth", "ssn_last_four",
        "is_married", "spouse_first_name", "spouse_last_name",
        "spouse_dob", "spouse_ssn_last_four",
        "monthly_salary", "agreed_expense_budget", "private_reserve_target",
        "retirement_accounts", "non_retirement_accounts", "trust_info", "liabilities",
        "notes"
    ]
    
    
    # ============================================
    # CREATE
    # ============================================
    
    @classmethod
    def create(cls, data):
        """
        Create a new client record from form data.
        
        Args:
            data (dict): Dictionary containing client fields
                {
                    "first_name": "John",
                    "last_name": "Doe",
                    "date_of_birth": "1970-05-15",
                    "ssn_last_four": "1234",
                    "is_married": 1,  # 0 or 1
                    "spouse_first_name": "Jane",  # optional
                    "spouse_last_name": "Doe",    # optional
                    "spouse_dob": "1972-08-22",   # optional
                    "spouse_ssn_last_four": "5678", # optional
                    "monthly_salary": 15000.00,
                    "agreed_expense_budget": 11000.00,
                    "private_reserve_target": 0,  # auto-calculated if 0
                    "retirement_accounts": [],    # list of dicts
                    "non_retirement_accounts": [], # list of dicts
                    "trust_info": {},             # dict
                    "liabilities": [],            # list of dicts
                    "notes": ""                   # text
                }
        
        Returns:
            int: The new client's ID
        
        Raises:
            ValueError: If required fields are missing
        """
        # Validate required fields
        required = ["first_name", "last_name", "date_of_birth", "ssn_last_four"]
        for field in required:
            if not data.get(field):
                raise ValueError(f"Required field missing: {field}")
        
        # Serialize JSON fields
        retirement = json.dumps(data.get("retirement_accounts", []))
        non_retirement = json.dumps(data.get("non_retirement_accounts", []))
        trust = json.dumps(data.get("trust_info", {}))
        liabilities = json.dumps(data.get("liabilities", []))
        
        query = """
            INSERT INTO clients (
                first_name, last_name, date_of_birth, ssn_last_four,
                is_married, spouse_first_name, spouse_last_name,
                spouse_dob, spouse_ssn_last_four,
                monthly_salary, agreed_expense_budget, private_reserve_target,
                retirement_accounts, non_retirement_accounts, trust_info, liabilities,
                notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            data["first_name"], data["last_name"], data["date_of_birth"],
            data["ssn_last_four"], data.get("is_married", 0),
            data.get("spouse_first_name"), data.get("spouse_last_name"),
            data.get("spouse_dob"), data.get("spouse_ssn_last_four"),
            float(data.get("monthly_salary", 0)),
            float(data.get("agreed_expense_budget", 0)),
            float(data.get("private_reserve_target", 0)),
            retirement, non_retirement, trust, liabilities,
            data.get("notes", "")
        )
        
        return execute_query(query, params)
    
    
    # ============================================
    # READ
    # ============================================
    
    @classmethod
    def get_by_id(cls, client_id):
        """
        Retrieve a single client by ID.
        
        Args:
            client_id (int): The client's primary key
        
        Returns:
            dict: Client data with JSON fields parsed, or None if not found
        """
        query = "SELECT * FROM clients WHERE id = ?"
        result = execute_query(query, (client_id,), fetch_one=True)
        
        if result:
            # Parse JSON fields back to Python objects
            result = cls._parse_json_fields(result)
        
        return result
    
    
    @classmethod
    def get_all(cls):
        """
        Retrieve all clients, ordered by last name then first name.
        
        Returns:
            list: List of client dictionaries, each with JSON fields parsed
        """
        query = "SELECT * FROM clients ORDER BY last_name, first_name"
        results = execute_query(query)
        
        return [cls._parse_json_fields(r) for r in results]
    
    
    @classmethod
    def get_last_report_date(cls, client_id):
        """
        Get the most recent report date for a client.
        
        Args:
            client_id (int): The client's ID
        
        Returns:
            dict: {quarter, year, created_at} or None
        """
        query = """
            SELECT quarter, year, MAX(created_at) as last_report_date
            FROM reports
            WHERE client_id = ?
            GROUP BY client_id
        """
        return execute_query(query, (client_id,), fetch_one=True)
    
    
    # ============================================
    # UPDATE
    # ============================================
    
    @classmethod
    def update(cls, client_id, data):
        """
        Update client profile fields.
        Only updates fields provided in data dictionary.
        
        Args:
            client_id (int): Client to update
            data (dict): Fields to update (partial update supported)
        
        Returns:
            bool: True if successful
        """
        # Get existing client
        existing = cls.get_by_id(client_id)
        if not existing:
            raise ValueError(f"Client {client_id} not found")
        
        # Build dynamic update query (only update provided fields)
        updates = []
        params = []
        
        for field in cls.COLUMNS:
            if field in data:
                # Handle boolean conversion
                if field == "is_married":
                    data[field] = 1 if data[field] else 0
                
                # Serialize JSON fields
                if field in ["retirement_accounts", "non_retirement_accounts", "trust_info", "liabilities"]:
                    data[field] = json.dumps(data[field])
                
                updates.append(f"{field} = ?")
                params.append(data[field])
        
        if not updates:
            return True  # Nothing to update
        
        query = f"UPDATE clients SET {', '.join(updates)} WHERE id = ?"
        params.append(client_id)
        
        execute_query(query, tuple(params))
        return True
    
    
    # ============================================
    # DELETE
    # ============================================
    
    @classmethod
    def delete(cls, client_id):
        """
        Delete a client and all associated reports (cascade).
        
        Args:
            client_id (int): Client to delete
        
        Returns:
            bool: True if deleted
        """
        # Due to ON DELETE CASCADE in reports table, 
        # all reports for this client will be auto-deleted
        query = "DELETE FROM clients WHERE id = ?"
        execute_query(query, (client_id,))
        return True
    
    
    # ============================================
    # HELPER METHODS
    # ============================================
    
    @classmethod
    def _parse_json_fields(cls, record):
        """
        Parse JSON string fields back to Python objects.
        Also calculate age from DOB.
        """
        json_fields = ["retirement_accounts", "non_retirement_accounts", "trust_info", "liabilities"]
        
        for field in json_fields:
            if field in record and record[field]:
                try:
                    record[field] = json.loads(record[field])
                except (json.JSONDecodeError, TypeError):
                    record[field] = {} if field == "trust_info" else []
        
        # Calculate age from DOB
        if record.get("date_of_birth"):
            try:
                from datetime import datetime
                dob = datetime.strptime(record["date_of_birth"], "%Y-%m-%d")
                today = datetime.now()
                age = today.year - dob.year
                if today.month < dob.month or (today.month == dob.month and today.day < dob.day):
                    age -= 1
                record["age"] = age
            except (ValueError, TypeError):
                record["age"] = None
        
        return record
    
    
    @classmethod
    def get_account_names(cls, client):
        """
        Extract a flat list of account display names for forms.
        
        Returns a list of dicts like:
            [
                {"id": "ira_1", "name": "Client 1 IRA", "type": "retirement", "is_spouse": False},
                ...
            ]
        """
        accounts = []
        
        # Client 1 retirement accounts
        for idx, acc in enumerate(client.get("retirement_accounts", []), 1):
            acc_type = acc.get("type", "Retirement Account")
            accounts.append({
                "id": f"c1_ret_{idx}",
                "name": f"Client 1 {acc_type}",
                "type": "retirement",
                "is_spouse": False
            })
        
        # Client 2 (spouse) retirement accounts
        for idx, acc in enumerate(client.get("retirement_accounts", []), 1):
            if client.get("is_married"):
                # Note: In a real app, we'd track which accounts belong to whom
                # For now, we assume the same accounts structure for illustration
                acc_type = acc.get("type", "Retirement Account")
                accounts.append({
                    "id": f"c2_ret_{idx}",
                    "name": f"Client 2 {acc_type}",
                    "type": "retirement",
                    "is_spouse": True
                })
        
        # Non-retirement accounts
        for idx, acc in enumerate(client.get("non_retirement_accounts", []), 1):
            acc_type = acc.get("type", "Brokerage")
            accounts.append({
                "id": f"non_ret_{idx}",
                "name": f"{acc_type}",
                "type": "non_retirement",
                "is_joint": True
            })
        
        return accounts
