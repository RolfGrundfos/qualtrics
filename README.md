# Qualtrics API Export Tool

A Python tool for exporting survey data from Qualtrics to CSV files using the Qualtrics API. Designed for teams to easily download survey responses for analysis.

## Features

- 🔄 Export any Qualtrics survey to CSV
- 📊 Interactive survey selection
- 🛠️ Reusable class for custom implementations
- 🧹 CSV header cleaning utilities
- 🔒 Secure credential management

## Setup

### 1. Clone and Install

```bash
git clone https://github.com/RolfGrundfos/qualtrics.git
cd qualtrics
pip install -r requirements.txt
```

### 2. Configure Credentials

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your Qualtrics credentials:
   ```bash
   QUALTRICS_DATACENTER_ID=your_datacenter_id
   QUALTRICS_ORG_ID=your_organization_id
   QUALTRICS_USER_ID=your_user_id
   QUALTRICS_API_TOKEN=your_api_token
   QUALTRICS_USERNAME=your_email@company.com#your_organization
   ```

### 3. Get Your Qualtrics API Credentials

1. Log into Qualtrics
2. Go to **Account Settings** → **Qualtrics IDs**
3. Copy your User ID, Organization ID, and Data Center ID
4. Generate an API Token from the same page

## Usage

### Quick Export (Interactive)

```bash
python qualtrics_export.py
```

This will:
- List all available surveys
- Let you select which to export
- Download responses to CSV

### Custom Export Scripts

Create specific export scripts for your surveys:

```python
from qualtrics_export import QualtricsExporter

# Initialize exporter
exporter = QualtricsExporter()

# Export specific survey by ID
exporter.export_survey_to_csv('SV_XXXXXXXXX', 'my_survey.csv')

# Or find survey by name
survey = exporter.find_survey_by_name('Employee Survey')
if survey:
    exporter.export_survey_to_csv(survey['id'], 'employee_responses.csv')
```

## File Structure

```
qualtrics/
├── qualtrics_export.py     # Main reusable export class
├── export_ems.py          # Example: EMS survey export script
├── fix_csv_headers.py     # Utility to clean Qualtrics validation text
├── requirements.txt       # Python dependencies
├── .env.example          # Template for credentials
└── README.md             # This file
```

## Security Notes

- ⚠️ **Never commit your `.env` file** - it contains sensitive API credentials
- 📁 CSV exports are automatically ignored by git (may contain sensitive data)
- 🔐 Keep your API token secure and regenerate if compromised

## Troubleshooting

### Common Issues

1. **"Missing required environment variables"**
   - Check your `.env` file exists and contains all required variables
   - Verify your API token is valid

2. **"Error 401: Unauthorized"**
   - Double-check your API token and data center ID
   - Ensure your account has API access enabled

3. **"Export timed out"**
   - Large surveys may take longer to export
   - Increase the `max_wait_time` parameter in your export call

## Team Usage

This tool is designed for team sharing:

1. Each team member needs their own `.env` file with their Qualtrics credentials
2. Share custom export scripts in this repository
3. CSV files are automatically ignored to prevent sensitive data commits

## Contributing

When adding new export scripts:
1. Use the `QualtricsExporter` class as the base
2. Follow the naming pattern: `export_[survey_name].py`
3. Add documentation for any new features