# ALX Travel App 0x03

This project (`alx_travel_app_0x03`) is a RESTful API built with Django and Django REST Framework. It provides endpoints to manage **listings** and **bookings** for a travel application. The API supports full CRUD operations and is documented with Swagger.

---

## 🔁 Project Duplication

This project is a duplicate of `alx_travel_app_0x03`, enhanced with:

- ViewSets for Listings and Bookings
- API routing using DRF routers
<!-- - Swagger auto-generated API documentation -->

---

## 📁 Project Structure

```
alx_travel_app_0x03/
├── listings/
│   ├── models.py
│   ├── views.py          ← ListingView and BookingView defined here
│   ├── serializers.py
│   └── urls.py
├── alx_travel_app/
│   └── urls.py           ← Main router config for /api/ endpoints
├── manage.py
└── ...
```

---

## 🛠️ Installation

1. **Clone the Repository**

   ```bash
   git clone <your-repo-url>
   cd alx_travel_app_0x03
   ```

2. **Create & Activate Virtual Environment**

   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Apply Migrations**

   ```bash
   python manage.py migrate
   ```

5. **Run Server**

   ```bash
   python manage.py runserver
   ```

---

## 🔐 Authentication

> Endpoints require authentication using Django’s built-in authentication system or JWT (if configured).

---

## 🚀 API Endpoints

| Endpoint             | Method | Description          |
| -------------------- | ------ | -------------------- |
| `/api/listings/`     | GET    | List all listings    |
| `/api/listings/`     | POST   | Create a new listing |
| `/api/listings/:id/` | PUT    | Update a listing     |
| `/api/listings/:id/` | DELETE | Delete a listing     |
| `/api/bookings/`     | GET    | List user’s bookings |
| `/api/bookings/`     | POST   | Create a new booking |
| `/api/bookings/:id/` | PUT    | Update a booking     |
| `/api/bookings/:id/` | DELETE | Delete a booking     |

---

## 🧲 Testing Endpoints

Use [Postman](https://www.postman.com/) or [cURL](https://curl.se/) to test endpoints:

- **GET** `/api/listings/`
- **POST** `/api/bookings/`
- **PUT** `/api/bookings/1/`
- **DELETE** `/api/listings/2/`

Ensure you're authenticated (e.g., via Token or Session auth).

---

## ✅ Features

- Full CRUD for Listings and Bookings
- Authenticated access
- RESTful URL routing
- Organized with Django apps

---

## ✍️ Author

Built as part of the **ALX Backend Specialization**.
