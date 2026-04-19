# AbideWord

A Flask web application for biblical studies and content management.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. Navigate to the project directory:
```bash
cd bibleAbideWord
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

4. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the Flask development server:
```bash
python app.py
```

2. The application will be available at: `http://127.0.0.1:5000/`

3. On first run, the SQLite database (`database.db`) will be automatically created with the following tables:
   - `categories` - Subject areas for biblical studies
   - `topics` - Individual biblical study topics
   - `users` - Administrator accounts

