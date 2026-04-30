## MyFinance — AI Personal Finance Tracker

A feature-rich personal finance tracker built with Streamlit that helps users manage expenses, track budgets, and gain AI-powered financial insights.

## Live Demo
https://myfinance---ai-personal-finance-tracker-jyrtg65zj47aoliwjdilpi.streamlit.app/

## Features
# 1. User Authentication
Signup & login system,
Secure session handling

# 2. Transaction Management
Add income & expenses,
Categorize spending,
Add notes for each transaction

# 3. Interactive Dashboard
Monthly income, expense & balance,
Savings rate calculation,
Category-wise spending breakdown,
Daily expense visualization
# 4. Search & History
Filter by month, category, type ,,
Keyword search,
Delete transactions

# 5. Advanced Analysis
Category distribution (pie chart),
Daily spending trends,
Month-over-month comparison,
Spending statistics

# 6. Budget Tracker
Set monthly budgets per category,
Track spending vs budget,
Alerts for overspending

# 7. AI Insights
Personalized financial tips,
Spending pattern detection (KMeans clustering),
Expense forecasting (Linear Regression),
Unusual spending alerts

## Tech Stack
- Frontend & App Framework: Streamlit
- Data Handling: Pandas, NumPy
- Visualization: Matplotlib
- Machine Learning: Scikit-learn

## Project Structure
├── app.py              # Main application
├── data.csv            # Stores transactions
├── users.csv           # Stores user credentials
├── budgets.csv         # Stores budget data
└── README.md           # Project documentation

## Installation & Setup

# 1️. Open Project Folder
Open the folder in terminal or VS Code
# 2.Install dependencies
pip install -r requirements.txt
# 3.Run the application
streamlit run app.py


## Screens / Modules
📊 Dashboard
➕ Add Transaction
🔍 Search & History
📈 Analysis
🎯 Budget Tracker
🤖 AI Insights

## How It Works
- Data is stored locally using CSV files
- User-specific data is filtered using session state
- Machine learning models:
- KMeans → groups spending patterns
- Linear Regression → predicts future expenses
- Real-time insights are generated from your transaction history

## Future Improvements
Cloud database integration (Firebase / MongoDB)
Expense auto-categorization using NLP
Mobile app version
Bank API integration
Multi-user analytics dashboard

## Author
Prachi Munjewar
