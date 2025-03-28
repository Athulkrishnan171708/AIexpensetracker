# AI-Powered Expense Tracker

A modern expense management application built with Django that helps you track and manage your expenses with AI-powered insights.

## Features

- User authentication and authorization
- Expense tracking and categorization
- AI-powered expense analysis and predictions
- Interactive dashboards and reports
- Export functionality for expense data
- Mobile-responsive design

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-powered-expense-tracker.git
cd ai-powered-expense-tracker
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=your-domain.com
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

## Deployment

This application can be deployed on various platforms:

### Heroku
1. Create a Heroku account and install the Heroku CLI
2. Create a new Heroku app
3. Add PostgreSQL addon
4. Deploy using Heroku Git:
```bash
git push heroku main
```

### Google Cloud Platform
1. Create a Google Cloud project
2. Enable Cloud SQL and create a PostgreSQL instance
3. Deploy using Cloud Run or App Engine

### AWS
1. Create an AWS account
2. Set up an RDS PostgreSQL instance
3. Deploy using Elastic Beanstalk or EC2

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers. 