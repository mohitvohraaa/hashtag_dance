# Hashtag Dance Studio

A Django-based web application for managing dance event bookings.

## Features

- User authentication
- Event management
- Seat selection
- Online payment integration with Razorpay
- Email notifications

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/yourusername/hashtag-dance.git
cd hashtag-dance
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the project root with:
```
SECRET_KEY=your_secret_key
DEBUG=True
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
EMAIL_HOST_USER=your_email
EMAIL_HOST_PASSWORD=your_email_password
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

## Deployment

1. Set `DEBUG=False` in settings.py
2. Update `ALLOWED_HOSTS` with your domain
3. Configure static files:
```bash
python manage.py collectstatic
```

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License. 