import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Currency conversion rates (as of August 2024, for illustration purposes)
USD_TO_INR = 75
JPY_TO_INR = 0.68

def inject_css():
    st.markdown("""
    <style>
    /* CSS styles remain the same as in the original code */
    </style>
    """, unsafe_allow_html=True)

def format_currency(value, country):
    if country == 'India':
        if value >= 10000000:  # 1 Crore
            return f"₹{value/10000000:.2f} Cr"
        else:
            return f"₹{value/100000:.2f} Lakh"
    elif country == 'US':
        if value >= 1000000:
            return f"${value/1000000:.2f}M"
        elif value >= 1000:
            return f"${value/1000:.2f}K"
        else:
            return f"${value:.2f}"
    else:  # Japan
        if value >= 100000000:  # 1億
            return f"¥{value/100000000:.2f}億"
        elif value >= 10000:  # 1万
            return f"¥{value/10000:.2f}万"
        else:
            return f"¥{value:.0f}"

def convert_to_selected_currency(value, from_country, to_country):
    if from_country == to_country:
        return value
    if from_country == 'India':
        if to_country == 'US':
            return value / USD_TO_INR
        else:  # Japan
            return value / JPY_TO_INR
    elif from_country == 'US':
        if to_country == 'India':
            return value * USD_TO_INR
        else:  # Japan
            return value * USD_TO_INR / JPY_TO_INR
    else:  # from_country is Japan
        if to_country == 'India':
            return value * JPY_TO_INR
        else:  # US
            return value * JPY_TO_INR / USD_TO_INR

def simulate_retirement_savings(
    initial_investment,
    initial_monthly_contribution,
    annual_return_rate,
    inflation_rate,
    years_to_retirement,
    annual_income_growth_rate=0.03,
    plan_for_family=False,
    family_growth_year=5,
    family_growth_expense=0,
    country='India'
):
    monthly_return_rate = (1 + annual_return_rate) ** (1/12) - 1
    monthly_inflation_rate = (1 + inflation_rate) ** (1/12) - 1
    monthly_income_growth_rate = (1 + annual_income_growth_rate) ** (1/12) - 1
    
    months = np.arange(years_to_retirement * 12 + 1)
    portfolio_value = np.zeros(len(months))
    portfolio_value[0] = initial_investment
    monthly_contribution = np.zeros(len(months))
    monthly_contribution[0] = initial_monthly_contribution
    
    for i in range(1, len(months)):
        monthly_contribution[i] = monthly_contribution[i-1] * (1 + monthly_income_growth_rate)
        
        if plan_for_family and i >= family_growth_year * 12:
            adjusted_contribution = max(0, monthly_contribution[i] - family_growth_expense)
        else:
            adjusted_contribution = monthly_contribution[i]
        
        portfolio_value[i] = (
            portfolio_value[i-1] * (1 + monthly_return_rate) +
            adjusted_contribution
        )
    
    real_value = portfolio_value / (1 + monthly_inflation_rate) ** months
    
    if country == 'India':
        divisor = 10000000  # 1 Crore
        value_label = 'Value (Cr)'
        contribution_divisor = 100000  # 1 Lakh
        contribution_label = 'Monthly Contribution (Lakhs)'
    elif country == 'US':
        divisor = 1000000  # 1 Million
        value_label = 'Value (Millions)'
        contribution_divisor = 1000  # 1 Thousand
        contribution_label = 'Monthly Contribution (Thousands)'
    else:  # Japan
        divisor = 1000000  # 1 Million
        value_label = '価値 (百万)'
        contribution_divisor = 1000  # 1 Thousand
        contribution_label = '月々の積立 (千)'
    
    df = pd.DataFrame({
        'Month': months,
        f'Nominal {value_label}': portfolio_value / divisor,
        f'Real {value_label}': real_value / divisor,
        contribution_label: monthly_contribution / contribution_divisor
    })
    df['Year'] = df['Month'] // 12 + 2024
    
    return df

def create_portfolio_value_plot(results, country):
    fig = go.Figure()

    nominal_col = f"Nominal {'Value (Cr)' if country == 'India' else 'Value (Millions)' if country == 'US' else '価値 (百万)'}"
    real_col = f"Real {'Value (Cr)' if country == 'India' else 'Value (Millions)' if country == 'US' else '価値 (百万)'}"

    # Convert values to the appropriate scale
    scale_factor = 10000000 if country == 'India' else 1000000  # For US and Japan
    nominal_values = results[nominal_col] * scale_factor
    real_values = results[real_col] * scale_factor

    fig.add_trace(go.Scatter(
        x=results['Year'],
        y=nominal_values,
        mode='lines',
        name='Nominal Value' if country != 'Japan' else '名目価値',
        line=dict(color='#1f77b4', width=2)
    ))

    fig.add_trace(go.Scatter(
        x=results['Year'],
        y=real_values,
        mode='lines',
        name='Real Value' if country != 'Japan' else '実質価値',
        line=dict(color='#ff7f0e', width=2)
    ))

    # Update y-axis to use appropriate formatting
    fig.update_layout(
        autosize=True,
        height=400,
        xaxis_title="Years" if country != 'Japan' else '年',
        yaxis_title="Value" if country != 'Japan' else '価値',
        yaxis=dict(
            tickformat=".2s" if country == "US" else "",
            tickprefix="₹" if country == "India" else "$" if country == "US" else "¥",
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=20, b=20)
    )

    return fig

def create_contribution_plot(results, country):
    fig = go.Figure()

    contribution_col = f"{'Monthly Contribution (Lakhs)' if country == 'India' else 'Monthly Contribution (Thousands)' if country == 'US' else '月々の積立 (千)'}"

    # Convert values to the appropriate scale
    scale_factor = 100000 if country == 'India' else 1000  # For US and Japan
    contribution_values = results[contribution_col] * scale_factor

    fig.add_trace(go.Scatter(
        x=results['Year'],
        y=contribution_values,
        mode='lines',
        name='Monthly Contribution' if country != 'Japan' else '月々の積立',
        line=dict(color='#2ca02c', width=2)
    ))

    # Update y-axis to use appropriate formatting
    fig.update_layout(
        height=400,
        xaxis_title="Years" if country != 'Japan' else '年',
        yaxis_title="Monthly Contribution" if country != 'Japan' else '月々の積立',
        yaxis=dict(
            tickformat=".2s" if country == "US" else "",
            tickprefix="₹" if country == "India" else "$" if country == "US" else "¥",
        ),
        margin=dict(l=20, r=20, t=20, b=20)
    )

    return fig

def main():
    inject_css()
    
    country = st.sidebar.selectbox(
        "Select Country",
        ["India", "US", "Japan"],
        format_func=lambda x: {"India": "India (₹)", "US": "US ($)", "Japan": "日本 (¥)"}[x]
    )

    st.session_state['country'] = country

    # Update the title based on the selected country
    if country == "India":
        st.title("Retirement Savings Simulation")
    elif country == "US":
        st.title("Retirement Savings Simulation")
    else:  # Japan
        st.title("退職貯蓄シミュレーション")

    labels = {
        "Initial Investment": "Initial Investment (₹)" if country == "India" else "Initial Investment ($)" if country == "US" else "初期投資 (¥)",
        "Initial Monthly Contribution": "Initial Monthly Contribution (₹)" if country == "India" else "Initial Monthly Contribution ($)" if country == "US" else "初期月額積立 (¥)",
        "Annual Return Rate": "Annual Return Rate" if country != "Japan" else "年間リターン率",
        "Inflation Rate": "Inflation Rate" if country != "Japan" else "インフレ率",
        "Years to Retirement": "Years to Retirement" if country != "Japan" else "退職までの年数",
        "Annual Income Growth Rate": "Annual Income Growth Rate" if country != "Japan" else "年間収入成長率",
        "Plan for Family Growth": "Plan for Family Growth" if country != "Japan" else "家族成長の計画",
        "Family Growth Year": "Family Growth Year" if country != "Japan" else "家族成長の年",
        "Family Growth Expense": "Family Growth Expense (₹/month)" if country == "India" else "Family Growth Expense ($/month)" if country == "US" else "家族成長の費用 (¥/月)"
    }

    st.sidebar.header("Input Parameters" if country != "Japan" else "入力パラメータ")
    initial_investment = st.sidebar.number_input(labels["Initial Investment"], value=1000000 if country == "India" else 13000 if country == "US" else 1500000, step=10000 if country == "India" else 100 if country == "US" else 10000, format="%d")
    initial_monthly_contribution = st.sidebar.number_input(labels["Initial Monthly Contribution"], value=100000 if country == "India" else 1300 if country == "US" else 150000, step=1000 if country == "India" else 10 if country == "US" else 1000, format="%d")
    annual_return_rate = st.sidebar.slider(labels["Annual Return Rate"], 0.01, 0.15, 0.08, 0.01, format="%.2f")
    inflation_rate = st.sidebar.slider(labels["Inflation Rate"], 0.01, 0.10, 0.04, 0.01, format="%.2f")
    years_to_retirement = st.sidebar.slider(labels["Years to Retirement"], 5, 40, 30, 1)
    annual_income_growth_rate = st.sidebar.slider(labels["Annual Income Growth Rate"], 0.01, 0.10, 0.05, 0.01, format="%.2f")
    
    plan_for_family = st.sidebar.checkbox(labels["Plan for Family Growth"], value=False)
    family_growth_year = None
    family_growth_expense = 0
    if plan_for_family:
        family_growth_year = st.sidebar.slider(labels["Family Growth Year"], 1, 20, 5, 1)
        family_growth_expense = st.sidebar.number_input(labels["Family Growth Expense"], value=50000 if country == "India" else 650 if country == "US" else 75000, step=1000 if country == "India" else 10 if country == "US" else 1000, format="%d")

    results = simulate_retirement_savings(
        initial_investment,
        initial_monthly_contribution,
        annual_return_rate,
        inflation_rate,
        years_to_retirement,
        annual_income_growth_rate,
        plan_for_family,
        family_growth_year,
        family_growth_expense,
        country
    )

    params = {
        labels["Initial Investment"]: format_currency(initial_investment, country),
        labels["Initial Monthly Contribution"]: format_currency(initial_monthly_contribution, country),
        labels["Annual Return Rate"]: f"{annual_return_rate:.1%}",
        labels["Inflation Rate"]: f"{inflation_rate:.1%}",
        labels["Years to Retirement"]: years_to_retirement,
        labels["Annual Income Growth Rate"]: f"{annual_income_growth_rate:.1%}",
    }
    if plan_for_family:
        params[labels["Family Growth Year"]] = family_growth_year
        params[labels["Family Growth Expense"]] = format_currency(family_growth_expense, country) + ("/month" if country != "Japan" else "/月")

    # Generate and display the plots
    st.header("Portfolio Value Over Time" if country != "Japan" else "ポートフォリオ価値の推移")
    portfolio_value_fig = create_portfolio_value_plot(results, country)
    st.plotly_chart(portfolio_value_fig, use_container_width=True)

    st.header("Monthly Contribution Over Time" if country != "Japan" else "月々の積立の推移")
    contribution_fig = create_contribution_plot(results, country)
    st.plotly_chart(contribution_fig, use_container_width=True)

    st.header("Simulation Parameters" if country != "Japan" else "シミュレーションパラメータ")
    for key, value in params.items():
        st.text(f"{key}: {value}")

    st.header("Final Values" if country != "Japan" else "最終的な価値")
    value_col = 'Value (Cr)' if country == 'India' else 'Value (Millions)' if country == 'US' else '価値 (百万)'
    contribution_col = 'Monthly Contribution (Lakhs)' if country == 'India' else 'Monthly Contribution (Thousands)' if country == 'US' else '月々の積立 (千)'
    
    final_nominal = results[f'Nominal {value_col}'].iloc[-1]
    final_real = results[f'Real {value_col}'].iloc[-1]
    final_contribution = results[contribution_col].iloc[-1]
    
    st.text(f"{'Nominal Value' if country != 'Japan' else '名目価値'}: {format_currency(final_nominal * (10000000 if country == 'India' else 1000000), country)}")
    st.text(f"{'Real Value (adjusted for inflation)' if country != 'Japan' else '実質価値 (インフレ調整後)'}: {format_currency(final_real * (10000000 if country == 'India' else 1000000), country)}")
    st.text(f"{'Final Monthly Contribution' if country != 'Japan' else '最終月額積立'}: {format_currency(final_contribution * (100000 if country == 'India' else 1000), country)}")

if __name__ == "__main__":
    main()