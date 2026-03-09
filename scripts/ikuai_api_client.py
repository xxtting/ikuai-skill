#!/usr/bin/env python3
"""
iKuai OpenAPI Client Library

Provides a Python interface for interacting with iKuai router OpenAPI.
Supports both router 2.x and 3.x API versions.
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta


class IkuaiAPIClient:
    """Client for iKuai OpenAPI interactions."""
    
    # API Endpoints
    BASE_URL = "https://open.ikuai8.com"
    TOKEN_URL = f"{BASE_URL}/api/v1/token"
    
    # API IDs for Router 2.x
    API_IDS = {
        'get_accounts': 1,
        'kick_user': 3,
        'get_online_users': 4,
        'add_account': 5,
        'modify_account': 6,
        'enable_disable_account': 7,
        'delete_account': 8,
        'get_router_status': 9,
        'set_whitelist': 10,
        'query_account': 11,
    }
    
    def __init__(self, app_id: str, app_secret: str, api_version: str = "2.x"):
        """
        Initialize the iKuai API client.
        
        Args:
            app_id: Application ID from iKuai OpenAPI
            app_secret: Application secret key
            api_version: Router API version ("2.x" or "3.x")
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.api_version = api_version
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        self.open_id = None
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'iKuaiAPIClient/1.0'
        })
    
    def get_access_token(self) -> Dict[str, Any]:
        """
        Obtain access token from iKuai OpenAPI.
        
        Returns:
            Dictionary containing token information
            
        Raises:
            Exception: If token request fails
        """
        payload = {
            'app_id': self.app_id,
            'app_secret': self.app_secret
        }
        
        try:
            response = self.session.post(
                self.TOKEN_URL,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('errno') == 0:
                self.access_token = data.get('data', {}).get('access_token')
                self.refresh_token = data.get('data', {}).get('refresh_token')
                expires_in = data.get('data', {}).get('expires_in', 3600)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)  # Refresh 5 min before expiry
                self.open_id = data.get('data', {}).get('open_id')
                
                print(f"✓ Access token obtained, expires at {self.token_expires_at}")
                return data
            else:
                raise Exception(f"Failed to get token: {data.get('errmsg')}")
                
        except requests.RequestException as e:
            raise Exception(f"Network error while getting token: {str(e)}")
    
    def refresh_access_token(self) -> Dict[str, Any]:
        """
        Refresh access token using refresh token.
        
        Returns:
            Dictionary containing new token information
        """
        if not self.refresh_token:
            raise Exception("No refresh token available")
        
        payload = {
            'refresh_token': self.refresh_token
        }
        
        try:
            response = self.session.post(
                f"{self.BASE_URL}/api/v1/token/refresh",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('errno') == 0:
                self.access_token = data.get('data', {}).get('access_token')
                self.refresh_token = data.get('data', {}).get('refresh_token')
                expires_in = data.get('data', {}).get('expires_in', 3600)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)
                
                print("✓ Access token refreshed")
                return data
            else:
                raise Exception(f"Failed to refresh token: {data.get('errmsg')}")
                
        except requests.RequestException as e:
            raise Exception(f"Network error while refreshing token: {str(e)}")
    
    def _ensure_token_valid(self):
        """Ensure access token is valid, refresh if necessary."""
        if not self.access_token or (self.token_expires_at and datetime.now() >= self.token_expires_at):
            print("Token expired or missing, refreshing...")
            self.get_access_token()
    
    def _make_api_call(
        self,
        dev_id: str,
        api_id: int,
        data: Optional[Dict[str, Any]] = None,
        method: str = "POST"
    ) -> Dict[str, Any]:
        """
        Make an API call to iKuai router.
        
        Args:
            dev_id: Device ID of the router
            api_id: API ID for the specific operation
            data: Request payload data
            method: HTTP method (POST or GET)
            
        Returns:
            API response dictionary
        """
        self._ensure_token_valid()
        
        if not self.open_id:
            raise Exception("Open ID not available, please get access token first")
        
        # Construct API URL
        api_url = f"{self.BASE_URL}/apis/action/{self.open_id}/{dev_id}/{api_id}"
        
        # Set authorization header
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        
        try:
            if method.upper() == 'POST':
                response = self.session.post(
                    api_url,
                    json=data or {},
                    headers=headers,
                    timeout=30
                )
            else:
                response = self.session.get(
                    api_url,
                    params=data or {},
                    headers=headers,
                    timeout=30
                )
            
            response.raise_for_status()
            result = response.json()
            
            # Check for errors
            if result.get('errno') != 0:
                print(f"⚠ API Error (errno={result.get('errno')}): {result.get('errmsg')}")
            
            return result
            
        except requests.RequestException as e:
            raise Exception(f"API call failed: {str(e)}")
    
    def get_accounts(self, dev_id: str) -> Dict[str, Any]:
        """
        Get list of all user accounts.
        
        Args:
            dev_id: Device ID
            
        Returns:
            Account list data
        """
        return self._make_api_call(dev_id, self.API_IDS['get_accounts'])
    
    def get_online_users(self, dev_id: str) -> Dict[str, Any]:
        """
        Get list of currently online users.
        
        Args:
            dev_id: Device ID
            
        Returns:
            Online users data
        """
        return self._make_api_call(dev_id, self.API_IDS['get_online_users'])
    
    def kick_user(self, dev_id: str, account_id: str) -> Dict[str, Any]:
        """
        Kick a user offline.
        
        Args:
            dev_id: Device ID
            account_id: Account ID to kick
            
        Returns:
            API response
        """
        data = {
            'id': account_id
        }
        return self._make_api_call(dev_id, self.API_IDS['kick_user'], data)
    
    def add_account(
        self,
        dev_id: str,
        username: str,
        password: str,
        group: str = "default",
        comments: str = ""
    ) -> Dict[str, Any]:
        """
        Add a new user account.
        
        Args:
            dev_id: Device ID
            username: New account username
            password: Account password
            group: User group (default: "default")
            comments: Account description/notes
            
        Returns:
            API response
        """
        data = {
            'username': username,
            'password': password,
            'group': group,
            'comments': comments
        }
        return self._make_api_call(dev_id, self.API_IDS['add_account'], data)
    
    def modify_account(
        self,
        dev_id: str,
        account_id: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        group: Optional[str] = None,
        comments: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Modify an existing user account.
        
        Args:
            dev_id: Device ID
            account_id: Account ID to modify
            username: New username (optional)
            password: New password (optional)
            group: New group (optional)
            comments: New comments (optional)
            
        Returns:
            API response
        """
        data = {
            'id': account_id
        }
        
        if username is not None:
            data['username'] = username
        if password is not None:
            data['password'] = password
        if group is not None:
            data['group'] = group
        if comments is not None:
            data['comments'] = comments
        
        return self._make_api_call(dev_id, self.API_IDS['modify_account'], data)
    
    def enable_account(self, dev_id: str, account_id: str) -> Dict[str, Any]:
        """
        Enable a user account.
        
        Args:
            dev_id: Device ID
            account_id: Account ID to enable
            
        Returns:
            API response
        """
        data = {
            'id': account_id,
            'state': 'up'
        }
        return self._make_api_call(dev_id, self.API_IDS['enable_disable_account'], data)
    
    def disable_account(self, dev_id: str, account_id: str) -> Dict[str, Any]:
        """
        Disable a user account.
        
        Args:
            dev_id: Device ID
            account_id: Account ID to disable
            
        Returns:
            API response
        """
        data = {
            'id': account_id,
            'state': 'down'
        }
        return self._make_api_call(dev_id, self.API_IDS['enable_disable_account'], data)
    
    def delete_account(self, dev_id: str, account_id: str) -> Dict[str, Any]:
        """
        Delete a user account.
        
        Args:
            dev_id: Device ID
            account_id: Account ID to delete
            
        Returns:
            API response
        """
        data = {
            'id': account_id
        }
        return self._make_api_call(dev_id, self.API_IDS['delete_account'], data)
    
    def query_account(self, dev_id: str, account_id: str) -> Dict[str, Any]:
        """
        Query details of a specific account.
        
        Args:
            dev_id: Device ID
            account_id: Account ID to query
            
        Returns:
            Account details
        """
        data = {
            'id': account_id
        }
        return self._make_api_call(dev_id, self.API_IDS['query_account'], data)
    
    def get_router_status(self, dev_id: str) -> Dict[str, Any]:
        """
        Get router status information.
        
        Args:
            dev_id: Device ID
            
        Returns:
            Router status data
        """
        return self._make_api_call(dev_id, self.API_IDS['get_router_status'])
    
    def set_whitelist(self, dev_id: str, whitelist_data: str) -> Dict[str, Any]:
        """
        Set router whitelist.
        
        Args:
            dev_id: Device ID
            whitelist_data: Whitelist configuration data
            
        Returns:
            API response
        """
        data = {
            'data': whitelist_data
        }
        return self._make_api_call(dev_id, self.API_IDS['set_whitelist'], data)
    
    def batch_kick_users(self, dev_id: str, account_ids: List[str]) -> Dict[str, Any]:
        """
        Kick multiple users offline.
        
        Args:
            dev_id: Device ID
            account_ids: List of account IDs to kick
            
        Returns:
            Dictionary with results for each account
        """
        results = {}
        for account_id in account_ids:
            results[account_id] = self.kick_user(dev_id, account_id)
        return results
    
    def close(self):
        """Close the session."""
        self.session.close()


def main():
    """Example usage of IkuaiAPIClient."""
    # Configuration
    APP_ID = "your_app_id"
    APP_SECRET = "your_app_secret"
    DEV_ID = "your_device_id"
    
    # Initialize client
    client = IkuaiAPIClient(APP_ID, APP_SECRET)
    
    try:
        # Get access token
        client.get_access_token()
        
        # Get router status
        print("\n=== Router Status ===")
        status = client.get_router_status(DEV_ID)
        print(json.dumps(status, indent=2, ensure_ascii=False))
        
        # Get online users
        print("\n=== Online Users ===")
        online = client.get_online_users(DEV_ID)
        print(json.dumps(online, indent=2, ensure_ascii=False))
        
        # Get all accounts
        print("\n=== All Accounts ===")
        accounts = client.get_accounts(DEV_ID)
        print(json.dumps(accounts, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
