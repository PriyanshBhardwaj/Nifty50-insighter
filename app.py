import streamlit as st
import json

import urllib.request
import urllib.parse
from datetime import datetime, timedelta

import os
from dotenv import load_dotenv

# load the JSON file
def load_data():
    with open("companies.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    return data

# extract company names from JSON data
def get_company_names(data):
    return [company["company"] for company in data]

# get nifty50 history
def get_nifty50_history(company_name, company_data):
    """Returns NIFTY50 history insights for a given company in a bullet-point list."""

    # Convert 'date_added' to datetime object
    date_added = datetime.strptime(company_data["date_added"], "%d %B %Y")
    today = datetime.today()

    # Define time thresholds
    one_year_ago = today - timedelta(days=365)
    five_years_ago = today - timedelta(days=5 * 365)
    ten_years_ago = today - timedelta(days=10 * 365)

    # Prepare history list
    history_status = [f"{company_name} is added to the NIFTY50 list on {company_data['date_added']}"]

    history_status.append(f"It is a part of NIFTY50 list from last 10 years" if date_added <= ten_years_ago else f"It is not a part of NIFTY50 list from last 10 years")
    history_status.append(f"It is a part of NIFTY50 list from last 5 years" if date_added <= five_years_ago else f"It is not a part of NIFTY50 list from last 5 years")
    history_status.append(f"It is a part of NIFTY50 list from last 12 months" if date_added <= one_year_ago else f"It is not a part of NIFTY50 list from last 12 months")

    return history_status

# fetch news from Gnews API
def fetch_latest_news(query, max_results=5, country="in", lang="en", time_range="2d"):
    """
    Fetch the latest news articles about a given query using the GNews API.

    Args:
        query (str): The search query (e.g., company name like 'Adani Enterprises Ltd').
        api_key (str): Your GNews API key.
        max_results (int, optional): Number of articles to fetch (default: 2).
        country (str, optional): Country filter for the news (default: 'in' for India).
        lang (str, optional): Language filter (default: 'en' for English).

    Returns:
        list[dict]: A list of news articles with 'title', 'description', 'content', 'url', and 'summary'.
    """

    # # Calculate the date 24 hours ago
    # from_date = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')

    # Load API Key from .env file
    api_key = os.getenv("GNEWS_API_KEY")
    
    if not api_key:
        raise ValueError("GNEWS_API_KEY is missing in .env file.")


    # Construct the API URL
    url = f"https://gnews.io/api/v4/search?q={urllib.parse.quote(query)}&category=business&lang={lang}&country={country}&max={max_results}&from={time_range}&apikey={api_key}"

    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode("utf-8"))
            articles = data.get("articles", [])

            if not articles:
                print("No recent news found. Expanding search...")
                return fetch_latest_news(query, max_results=2, country="in", lang="en", time_range="7d")  # Try last 7 days

            news_list = []
            if not articles:
                return [{"message": "No recent news found for the specified query."}]

            for article in articles:
                # content = article.get("content", "")
                description = article.get("description", "")
                # title = article.get("title", "")
                url = article.get("url", "")

                news_list.append({
                    # "title": title,
                    "news": description,
                    # "content": content,
                    "url": url
                })

            return news_list

    except urllib.error.URLError as e:
        return [{"error": f"Failed to fetch data: {e.reason}"}]
    except json.JSONDecodeError:
        return [{"error": "Failed to parse JSON response."}]


# Main function
def main():
    st.title("NIFTY50 Company Insights")
    
    # Load data
    data = load_data()
    company_names = get_company_names(data)
    
    # Streamlit dropdown
    selected_company = st.selectbox("Select a company", ["None"] + company_names)
    
    # Display history and insights
    if selected_company != "None":
        # company data
        company_data = next(item for item in data if item["company"] == selected_company)
        
        # company nifty50 history
        company_nifty50_history = get_nifty50_history(selected_company, company_data)
        
        st.subheader("Company History")
        st.write(company_data["history"])

        st.subheader("NIFTY50 History")
        for status in company_nifty50_history:
            st.write(f"- {status}")
        
        st.subheader("Financial Insights")
        for insight in company_data["insights"]:
            st.write(f"- {insight}")
        
        
        st.subheader("Company News")
        #get company news
        company_news = fetch_latest_news(selected_company)

        for news in company_news:
            # st.write(f"- {news['news']}")
            # st.write(f" {news['url']}")

            st.markdown(f"""
                - {news['news']}
                    - {news['url']}
                """)
        


if __name__ == "__main__":
    main()
