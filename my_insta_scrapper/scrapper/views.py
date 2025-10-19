from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.template import loader
from .models import Scrapper
from django.http import JsonResponse
from django.conf import settings
from pathlib import Path
from .instagram_tool.selenium import InstagramSession 
from .instagram_tool.beautifulsope import InstagramScraper
import json
import os

def instagram_dashboard(request):
    """
    Main dashboard view that handles all functionality
    """
    json_path = Path(__file__).resolve().parent / "instagram_tool" / "instagram_profile_data.json"
    data = {}
    
    # Load existing data if available
    if json_path.exists():
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error loading JSON data: {e}")
    
    # Handle form submission for scraping
    if request.method == "POST":
        profile_url = request.POST.get('profile_url')
        
        if profile_url:
            # Step 1: Login and scrape with Selenium
            insta = InstagramSession()
            USERNAME = os.getenv('INSTAGRAM_USERNAME', "add your insta username") #add your insta username
            PASSWORD = os.getenv('INSTAGRAM_PASSWORD', "add your insta password") #add your insta password
            
            try:
                if insta.initialize_session(USERNAME, PASSWORD):
                    insta.perform_action(str(profile_url))
                    
                    # Step 2: Process the scraped HTML with BeautifulSoup
                    save_path = Path(__file__).resolve().parent / "instagram_tool"
                    file_path = save_path / "full_page.html"
                    
                    if file_path.exists():
                        with open(file_path, "r", encoding="utf-8") as f:
                            html_content = f.read()
                        
                        scraper = InstagramScraper(html_content)
                        data = scraper.extract_all_data()
                        
                        # Save the data
                        json_file_path = save_path / "instagram_profile_data.json"
                        with open(json_file_path, "w", encoding="utf-8") as f:
                            json.dump(data, f, indent=2, ensure_ascii=False)
                        
                        messages.success(request, f"Instagram data fetched successfully from {profile_url}")
                    else:
                        messages.error(request, "Scraped HTML file not found")
                else:
                    messages.error(request, "Instagram login failed. Please check credentials.")
            except Exception as e:
                messages.error(request, f"Error scraping data: {str(e)}")
        
        return redirect('instagram_dashboard')
    
    return render(request, "main.html", {"data": data})