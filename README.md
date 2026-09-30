# Chatbot Assistant System using Python
## Enhancing Cybersecurity Awareness and Support

### New final-year features
- Administrator dashboard
- SQLite chatbot knowledge database
- Add/update/delete chatbot knowledge
- User management view
- User activity reports
- Login/logout auditing
- Chat activity auditing
- Password checker
- URL heuristic checker
- Security tips
- Responsive Flask UI

### Demo admin
Username: `admin`
Password: `Admin@123`

Change the demo administrator password before any real deployment.

### Run
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Open `http://127.0.0.1:5000`.

### Project modules
1. Authentication Module
2. Chatbot Module
3. Knowledge Management Module
4. Password Security Module
5. URL Awareness Module
6. Activity Monitoring Module
7. Admin Dashboard Module
8. SQLite Database Module

### Production security
Use environment variables for secrets, HTTPS, CSRF protection, secure password hashing such as Argon2/Werkzeug, rate limiting, secure cookies, input validation, and proper backup/access controls.
