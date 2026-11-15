# BrightMart Inventory Management System — Frontend

A React interface connected to the IU02 Django REST API.

## Requirements

- Node.js and npm
- The configured BrightMart Django backend
- The backend database
- An existing BrightMart user account

## Backend setup

From the brightmart_ims folder, activate the Python virtual
environment in Windows Git Bash:

```bash
source venv/Scripts/activate
```

Install dependencies and apply migrations:

```bash
python -m pip install -r requirements.txt
python manage.py migrate
```

Configure the backend .env with the required local database
settings and secret key.

Start Django:

```bash
python manage.py runserver
```

## Frontend setup

Open a separate terminal in the frontend folder:

```bash
npm install
```

Create frontend/.env containing:

```dotenv
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

Start the development server:

```bash
npm run dev
```

Open the Local URL printed in the terminal.

Django must allow the frontend origin through its CORS settings.

## Production build and local preview

```bash
npm run build
npm run preview
```

Open the preview URL printed in the terminal.
Keep Django running while using the frontend.

## Main features

- Token-based login and browser-tab logout
- Protected frontend routes
- Live product and supplier information
- Receive-stock and issue-stock forms
- Low-stock information and transaction history
- Validation, loading indicators, and error messages
- Responsive layouts and keyboard-accessible controls

## Usage

Log in with an existing BrightMart account.
Use Inventory Dashboard to view current stock.
Use Stock Management to receive or issue stock.
Use Stock & Transactions to review low-stock products and history.

Stock submissions change real database records.