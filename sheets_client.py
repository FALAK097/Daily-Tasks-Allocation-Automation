import os
import datetime
from typing import List, Tuple, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build

class SheetsClient:
    def __init__(self):
        self.sheet_url = os.getenv("SHEET_URL")
        self.service_account_file = os.getenv("SERVICE_ACCOUNT_FILE")
        self.sheet_id = self.sheet_url.split('/d/')[1].split('/')[0]
        self.service = self._create_service()

    def _create_service(self):
        creds = service_account.Credentials.from_service_account_file(
            self.service_account_file, 
            scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
        )
        return build('sheets', 'v4', credentials=creds)

    def get_sheet_data(self, date: datetime.date) -> List[List[str]]:
        target_date = date.strftime("%d %B")
        gid, sheet_name = self._get_sheet_info(target_date)
        
        if not sheet_name:
            print(f"No sheet found for date: {target_date}")
            return []

        try:
            range_name = f"'{sheet_name}'!A1:Z1000"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=range_name
            ).execute()
            return result.get('values', [])
        except Exception as e:
            print(f"Error fetching data: {e}")
            return []

    def _get_sheet_info(self, target_date: str) -> Tuple[Optional[str], Optional[str]]:
        try:
            sheets_metadata = self.service.spreadsheets().get(
                spreadsheetId=self.sheet_id
            ).execute()
            
            for sheet in sheets_metadata['sheets']:
                if target_date in sheet['properties']['title']:
                    return (
                        str(sheet['properties']['sheetId']),
                        sheet['properties']['title']
                    )
            return None, None
        except Exception as e:
            print(f"Error fetching sheet metadata: {e}")
            return None, None
