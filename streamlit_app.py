# Import python packages
import pandas as pd
import requests
import streamlit as st
from snowflake.snowpark.functions import col

# Write directly to the app
st.title("🥤 Customize Your Smoothie 🥤")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """
)

# Sanitize name_on_order input
name_on_order = st.text_input("Name on Smoothie:")
sanitized_name = name_on_order.strip()
st.write("The name on your Smoothie will be:", sanitized_name)

cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert the Snowpark Dataframe to a Pandas Dataframe so we can use the LOC function
pd_df = my_dataframe.to_pandas()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:'
    , my_dataframe
    , max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        
        try:
            # Secure API request with error handling
            fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
            fruityvice_response.raise_for_status()  # Raise exception for non-200 status codes
            fv_json = fruityvice_response.json()

            st.subheader(fruit_chosen + ' Nutrition Information')
            fv_df = st.dataframe(data=fv_json, use_container_width=True)
        except requests.RequestException as e:
            st.error(f"Error accessing API: {e}")

    # Validate selected ingredients
    if not all(ingredient in pd_df['FRUIT_NAME'].values for ingredient in ingredients_list):
        st.error("Invalid ingredient selected.")
    
    # Use parameterized query to prevent SQL injection
    my_insert_stmt = "INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES (?, ?)"
    try:
        session.sql(my_insert_stmt, (ingredients_string, sanitized_name))
    except Exception as e:
        st.error(f"Error inserting order into database: {e}")

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        try:
            session.sql(my_insert_stmt, (ingredients_string, sanitized_name)).collect()
            success_text = f"Your Smoothie is ordered, {sanitized_name}!"
            st.success(success_text, icon="✅")
        except Exception as e:
            st.error(f"Error submitting order: {e}")
