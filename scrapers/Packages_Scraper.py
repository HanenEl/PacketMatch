# ══════════════════════════════════════════════════════════════════════════════
# Scrapes WE internet package details (size, price, speed) from the TE website
# across all plan categories, then loads the results into a DataFrame.
# ══════════════════════════════════════════════════════════════════════════════

import requests
from bs4 import BeautifulSoup
import pandas as pd

base_urls = {
    "Super": "https://te.eg/wps/portal/te/Personal/WEInternet/WESpaceSuper",
    "Mega": "https://te.eg/wps/portal/te/Personal/WEInternet/WESpaceMega",
    "Ultra": "https://te.eg/wps/portal/te/Personal/WEInternet/WESpaceUltra",
    "Max": "https://te.eg/wps/portal/te/Personal/WEInternet/WESpaceMax/",
    "MaxP": "https://te.eg/wps/portal/te/Personal/WEInternet/WESpaceMaxPlus/"
}
def main():
    all_packages = []
    for plan_type, url in base_urls.items():
        
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "lxml")

        sections = soup.find_all("div", class_="plan-card")
        for section in sections:
            size = section.find("h4", class_="title")
            price = section.find("h5", class_="sub-title")
            yearly_price = section.find("h6", class_="desc")
            speed = section.find("h6", class_="info")

            all_packages.append({
                "Category": plan_type,
                "Package Size": size.get_text(strip=True) if size else None,
                "Monthly Price": price.get_text(strip=True) if price else None,
                "Yearly Price": yearly_price.get_text(strip=True) if yearly_price else None,
                "Speed": speed.get_text(strip=True) if speed else None
            })

    df = pd.DataFrame(all_packages)
    print(df)
if __name__ == "__main__":
    main()