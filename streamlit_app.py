# Import python packages
import streamlit as st
import requests

# Function to insert order into Snowflake database
def insert_order(ingredients, name_on_order):
    try:
        cnx = st.connection("snowflake")
        session = cnx.session()

        # Use parameterized query to prevent SQL injection
        insert_query = "INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES (?, ?)"
        session.execute(insert_query, (ingredients, name_on_order))
        
        return True
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return False

# Streamlit app
def main():
    st.title("🥤 Customize Your Smoothie 🥤")
    st.write("""Choose the fruits you want in your custom Smoothie!""")
    
    name_on_order = st.text_input("Name on Smoothie:")
    st.write("The name on your Smoothie will be:", name_on_order)

    my_dataframe = st.experimental_get_query_params()['snowflake'].table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
    
    ingredients_list = st.multiselect(
        'Choose up to 5 ingredients:'
        , my_dataframe
        , max_selections=5
    )

    if st.button('Submit Order'):
        ingredients_string = ', '.join(ingredients_list)
        if ingredients_list:
            if insert_order(ingredients_string, name_on_order):
                success_text = f"Your Smoothie is ordered, {name_on_order.strip()}!"
                st.success(success_text, icon="✅")

    # Display nutrition information
    fruityvice_response = requests.get("https://fruityvice.com/api/fruit/watermelon")
    st.text(fruityvice_response.json())

if __name__ == "__main__":
    main()
