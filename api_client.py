import requests
import json
import logging

class TaqticsAPIClient:
    def __init__(self, subdomain, username, password):
        self.base_url = f"https://{subdomain}"
        self.username = username
        self.password = password
        self.token = None
        self.headers = {
            "Content-Type": "application/json"
        }

    def authenticate(self):
        """
        Authenticates with the Taqtics API and retrieves a JWT token.
        POST /api/v1/external/auth
        """
        url = f"{self.base_url}/api/v1/external/auth"
        payload = {
            "email": self.username,
            "password": self.password
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            if response.status_code != 200:
                logging.error(f"Auth failed with status {response.status_code}: {response.text}")
            response.raise_for_status()
            data = response.json()
            # The API returns 'token' instead of 'access-token' in the auth response
            self.token = data.get("token") or data.get("access-token")
            if not self.token:
                raise ValueError("Authentication successful but no token received in response.")
            
            # Update headers with token for subsequent requests
            self.headers["access-token"] = self.token
            logging.info("Successfully authenticated with Taqtics API.")
            return True
        except Exception as e:
            logging.error(f"Authentication failed: {e}")
            raise

    def get_csv_for_form(self, form_id, month_year):
        """
        Fetches the CSV for a specific form and month.
        The API returns a JSON with a 'url' to the actual CSV blob.
        """
        url = f"{self.base_url}/api/v1/external/blobs/csvs/monthly"
        params = {
            "formId": form_id,
            "monthYear": month_year
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 404:
                logging.warning(f"No data found for form {form_id} in {month_year}")
                return ""
            
            response.raise_for_status()
            data = response.json()
            logging.info(f"API Response for {form_id}/{month_year}: {data}")
            # The API uses 'fileUrl' for the CSV blob
            blob_url = data.get("fileUrl") or data.get("url")
            
            if not blob_url:
                logging.warning(f"No blob URL received for form {form_id} in {month_year}")
                return ""
            
            logging.info(f"Downloading CSV blob from: {blob_url[:50]}...")
            csv_response = requests.get(blob_url)
            csv_response.raise_for_status()
            content = csv_response.text
            logging.info(f"Downloaded {len(content)} characters for form {form_id}")
            return content
        except Exception as e:
            logging.error(f"Failed to fetch CSV for form {form_id}: {e}")
            return ""

    def get_monthly_csv(self, form_ids, month_year):
        """
        Iterates through all form IDs and combines their CSV data.
        """
        if not self.token:
            self.authenticate()

        combined_csv_content = ""
        header_added = False
        
        for form_id in form_ids:
            content = self.get_csv_for_form(form_id, month_year)
            if not content:
                continue
            
            lines = content.strip().splitlines()
            if not lines:
                continue
            
            if not header_added:
                combined_csv_content = content
                header_added = True
            else:
                # Add rows without the header
                combined_csv_content += "\n" + "\n".join(lines[1:])
        
        return combined_csv_content
