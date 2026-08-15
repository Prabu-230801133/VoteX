````markdown
# VoteX — College Online Voting System

VoteX is a full-stack college voting platform designed to digitize and streamline the college election process.

The system provides secure student registration, email verification, Google authentication, election management, OTP-verified voting, automated email notifications, AI-powered assistance, and result publication.

## Live Application

https://votex-production-4825.up.railway.app/

---

## Features

### Student Registration

- Registration using an official college email address
- College email domain validation
- Email OTP verification
- Secure password hashing
- Automatic student account creation

### Authentication

- Username and password authentication
- Google OAuth 2.0 authentication
- College Google account association
- Password reset using email OTP
- Role-based authentication
- Separate student and administrator access

### Election Management

Administrators can:

- Create and manage elections
- Configure election start and end times
- Add and manage candidates
- Assign students to elections
- Monitor election status
- Publish election results

### Secure Voting

- Students can vote only in eligible elections
- OTP verification before vote submission
- One vote per student per position
- Database-level duplicate vote prevention
- Vote confirmation through email
- Results available after the election ends

### Email Notifications

VoteX uses the **Brevo Transactional Email API** for application emails.

The system can send:

- Student signup OTP
- Login credentials
- Vote verification OTP
- Vote confirmation
- Password reset OTP
- Election announcements
- Voting reminders
- Results publication notifications

### AI-Powered Voting Assistant

VoteX includes an AI-powered chatbot that provides students with interactive assistance while using the platform.

The chatbot can help users with:

- Understanding the voting process
- Registration and email verification
- OTP-related guidance
- Election-related questions
- Navigating the platform
- General VoteX-related queries

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | Python, Django |
| Database | MySQL |
| Frontend | HTML5, CSS3, JavaScript |
| Authentication | Django Authentication |
| Social Authentication | Google OAuth 2.0 |
| Email | Brevo Transactional Email API |
| AI Assistant | Groq API / LLM |
| Image Storage | Cloudinary |
| REST API | Django REST Framework |
| Deployment | Railway |
| Version Control | Git, GitHub |

---

## Architecture

```text
                    ┌─────────────────────┐
                    │      Student        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    VoteX Frontend   │
                    │ HTML/CSS/JavaScript │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Django Backend   │
                    │ Authentication      │
                    │ Voting Logic        │
                    │ Election Management │
                    └──────┬───────┬──────┘
                           │       │
              ┌────────────┘       └──────────────┐
              ▼                                   ▼
       ┌──────────────┐                    ┌──────────────┐
       │    MySQL     │                    │ External APIs│
       │   Database   │                    │              │
       └──────────────┘                    │ Google OAuth │
                                           │ Brevo Email  │
                                           │ Groq AI      │
                                           │ Cloudinary   │
                                           └──────────────┘
````

---

## Project Structure

```text
VoteX/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── accounts/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   ├── pipeline.py
│   ├── decorators.py
│   ├── utils.py
│   └── migrations/
│
├── voting/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── ...
│
├── web_admin/
│   ├── views.py
│   └── ...
│
├── api/
│   ├── views.py
│   ├── serializers.py
│   └── ...
│
├── chat/
│   ├── views.py
│   └── ...
│
├── templates/
│   ├── accounts/
│   ├── voting/
│   └── ...
│
├── static/
│   ├── css/
│   └── js/
│
├── manage.py
├── requirements.txt
└── README.md
```

---

## Authentication Flow

### Student Signup

```text
Student enters college email
          ↓
College email domain validation
          ↓
Signup OTP generated
          ↓
OTP sent through Brevo
          ↓
Student verifies OTP
          ↓
Student account created
          ↓
Student can log in
```

### Google Login

```text
Student selects Google Login
          ↓
Google OAuth authentication
          ↓
Google email verified
          ↓
Existing college account matched
          ↓
Role-based authentication
          ↓
Student Dashboard
```

---

## Voting Flow

```text
Student Login
     ↓
Student Dashboard
     ↓
Select Active Election
     ↓
Select Candidate
     ↓
Request Vote OTP
     ↓
OTP sent to registered email
     ↓
Enter OTP
     ↓
Validate OTP
     ↓
Cast Vote
     ↓
Vote recorded
     ↓
Confirmation Email
```

---

## Security

VoteX implements multiple security mechanisms:

* Django password hashing
* CSRF protection
* Authentication-protected views
* Role-based access control
* College email validation
* Email OTP verification
* Vote OTP verification
* Duplicate vote prevention
* Database-level vote constraints
* Environment variables for secrets
* OAuth-based authentication
* Server-side validation
* Production HTTPS deployment

Sensitive credentials such as:

```text
SECRET_KEY
DATABASE_PASSWORD
GOOGLE_CLIENT_SECRET
BREVO_API_KEY
GROQ_API_KEY
CLOUDINARY_API_SECRET
```

are stored using environment variables and are not committed to the repository.

---

## REST API

VoteX also provides REST API endpoints through Django REST Framework.

| Method | Endpoint                | Description                         |
| ------ | ----------------------- | ----------------------------------- |
| GET    | `/api/elections/`       | Retrieve active elections           |
| GET    | `/api/candidates/<id>/` | Retrieve candidates                 |
| GET    | `/api/results/<id>/`    | Retrieve published results          |
| GET    | `/api/my-votes/`        | Retrieve authenticated user's votes |

---

## Local Development

### 1. Clone the Repository

```bash
git clone https://github.com/Prabu-230801133/VoteX.git
cd VoteX
```

### 2. Create a Virtual Environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file:

```env
SECRET_KEY=your_secret_key
DEBUG=True

DB_NAME=college_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306

COLLEGE_EMAIL_DOMAIN=rajalakshmi.edu.in

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=your_google_client_id
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=your_google_client_secret

BREVO_API_KEY=your_brevo_api_key
BREVO_SENDER_EMAIL=your_verified_sender_email
BREVO_SENDER_NAME=VoteX

GROQ_API_KEY=your_groq_api_key

CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_secret
```

Never commit your `.env` file or API keys to GitHub.

### 5. Create the Database

Create a MySQL database:

```sql
CREATE DATABASE college_db
CHARACTER SET utf8mb4;
```

### 6. Run Migrations

```bash
python manage.py migrate
```

### 7. Create an Administrator

```bash
python manage.py createsuperuser
```

### 8. Start the Development Server

```bash
python manage.py runserver
```

Open:

[http://localhost:8000](http://localhost:8000)

---

## Google OAuth Configuration

Create OAuth credentials in Google Cloud Console.

Add the local redirect URI:

```text
http://localhost:8000/social-auth/complete/google-oauth2/
```

For production, add:

```text
https://votex-production-4825.up.railway.app/social-auth/complete/google-oauth2/
```

Configure the Google Client ID and Client Secret through environment variables.

---

## Email Configuration

VoteX uses the **Brevo Transactional Email API** instead of direct SMTP connections.

Required environment variables:

```env
BREVO_API_KEY=your_api_key
BREVO_SENDER_EMAIL=your_verified_sender_email
BREVO_SENDER_NAME=VoteX
```

The application uses the Brevo HTTPS API to send transactional emails such as OTPs, confirmations, and election notifications.

---

## Deployment

VoteX is deployed on **Railway**.

Production configuration includes:

* Django + Gunicorn
* MySQL database
* WhiteNoise for static files
* Environment-based configuration
* Google OAuth production credentials
* Brevo transactional email
* Cloudinary media storage
* Production database migrations
* HTTPS

Live application:

[https://votex-production-4825.up.railway.app/](https://votex-production-4825.up.railway.app/)

---

## What I Learned

Building VoteX provided practical experience with:

* Full-stack web application development
* Django architecture
* Relational database design
* Authentication and authorization
* Google OAuth integration
* OTP-based verification
* Transactional email APIs
* REST API development
* AI API integration
* Cloud-based deployment
* Environment configuration
* Database migrations
* Production debugging
* Git and GitHub workflows

---

## Future Improvements

Planned improvements include:

* Enhanced election analytics
* Improved AI assistant capabilities
* Administrative reporting
* Advanced audit logging
* Improved notification management
* Performance optimization
* Automated testing and CI/CD

---

## License

This project is developed for educational and portfolio purposes.

```
```
