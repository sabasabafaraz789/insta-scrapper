# **Instagram Profile Scraper:** <br>
A powerful Python-based web scraping tool that extracts comprehensive data from Instagram profiles using Selenium for browser automation and BeautifulSoup for HTML parsing.

# **🚀 Features:** <br>
🔐 Smart Session Management
Cookie-based authentication for persistent login sessions

Automatic session validation and renewal

Secure credential handling with environment variables support

Proxy configuration support for enhanced privacy

📊 Comprehensive Data Extraction
Profile Information: Username, full name, bio, verification status, profile picture

Account Statistics: Posts count, followers, following (with smart number parsing for K/M suffixes)

Post Details: Media URLs, captions, post types (image/reel/carousel), pinned status

Story Highlights: Titles, cover images, positioning data﻿# insta-                                                 

**🛡 Security & Ethics:** <br>
Environment variable support for sensitive data

Secure session storage with pickle serialization

Input validation and comprehensive error handling

Clear usage guidelines to promote ethical scraping practices


# **🚀 Quick Start:** <br>
Make sure Python is installed in your environment.

Clone git repository:

```bash
git clone https://github.com/sabasabafaraz789/insta-scrapper.git
```

Navigate to the instagram-scrapper folder and run:

```bash
Scripts\activate.bat
```

modify my_insta_scrapper/scrapper/view.py to input credentials manually:
 ```bash
 USERNAME = os.getenv('INSTAGRAM_USERNAME', "add your insta username") #add your insta username
 PASSWORD = os.getenv('INSTAGRAM_PASSWORD', "add your insta password") #add your insta password
```


Navigate to the instagram-scrapper/my_insta_scrapper then execute this command in the terminal:

```bash
python manage.py runserver  
```

Access the application:
Open your browser and go to http://127.0.0.1:8000/


