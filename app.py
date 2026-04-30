# ===============================
# PRO-LEVEL AI PERSONAL FINANCE TRACKER — REAL-LIFE EDITION
# ===============================

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
import os
import calendar

# ---------------- CONFIG ----------------
st.set_page_config(page_title="MyFinance", layout="wide", page_icon="💸")
DATA_FILE   = "data.csv"
USER_FILE   = "users.csv"
BUDGET_FILE = "budgets.csv"

CATEGORIES = ["Food", "Transport", "Shopping", "Bills & Utilities",
              "Health", "Investment", "Education", "Entertainment",
              "Rent", "Groceries", "EMI / Loan", "Other"]

DARK   = "#0e1117"
CARD   = "#1c1f26"
ACCENT = "#00e5a0"
RED    = "#ff4b4b"
BLUE   = "#00c8ff"

# ---------------- STYLING ----------------
st.markdown(f"""
<style>
body, .main {{ background-color:{DARK}; color:#f0f0f0; }}
.block-container {{ padding-top:1.5rem; padding-bottom:2rem; }}
div[data-testid="metric-container"] {{
    background:{CARD}; border-radius:12px; padding:16px 20px;
    border-left: 4px solid {ACCENT};
    box-shadow: 0 4px 14px rgba(0,0,0,0.5);
}}
.stProgress > div > div {{ background-color:{ACCENT} !important; }}
div.stButton > button {{
    background: {ACCENT}; color:#000; font-weight:700;
    border-radius:8px; border:none; padding:0.4rem 1.2rem;
}}
div.stButton > button:hover {{ opacity:0.85; }}
.section-title {{
    font-size:1.1rem; font-weight:700; color:{ACCENT};
    border-bottom:1px solid #333; padding-bottom:6px; margin-bottom:12px;
}}
</style>
""", unsafe_allow_html=True)

# ---------------- HELPERS ----------------
def dark_fig(w=6, h=4):
    fig, ax = plt.subplots(figsize=(w, h), facecolor=DARK)
    ax.set_facecolor(CARD)
    ax.tick_params(colors="#aaa")
    for spine in ax.spines.values():
        spine.set_edgecolor("#333")
    return fig, ax

def load_users():
    if os.path.exists(USER_FILE):
        return pd.read_csv(USER_FILE, dtype=str)
    return pd.DataFrame(columns=["username", "password"])

def save_user(u, p):
    df = load_users()
    if (df["username"] == u).any():
        return False
    df = pd.concat([df, pd.DataFrame([[u, p]], columns=["username","password"])], ignore_index=True)
    df.to_csv(USER_FILE, index=False)
    return True

def load_all_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE, dtype={"User": str})
    return pd.DataFrame(columns=["Date","Category","Amount","Type","Note","User"])

def get_user_data(username):
    df = load_all_data()
    if "User" in df.columns:
        return df[df["User"] == username].copy()
    return pd.DataFrame(columns=["Date","Category","Amount","Type","Note","User"])

def save_transaction(row: pd.DataFrame):
    df = load_all_data()
    df = pd.concat([df, row], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# ---------------- BUDGET ----------------
def load_budgets(username):
    if os.path.exists(BUDGET_FILE):
        df = pd.read_csv(BUDGET_FILE, dtype={"User": str})
        row = df[df["User"] == username]
        if not row.empty:
            return dict(zip(row["Category"], row["Budget"].astype(float)))
    return {}

def save_budgets(username, budgets: dict):
    rows = [{"User": username, "Category": cat, "Budget": amt}
            for cat, amt in budgets.items() if amt > 0]
    new_df = pd.DataFrame(rows)
    if os.path.exists(BUDGET_FILE):
        df = pd.read_csv(BUDGET_FILE, dtype={"User": str})
        df = df[df["User"] != username]
        df = pd.concat([df, new_df], ignore_index=True)
    else:
        df = new_df
    df.to_csv(BUDGET_FILE, index=False)

# ===================== SESSION =====================
if "user" not in st.session_state:
    st.session_state.user = None

# ===================== LOGIN =====================
if st.session_state.user is None:
    st.markdown("<h1 style='text-align:center;margin-top:3rem;'>💸 MyFinance</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#888;'>Your personal AI-powered finance tracker</p>", unsafe_allow_html=True)
    col = st.columns([1,2,1])[1]
    with col:
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Signup"])
        with tab1:
            u = st.text_input("Username", key="lu")
            p = st.text_input("Password", type="password", key="lp")
            if st.button("Login", use_container_width=True):
                users = load_users()
                if ((users["username"]==u) & (users["password"]==p)).any():
                    st.session_state.user = u
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        with tab2:
            u2 = st.text_input("New Username", key="su")
            p2 = st.text_input("New Password", type="password", key="sp")
            if st.button("Create Account", use_container_width=True):
                if not u2.strip() or not p2.strip():
                    st.error("Fields cannot be empty.")
                elif save_user(u2.strip(), p2):
                    st.success("Account created! Please log in.")
                else:
                    st.error("Username already exists.")
    st.stop()

# ===================== SIDEBAR =====================
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.user}")
    today = datetime.today()
    st.caption(f"📅 {today.strftime('%A, %d %B %Y')}")
    st.divider()

    df_sidebar = get_user_data(st.session_state.user)
    if not df_sidebar.empty:
        df_sidebar["Date"]   = pd.to_datetime(df_sidebar["Date"])
        df_sidebar["Amount"] = pd.to_numeric(df_sidebar["Amount"], errors="coerce").fillna(0)
        this_month_s = df_sidebar[
            (df_sidebar["Date"].dt.month == today.month) &
            (df_sidebar["Date"].dt.year  == today.year)
        ]
        inc_m = this_month_s[this_month_s["Type"]=="Income"]["Amount"].sum()
        exp_m = this_month_s[this_month_s["Type"]=="Expense"]["Amount"].sum()
        bal_m = inc_m - exp_m
        st.markdown("**This Month**")
        st.metric("💚 Income",  f"₹{inc_m:,.0f}")
        st.metric("🔴 Expense", f"₹{exp_m:,.0f}")
        st.metric("💰 Balance", f"₹{bal_m:,.0f}")
        st.divider()

        # Budget alerts
        budgets_s = load_budgets(st.session_state.user)
        if budgets_s and not this_month_s.empty:
            exp_by_cat_s = this_month_s[this_month_s["Type"]=="Expense"].groupby("Category")["Amount"].sum()
            for cat, limit in budgets_s.items():
                spent = exp_by_cat_s.get(cat, 0)
                if spent >= limit:
                    st.warning(f"🚨 {cat} over budget!\n₹{spent:,.0f} / ₹{limit:,.0f}")
                elif spent >= 0.8 * limit:
                    st.warning(f"⚠️ {cat} near limit\n₹{spent:,.0f} / ₹{limit:,.0f}")
            st.divider()

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.user = None
        st.rerun()

# ===================== NAV =====================
st.markdown("<h2 style='margin-bottom:0.3rem;'>💸 MyFinance</h2>", unsafe_allow_html=True)
menu = st.radio("", ["📊 Dashboard", "➕ Add Transaction", "🔍 Search & History",
                     "📈 Analysis", "🎯 Budget Tracker", "🤖 AI Insights"],
                horizontal=True, label_visibility="collapsed")

df_main = get_user_data(st.session_state.user)
if not df_main.empty:
    df_main["Date"]   = pd.to_datetime(df_main["Date"])
    df_main["Amount"] = pd.to_numeric(df_main["Amount"], errors="coerce").fillna(0)

# =========================================================
# 📊 DASHBOARD
# =========================================================
if menu == "📊 Dashboard":
    if df_main.empty:
        st.info("No transactions yet. Go to ➕ Add Transaction to get started.")
    else:
        df = df_main.copy()
        df["Month"] = df["Date"].dt.to_period("M")

        month_opts  = sorted(df["Month"].astype(str).unique(), reverse=True)
        month_names = [datetime.strptime(m, "%Y-%m").strftime("%B %Y") for m in month_opts]
        sel_idx = st.selectbox("📅 Select Month", range(len(month_opts)),
                               format_func=lambda i: month_names[i])
        sel_month = month_opts[sel_idx]
        df_m = df[df["Month"].astype(str) == sel_month]

        income  = df_m[df_m["Type"]=="Income"]["Amount"].sum()
        expense = df_m[df_m["Type"]=="Expense"]["Amount"].sum()
        balance = income - expense
        savings_rate = (balance / income * 100) if income > 0 else 0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("💚 Income",        f"₹{income:,.0f}")
        c2.metric("🔴 Expense",       f"₹{expense:,.0f}")
        c3.metric("💰 Balance",       f"₹{balance:,.0f}")
        c4.metric("📊 Savings Rate",  f"{savings_rate:.1f}%",
                  delta="Good ✓" if savings_rate >= 20 else "Low ⚠")

        st.markdown("<br>", unsafe_allow_html=True)

        budgets = load_budgets(st.session_state.user)
        exp_cat = df_m[df_m["Type"]=="Expense"].groupby("Category")["Amount"].sum().sort_values(ascending=False)

        if not exp_cat.empty:
            col1, col2 = st.columns([3, 2])
            with col1:
                st.markdown('<div class="section-title">💳 Spending by Category</div>', unsafe_allow_html=True)
                for cat, spent in exp_cat.items():
                    limit = budgets.get(cat, 0)
                    ratio = min(spent / limit, 1.0) if limit > 0 else None
                    label_right = f"₹{spent:,.0f}" + (f" / ₹{limit:,.0f}" if limit > 0 else "")
                    ca, cb = st.columns([1, 3])
                    ca.markdown(f"<small>{cat}</small>", unsafe_allow_html=True)
                    if ratio is not None:
                        color = RED if ratio >= 1.0 else (ACCENT if ratio < 0.8 else "#ffaa00")
                        cb.markdown(
                            f"""<div style='background:#333;border-radius:6px;height:16px;'>
                            <div style='background:{color};width:{ratio*100:.0f}%;height:16px;border-radius:6px;'></div>
                            </div><small style='color:#aaa'>{label_right}</small>""",
                            unsafe_allow_html=True)
                    else:
                        cb.markdown(f"<small style='color:#aaa'>₹{spent:,.0f} <span style='color:#555'>(no budget set)</span></small>",
                                    unsafe_allow_html=True)
                    st.markdown("")

            with col2:
                st.markdown('<div class="section-title">🗂️ Top 5 Expenses</div>', unsafe_allow_html=True)
                top5 = df_m[df_m["Type"]=="Expense"].nlargest(5, "Amount")[["Date","Category","Amount","Note"]].copy()
                top5["Date"]   = top5["Date"].dt.strftime("%d %b")
                top5["Amount"] = top5["Amount"].apply(lambda x: f"₹{x:,.0f}")
                st.dataframe(top5, hide_index=True, use_container_width=True)

        # Daily spending bar chart
        st.markdown('<div class="section-title">📆 Daily Spending This Month</div>', unsafe_allow_html=True)
        year_  = int(sel_month.split("-")[0])
        month_ = int(sel_month.split("-")[1])
        days_in_month = calendar.monthrange(year_, month_)[1]
        daily = df_m[df_m["Type"]=="Expense"].groupby(df_m["Date"].dt.day)["Amount"].sum()
        all_days = pd.Series(0.0, index=range(1, days_in_month+1))
        daily = all_days.add(daily, fill_value=0)

        mean_daily = daily[daily > 0].mean() if (daily > 0).any() else 0
        colors_ = [RED if v > mean_daily * 1.5 else ACCENT if v > 0 else "#2a2a2a" for v in daily]

        fig, ax = dark_fig(12, 2.5)
        ax.bar(daily.index, daily.values, color=colors_, width=0.8)
        ax.set_xlabel("Day of Month", color="#aaa", fontsize=9)
        ax.set_ylabel("₹", color="#aaa", fontsize=9)
        ax.set_xticks(range(1, days_in_month+1))
        ax.tick_params(labelsize=8)
        plt.tight_layout()
        st.pyplot(fig)

# =========================================================
# ➕ ADD TRANSACTION
# =========================================================
elif menu == "➕ Add Transaction":
    st.markdown('<div class="section-title">➕ Add New Transaction</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        t_type   = st.radio("Type", ["Expense", "Income"], horizontal=True)
        date_inp = st.date_input("Date", datetime.today())
        category = st.selectbox("Category", CATEGORIES)
    with col2:
        amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0)
        note   = st.text_input("Note / Description", placeholder="e.g. Lunch at Swiggy")

    if st.button("✅ Add Transaction", use_container_width=True):
        if amount <= 0:
            st.error("Amount must be greater than ₹0.")
        else:
            new = pd.DataFrame(
                [[str(date_inp), category, amount, t_type, note, st.session_state.user]],
                columns=["Date","Category","Amount","Type","Note","User"]
            )
            save_transaction(new)
            st.success(f"{'💸' if t_type=='Expense' else '💚'} ₹{amount:,.0f} added as {t_type}!")
            st.balloons()

    # Quick-add recurring bills
    st.divider()
    st.markdown('<div class="section-title">⏰ Quick-Add Common Bills</div>', unsafe_allow_html=True)
    st.caption("Tap to pre-fill category for common recurring expenses:")
    reminders = [("Rent", "Rent"), ("Electricity", "Bills & Utilities"),
                 ("Phone Recharge", "Bills & Utilities"), ("Internet", "Bills & Utilities"),
                 ("OTT / Subscriptions", "Entertainment"), ("EMI / Loan", "EMI / Loan"),
                 ("Groceries", "Groceries"), ("Petrol / Fuel", "Transport")]
    cols = st.columns(4)
    for i, (label, cat_val) in enumerate(reminders):
        if cols[i % 4].button(f"+ {label}", key=f"quick_{i}"):
            st.info(f"Select **{cat_val}** in the Category dropdown above, enter amount, and click Add.")

# =========================================================
# 🔍 SEARCH & HISTORY
# =========================================================
elif menu == "🔍 Search & History":
    st.markdown('<div class="section-title">🔍 Search & Transaction History</div>', unsafe_allow_html=True)

    if df_main.empty:
        st.info("No transactions yet.")
    else:
        df = df_main.copy()
        df["Month"] = df["Date"].dt.to_period("M")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            month_opts  = ["All Months"] + sorted(df["Month"].astype(str).unique(), reverse=True)
            month_names = ["All Months"] + [
                datetime.strptime(m, "%Y-%m").strftime("%B %Y") for m in month_opts[1:]
            ]
            sel_idx = st.selectbox("📅 Month", range(len(month_opts)),
                                   format_func=lambda i: month_names[i])
            sel_month = month_opts[sel_idx]
        with col2:
            type_filter = st.selectbox("💳 Type", ["All", "Expense", "Income"])
        with col3:
            cat_filter = st.selectbox("🗂️ Category", ["All"] + CATEGORIES)
        with col4:
            search_kw = st.text_input("🔎 Search Note / Category")

        # Apply filters
        filtered = df.copy()
        if sel_month != "All Months":
            filtered = filtered[filtered["Month"].astype(str) == sel_month]
        if type_filter != "All":
            filtered = filtered[filtered["Type"] == type_filter]
        if cat_filter != "All":
            filtered = filtered[filtered["Category"] == cat_filter]
        if search_kw:
            kw = search_kw.lower()
            filtered = filtered[
                filtered["Note"].str.lower().str.contains(kw, na=False) |
                filtered["Category"].str.lower().str.contains(kw, na=False)
            ]

        filtered = filtered.sort_values("Date", ascending=False).reset_index(drop=True)

        # Summary strip
        sc1, sc2, sc3 = st.columns(3)
        sc1.metric("Total Expense", f"₹{filtered[filtered['Type']=='Expense']['Amount'].sum():,.0f}")
        sc2.metric("Total Income",  f"₹{filtered[filtered['Type']=='Income']['Amount'].sum():,.0f}")
        sc3.metric("Transactions",  len(filtered))

        st.markdown("<br>", unsafe_allow_html=True)

        display_df = filtered[["Date","Type","Category","Amount","Note"]].copy()
        display_df["Date"]   = display_df["Date"].dt.strftime("%d %b %Y")
        display_df["Amount"] = display_df["Amount"].apply(lambda x: f"₹{x:,.0f}")
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # Delete
        st.divider()
        st.markdown("**🗑️ Delete a Transaction**")
        if len(filtered) > 0:
            del_idx = st.number_input("Row number to delete (starts at 0)", min_value=0,
                                      max_value=max(len(filtered)-1, 0), step=1)
            if st.button("Delete Selected Row"):
                row_to_del = filtered.iloc[del_idx]
                all_data = load_all_data()
                all_data["Date"]   = pd.to_datetime(all_data["Date"])
                all_data["Amount"] = pd.to_numeric(all_data["Amount"], errors="coerce")
                mask = (
                    (all_data["User"]     == st.session_state.user) &
                    (all_data["Date"]     == row_to_del["Date"]) &
                    (all_data["Amount"]   == row_to_del["Amount"]) &
                    (all_data["Category"] == row_to_del["Category"])
                )
                idx_drop = all_data[mask].index
                if len(idx_drop):
                    all_data = all_data.drop(index=idx_drop[0])
                    all_data.to_csv(DATA_FILE, index=False)
                    st.success("✅ Transaction deleted.")
                    st.rerun()
                else:
                    st.error("Could not find transaction to delete.")

# =========================================================
# 📈 ANALYSIS
# =========================================================
elif menu == "📈 Analysis":
    st.markdown('<div class="section-title">📈 Spending Analysis</div>', unsafe_allow_html=True)

    if df_main.empty:
        st.info("No transactions yet.")
    else:
        df = df_main.copy()
        df["Month"] = df["Date"].dt.to_period("M")

        month_opts  = sorted(df["Month"].astype(str).unique(), reverse=True)
        month_names = [datetime.strptime(m, "%Y-%m").strftime("%B %Y") for m in month_opts]
        sel_idx = st.selectbox("📅 Select Month for Analysis", range(len(month_opts)),
                               format_func=lambda i: month_names[i])
        sel_month = month_opts[sel_idx]
        df_m = df[df["Month"].astype(str) == sel_month]
        exp  = df_m[df_m["Type"]=="Expense"]

        if exp.empty:
            st.info("No expenses for this month.")
        else:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Category Breakdown**")
                cat_data = exp.groupby("Category")["Amount"].sum().sort_values(ascending=False)
                fig, ax = dark_fig(5, 4)
                wedges, texts, autotexts = ax.pie(
                    cat_data, labels=cat_data.index, autopct="%1.0f%%",
                    textprops={"color":"#ccc","fontsize":8},
                    colors=plt.cm.Set2.colors, startangle=140
                )
                for at in autotexts:
                    at.set_color("white")
                plt.tight_layout()
                st.pyplot(fig)

            with col2:
                st.markdown("**Daily Spending Trend**")
                trend = exp.groupby(exp["Date"].dt.day)["Amount"].sum()
                fig2, ax2 = dark_fig(5, 4)
                ax2.fill_between(trend.index, trend.values, alpha=0.25, color=ACCENT)
                ax2.plot(trend.index, trend.values, color=ACCENT, linewidth=2, marker="o", markersize=4)
                ax2.set_xlabel("Day of Month", color="#aaa")
                ax2.set_ylabel("₹", color="#aaa")
                plt.tight_layout()
                st.pyplot(fig2)

            # Month-over-month comparison
            st.markdown("**📊 Month-over-Month Comparison**")
            monthly_exp = df[df["Type"]=="Expense"].groupby("Month")["Amount"].sum()
            monthly_inc = df[df["Type"]=="Income"].groupby("Month")["Amount"].sum()
            months_str  = [str(m) for m in monthly_exp.index]

            fig3, ax3 = dark_fig(10, 3.5)
            x = np.arange(len(months_str))
            w = 0.35
            ax3.bar(x - w/2, monthly_exp.values, w, label="Expense", color=RED,   alpha=0.85)
            ax3.bar(x + w/2,
                    monthly_inc.reindex(monthly_exp.index, fill_value=0).values,
                    w, label="Income", color=ACCENT, alpha=0.85)
            ax3.set_xticks(x)
            ax3.set_xticklabels(
                [datetime.strptime(m,"%Y-%m").strftime("%b %y") for m in months_str],
                color="#aaa", fontsize=8
            )
            ax3.legend(facecolor=CARD, labelcolor="white")
            ax3.set_ylabel("₹", color="#aaa")
            plt.tight_layout()
            st.pyplot(fig3)

            # Category summary table
            st.markdown("**Category Totals**")
            cat_table = exp.groupby("Category")["Amount"].agg(["sum","count","mean"]).reset_index()
            cat_table.columns = ["Category","Total Spent","# Transactions","Avg per Txn"]
            cat_table["Total Spent"]    = cat_table["Total Spent"].apply(lambda x: f"₹{x:,.0f}")
            cat_table["Avg per Txn"]    = cat_table["Avg per Txn"].apply(lambda x: f"₹{x:,.0f}")
            cat_table = cat_table.sort_values("# Transactions", ascending=False)
            st.dataframe(cat_table, hide_index=True, use_container_width=True)

# =========================================================
# 🎯 BUDGET TRACKER
# =========================================================
elif menu == "🎯 Budget Tracker":
    st.markdown('<div class="section-title">🎯 Monthly Budget Tracker</div>', unsafe_allow_html=True)
    st.caption("Set how much you want to spend per category each month.")

    budgets = load_budgets(st.session_state.user)

    with st.form("budget_form"):
        st.markdown("**Set Monthly Budgets (₹)**")
        new_budgets = {}
        cols = st.columns(3)
        for i, cat in enumerate(CATEGORIES):
            with cols[i % 3]:
                new_budgets[cat] = st.number_input(
                    cat, min_value=0.0, step=100.0,
                    value=float(budgets.get(cat, 0)),
                    key=f"bgt_{cat}"
                )
        if st.form_submit_button("💾 Save Budgets", use_container_width=True):
            save_budgets(st.session_state.user, new_budgets)
            st.success("Budgets saved!")
            st.rerun()

    # Budget vs actual
    if not df_main.empty:
        st.divider()
        today_ = datetime.today()
        df_m   = df_main[
            (df_main["Date"].dt.month == today_.month) &
            (df_main["Date"].dt.year  == today_.year)
        ]
        exp_by_cat = df_m[df_m["Type"]=="Expense"].groupby("Category")["Amount"].sum()
        budgets    = load_budgets(st.session_state.user)

        if budgets:
            st.markdown(f'<div class="section-title">📊 Budget vs Actual — {today_.strftime("%B %Y")}</div>',
                        unsafe_allow_html=True)
            days_in_month  = calendar.monthrange(today_.year, today_.month)[1]
            day_of_month   = today_.day
            month_progress = day_of_month / days_in_month

            total_budget = sum(budgets.values())
            total_spent  = float(exp_by_cat.sum())
            remaining    = total_budget - total_spent
            st.metric("Total Budget", f"₹{total_budget:,.0f}", delta=f"₹{remaining:,.0f} remaining")

            for cat, limit in sorted(budgets.items()):
                if limit <= 0:
                    continue
                spent = float(exp_by_cat.get(cat, 0))
                pct   = spent / limit
                bar_color = ACCENT if pct < 0.8 else (RED if pct >= 1.0 else "#ffaa00")
                status = "🟢" if pct <= month_progress else ("🔴" if pct >= 1.0 else "🟡")

                st.markdown(
                    f"""<div style='margin-bottom:14px;'>
                    <div style='display:flex;justify-content:space-between;margin-bottom:3px;'>
                        <span>{status} <b>{cat}</b></span>
                        <span style='color:#aaa;font-size:0.85rem;'>₹{spent:,.0f} / ₹{limit:,.0f} ({pct*100:.0f}%)</span>
                    </div>
                    <div style='background:#333;border-radius:8px;height:14px;position:relative;'>
                        <div style='background:{bar_color};width:{min(pct,1)*100:.1f}%;height:14px;border-radius:8px;'></div>
                        <div style='position:absolute;top:0;left:{month_progress*100:.1f}%;
                                    width:2px;height:14px;background:white;opacity:0.5;'></div>
                    </div>
                    <small style='color:#555;'>│ = expected spend on day {day_of_month}/{days_in_month}</small>
                    </div>""",
                    unsafe_allow_html=True
                )
        else:
            st.info("Set budgets using the form above to see tracking here.")

# =========================================================
# 🤖 AI INSIGHTS
# =========================================================
elif menu == "🤖 AI Insights":
    st.markdown('<div class="section-title">🤖 AI-Powered Insights</div>', unsafe_allow_html=True)

    if df_main.empty:
        st.info("No transactions yet.")
    else:
        df  = df_main.copy()
        exp = df[df["Type"]=="Expense"].copy()

        # ---- Personalised Tips ----
        st.markdown("**💡 Personalised Money Tips**")
        today_  = datetime.today()
        budgets = load_budgets(st.session_state.user)
        df_m    = df[(df["Date"].dt.month==today_.month)&(df["Date"].dt.year==today_.year)]
        exp_m   = df_m[df_m["Type"]=="Expense"]
        inc_m   = df_m[df_m["Type"]=="Income"]["Amount"].sum()
        exp_sum = exp_m["Amount"].sum()
        tips    = []

        if inc_m > 0:
            sr = (inc_m - exp_sum) / inc_m * 100
            if sr < 10:
                tips.append(f"🔴 Your savings rate is only **{sr:.1f}%** this month. Aim for at least 20%.")
            elif sr >= 30:
                tips.append(f"🟢 Great! You're saving **{sr:.1f}%** of income this month.")
            else:
                tips.append(f"🟡 Savings rate: **{sr:.1f}%**. Try to push towards 20-30%.")

        if not exp_m.empty:
            top_cat = exp_m.groupby("Category")["Amount"].sum().idxmax()
            top_amt = exp_m.groupby("Category")["Amount"].sum().max()
            tips.append(f"📌 Highest spending category: **{top_cat}** at ₹{top_amt:,.0f} this month.")

            weekend_exp = exp[exp["Date"].dt.dayofweek >= 5]["Amount"].sum()
            weekday_exp = exp[exp["Date"].dt.dayofweek < 5]["Amount"].sum()
            if weekday_exp > 0 and weekend_exp / (weekday_exp + 1) > 0.4:
                tips.append("🎉 You spend a lot on weekends. Consider setting a weekend budget.")

        if len(exp) >= 3:
            avg_txn = exp["Amount"].mean()
            tips.append(f"💳 Your average transaction size is **₹{avg_txn:,.0f}**.")

        if not tips:
            tips.append("Keep adding transactions for personalised tips!")

        for tip in tips:
            st.markdown(f"> {tip}")

        st.divider()

        # ---- Spending Clusters ----
        st.markdown("**🔍 Transaction Clusters (Smart Grouping)**")
        if len(exp) >= 3:
            k  = min(3, len(exp))
            km = KMeans(n_clusters=k, n_init=10, random_state=42)
            exp = exp.copy()
            exp["Cluster"] = km.fit_predict(exp[["Amount"]])
            centers = km.cluster_centers_.flatten()
            sorted_clusters = sorted(range(k), key=lambda c: centers[c])
            level_names = ["Low Spend", "Mid Spend", "High Spend"][:k]
            label_map = {cid: level_names[rank] for rank, cid in enumerate(sorted_clusters)}
            exp["Spending Level"] = exp["Cluster"].map(label_map)

            col1, col2 = st.columns([2, 1])
            with col1:
                show = exp[["Date","Category","Amount","Spending Level","Note"]].copy()
                show["Date"]   = show["Date"].dt.strftime("%d %b %Y")
                show["Amount"] = show["Amount"].apply(lambda x: f"₹{x:,.0f}")
                st.dataframe(show.sort_values("Date", ascending=False), hide_index=True, use_container_width=True)
            with col2:
                for lvl in level_names:
                    cnt = (exp["Spending Level"]==lvl).sum()
                    avg = exp[exp["Spending Level"]==lvl]["Amount"].mean()
                    st.metric(lvl, f"{cnt} txns", delta=f"avg ₹{avg:,.0f}")
        else:
            st.info("Add at least 3 expense transactions for clustering.")

        st.divider()

        # ---- Next Month Prediction ----
        st.markdown("**📅 Next Month Spending Forecast**")
        if len(exp) >= 5:
            exp_s = exp.sort_values("Date").copy()
            min_d = exp_s["Date"].min()
            exp_s["Days"] = (exp_s["Date"] - min_d).dt.days
            model = LinearRegression()
            model.fit(exp_s[["Days"]], exp_s["Amount"])

            future_days   = [exp_s["Days"].max() + i for i in range(1, 31)]
            preds         = model.predict([[d] for d in future_days])
            monthly_pred  = max(sum(preds), 0)
            avg_monthly   = exp_s.groupby(exp_s["Date"].dt.to_period("M"))["Amount"].sum().mean()

            col1, col2 = st.columns(2)
            col1.metric("Predicted Next Month Spend", f"₹{monthly_pred:,.0f}")
            col2.metric("Avg Monthly Spend (history)", f"₹{avg_monthly:,.0f}")

            fig, ax = dark_fig(10, 3)
            actual_daily = exp_s.groupby("Days")["Amount"].sum()
            ax.plot(actual_daily.index, actual_daily.values, color=ACCENT, label="Actual", linewidth=2)
            ax.plot(future_days, preds, color=RED, linestyle="--", label="Forecast", linewidth=1.5)
            ax.axvline(exp_s["Days"].max(), color="#555", linestyle=":", linewidth=1)
            ax.legend(facecolor=CARD, labelcolor="white")
            ax.set_xlabel("Days since first transaction", color="#aaa")
            ax.set_ylabel("₹", color="#aaa")
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.info("Add at least 5 expense transactions for forecasting.")

        st.divider()

        # ---- Spike Detection ----
        st.markdown("**⚠️ Unusual Spending Detection**")
        if len(exp) >= 5:
            mean_, std_ = exp["Amount"].mean(), exp["Amount"].std()
            spikes = exp[exp["Amount"] > mean_ + 2 * std_].copy()
            if not spikes.empty:
                st.warning(f"🚨 {len(spikes)} unusually large transaction(s) detected!")
                spikes["Date"]   = spikes["Date"].dt.strftime("%d %b %Y")
                spikes["Amount"] = spikes["Amount"].apply(lambda x: f"₹{x:,.0f}")
                st.dataframe(spikes[["Date","Category","Amount","Note"]], hide_index=True, use_container_width=True)
            else:
                st.success("✅ No spending spikes detected. Your expenses look consistent.")
        else:
            st.info("Add at least 5 expense transactions for spike detection.")

# ===================== FOOTER =====================
st.markdown("---")
st.markdown("<center><small style='color:#444;'>💸 MyFinance — Personal AI Finance Tracker</small></center>",
            unsafe_allow_html=True)
