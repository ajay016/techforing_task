# techforing_task## Getting Started with Project Management API (Django)

### Requirements

    - Python 3.10+
    - pip
    - Git
    - SQLite (default)


### 1. Clone the Repository
    open git bash make a new directory and navigate to it. Then, clone the repository using the following command:

    `git clone https://github.com/ajay016/techforing_task.git`
    `cd yourproject`

### 2. Create and Activate Virtual Environment
    `python -m venv venv`
    `source venv/bin/activate`      # Linux/macOS
    `venv\Scripts\activate `        # Windows


### 3. Install Dependencies
    `pip install -r requirements.txt`

### 4. Migration
    `python manage.py migrate`

### 5. Load Sample Data (if required)
    Load this sample data into the database if required
    `python manage.py loaddata sample_data.json` 