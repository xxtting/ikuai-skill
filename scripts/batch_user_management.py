#!/usr/bin/env python3
"""
Batch User Management for iKuai Routers

Provides batch operations for managing user accounts including import/export,
bulk enable/disable, and batch deletion.
"""

import csv
import json
from typing import List, Dict, Any
from ikuai_api_client import IkuaiAPIClient


class BatchUserManager:
    """Manager for batch user operations on iKuai routers."""
    
    def __init__(self, client: IkuaiAPIClient, dev_id: str):
        """
        Initialize batch user manager.
        
        Args:
            client: IkuaiAPIClient instance
            dev_id: Device ID of the router
        """
        self.client = client
        self.dev_id = dev_id
        self.results = []
    
    def import_users_from_csv(
        self,
        csv_file: str,
        dry_run: bool = True,
        skip_existing: bool = True
    ) -> Dict[str, Any]:
        """
        Import users from CSV file.
        
        CSV Format:
        username,password,group,comments
        user1,password123,default,Department A
        user2,pass456,default,Department B
        
        Args:
            csv_file: Path to CSV file
            dry_run: If True, only validate without creating users
            skip_existing: If True, skip users that already exist
            
        Returns:
            Dictionary with import results
        """
        results = {
            'success': [],
            'failed': [],
            'skipped': [],
            'total': 0
        }
        
        try:
            # Get existing accounts
            existing_accounts = set()
            if skip_existing:
                accounts_resp = self.client.get_accounts(self.dev_id)
                if accounts_resp.get('errno') == 0 and 'data' in accounts_resp:
                    for account in accounts_resp['data']:
                        existing_accounts.add(account.get('username'))
            
            # Read CSV file
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    results['total'] += 1
                    username = row.get('username', '').strip()
                    password = row.get('password', '').strip()
                    group = row.get('group', 'default').strip()
                    comments = row.get('comments', '').strip()
                    
                    # Validate required fields
                    if not username or not password:
                        results['failed'].append({
                            'username': username,
                            'error': 'Missing username or password'
                        })
                        continue
                    
                    # Check if account exists
                    if skip_existing and username in existing_accounts:
                        results['skipped'].append({
                            'username': username,
                            'reason': 'Account already exists'
                        })
                        continue
                    
                    if dry_run:
                        # Dry run - just validate
                        results['success'].append({
                            'username': username,
                            'action': 'validated (dry run)'
                        })
                    else:
                        # Create account
                        try:
                            resp = self.client.add_account(
                                self.dev_id,
                                username=username,
                                password=password,
                                group=group,
                                comments=comments
                            )
                            
                            if resp.get('errno') == 0:
                                results['success'].append({
                                    'username': username,
                                    'action': 'created'
                                })
                                existing_accounts.add(username)
                            else:
                                results['failed'].append({
                                    'username': username,
                                    'error': resp.get('errmsg', 'Unknown error')
                                })
                                
                        except Exception as e:
                            results['failed'].append({
                                'username': username,
                                'error': str(e)
                            })
            
            print(f"\n✓ Import completed: {len(results['success'])} success, "
                  f"{len(results['failed'])} failed, {len(results['skipped'])} skipped")
            
            return results
            
        except FileNotFoundError:
            raise Exception(f"CSV file not found: {csv_file}")
        except Exception as e:
            raise Exception(f"Import failed: {str(e)}")
    
    def export_users_to_csv(self, csv_file: str) -> Dict[str, Any]:
        """
        Export all users to CSV file.
        
        Args:
            csv_file: Path to output CSV file
            
        Returns:
            Export results
        """
        try:
            # Get all accounts
            accounts_resp = self.client.get_accounts(self.dev_id)
            
            if accounts_resp.get('errno') != 0:
                raise Exception(f"Failed to get accounts: {accounts_resp.get('errmsg')}")
            
            accounts = accounts_resp.get('data', [])
            
            # Write to CSV
            with open(csv_file, 'w', encoding='utf-8', newline='') as f:
                fieldnames = ['username', 'group', 'comments', 'upload_speed', 'download_speed', 'status']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for account in accounts:
                    writer.writerow({
                        'username': account.get('username', ''),
                        'group': account.get('group', ''),
                        'comments': account.get('comments', ''),
                        'upload_speed': account.get('up_speed', 0),
                        'download_speed': account.get('down_speed', 0),
                        'status': account.get('state', '')
                    })
            
            result = {
                'success': True,
                'file': csv_file,
                'count': len(accounts)
            }
            
            print(f"✓ Exported {len(accounts)} users to {csv_file}")
            return result
            
        except Exception as e:
            raise Exception(f"Export failed: {str(e)}")
    
    def bulk_enable_accounts(self, usernames: List[str]) -> Dict[str, Any]:
        """
        Bulk enable user accounts.
        
        Args:
            usernames: List of usernames to enable
            
        Returns:
            Dictionary with enable results
        """
        results = {
            'success': [],
            'failed': []
        }
        
        # Get all accounts to find account IDs
        accounts_resp = self.client.get_accounts(self.dev_id)
        
        if accounts_resp.get('errno') != 0:
            raise Exception(f"Failed to get accounts: {accounts_resp.get('errmsg')}")
        
        # Create username to account_id mapping
        accounts = accounts_resp.get('data', [])
        username_to_id = {acc.get('username'): acc.get('id') for acc in accounts}
        
        for username in usernames:
            account_id = username_to_id.get(username)
            
            if not account_id:
                results['failed'].append({
                    'username': username,
                    'error': 'Account not found'
                })
                continue
            
            try:
                resp = self.client.enable_account(self.dev_id, account_id)
                
                if resp.get('errno') == 0:
                    results['success'].append({
                        'username': username,
                        'account_id': account_id
                    })
                else:
                    results['failed'].append({
                        'username': username,
                        'error': resp.get('errmsg', 'Unknown error')
                    })
                    
            except Exception as e:
                results['failed'].append({
                    'username': username,
                    'error': str(e)
                })
        
        print(f"✓ Bulk enable: {len(results['success'])} success, {len(results['failed'])} failed")
        return results
    
    def bulk_disable_accounts(self, usernames: List[str]) -> Dict[str, Any]:
        """
        Bulk disable user accounts.
        
        Args:
            usernames: List of usernames to disable
            
        Returns:
            Dictionary with disable results
        """
        results = {
            'success': [],
            'failed': []
        }
        
        # Get all accounts to find account IDs
        accounts_resp = self.client.get_accounts(self.dev_id)
        
        if accounts_resp.get('errno') != 0:
            raise Exception(f"Failed to get accounts: {accounts_resp.get('errmsg')}")
        
        # Create username to account_id mapping
        accounts = accounts_resp.get('data', [])
        username_to_id = {acc.get('username'): acc.get('id') for acc in accounts}
        
        for username in usernames:
            account_id = username_to_id.get(username)
            
            if not account_id:
                results['failed'].append({
                    'username': username,
                    'error': 'Account not found'
                })
                continue
            
            try:
                resp = self.client.disable_account(self.dev_id, account_id)
                
                if resp.get('errno') == 0:
                    results['success'].append({
                        'username': username,
                        'account_id': account_id
                    })
                else:
                    results['failed'].append({
                        'username': username,
                        'error': resp.get('errmsg', 'Unknown error')
                    })
                    
            except Exception as e:
                results['failed'].append({
                    'username': username,
                    'error': str(e)
                })
        
        print(f"✓ Bulk disable: {len(results['success'])} success, {len(results['failed'])} failed")
        return results
    
    def bulk_delete_accounts(self, usernames: List[str], confirm: bool = False) -> Dict[str, Any]:
        """
        Bulk delete user accounts.
        
        WARNING: This action cannot be undone.
        
        Args:
            usernames: List of usernames to delete
            confirm: Must be True to confirm deletion
            
        Returns:
            Dictionary with deletion results
        """
        if not confirm:
            raise Exception("Deletion not confirmed. Set confirm=True to proceed.")
        
        results = {
            'success': [],
            'failed': []
        }
        
        # Get all accounts to find account IDs
        accounts_resp = self.client.get_accounts(self.dev_id)
        
        if accounts_resp.get('errno') != 0:
            raise Exception(f"Failed to get accounts: {accounts_resp.get('errmsg')}")
        
        # Create username to account_id mapping
        accounts = accounts_resp.get('data', [])
        username_to_id = {acc.get('username'): acc.get('id') for acc in accounts}
        
        print(f"⚠ WARNING: Deleting {len(usernames)} accounts - this cannot be undone!")
        
        for username in usernames:
            account_id = username_to_id.get(username)
            
            if not account_id:
                results['failed'].append({
                    'username': username,
                    'error': 'Account not found'
                })
                continue
            
            try:
                resp = self.client.delete_account(self.dev_id, account_id)
                
                if resp.get('errno') == 0:
                    results['success'].append({
                        'username': username,
                        'account_id': account_id
                    })
                    print(f"  ✓ Deleted: {username}")
                else:
                    results['failed'].append({
                        'username': username,
                        'error': resp.get('errmsg', 'Unknown error')
                    })
                    print(f"  ✗ Failed to delete: {username}")
                    
            except Exception as e:
                results['failed'].append({
                    'username': username,
                    'error': str(e)
                })
                print(f"  ✗ Failed to delete: {username} - {str(e)}")
        
        print(f"\n✓ Bulk delete: {len(results['success'])} success, {len(results['failed'])} failed")
        return results
    
    def get_accounts_by_group(self, group_name: str) -> List[Dict[str, Any]]:
        """
        Get all accounts belonging to a specific group.
        
        Args:
            group_name: Name of the group
            
        Returns:
            List of accounts in the group
        """
        accounts_resp = self.client.get_accounts(self.dev_id)
        
        if accounts_resp.get('errno') != 0:
            raise Exception(f"Failed to get accounts: {accounts_resp.get('errmsg')}")
        
        accounts = accounts_resp.get('data', [])
        
        filtered_accounts = [
            acc for acc in accounts if acc.get('group') == group_name
        ]
        
        print(f"✓ Found {len(filtered_accounts)} accounts in group '{group_name}'")
        return filtered_accounts
    
    def generate_user_report(self, output_file: str = None) -> Dict[str, Any]:
        """
        Generate a comprehensive user report.
        
        Args:
            output_file: Optional file path to save report
            
        Returns:
            Report data
        """
        # Get accounts and online users
        accounts_resp = self.client.get_accounts(self.dev_id)
        online_resp = self.client.get_online_users(self.dev_id)
        
        if accounts_resp.get('errno') != 0 or online_resp.get('errno') != 0:
            raise Exception("Failed to retrieve data")
        
        accounts = accounts_resp.get('data', [])
        online_users = online_resp.get('data', [])
        
        # Generate report
        report = {
            'summary': {
                'total_accounts': len(accounts),
                'total_online': len(online_users),
                'enabled_accounts': len([a for a in accounts if a.get('state') == 'up']),
                'disabled_accounts': len([a for a in accounts if a.get('state') == 'down']),
                'groups': list(set(acc.get('group') for acc in accounts if acc.get('group')))
            },
            'accounts': accounts,
            'online_users': online_users,
            'generated_at': str(datetime.now())
        }
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"✓ Report saved to {output_file}")
        
        print(f"\n=== User Report ===")
        print(f"Total Accounts: {report['summary']['total_accounts']}")
        print(f"Online Users: {report['summary']['total_online']}")
        print(f"Enabled: {report['summary']['enabled_accounts']}")
        print(f"Disabled: {report['summary']['disabled_accounts']}")
        print(f"Groups: {', '.join(report['summary']['groups'])}")
        
        return report


def main():
    """Example usage."""
    from datetime import datetime
    
    APP_ID = "your_app_id"
    APP_SECRET = "your_app_secret"
    DEV_ID = "your_device_id"
    
    # Initialize client and manager
    client = IkuaiAPIClient(APP_ID, APP_SECRET)
    client.get_access_token()
    
    manager = BatchUserManager(client, DEV_ID)
    
    try:
        # Example: Import users from CSV
        print("\n=== Import Users ===")
        results = manager.import_users_from_csv(
            'users.csv',
            dry_run=True  # Set to False to actually create users
        )
        print(f"Results: {json.dumps(results, indent=2, ensure_ascii=False)}")
        
        # Example: Export users to CSV
        print("\n=== Export Users ===")
        manager.export_users_to_csv('users_export.csv')
        
        # Example: Bulk enable accounts
        print("\n=== Bulk Enable ===")
        manager.bulk_enable_accounts(['user1', 'user2'])
        
        # Example: Generate report
        print("\n=== Generate Report ===")
        manager.generate_user_report('user_report.json')
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
