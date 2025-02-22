import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Load saved expenses when the app starts
if 'expenses' not in st.session_state:
    try:
        st.session_state.expenses = pd.read_csv('expenses.csv')
        st.session_state.expenses['Date'] = pd.to_datetime(st.session_state.expenses['Date']).dt.date
    except FileNotFoundError:
        st.session_state.expenses = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Description'])

# Function to add a new expense
def add_expense(date, category, amount, description):
    new_expense = pd.DataFrame([[date, category, amount, description]], columns=['Date', 'Category', 'Amount', 'Description'])
    st.session_state.expenses = pd.concat([st.session_state.expenses, new_expense], ignore_index=True)
    save_expenses()

# Function to clear all expenses
def clear_expenses():
    st.session_state.expenses = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Description'])
    save_expenses()
    st.success("All expenses cleared!")

# Function to load expenses from a file
def load_expenses(uploaded_file):
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.csv'):
            st.session_state.expenses = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xls', '.xlsx')):
            st.session_state.expenses = pd.read_excel(uploaded_file)
        
        st.session_state.expenses['Date'] = pd.to_datetime(st.session_state.expenses['Date'], errors='coerce').dt.date
        required_columns = ['Date', 'Category', 'Amount', 'Description']
        for col in required_columns:
            if col not in st.session_state.expenses.columns:
                st.error(f"Missing required column: {col}")
                return
        
        st.session_state.expenses = st.session_state.expenses[required_columns]
        save_expenses()

# Function to save expenses
def save_expenses():
    st.session_state.expenses.to_csv('expenses.csv', index=False)
    st.session_state.expenses.to_excel('expenses.xlsx', index=False)
    st.success("Expenses Saved Successfully")

# Function to visualize expenses
def visualize_expenses(start_date, end_date):
    if not st.session_state.expenses.empty:
        filtered_expenses = st.session_state.expenses[
            (st.session_state.expenses['Date'] >= start_date) & (st.session_state.expenses['Date'] <= end_date)
        ]
        if not filtered_expenses.empty:
            expense_summary = filtered_expenses.groupby('Category')['Amount'].sum().reset_index()
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(data=expense_summary, x='Category', y='Amount', ax=ax, palette='viridis')
            plt.xticks(rotation=45)
            plt.title(f'Total Expenses by Category from {start_date} to {end_date}')
            st.pyplot(fig)
        else:
            st.warning(f"No expenses found between {start_date} and {end_date}.")
    else:
        st.warning("No expenses available to visualize.")

# Function to calculate total expenses in a date range
def display_summary(start_date, end_date):
    filtered_expenses = st.session_state.expenses[
        (st.session_state.expenses['Date'] >= start_date) & (st.session_state.expenses['Date'] <= end_date)
    ]
    return filtered_expenses['Amount'].sum()

# Streamlit app layout
st.title("BudgetBuddy Expense Tracker")

with st.sidebar:
    st.header('Add Expense')
    date = st.date_input('Date', datetime.today())
    category = st.selectbox('Category', ['Food', 'Transport', 'Entertainment', 'Utilities', 'Other'])
    amount = st.number_input('Amount', min_value=0.0, format="%.2f")
    description = st.text_input('Description')
    if st.button('Add'):
        add_expense(date, category, amount, description)
        st.success("Expense Added!")

    st.header('File Operations')
    uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xlsx', 'xls'])
    if uploaded_file is not None:
        load_expenses(uploaded_file)
        st.success("Expenses Loaded Successfully")
    
    if st.button('Save Expenses'):
        save_expenses()
    
    if st.button('Clear All Expenses'):
        clear_expenses()

# Display the expenses DataFrame
st.header('Expenses')
st.write(st.session_state.expenses)

# Select date range for summary
st.header("Expense Summary")
start_date = st.date_input('Start Date', datetime.today().replace(day=1))
end_date = st.date_input('End Date', datetime.today())
total_amount_spent = display_summary(start_date, end_date)

total_budget = st.number_input(f'Enter your total budget for selected period:', min_value=0.0, format="%.2f")
remaining_budget = total_budget - total_amount_spent

st.write(f'**Total Budget:** ${total_budget:.2f}')
st.write(f'**Total Amount Spent:** ${total_amount_spent:.2f}')
st.write(f'**Remaining Budget:** ${remaining_budget:.2f}')

if remaining_budget >= 0:
    st.success(f'You are within budget! ${remaining_budget:.2f} remaining.')
else:
    st.error(f'You have exceeded your budget by ${abs(remaining_budget):.2f}.')

st.header('Visualization')
if st.button('Visualize Expenses'):
    visualize_expenses(start_date, end_date)

st.write('Keep track of your expenses to stay on top of your budget!')
