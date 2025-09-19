import requests
import zipfile
import json
import io
import os
import time
import pandas as pd
from dotenv import load_dotenv

class QualtricsExporter:
    def __init__(self):
        load_dotenv()
        self.api_token = os.getenv('QUALTRICS_API_TOKEN')
        self.data_center = os.getenv('QUALTRICS_DATACENTER_ID')
        self.org_id = os.getenv('QUALTRICS_ORG_ID')

        if not all([self.api_token, self.data_center]):
            raise ValueError("Missing required environment variables. Check your .env file.")

        self.base_url = f"https://{self.data_center}.qualtrics.com/API/v3"
        self.headers = {
            "content-type": "application/json",
            "x-api-token": self.api_token,
        }

    def get_surveys(self):
        """Get list of all surveys in the account"""
        url = f"{self.base_url}/surveys"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            surveys = response.json()['result']['elements']
            return surveys
        else:
            print(f"Error getting surveys: {response.status_code}")
            print(response.text)
            return []

    def find_survey_by_name(self, survey_name):
        """Find survey by name (case-insensitive partial match)"""
        surveys = self.get_surveys()
        survey_name_lower = survey_name.lower()

        for survey in surveys:
            if survey_name_lower in survey['name'].lower():
                return survey
        return None

    def create_response_export(self, survey_id, file_format="csv", use_labels=True):
        """Create a response export request"""
        url = f"{self.base_url}/surveys/{survey_id}/export-responses"

        payload = {
            "format": file_format,
            "useLabels": use_labels,
            "compress": True
        }

        response = requests.post(url, json=payload, headers=self.headers)

        if response.status_code == 200:
            return response.json()['result']['progressId']
        else:
            print(f"Error creating export: {response.status_code}")
            print(response.text)
            return None

    def check_export_progress(self, survey_id, progress_id):
        """Check the progress of an export request"""
        url = f"{self.base_url}/surveys/{survey_id}/export-responses/{progress_id}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()['result']
        else:
            print(f"Error checking progress: {response.status_code}")
            print(response.text)
            return None

    def download_export_file(self, survey_id, file_id):
        """Download the exported file"""
        url = f"{self.base_url}/surveys/{survey_id}/export-responses/{file_id}/file"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.content
        else:
            print(f"Error downloading file: {response.status_code}")
            print(response.text)
            return None

    def export_survey_to_csv(self, survey_id, output_filename=None, max_wait_time=300):
        """
        Complete workflow to export survey responses to CSV

        Args:
            survey_id: The Qualtrics survey ID
            output_filename: Name of output CSV file (optional)
            max_wait_time: Maximum time to wait for export completion (seconds)
        """
        print(f"Starting export for survey ID: {survey_id}")

        # Create export request
        progress_id = self.create_response_export(survey_id)
        if not progress_id:
            return False

        print(f"Export request created. Progress ID: {progress_id}")
        print("Waiting for export to complete...")

        # Poll for completion
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            progress = self.check_export_progress(survey_id, progress_id)
            if not progress:
                return False

            status = progress.get('status')
            print(f"Export status: {status}")

            if status == 'complete':
                file_id = progress.get('fileId')
                if file_id:
                    # Download the file
                    file_content = self.download_export_file(survey_id, file_id)
                    if file_content:
                        # Extract ZIP file and save CSV
                        return self._save_csv_from_zip(file_content, survey_id, output_filename)
                break
            elif status == 'failed':
                print("Export failed!")
                return False

            time.sleep(5)  # Wait 5 seconds before checking again

        print("Export timed out!")
        return False

    def _save_csv_from_zip(self, zip_content, survey_id, output_filename=None):
        """Extract CSV from ZIP content and save to file"""
        try:
            with zipfile.ZipFile(io.BytesIO(zip_content)) as zip_file:
                # Get the first (and usually only) file in the ZIP
                csv_filename = zip_file.namelist()[0]
                csv_content = zip_file.read(csv_filename)

                # Determine output filename
                if not output_filename:
                    output_filename = f"survey_{survey_id}_responses.csv"

                # Save CSV file
                with open(output_filename, 'wb') as f:
                    f.write(csv_content)

                print(f"Successfully saved survey responses to: {output_filename}")

                # Also load and display basic info about the data
                df = pd.read_csv(output_filename)
                print(f"Exported {len(df)} responses with {len(df.columns)} columns")
                print(f"Columns: {list(df.columns[:10])}{'...' if len(df.columns) > 10 else ''}")

                return True

        except Exception as e:
            print(f"Error extracting CSV from ZIP: {e}")
            return False

    def list_surveys_interactive(self):
        """List all surveys and let user choose which to export"""
        surveys = self.get_surveys()
        if not surveys:
            print("No surveys found or unable to fetch surveys.")
            return

        print("\nAvailable surveys:")
        print("-" * 80)
        for i, survey in enumerate(surveys):
            print(f"{i+1:2d}. {survey['name'][:60]:<60} ID: {survey['id']}")

        print("-" * 80)

        while True:
            try:
                choice = input(f"\nEnter survey number (1-{len(surveys)}) or 'q' to quit: ").strip()
                if choice.lower() == 'q':
                    return

                survey_index = int(choice) - 1
                if 0 <= survey_index < len(surveys):
                    selected_survey = surveys[survey_index]
                    print(f"\nSelected: {selected_survey['name']}")

                    # Ask for filename
                    filename = input("Enter output filename (press Enter for default): ").strip()
                    if not filename:
                        filename = None

                    # Export the survey
                    success = self.export_survey_to_csv(
                        selected_survey['id'],
                        filename
                    )

                    if success:
                        print("Export completed successfully!")
                    else:
                        print("Export failed!")

                    return
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")

def main():
    """Main function to run the exporter"""
    try:
        exporter = QualtricsExporter()

        print("Qualtrics Survey Exporter")
        print("=" * 50)

        # Check if we can find EMS survey specifically
        ems_survey = exporter.find_survey_by_name("EMS")
        if ems_survey:
            print(f"Found EMS survey: {ems_survey['name']} (ID: {ems_survey['id']})")

            choice = input("Export EMS survey? (y/n): ").strip().lower()
            if choice == 'y':
                filename = input("Enter filename for EMS export (or press Enter for default): ").strip()
                if not filename:
                    filename = "EMS_survey_responses.csv"

                success = exporter.export_survey_to_csv(ems_survey['id'], filename)
                if success:
                    print("EMS survey export completed!")
                    return
                else:
                    print("EMS survey export failed!")

        # If EMS not found or user declined, show all surveys
        print("\nLet's look at all available surveys:")
        exporter.list_surveys_interactive()

    except Exception as e:
        print(f"Error: {e}")
        print("Make sure your .env file contains the correct Qualtrics credentials.")

if __name__ == "__main__":
    main()