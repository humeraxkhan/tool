
import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import time
import os
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# User configs
GECKODRIVER_PATH = r"C:\Users\DELL\Downloads\geckodriver-v0.35.0-win32\geckodriver.exe"
FIREFOX_BINARY_PATH = r"C:\Program Files\Mozilla Firefox\firefox.exe"
MOBILE_NUMBER = "6261277633"  # Optional: You can remove login if not needed

# Streamlit UI
st.set_page_config(page_title="IndiaMART Scraper", layout="centered")
st.title("📦 IndiaMART Product Scraper")

query = st.text_input("🔍 Enter Product Search Query", value="infrared lamp sensor")
scroll_duration = st.number_input("⏱ Scroll Duration per Page (seconds)", value=30, min_value=10)
total_pages = st.number_input("📄 Number of Pages to Scrape", value=2, min_value=1)

if st.button("🚀 Start Scraping"):
    if not os.path.exists(GECKODRIVER_PATH):
        st.error("❌ GeckoDriver path is invalid.")
    elif not os.path.exists(FIREFOX_BINARY_PATH):
        st.error("❌ Firefox binary path is invalid.")
    else:
        st.success("✅ Starting browser...")

        options = Options()
        options.binary_location = FIREFOX_BINARY_PATH
        options.add_argument("--width=1200")
        options.add_argument("--height=800")
        service = Service(GECKODRIVER_PATH)
        driver = webdriver.Firefox(service=service, options=options)

        # Data containers
        product_names, prices, cities, addresses, companies = [], [], [], [], []

        try:
            for page in range(1, total_pages + 1):
                url = f"https://dir.indiamart.com/search.mp?ss={query.replace(' ', '+')}&page={page}"
                driver.get(url)
                st.info(f"🌐 Loaded Page {page}: {url}")
                time.sleep(5)

                # Optional Login (skip if not needed)
                if page == 1:  # Only attempt login on first page
                    try:
                        sign_in_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.LINK_TEXT, "Sign In"))
                        )
                        sign_in_button.click()
                        time.sleep(3)
                        mobile_field = WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((By.ID, "mobile"))
                        )
                        mobile_field.send_keys(MOBILE_NUMBER)
                        otp_button = WebDriverWait(driver, 15).until(
                            EC.element_to_be_clickable((By.ID, "passwordbtn1"))
                        )
                        otp_button.click()
                        st.warning("📩 Waiting for OTP... Please complete manually!")
                        WebDriverWait(driver, 300).until(
                            EC.presence_of_element_located((By.ID, "after_verified"))
                        )
                        st.success("✅ Logged in successfully")
                    except Exception:
                        st.warning("⚠ Could not log in. Proceeding anyway...")

                # Scroll for X seconds
                st.info(f"⏳ Scrolling Page {page} for {scroll_duration} seconds...")
                start = time.time()
                while time.time() - start < scroll_duration:
                    try:
                        show_more = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Show more results')]"))
                        )
                        show_more.click()
                        time.sleep(2)
                    except:
                        time.sleep(2)

                # Parse and extract
                soup = BeautifulSoup(driver.page_source, "html.parser")
                cards = soup.find_all("div", class_="card")

                for card in cards:
                    name = card.find("a", class_="cardlinks")
                    price = card.find("p", class_="price")
                    city_span = card.find("span", class_="elps elps1")
                    address_p = card.find("p", class_="tac wpw")
                    company = card.find("a", {"data-click": "^CompanyName"})

                    product_names.append(name.text.strip() if name else "No Name")
                    prices.append(price.text.strip() if price else "N/A")
                    cities.append(city_span.text.strip() if city_span else "N/A")
                    addresses.append(address_p.text.strip() if address_p else "N/A")
                    companies.append(company.text.strip() if company else "N/A")

            # Final DataFrame
            df = pd.DataFrame({
                "Product Name": product_names,
                "Price": prices,
                "City": cities,
                "Address": addresses,
                "Company": companies
            })

            filename = f"{query.replace(' ', '_')}_indiamart_results.xlsx"
            df.to_excel(filename, index=False)
            st.success("✅ Scraping complete!")

            with open(filename, "rb") as f:
                st.download_button("📥 Download Excel", f, file_name=filename)

        except Exception as e:
            st.error(f"❌ Error occurred: {e}")
        finally:
            driver.quit()