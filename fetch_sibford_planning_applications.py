import json

from bs4 import BeautifulSoup
from playwright.sync_api import Playwright, expect, sync_playwright

applications = []

def extract_planning_applications(html_content):
    """
    Extract planning application references and URLs from the HTML content.
    
    Args:
        html_content (str): HTML content as a string
        
    Returns:
        list: List of dictionaries containing reference numbers and URLs
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all rows in the results table
    results = []
    rows = soup.select('table.tblResults tbody tr')
    
    for row in rows:
        # Find the link element that contains both reference number and URL
        link = row.select_one('td a[href^="/Planning/Display/"]')
        
        if link:
            results.append({
                'reference': link.text.strip(),
                'url': link['href']
            })
    
    return results


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    for parish in ["SIBG", "SIBF"]:
        page.goto("https://planningregister.cherwell.gov.uk/Search/Advanced")
        page.get_by_label("Checkbox input: Search planning records.").check()
        page.get_by_label("Dropdown input: Select a parish.").select_option(parish)
        page.get_by_label("Button: Search.").click()
        page.get_by_text("Skip to results. Back to").click()

        area = page.get_by_text("Skip to results. Back to")

        parish_applications = extract_planning_applications(area.inner_html())
        applications.extend(parish_applications)

    # ---------------------
    context.close()
    browser.close()

    # write output to JSON file
    with open('applications.json', 'w') as f:
        json.dump(applications, f)



with sync_playwright() as playwright:
    run(playwright)
