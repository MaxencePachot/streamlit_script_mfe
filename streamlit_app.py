import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from connexion_mariadbazure import get_mariadb_connection

# Connect to your MySQL database
conn = get_mariadb_connection()

# Function to fetch data from the database
@st.cache_resource
def fetch_orders_by_year():   
    data = None  # Assign an initial value to data 
    with conn.cursor() as cur:
        try:
            cur.execute("""
                        SELECT YEAR(orders_date) AS year, COUNT(*) AS order_count
                        FROM orders
                        GROUP BY year
                        ORDER BY year
                        """)
            # Fetch the number of orders by year
            data = cur.fetchall()
            conn.commit()
        except Exception as e:
            print("Exeception occured:{}".format(e))
            conn.rollback()
    return data

@st.cache_resource
def fetch_orders_by_city():
    data = None  # Assign an initial value to data
    with conn.cursor() as cur:
        try:
            cur.execute("""
                        SELECT city.city_name, COUNT(*) AS order_count
                        FROM orders
                        INNER JOIN customer ON orders.orders_customer_id = customer.customer_id
                        INNER JOIN address ON customer.customer_address_id = address.address_id
                        INNER JOIN city ON address.address_city_id = city.city_id
                        GROUP BY city_name
                        """)
            # Fetch the number of orders by city
            data = cur.fetchall()
            conn.commit()
        except Exception as e:
            print("Exeception occured:{}".format(e))
            conn.rollback()
    return data

@st.cache_resource
def fetch_orders_by_shipper():
    data = None  # Assign an initial value to data
    with conn.cursor() as cur:
        try:
            cur.execute("""
                        SELECT shipper.shipper_name, COUNT(*) AS order_count
                        FROM orders
                        INNER JOIN shipper ON orders.orders_shipper_id = shipper.shipper_id
                        GROUP BY shipper_name
                        """)
            # Fetch the number of orders by shipper
            data = cur.fetchall()
            conn.commit()
        except Exception as e:
            print("Exeception occured:{}".format(e))
            conn.rollback()
    return data

@st.cache_resource
def fetch_product_name():
    with conn.cursor() as cur:
        try:
            cur.execute("""
                        SELECT product_name
                        FROM product
                        """)
            # Fetch the product name
            data = cur.fetchall()
            conn.commit()
        except Exception as e:
            print("Exception occurred: {}".format(e))
            conn.rollback()
    return data

def select_product(data_product):
    # Convert the tuple into a list
    product_name_tuple = st.selectbox("Select a product", data_product)
    # Extract the product name from the tuple
    product_name = product_name_tuple[0]
    return product_name

def fetch_product_orders_by_year(data_product): 
    data = None  # Assign an initial value to data
    with conn.cursor() as cur:
        try:
            product_name = select_product(data_product)
            # Fetch the number of orders by product and year
            query = ("""
                    SELECT YEAR(orders.orders_date) AS year, SUM(orders_quantity.orders_quantity_quantity) AS quantity, product.product_name 
                    FROM orders
                    JOIN orders_quantity ON orders.orders_id = orders_quantity.orders_quantity_orders_id
                    JOIN product ON orders_quantity.orders_quantity_product_id = product.product_id
                    WHERE product.product_name = %s
                    GROUP BY year, product.product_name
                    ORDER BY year;
                    """)
            # Pass the parameter as a tuple
            cur.execute(query, (product_name,))  
            data = cur.fetchall()
            conn.commit()
        except Exception as e:
            print("Exception occurred: {}".format(e))
            conn.rollback()
        return data

@st.cache_resource
def fetch_category_orders_by_year():
    data = None  # Assign an initial value to data
    with conn.cursor() as cur:
        try:
            cur.execute("""
                        SELECT category_name as category, SUM(orders_quantity.orders_quantity_quantity) AS quantity
                        FROM orders
                        JOIN orders_quantity ON orders.orders_id = orders_quantity.orders_quantity_orders_id
                        JOIN product ON orders_quantity.orders_quantity_product_id = product.product_id
                        JOIN category ON product.product_category_id = category.category_id
                        GROUP BY category_name
                        """)
            # Fetch the number of orders by category and year
            data = cur.fetchall()
            conn.commit()
        except Exception as e:
            print("Exeception occured:{}".format(e))
            conn.rollback()
    return data

def main():

    # Fetch the product name
    data_product = fetch_product_name()

    # Add custom CSS styles for colors
    st.markdown(
        """
        <style>
        body {
            background-color: #f5f5f5;
        }
        h1 {
            color: #3366cc;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Make interactive dropdown list
    st.sidebar.title("Menu")
    
    # Choose the graph to display
    # Basic, none is selected
    graph = st.sidebar.selectbox("Select a graph", ["Choose a graph to display", "Number of Orders Year After Year", "Number of Orders by City", "Number of Orders by Shipper", "Product Orders by Year", "Category Orders by Year"])

    if graph == "Choose a graph to display":
        # Diplay general information
        st.title("Menu")
        st.write("This is a dashboard to display the data from the MariaDB Azure database.")
        st.write("The data is displayed in the form of graphs and tables.")
        st.write("The data is fetched from the database using Python and the Streamlit library is used to display the data.")

        # Add an image from a local file
        st.image("reception.jpg", use_column_width=True)
   
    # Display the selected graph
    elif graph == "Number of Orders Year After Year":
        #
        # Number of Orders Year After Year
        #

        st.title("Number of Orders Year After Year")

        # Fetch data from the database
        data_ooy = fetch_orders_by_year()

        # Convert the data into a Pandas DataFrame
        df = pd.DataFrame(data_ooy, columns=["Year", "Order Count"])

        if not df.empty:
            # Create a bar plot using the DataFrame
            fig, ax = plt.subplots()
            ax.plot(df["Year"], df["Order Count"], marker="o")

            ax.set_xlabel("Years")
            ax.set_ylabel("Number of Orders")
            ax.set_title("Number of Orders Year After Year")

            # Display the plot using Streamlit
            st.pyplot(fig)

            # Display the data table
            st.subheader("Data Table")
            st.table(df)

        else:
            st.write("No data to display.")    

    elif graph == "Number of Orders by City":
        #
        # Number of Orders by City
        #

        st.title("Number of Orders by City")

        # Fetch data from the database
        data_obc = fetch_orders_by_city()

        # Convert the data into a Pandas DataFrame
        df = pd.DataFrame(data_obc, columns=["City", "Order Count"])

        if not df.empty:
            # Create a bar plot using the DataFrame
            fig, ax = plt.subplots()
            ax.bar(df["City"], df["Order Count"])

            ax.set_xlabel("Cities")
            ax.set_ylabel("Number of Orders")
            ax.set_title("Number of Orders by City")

            # Rotate the x-axis labels
            plt.xticks(rotation=90)

            # Display the plot using Streamlit
            st.pyplot(fig)

            # Display the data table
            st.subheader("Data Table")
            st.table(df)
        else:
            st.write("No data to display.")

    elif graph == "Number of Orders by Shipper":
        #
        # Number of Orders by shipper
        #

        st.title("Number of Orders by Shipper")

        # Fetch data from the database
        data_obs = fetch_orders_by_shipper()

        # Convert the data into a Pandas DataFrame
        df = pd.DataFrame(data_obs, columns=["Shipper", "Order Count"])

        if not df.empty:
            # Create a pie plot using the DataFrame
            fig, ax = plt.subplots()
            ax.pie(df["Order Count"], labels=df["Shipper"], autopct="%1.1f%%", startangle=90)

            ax.set_title("Number of Orders by Shipper")

            # Display the plot using Streamlit
            st.pyplot(fig)

            # Display the data table
            st.subheader("Data Table")
            st.table(df)
        else: 
            st.write("No data to display.")

    elif graph == "Product Orders by Year":
        #
        # Number of Orders by Product Year After Year
        #

        st.title("Product Orders Year After Year")

        # Fetch data from the database
        data = fetch_product_orders_by_year(data_product)

        # Convert the data into a Pandas DataFrame
        df = pd.DataFrame(data, columns=["Year", "Quantity", "Product"])

        if not df.empty:
            # Create a line plot using the DataFrame
            fig, ax = plt.subplots()
            ax.plot(df["Year"], df["Quantity"], marker="o", label=df["Product"].iloc[0])  # Use iloc[0] to access the first value

            ax.set_xlabel("Year")
            ax.set_ylabel("Quantity")
            ax.set_title("Product Orders Year After Year")
            ax.legend()

            # Display the plot using Streamlit
            st.pyplot(fig)
        else:
            st.write("No data available for the selected product.")
        
        # Display the data table
        st.subheader("Data Table")
        st.table(df)

    elif graph == "Category Orders by Year":
        #
        # Number of Orders by Category Year After Year
        #

        st.title("Category Orders Year After Year")

        # Fetch data from the database
        data = fetch_category_orders_by_year()

        # Convert the data into a Pandas DataFrame
        df = pd.DataFrame(data, columns=["Category","Quantity"])

        if not df.empty:
            # Create a bar plot using the DataFrame
            fig, ax = plt.subplots()
            ax.bar(df["Category"], df["Quantity"])

            ax.set_xlabel("Categories")
            ax.set_ylabel("Quantity")
            ax.set_title("Quantity of Products by Category")

            # Display the plot using Streamlit
            st.pyplot(fig)

            # Display the data table
            st.subheader("Data Table")
            st.table(df)

        else:
            st.write("No data available for the selected category.")

if __name__ == "__main__":
    main()



