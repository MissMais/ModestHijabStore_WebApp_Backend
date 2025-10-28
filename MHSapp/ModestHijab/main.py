import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

# Gemini Configuration
api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")

# Load Dataset
data = pd.read_csv("MHSapp/ModestHijab/hijab_store.csv")  

# Helper Function for Filtering
def filter_products(query: str):
    """
    Extract keywords from the query and filter the hijab dataset.
    Returns top matching products as a small dataframe.
    """
    query_lower = query.lower()

    # Filter based on common attributes
    df_filtered = data[
        data.apply(lambda row:
                   (str(row["color"]).lower() in query_lower) or
                   (str(row["fabric"]).lower() in query_lower) or
                   (str(row["type"]).lower() in query_lower),
                   axis=1)
    ]

    # In case nothing matches
    if df_filtered.empty:
        return None

    # Limit results to top 5 products
    return df_filtered.head(5)

# Create LLM Prompt Function
def generate_response(user_query: str):
    """
    Uses the helper function to filter data, then passes it to Gemini.
    Produces a customer-friendly answer.
    """
    filtered = filter_products(user_query)

    if filtered is None:
        return "I'm sorry, I couldn’t find any hijabs matching your request. Could you please specify color or fabric?"

    # Convert filtered rows to text (compact view)
    product_info = "\n".join(
        [f"- {row['name']} | {row['color']} | {row['fabric']} | ₹{row['price']} | {row['availability']} | {row['link']}"
         for _, row in filtered.iterrows()]
    )

    # Instruction for Gemini
    prompt = f"""
You are a friendly shopping assistant for a hijab store.
The user asked: "{user_query}"

Here are some matching hijabs from the inventory:
{product_info}

Your task:
1. Greet the customer warmly.
2. Recommend the best matching hijabs.
3. Present each item neatly with emojis and links.
4. Keep tone elegant, short, and pleasing.

If there are multiple options, list 2–3 best ones nicely.
"""

    response = model.generate_content(prompt)
    print(product_info)
    return response.text

# Example Usage
# user_query = "I want a satin hijab "
# final_response = generate_response(user_query)
# print(final_response)