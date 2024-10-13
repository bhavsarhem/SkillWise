import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from io import BytesIO
import numpy as np  # Import numpy for trigonometric functions

# Initialize an empty DataFrame or load existing data
if "expenses" not in st.session_state:
    st.session_state["expenses"] = pd.DataFrame(columns=["Date", "Category", "Description", "Amount"])

# App title
st.title("Personal Expense Tracker")

# Input form to add new expenses
st.header("Add a New Expense")
with st.form("expense_form"):
    date = st.date_input("Date", datetime.now())
    category = st.selectbox("Category", ["Food", "Transport", "Utilities", "Entertainment", "Health", "Other"])
    description = st.text_input("Description")
    amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    submit = st.form_submit_button("Add Expense")

    # Add expense to DataFrame
    if submit:
        new_expense = pd.DataFrame([[date, category, description, amount]], columns=["Date", "Category", "Description", "Amount"])
        st.session_state["expenses"] = pd.concat([st.session_state["expenses"], new_expense], ignore_index=True)
        st.success("Expense added successfully!")

# Display the expense data
st.header("Expense History")
if not st.session_state["expenses"].empty:
    # Show the data as a table
    st.dataframe(st.session_state["expenses"])

    # Show total expense
    total_expense = st.session_state["expenses"]["Amount"].sum()
    st.subheader(f"Total Expense: ₹{total_expense:.2f}")

    # Filter expenses by category
    st.header("Filter by Category")
    categories = ["All"] + list(st.session_state["expenses"]["Category"].unique())
    selected_category = st.selectbox("Select a Category to Filter", options=categories, index=0)
    if selected_category != "All":
        filtered_expenses = st.session_state["expenses"][st.session_state["expenses"]["Category"] == selected_category]
        st.dataframe(filtered_expenses)
        total_filtered_expense = filtered_expenses["Amount"].sum()
        st.subheader(f"Total for {selected_category}: ₹{total_filtered_expense:.2f}")

# Create and download category-wise chart
st.header("Download Category-wise Expense Chart")
if st.button("Generate Chart"):
    if st.session_state["expenses"].empty:
        st.error("No data available to generate the chart. Please add some expenses first.")
    else:
        fig, ax = plt.subplots()
        category_expenses = st.session_state["expenses"].groupby("Category")["Amount"].sum()
        
        # Create a half-pie chart
        wedges, texts, autotexts = ax.pie(
            category_expenses,
            autopct='%1.1f%%',
            startangle=90,
            counterclock=False,
            wedgeprops=dict(width=0.3)
        )
        
        # Set the figure background to be transparent
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        
        # Customize text headings
        for text in texts + autotexts:
            text.set_color('blue')  # Change this to any color you prefer, except black

        ax.set_title("Expenses by Category", color='red')  # Change this to any color you prefer, except black)
        ax.set_ylabel("")  # Remove the y-label for a cleaner pie chart

        # Add category names with different colors
        colors = ['blue', 'green', 'red', 'purple', 'orange', 'brown']  # Add more colors as needed
        for i, (wedge, category) in enumerate(zip(wedges, category_expenses.index)):
            angle = (wedge.theta2 - wedge.theta1) / 2.0 + wedge.theta1
            x = 0.35 * np.cos(np.radians(angle))
            y = 0.35 * np.sin(np.radians(angle))
            ax.text(x, y, category, horizontalalignment='center', color=colors[i % len(colors)])

        buf = BytesIO()
        fig.savefig(buf, format="png", transparent=True)
        buf.seek(0)
        st.download_button(
            label="Download Chart",
            data=buf,
            file_name="category_expenses_chart.png",
            mime="image/png"
        )
        st.pyplot(fig)

# Add an option to reset the tracker
if st.button("Reset All Data"):
    st.session_state["expenses"] = pd.DataFrame(columns=["Date", "Category", "Description", "Amount"])
    st.warning("All data has been reset.")

# Add a sidebar with app information
st.sidebar.title("About")
st.sidebar.info("This is a simple personal expense tracker built with Streamlit. You can add expenses, view your expense history, and filter by category.")
