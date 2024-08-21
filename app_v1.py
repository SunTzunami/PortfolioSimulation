import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def simulate_retirement_savings(
    initial_investment,
    initial_monthly_contribution,
    annual_return_rate,
    inflation_rate,
    years_to_retirement,
    career_progression_rate=3,  # Number of years after which a pay raise happens
    pay_raise_percentage=0.05,
    plan_for_family=False,
    family_growth_year=5,
    family_growth_expense=0,
    country='India'
):
    monthly_return_rate = (1 + annual_return_rate) ** (1/12) - 1
    monthly_inflation_rate = (1 + inflation_rate) ** (1/12) - 1
    months = np.arange(years_to_retirement * 12 + 1)
    portfolio_value = np.zeros(len(months))
    portfolio_value[0] = initial_investment
    
    # Calculate the number of months per pay raise interval
    raise_interval_months = career_progression_rate * 12
    monthly_contribution = np.zeros(len(months))
    monthly_contribution[0] = initial_monthly_contribution
    
    # Initialize the contribution increment
    current_contribution = initial_monthly_contribution
    next_raise_month = raise_interval_months

    for i in range(1, len(months)):
        if i >= next_raise_month:
            # Apply pay raise
            current_contribution *= (1 + pay_raise_percentage)
            next_raise_month += raise_interval_months
        
        monthly_contribution[i] = current_contribution
        
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
        value_divisor = 10000000  # 1 Crore
        value_label = 'Value (Cr)'
        contribution_value_divisor = 100000  # 1 Lakh
        contribution_label = 'Monthly Contribution (Lakhs)'
    elif country == 'US':
        value_divisor = 1000000  # 1 Million
        value_label = 'Value (Millions)'
        contribution_value_divisor = 1000  # 1 Thousand
        contribution_label = 'Monthly Contribution (Thousands)'
    else:  # Japan
        value_divisor = 1000000  # 1 Million
        value_label = '価値 (百万)'
        contribution_value_divisor = 1000  # 1 Thousand
        contribution_label = '月々の積立 (千)'
    
    df = pd.DataFrame({
        'Month': months,
        f'Nominal {value_label}': portfolio_value / value_divisor,
        f'Real {value_label}': real_value / value_divisor,
        contribution_label: monthly_contribution / contribution_value_divisor
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

    country_options = {
        "India": "India ₹",
        "US": "US $",
        "Japan": "Japan ¥"
    }
    
    # Select country with flags
    country = st.sidebar.selectbox(
        "Select Country / 国を選択してください",
        list(country_options.keys()),
        format_func=lambda x: country_options[x]
    )
    
    st.session_state['country'] = country

    # Update the title based on the selected country
    if country == "India":
        st.title("Retirement Savings Simulation")
    elif country == "US":
        st.title("Retirement Savings Simulation")
    else:
        st.title("退職後の貯蓄シミュレーション")

    initial_investment = st.sidebar.number_input(
        "Initial Investment" if country != "Japan" else "初期投資",
        min_value=0.0,
        value=0.0,
        step=100000.0,
        format="%.2f"
    )

    initial_monthly_contribution = st.sidebar.number_input(
        "Initial Monthly Contribution" if country != "Japan" else "初回月額拠出金",
        min_value=0.0,
        value=50000.0,
        step=1000.0,
        format="%.2f"
    )

    annual_return_rate = st.sidebar.slider(
        "Expected Annual Return Rate (%)" if country != "Japan" else "予想年間リターン率 (%)",
        min_value=0.0,
        max_value=20.0,
        value=8.0,
        step=0.1,
        format="%.2f"
    ) / 100

    inflation_rate = st.sidebar.slider(
        "Expected Annual Inflation Rate (%)" if country != "Japan" else "予想年間インフレ率 (%)",
        min_value=0.0,
        max_value=10.0,
        value=3.0,
        step=0.1,
        format="%.2f"
    ) / 100

    years_to_retirement = st.sidebar.slider(
        "Years to Retirement" if country != "Japan" else "退職までの年数",
        min_value=1,
        max_value=50,
        value=30
    )

    career_progression_rate = st.sidebar.slider(
        "Years After Which Pay Raise Happens" if country != "Japan" else "昇給が発生する年数",
        min_value=1,
        max_value=10,
        value=3
    )

    pay_raise_percentage = st.sidebar.slider(
        "Expected Pay Raise Percentage (%)" if country != "Japan" else "予想昇給率 (%)",
        min_value=0.0,
        max_value=60.0,
        value=5.0,
        step=0.5,
        format="%.2f"
    ) / 100

    plan_for_family = st.sidebar.checkbox(
        "Plan for Family Expenses (*TODO)" if country != "Japan" else "家族費用の計画 (*TODO)",
        value=False
    )

    if plan_for_family:
        family_growth_year = st.sidebar.slider(
            "Years After Which Family Growth Starts" if country != "Japan" else "家族の増加が始まる年数",
            min_value=1,
            max_value=years_to_retirement,
            value=5
        )

        family_growth_expense = st.sidebar.number_input(
            "Monthly Expense After Family Growth" if country != "Japan" else "家族の増加後の月額費用",
            min_value=0.0,
            value=20000.0,
            step=1000.0,
            format="%.2f"
        )
    else:
        family_growth_year = None
        family_growth_expense = None

    results = simulate_retirement_savings(
        initial_investment,
        initial_monthly_contribution,
        annual_return_rate,
        inflation_rate,
        years_to_retirement,
        career_progression_rate,
        pay_raise_percentage,
        plan_for_family,
        family_growth_year,
        family_growth_expense,
        country
    )

    portfolio_value_plot = create_portfolio_value_plot(results, country)
    contribution_plot = create_contribution_plot(results, country)

    st.plotly_chart(portfolio_value_plot)
    st.plotly_chart(contribution_plot)

if __name__ == "__main__":
    main()
