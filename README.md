# Daily Allocation Tasks Automation

Automatically sends daily task allocation emails using data from Google Sheets.

## Setup Instructions

1. **Clone the repository**
```bash
git clone git@github.com:FALAK097/Daily-Tasks-Allocation-Automation.git
cd Daily-Tasks-Allocation-Automation
```

2. **Install Poetry (if not installed)**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. **Install dependencies**
```bash
poetry install
```

4. **Google Sheets Setup**
- Go to [Google Cloud Console](https://console.cloud.google.com)
- Create a new project
- Enable Google Sheets API
- Create a Service Account
- Download the service account key as `credentials.json`
- Place `credentials.json` in the project root
- Share your Google Sheet with the service account email

5. **Gmail Setup**
- Enable 2-Step Verification in your Gmail account
- Go to Security → App Passwords
- Create a new app password
- Copy the 16-character password

6. **Environment Setup**
```bash
cp .env.example .env
```

Edit `.env` with your details:
- SHEET_URL: Your Google Sheet URL
- EMAIL_USERNAME: Your Gmail address
- EMAIL_PASSWORD: Your Gmail app password
- RECIPIENTS: Comma-separated list of email recipients
- CC_RECIPIENT: CC recipient email

7. **Run the Service**

Go into poetry shell:
```bash
poetry shell
```

To run as a standalone service:
```bash
poetry run python main.py
```

To run the API server:
```bash
poetry run python api_server.py
```

## Sheet Format Requirements

- Sheet names should be in the format "DD Month" (e.g., "24 March")
- Each sheet should contain task allocations in the specified format
- Required columns: Project, Task, Status

## API Endpoints

- `GET /health`: Check service health
- `POST /send-update/{message_id}`: Trigger update email