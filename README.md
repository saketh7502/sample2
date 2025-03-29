# SQL Injection CTF Challenges

A hands-on Capture The Flag (CTF) challenge focused on SQL injection vulnerabilities. This application contains multiple deliberately vulnerable endpoints that participants can exploit to extract hidden flags.

## Overview

This CTF challenge contains four different SQL injection vulnerabilities of increasing complexity:

1.  **Basic UNION-based Injection** - Simple SQL injection vulnerability allowing data extraction through UNION queries
2.  **Multi-Column UNION Injection** - Advanced SQL injection requiring matching multiple columns in UNION statements
3.  **UNION Injection with WHERE clause** - SQL injection in a search feature with filtering mechanisms
4.  **Login Form SQL Injection** - Authentication bypass vulnerability in the login system

## Getting Started

### Using Docker (Recommended)

1.  Clone this repository
2.  Build and run the Docker container:

    ```
    docker-compose up --build
    ```
3.  Access the application at http://localhost:8080

### Manual Setup

1.  Clone this repository
2.  Install the required dependencies:

    ```
    pip install flask
    ```
3.  Run the application:

    ```
    python app.py
    ```
4.  Access the application at http://localhost:8080

## Challenge Objectives

For each challenge, your goal is to:

1.  Identify the SQL injection vulnerability
2.  Exploit the vulnerability to extract the hidden flag
3.  The flag format is `picoCTF{...}`

## SQL Injection Tips

*   Use `' OR 1=1 --` to test if a field is vulnerable
*   Use `' UNION SELECT sqlite_version() --` to verify database type
*   List tables with `' UNION SELECT tbl_name FROM sqlite_master WHERE type='table' --`
*   Get column information with `' UNION SELECT sql FROM sqlite_master WHERE tbl_name='tablename' --`
*   Determine column count with `' ORDER BY 1--`, `' ORDER BY 2--`, etc. until you get an error

## CVSS Scores

Each vulnerability has been assigned a CVSS score to indicate its severity:

*   Challenge 1: 6.5
*   Challenge 2: 7.8
*   Challenge 3: 6.3
*   Challenge 4: 8.2

## Solutions
The solutions have been provided. Please check the solutions.txt file
