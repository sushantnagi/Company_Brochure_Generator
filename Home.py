import streamlit as st
import requests
from bs4 import BeautifulSoup
from google import genai
from google.genai import types
import json
from dotenv import load_dotenv
import time
import os

# Configure the Gemini client using Streamlit secrets
# api_key = st.secrets["GEMINI_API_KEY"]

# load_dotenv(override=True)
# api_key = os.getenv("GEMINI_API_KEY")
# api_key = st.secrets["api_keys"]["GEMINI_API_KEY"]
# print(api_key)

os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]


client = genai.Client()

# A class to represent a webpage
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    )
}


class Website:
    error_shown = False
    """
    A utility class to represent a scraped Website.
    It extracts the title, clean body text, and all hyperlinks.
    """

    def __init__(self, url):

        # Ensure URL starts with http/https
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        self.url = url
        self.title = "No title found"
        self.text = ""
        self.links = []

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            self.body = response.content

            soup = BeautifulSoup(self.body, "html.parser")

            self.title = soup.title.string.strip() if soup.title else "No title found"

            if soup.body:
                for irrelevant in soup.body(["script", "style", "img", "input"]):
                    irrelevant.decompose()
                self.text = soup.body.get_text(separator="\n", strip=True)
            else:
                self.text = ""

            links = [link.get("href") for link in soup.find_all("a")]
            self.links = [link for link in links if link]
            print(links)

        except Exception as e:
            if not Website.error_shown:
                st.error(f"This error indicates that either your WEBSITE or A PAGE IN YOUR WEBSITE in not accessible."
                "The program will proceed with Generating the Brochure anyways, based on whatever information it can find.")
                Website.error_shown = True

#            st.error(f"Failed to fetch or parse the webpage: {e}")

    def get_contents(self):
        return f"Webpage Title:\n{self.title}\n\nWebpage Contents:\n{self.text}\n\n..."


def get_combined_link_prompt(website):
    prompt = (
        "You are provided with a list of links found on a webpage. "
        "You are able to decide which of the links would be most relevant to include in a brochure about the company, "
        "such as links to an About page, or a Company page, or Careers/Jobs pages."
        "Atleast 13 Links. If a website has less than 13 links, decide atleast 6 Links.\n\n"

        "You should respond in JSON as in this example:\n"
        "{\n"
        '    "links": [\n'
        '        {"type": "about page", "url": "https://full.url/goes/here/about"},\n'
        '        {"type": "careers page", "url": "https://another.full.url/careers"}\n'
        "    ]\n"
        "}\n\n"
        
        "Respond with only raw JSON, no markdown or backticks. Don't add text like 'Here are your links'"

        f"Here is the list of links on the website of {website.url} - "
        "please decide which of these are relevant web links for a brochure about the company, respond with the full https URL in JSON format. "
        "Do not include Terms of Service, Privacy, email links.\n"
        "Links (some might be relative links):\n"
        f"{'\n'.join(website.links)}"
    )
    return prompt


def get_links(url):
    website = Website(url)
    prompt = get_combined_link_prompt(website)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            ),
        )

        full_response = response.text

        # Gemini should return valid JSON, so parse it
        return json.loads(full_response)

    except Exception as e:
        st.error(f"Failed to generate brochure links: {e}")
        return {"links": []}


# STEP 2 - Making the Brochure


def get_all_details(url):
    result = "Landing page:\n"
    result += Website(url).get_contents()
    links = get_links(url)
    for link in links["links"]:
        result += f"\n\n{link['type']}\n"
        result += Website(link["url"]).get_contents()
    return result


system_prompt_professional = (
    "You are an assistant that analyzes the contents of several relevant pages from a company website "
    "and creates a short brochure about the company for prospective customers, investors and recruits. Respond in markdown. "
    "Include details of company culture, customers and careers/jobs if you have the information."
)

system_prompt_sarcastic = (
    "You are an assistant that analyzes the contents of several relevant pages from a company website "
    "and creates a short humorous, entertaining, jokey brochure about the company for prospective customers, investors and recruits. Respond in markdown. "
    "Include details of company culture, customers and careers/jobs if you have the information."
)

system_prompt_bold = (
    "You are an assistant that analyzes the contents of several relevant pages from a company website "
    "and creates a bold, confident, no-nonsense brochure about the company for prospective customers, investors, and recruits. "
    "Respond in markdown. Use assertive language. Highlight achievements, mission, and values powerfully. "
    "Include details of company culture, customers, and careers/jobs if available."
)

system_prompt_casual = (
    "You are an assistant that analyzes the contents of several relevant pages from a company website "
    "and creates a chill, friendly, and conversational brochure for the company aimed at prospective customers, investors, and recruits. "
    "Respond in markdown. Write like you're talking to a friend. "
    "Include details of company culture, customers, and careers/jobs if you have them."
)

system_prompt_inspiring = (
    "You are an assistant that analyzes the contents of several relevant pages from a company website "
    "and creates an inspiring, visionary brochure for prospective customers, investors, and recruits. "
    "Respond in markdown. Focus on purpose, mission, impact, and transformation. "
    "Include details of company culture, customers, and careers/jobs if available."
)

system_prompt_minimalist = (
    "You are an assistant that analyzes the contents of several relevant pages from a company website "
    "and creates a clean, concise, minimalist brochure for prospective customers, investors, and recruits. "
    "Respond in markdown using short, impactful sentences and clean formatting. "
    "Include only the most essential details about company culture, customers, and careers/jobs if available."
)

system_prompt_friendly = (
    "You are an assistant that analyzes the contents of several relevant pages from a company website "
    "and creates a warm, inviting, friendly brochure for prospective customers, investors, and recruits. "
    "Respond in markdown. Use kind and encouraging language. "
    "Include details of company culture, customers, and careers/jobs if available."
)


def get_prompt_by_tone(tone):
    prompts = {
        "Professional": system_prompt_professional,
        "Sarcastic": system_prompt_sarcastic,
        "Bold": system_prompt_bold,
        "Casual": system_prompt_casual,
        "Inspiring": system_prompt_inspiring,
        "Minimalist": system_prompt_minimalist,
        "Friendly": system_prompt_friendly
    }
    return prompts.get(tone, system_prompt_professional)  # default fallback


def get_brochure_user_prompt(company_name, url):
    user_prompt = f"You are looking at a company called: {company_name}\n"
    user_prompt += (f"Here are the contents of its landing page and other relevant pages; use this information to "
                    f"build a short brochure of the company in markdown.\n")
    user_prompt += get_all_details(url)
    user_prompt = user_prompt[:5_000]  # Truncate if more than 5,000 characters
    return user_prompt


def create_brochure(system_prompt_text, user_prompt_text):
    full_prompt = f"{system_prompt_text}\n\n{user_prompt_text}"
    response = client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents=full_prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        )
    )

    st.subheader("Generated Brochure")
    brochure_output = ""
    for chunk in response:
        if chunk.candidates:
            for part in chunk.candidates[0].content.parts:
                brochure_output += part.text

    st.markdown(brochure_output)
    return brochure_output


st.set_page_config(
    page_title="AI Brochure Generator",
    page_icon="🧠",
    layout="wide"
)

st.image("image.png", width=500, use_container_width=False)

company_name_input = st.text_input("Enter the name of your company:")
company_website_input = st.text_input("Enter your company's website:")
selected_tone = st.selectbox(
    "Choose the tone of your brochure:",
    ["Professional", "Bold", "Sarcastic", "Casual", "Inspiring", "Minimalist", "Friendly"]
)

run = st.button("Generate Brochure")

if run:
    if not company_name_input or not company_website_input:
        st.error("Please enter both the company name and website.")
    else:

        with st.status("Extracting...", expanded=True) as status:
            time.sleep(0.5)
            status.update(label="Analyzing")
            time.sleep(0.5)
            status.update(label="Generating Brochure")
            time.sleep(1)
            status.update(label="Brochure generated! Displaying in a moment...", state="complete")

        final_system_prompt = get_prompt_by_tone(selected_tone)
        brochure_user_prompt = get_brochure_user_prompt(company_name_input, company_website_input)
        brochure_output = create_brochure(final_system_prompt, brochure_user_prompt)

















