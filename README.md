# 🏠 HomeNest

**HomeNest** is a Django-based property rental management platform designed to simplify the interaction between **property owners and tenants**.

The platform allows property owners to list and manage rental properties, handle rental requests, and monitor their properties through a dashboard. Tenants can browse available properties, search and filter listings, submit rental requests, track request status, and report maintenance issues.

---

## 📌 Project Overview

HomeNest provides separate workflows for **Owners** and **Tenants**.

### 👤 Owner Workflow

```text
Owner
  ↓
Login
  ↓
Owner Dashboard
  ↓
Add / Manage Properties
  ↓
Receive Rental Requests
  ↓
Approve / Reject Requests
  ↓
Manage Property Status
  ↓
View Statistics
```

### 👨‍💼 Tenant Workflow

```text
Tenant
  ↓
Register / Login
  ↓
Browse Properties
  ↓
Search & Filter
  ↓
View Property Details
  ↓
Submit Rental Request
  ↓
Track Request Status
  ↓
Report Maintenance Issues
```

---

## ✨ Features

### 👤 Authentication

* User registration
* User login and logout
* Role-based access
* Owner and Tenant roles
* Protected dashboard pages
* Django authentication system

### 🏡 Property Management

Owners can:

* Add new properties
* Edit property information
* Manage property listings
* Upload property images
* View property details
* Track available properties
* Track rented properties

Supported property types:

* House
* Apartment
* Villa
* Room
* PG

### 🔎 Property Search & Filtering

Tenants can search and filter available properties using:

* City
* Property type
* Maximum rent

Properties are displayed based on availability and can be sorted for easier browsing.

### 📄 Rental Requests

Tenants can:

* Submit rental requests
* View their rental requests
* Track rental request status

Owners can:

* View incoming rental requests
* Approve rental requests
* Reject rental requests
* Monitor rental status

Rental request statuses:

```text
PENDING
APPROVED
REJECTED
```

### 🛠️ Maintenance Management

Tenants can report maintenance problems for their rented property.

A maintenance request can contain:

* Issue title
* Description
* Photo
* Priority

Priority levels:

```text
LOW
MEDIUM
HIGH
URGENT
```

### 📊 Dashboard & Statistics

The application provides dashboard information such as:

* Total properties
* Available properties
* Rented properties
* Pending rental requests
* Approved rental requests
* Rejected rental requests

---

## 🖥️ Screenshots

### 🏠 Home Page

<img width="1835" height="898" alt="HomeNest Home Page" src="https://github.com/user-attachments/assets/c7d49aee-203f-4ed8-b873-5f77011e22f0" />

### 🏠 Featured Properties

<img width="1812" height="890" alt="HomeNest Featured Properties" src="https://github.com/user-attachments/assets/380a2c1f-cfa0-4843-b54b-eab8c7f96948" />

### 🔐 Login Page

<img width="1586" height="852" alt="HomeNest Login Page" src="https://github.com/user-attachments/assets/320fa5c6-7dbd-421c-a116-ebc16a360375" />

### 📝 Create Your Account

<img width="1646" height="890" alt="HomeNest Registration Page" src="https://github.com/user-attachments/assets/6339f861-e835-45da-a491-49def2560c6d" />

### 👤 Owner Dashboard

<img width="1865" height="826" alt="HomeNest Owner Dashboard" src="https://github.com/user-attachments/assets/7b6b4805-c4ec-448b-ab82-6e6262f35703" />

### 🏡 Property Management

<img width="1877" height="902" alt="HomeNest Property Management" src="https://github.com/user-attachments/assets/0e918252-d80c-494f-be62-5d4ccd673201" />

### ➕ Add Property

<img width="1907" height="835" alt="HomeNest Add Property" src="https://github.com/user-attachments/assets/9cfe8eaf-da00-4c37-b8ec-0f40f396ec18" />

### 📄 Rental Request

<img width="1732" height="905" alt="HomeNest Rental Request" src="https://github.com/user-attachments/assets/43896a00-f79b-41a8-8f7e-c1deef76c8ff" />

### 👨‍💼 Tenant Dashboard

<img width="1806" height="827" alt="HomeNest Tenant Dashboard" src="https://github.com/user-attachments/assets/413535ff-053f-41d2-bb6e-2a6e4ba9d2db" />

### 📋 Rental Requests

<img width="1890" height="677" alt="HomeNest Rental Requests" src="https://github.com/user-attachments/assets/80f3f9bd-3fe1-4cb1-9da6-599fa7b518da" />

### 🛠️ Maintenance Request

<img width="1761" height="836" alt="HomeNest Maintenance Request" src="https://github.com/user-attachments/assets/eb53b8ea-2c45-48a5-9bc4-bf42201b5f86" />

---

## 🛠️ Technology Stack

### Backend

* **Python**
* **Django**
* **Django ORM**
* **Django Authentication**

### Frontend

* **HTML5**
* **CSS3**
* **JavaScript**

### Database

* **SQLite**

### Development Tools

* **Git**
* **GitHub**
* **Visual Studio Code**
* **Postman**

---

## 📁 Project Structure

```text
HomeNest/
│
├── apps/
│   │
│   ├── accounts/
│   │   ├── migrations/
│   │   ├── templates/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── urls.py
│   │   └── views.py
│   │
│   ├── properties/
│   │   ├── migrations/
│   │   ├── templates/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── urls.py
│   │   └── views.py
│   │
│   └── tenants/
│       ├── migrations/
│       ├── templates/
│       ├── admin.py
│       ├── apps.py
│       ├── models.py
│       ├── urls.py
│       └── views.py
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/
│
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

> The `media/` directory is used locally for uploaded property and maintenance images and is excluded from version control.

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/prajwalk-sec/HomeNest.git
```

Move into the project directory:

```bash
cd HomeNest
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

#### Windows Command Prompt / PowerShell

```bash
venv\Scripts\activate
```

#### Git Bash

```bash
source venv/Scripts/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Apply Database Migrations

```bash
python manage.py migrate
```

### 6. Create a Superuser

To access Django's built-in administration panel:

```bash
python manage.py createsuperuser
```

Follow the instructions displayed in the terminal.

### 7. Start the Development Server

```bash
python manage.py runserver
```

Open the application:

```text
http://127.0.0.1:8000/
```

Django Admin:

```text
http://127.0.0.1:8000/admin/
```

---

## 🔐 User Roles

HomeNest currently supports two application roles:

| Role       | Responsibilities                                                         |
| ---------- | ------------------------------------------------------------------------ |
| **Owner**  | Manage properties and rental requests                                    |
| **Tenant** | Browse properties, submit rental requests, and report maintenance issues |

The project also uses Django's built-in `/admin/` interface for administrative management.

---

## 🗄️ Main Data Models

### User

Stores authentication and role information.

### Property

Stores property information such as:

* Title
* Description
* Address
* City
* Monthly rent
* Bedrooms
* Bathrooms
* Property type
* Availability status
* Property image

### Tenant Profile

Stores tenant-related information such as:

* Phone
* Address
* Profile image

### Rental Request

Tracks rental requests between tenants and property owners.

Possible statuses:

```text
PENDING
APPROVED
REJECTED
```

### Maintenance Request

Stores maintenance problems reported by tenants, including:

* Issue title
* Description
* Photo
* Priority
* Request status

---

## 🔄 Application Flow

```text
                         HomeNest
                            │
              ┌─────────────┴─────────────┐
              │                           │
            Owner                       Tenant
              │                           │
         Dashboard                    Dashboard
              │                           │
      Manage Properties            Browse Properties
              │                           │
      Rental Requests              Search & Filter
              │                           │
      Approve / Reject             Property Details
              │                           │
       Property Status             Rental Request
                                          │
                                  Maintenance Issue
```

---

## 🧪 Development Commands

### Check the Django Project

```bash
python manage.py check
```

### Create Migrations

After changing models:

```bash
python manage.py makemigrations
```

### Apply Migrations

```bash
python manage.py migrate
```

### Run Development Server

```bash
python manage.py runserver
```

---

## 📦 Requirements

Recommended development environment:

```text
Python 3.11+
Django 5.2+
```

Project dependencies are maintained in:

```text
requirements.txt
```

Install dependencies with:

```bash
pip install -r requirements.txt
```

---

## 🔒 Environment Variables

Sensitive configuration should be stored in environment variables instead of being committed to GitHub.

Example:

```text
SECRET_KEY=your-secret-key
DEBUG=True
```

The `.env` file should be included in `.gitignore`.

---

## 🚫 Files Excluded From Git

The following files and directories should not normally be committed:

```text
venv/
__pycache__/
*.pyc
.env
db.sqlite3
media/
.vscode/
```

---

## 🚀 Future Improvements

Planned improvements may include:

* 💳 Online rent payment
* 📧 Email notifications
* 🔔 Real-time notifications
* 📊 Advanced analytics
* 🏡 Improved property image galleries
* 🛠️ Enhanced maintenance tracking
* 🔐 Enhanced authentication and security
* 🌐 Production deployment
* 🐳 Docker support
* 🗄️ PostgreSQL database
* 🔌 Django REST Framework API
* 📱 Mobile-friendly improvements

---

## 📈 Project Status

**🚧 Active Development**

HomeNest is an ongoing portfolio project. New features, UI improvements, backend functionality, and performance improvements will be added as development continues.

---

## 🤝 Contributing

Contributions and suggestions are welcome.

### Clone the repository

```bash
git clone https://github.com/prajwalk-sec/HomeNest.git
cd HomeNest
```

### Create a feature branch

```bash
git checkout -b feature/new-feature
```

### Commit your changes

```bash
git add .
git commit -m "Add new feature"
```

### Push the branch

```bash
git push origin feature/new-feature
```

You can then create a Pull Request on GitHub.

---

## 👨‍💻 Author

**Prajwal K**

MCA Graduate | Python Developer | Django Developer | Backend Developer

### Skills

```text
Python
Django
SQL
REST APIs
HTML
CSS
JavaScript
Git
GitHub
```

---

## 📄 License

This project is currently developed for **learning, portfolio, and demonstration purposes**.

---

## ⭐ Acknowledgement

HomeNest was developed as a practical Django project to demonstrate:

* Backend development
* Django application architecture
* Database management
* Authentication
* CRUD operations
* Role-based workflows
* Property management
* Rental request management
* Maintenance request management
* Git and GitHub workflow

---

⭐ **If you find this project useful, consider giving the repository a star!**
