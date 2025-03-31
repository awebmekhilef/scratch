# Scratch
A video game storefront inspired by itch.io

# Features
- User authentication with 2FA support
- Create and customise game pages (screenshots, uploads, markdown description)
- Integrated web player for HTML5 games
- Natural language searching using Elasticsearch

# Getting Started
## Prerequisites
Ensure you have Python 3.8+ installed.

## Installation
1. Clone the repo
2. Create a virtual environment and install the dependencies
   ```
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Configure environment variables. An example `.env.example` is provided
4. Start the development server
   ```
   flask run
   ```
