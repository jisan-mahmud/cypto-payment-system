# Crypto Payment System

A Django-based cryptocurrency payment processing system.

## Features

- Cryptocurrency transaction processing
- Secure payment handling
- Django admin panel
- SQLite database

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/jisan-mahmud/cypto-payment-system.git
   cd cypto-payment-system
   ```

2. **Setup virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start server**
   ```bash
   python manage.py runserver
   ```

Access the app at `http://localhost:8000/` and admin panel at `http://localhost:8000/admin/`

## Tech Stack

- Python 3.x
- Django
- SQLite

## License

Open source

## Author

[Jisan Mahmud](https://github.com/jisan-mahmud)