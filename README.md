# PocketSmart AI

PocketSmart AI is a smart budget and recommendation assistant built using:

- Python
- FastAPI
- Jinja2
- SQLite
- JavaScript
- HTML
- CSS
- Google Gemini API

## Features

### Authentication

- User registration
- User login
- JWT authentication
- HttpOnly authentication cookie
- Logout
- Session management

### Home Interior Planner

Users can enter:

- Total budget
- Number of lights
- Number of fans
- Furniture requirements
- Dining tables
- Living room
- Kitchen
- Bedroom
- Additional requirements

The system creates a budget recommendation.

### Party Planner

Users can enter:

- Total budget
- Party type
- Guest count
- Venue type
- Catering
- Decoration
- Entertainment
- Additional requirements

### Jewelry Planner

Users can enter:

- Total budget
- Occasion
- Jewelry preferences
- Optional outfit image

The system generates jewelry recommendations.

### AI

The application uses Google Gemini when a valid API key is configured.

If Gemini is unavailable, the application uses a local fallback recommendation engine.

This means the application can still be tested without a Gemini API key.

### Shopping Links

Recommendations include search links for platforms such as:

- Amazon
- Flipkart
- Myntra
- Meesho
- Google
- Tanishq
- CaratLane
- BlueStone
- Melorra
- Booking
- MakeMyTrip
- OYO
- NoBroker

### Recommendation History

Generated recommendations are saved in SQLite.

Users can:

- View previous recommendations
- Open recommendation details
- Review budget allocations

---

# Installation

## Step 1

Open the project in VS Code.

## Step 2

Open the VS Code terminal.

## Step 3

Create virtual environment:

```powershell
py -3.10 -m venv .venv