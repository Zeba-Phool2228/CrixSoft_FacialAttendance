# Facial Recognition Employee Attendance System

An AI-powered employee attendance management system that uses facial recognition to automatically identify registered employees and record their attendance in real time, while providing a secure PIN-based alternative for employees who prefer not to use face-based attendance.

## Overview

The Facial Recognition Employee Attendance System is designed to modernize workplace attendance by replacing manual attendance entry with an automated, secure, and efficient recognition-based workflow.

The system uses facial recognition to identify enrolled employees through a camera. When a registered and active employee is recognized, their attendance is automatically recorded. Unknown or unregistered individuals are rejected and cannot mark attendance.

The system also provides an optional Employee ID + Secret PIN attendance method. This alternative supports employees who, for privacy, religious, cultural, or personal reasons, may not be comfortable revealing their face to a camera. In particular, it provides a practical option for Muslim women who observe Shar'i (Islamic) face covering and therefore may prefer not to use facial recognition.

The goal is not only automation, but also secure identity verification, privacy-aware design, reliable attendance recording, and practical usability in a real workplace environment.

---

## Key Features

- AI-based facial recognition for employee attendance
- Automatic camera-based face detection
- Recognition of enrolled employees using facial embeddings
- Attendance restricted to registered and active employees
- Unknown-person rejection to prevent unauthorized attendance
- Employee ID + Secret PIN alternative attendance method
- Secure password/PIN hashing
- One attendance record per employee per day
- Duplicate attendance prevention
- Real-time attendance recording
- Admin authentication and protected management pages
- Employee information and attendance overview
- SQLite database with foreign-key enforcement
- Environment-based secret key configuration using `.env`
- CPU-based face recognition using InsightFace and ONNX Runtime
- Automated dependency installation through `requirements.txt`

---

## How the System Works

### Face-Based Attendance

```text
Employee approaches the camera
            ↓
Camera captures the employee's face
            ↓
Face is detected
            ↓
Facial embedding is generated
            ↓
Embedding is compared with enrolled employee embeddings
            ↓
Similarity score is calculated
            ↓
Recognition threshold is applied
            ↓
Registered + active employee identified
            ↓
Attendance is recorded
```

The system does not simply mark attendance for any face detected by the camera.

A detected face must match an enrolled employee whose account is active. If no sufficiently similar registered employee is found, the person is treated as unknown and attendance is not recorded.

---

## Authorized Employee Verification

Only employees who have been enrolled in the system can receive attendance through facial recognition.

The system retrieves facial embeddings only for employees whose status is:

```text
active
```

This prevents an unknown person from receiving attendance simply by appearing in front of the camera.

The recognition process follows:

```text
Detected Face
     ↓
Compare with enrolled active employees
     ↓
Match found?
   ↙       ↘
 Yes        No
 ↓           ↓
Attendance   Rejected
marked       as unknown
```

This design helps reduce proxy attendance and unauthorized attendance entries.

---

## Privacy-Aware PIN Attendance

Facial recognition is the primary attendance method, but the system also provides an alternative verification method using:

```text
Employee ID + Secret PIN
```

This option is particularly important for employees who may not be comfortable with face-based verification.

From an Islamic and privacy-aware perspective, some Muslim women observe Shar'i face covering and may therefore prefer not to reveal their face to an attendance camera. For such employees, the system provides a practical alternative: they can enter their registered Employee ID and Secret PIN, and their attendance can be verified without requiring facial recognition.

This approach aims to balance:

* Workplace attendance requirements
* Employee privacy
* Religious considerations
* Identity verification
* Practical usability

The PIN is stored as a secure hash rather than as plain text.

---

## Duplicate Attendance Prevention

An employee can receive only one attendance record per day.

The system checks whether the employee has already attended before creating a new attendance record.

The database also enforces:

```text
UNIQUE(employee_id, date)
```

This provides an additional layer of protection against duplicate attendance records.

Example:

```text
09:00 AM → Attendance marked
10:00 AM → Already checked in today
```

The second attempt does not create another attendance record.

---

## Security

Security is an important part of the system design.

### Authentication

Administrative pages are protected through session-based authentication.

Unauthenticated users are redirected to the administrator login page.

### Password Protection

Administrator passwords and employee PINs are stored using secure password hashing rather than plain-text storage.

### Secret Key Management

The Flask application secret key is loaded from the environment:

```text
.env
```

The `.env` file is excluded from version control through `.gitignore`.

A `.env.example` file is provided as a configuration template without exposing the actual secret.

### Unknown User Protection

A person who is not enrolled in the employee database cannot receive attendance through facial recognition.

### Database Integrity

The system uses:

* Foreign-key constraints
* Unique constraints
* Parameterized SQL queries
* Employee status filtering
* Duplicate attendance prevention

---

## Technology Stack

| Technology    | Purpose                                       |
| ------------- | --------------------------------------------- |
| Python        | Core application development                  |
| Flask         | Web application framework                     |
| OpenCV        | Camera and image processing                   |
| InsightFace   | Face detection and recognition                |
| ArcFace       | Facial embedding generation                   |
| ONNX Runtime  | AI model inference                            |
| NumPy         | Numerical and embedding operations            |
| SQLite        | Attendance and employee database              |
| Werkzeug      | Password/PIN hashing and security utilities   |
| HTML          | Application interface                         |
| CSS           | User interface styling                        |
| JavaScript    | Camera interaction and real-time verification |
| python-dotenv | Environment variable management               |

---

## Facial Recognition Pipeline

The recognition engine uses InsightFace to process camera images.

For a detected face, the system generates a 512-dimensional facial embedding.

The embedding is then compared against stored embeddings of enrolled active employees using cosine similarity.

```text
Image
 ↓
Face Detection
 ↓
Face Embedding
 ↓
512-Dimensional Vector
 ↓
Cosine Similarity
 ↓
Recognition Threshold
 ↓
Employee Match / Unknown
```

The current recognition threshold is:

```text
0.45
```

This threshold is applied before an employee is considered a valid recognition match.

---

## Attendance Methods

### 1. Face Recognition

```text
Camera → Face → Recognition → Registered Employee → Attendance
```

Best suited for employees who choose camera-based attendance.

### 2. PIN Verification

```text
Employee ID + Secret PIN → Verification → Registered Employee → Attendance
```

Provides an alternative for employees who prefer not to use facial recognition.

---

## Database Structure

The application uses SQLite with the following main tables:

### `admins`

Stores administrator accounts and securely hashed passwords.

### `employees`

Stores employee information including:

* Employee code
* Name
* Department
* Position
* Email
* Account status
* Verification method
* Hashed PIN

### `embeddings`

Stores facial embeddings associated with enrolled employees.

### `attendance`

Stores:

* Employee ID
* Date
* Check-in time
* Attendance method
* Attendance status
* Creation timestamp

Relationships are enforced using foreign keys.

---

## Project Structure

```text
FacialAttendance/
│
├── ai/
│   └── face_recognizer.py
│
├── data/
│   └── employees/
│
├── database/
│   ├── database.py
│   └── employee_repo.py
│
├── docs/
│
├── embeddings/
│
├── routes/
│
├── static/
│   ├── css/
│   └── js/
│
├── templates/
│
├── uploads/
│
├── .env
├── .env.example
├── .gitignore
├── app.py
├── create_admin.py
├── enroll_employee.py
├── live_recognition_test.py
├── requirements.txt
└── README.md
```

---

## Installation

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd FacialAttendance
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

#### Windows PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

All required Python packages and their pinned versions are listed in `requirements.txt`.

### 5. Configure environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
```

Never commit the real `.env` file to GitHub.

### 6. Initialize the database

The application initializes the required database tables automatically when started.

---

## Creating an Administrator

Run:

```bash
python create_admin.py
```

The administrator credentials are entered securely through the terminal and are not stored as plain-text passwords.

---

## Enrolling Employees

Employees must be registered before they can receive attendance.

### Face-Based Enrollment

```bash
python enroll_employee.py face <employee_code> <name> <image_path>
```

The enrollment image must contain exactly one detectable face.

### PIN-Based Enrollment

```bash
python enroll_employee.py pin <employee_code> <name> <pin>
```

Only registered employees can use the corresponding attendance method.

---

## Running the Application

Start the application with:

```bash
python app.py
```

The application runs locally at:

```text
http://127.0.0.1:5000
```

Open the address in a web browser to access the system.

---

## Attendance Workflow

### Face Attendance

1. Open the face attendance interface.
2. Allow camera access.
3. Position the employee's face in front of the camera.
4. The system captures camera frames automatically.
5. The detected face is compared with enrolled active employees.
6. A recognized employee receives attendance.
7. An unknown person is rejected.
8. An employee who has already checked in that day cannot create another attendance record.

### PIN Attendance

1. Enter the registered Employee ID.
2. Enter the employee's Secret PIN.
3. The system verifies the credentials.
4. If verification succeeds, attendance is recorded.
5. If verification fails, attendance is rejected.
6. Duplicate attendance for the same day is prevented.

---

## Attendance Security Model

The system follows a registered-employee model:

```text
Person
  ↓
Is the person registered?
  ↓
 ┌───────────────┐
 │               │
No              Yes
│                │
Reject       Is employee active?
                 ↓
            ┌────┴────┐
            │         │
           No        Yes
            │         │
          Reject   Verify identity
                       ↓
                  ┌────┴────┐
                  │         │
                Match    No Match
                  │         │
              Attendance   Reject
```

This prevents arbitrary individuals from marking attendance.

---

## Testing

The system has been tested for core attendance and security scenarios including:

* Facial detection
* Facial embedding generation
* Registered employee recognition
* Unknown-person rejection
* PIN verification
* Incorrect PIN rejection
* Duplicate attendance prevention
* Active employee filtering
* Administrative authentication
* Secure secret-key configuration
* Database integrity
* Dependency reproducibility

A real facial recognition test successfully produced:

```text
Faces detected: 1
Embedding shape: (512,)
```

---

## Security Principles

The project follows several practical security principles:

* Do not store passwords or PINs in plain text.
* Do not commit `.env` files containing secrets.
* Do not allow unknown individuals to receive attendance.
* Restrict administrative functionality behind authentication.
* Use registered employee identities for attendance.
* Prevent duplicate attendance records at both application and database levels.
* Keep sensitive runtime data outside version control.
* Use environment variables for application secrets.

---

## Privacy and Responsible Use

Facial recognition is a sensitive technology and should be deployed responsibly.

Organizations using this system should ensure that employees are informed about:

* What biometric information is being processed
* Why it is being processed
* How it is stored
* Who can access it
* How long it is retained
* What alternative verification methods are available

The PIN-based attendance option demonstrates a privacy-aware and inclusive approach by providing an alternative to face-based verification.

---

## Real-World Use Case

The system is designed around a workplace scenario where employees are enrolled by an authorized administrator.

During normal attendance:

```text
Employee enters workplace
        ↓
Camera detects face
        ↓
System identifies enrolled employee
        ↓
Identity verified
        ↓
Attendance automatically recorded
```

For employees using the alternative method:

```text
Employee ID + Secret PIN
        ↓
Identity verification
        ↓
Attendance automatically recorded
```

This architecture can be extended for deployment in offices, educational institutions, laboratories, factories, and other controlled environments.

---

## Future Enhancements

Potential future improvements include:

* Multi-camera support
* Centralized cloud database
* Advanced liveness detection
* Anti-spoofing protection
* Improved low-light recognition
* Multiple-face simultaneous recognition
* Attendance reports and export
* Email notifications
* Role-based access control
* Detailed audit logs
* REST API integration
* Production-grade deployment using a WSGI server
* Desktop or kiosk packaging
* Organization-wide centralized attendance management

---

## Project Objectives

The project aims to:

1. Automate employee attendance using AI-based facial recognition.
2. Reduce manual attendance work.
3. Reduce proxy and fraudulent attendance.
4. Restrict attendance to registered employees.
5. Prevent duplicate attendance records.
6. Provide a secure alternative attendance method through Employee ID and Secret PIN.
7. Support privacy-aware and inclusive workplace attendance.
8. Provide real-time attendance information for management.
9. Demonstrate the practical integration of AI, backend development, databases, and security.

---

## Conclusion

The Facial Recognition Employee Attendance System combines artificial intelligence, computer vision, web development, database management, and security into a practical workplace application.

Rather than treating facial recognition as the only solution, the system incorporates an alternative PIN-based verification method to accommodate privacy, religious, and personal preferences.

Its core principle is simple:

> **Only registered and authorized employees can receive attendance, while employees who prefer not to use facial recognition have an alternative secure verification method.**

The project demonstrates how AI-based identity recognition can be integrated with secure application design to create a practical, privacy-aware, and extensible employee attendance solution.

---

## Author

**Zeba Phool**

BS Information Technology

**Project:** Facial Recognition Employee Attendance System
