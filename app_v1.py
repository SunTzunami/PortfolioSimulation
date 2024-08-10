import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def inject_css():
    st.markdown("""
    <style>
    /* Override specific elements while preserving Streamlit's dark background */
    .css-1v3fvcr {  /* Sidebar container */
        background-color: #2e2e2e !important;  /* Ensure sidebar remains dark */
    }
    .css-1lcbmhc {  /* Main container */
        background-color: #1e1e1e !important;  /* Ensure main content area remains dark */
    }
    .css-1aumxhk {  /* Main content area */
        color: #e0e0e0 !important;  /* Light text color for readability */
    }
    body, div, p, h1, h2, h3, h4, h5, h6, input, label {
        font-family: 'Arial', sans-serif !important;
        color: #e0e0e0 !important;  /* Light text color for readability */
    }
    
    @media (max-width: 768px) {
        .css-1v3fvcr {  /* Sidebar container */
            width: 100% !important;
        }
        .css-1lcbmhc {  /* Main container */
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        .css-1aumxhk p, .css-1aumxhk h1, .css-1aumxhk h2, .css-1aumxhk h3, .css-1aumxhk h4, .css-1aumxhk h5, .css-1aumxhk h6 {
            font-size: 1.5rem !important;  /* Adjust font size for smaller screens */
        }
    }
    </style>
    """, unsafe_allow_html=True)


def simulate_retirement_savings(
    initial_investment,
    initial_monthly_contribution,
    annual_return_rate,
    inflation_rate,
    years_to_retirement,
    annual_income_growth_rate=0.03,
    plan_for_family=False,
    family_growth_year=5,
    family_growth_expense=0
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
    
    df = pd.DataFrame({
        'Month': months,
        'Nominal Value (Cr)': portfolio_value / 10000000,
        'Real Value (Cr)': real_value / 10000000,
        'Monthly Contribution (Lakhs)': monthly_contribution / 100000
    })
    df['Year'] = df['Month'] // 12 + 2024
    
    return df

def create_portfolio_value_plot(results):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=results['Year'],
        y=results['Nominal Value (Cr)'],
        mode='lines',
        name='Nominal Value',
        line=dict(color='#1f77b4', width=2)
    ))

    fig.add_trace(go.Scatter(
        x=results['Year'],
        y=results['Real Value (Cr)'],
        mode='lines',
        name='Real Value',
        line=dict(color='#ff7f0e', width=2)
    ))

    fig.update_layout(
        height=400,
        title=dict(text="Portfolio Value Over Time", y=0.98, x=0.5, xanchor='center', yanchor='top'),
        xaxis_title="Years",
        yaxis_title="Value (Crores ₹)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return fig

def create_contribution_plot(results):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=results['Year'],
        y=results['Monthly Contribution (Lakhs)'],
        mode='lines',
        name='Monthly Contribution',
        line=dict(color='#2ca02c', width=2)
    ))

    fig.update_layout(
        height=400,
        title=dict(text="Monthly Contribution Over Time", y=0.98, x=0.5, xanchor='center', yanchor='top'),
        xaxis_title="Years",
        yaxis_title="Contribution (Lakhs ₹)",
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return fig

def main():
    inject_css()
    st.title("Retirement Savings Simulation")

    st.sidebar.header("Input Parameters")
    initial_investment = st.sidebar.number_input("Initial Investment (₹)", value=0, step=100000, format="%d")
    initial_monthly_contribution = st.sidebar.number_input("Initial Monthly Contribution (₹)", value=100000, step=1000, format="%d")
    annual_return_rate = st.sidebar.slider("Annual Return Rate", 0.01, 0.15, 0.08, 0.01, format="%.2f")
    inflation_rate = st.sidebar.slider("Inflation Rate", 0.01, 0.10, 0.04, 0.01, format="%.2f")
    years_to_retirement = st.sidebar.slider("Years to Retirement", 5, 40, 30, 1)
    annual_income_growth_rate = st.sidebar.slider("Annual Income Growth Rate", 0.01, 0.10, 0.05, 0.01, format="%.2f")
    
    plan_for_family = st.sidebar.checkbox("Plan for Family Growth", value=False)
    family_growth_year = None
    family_growth_expense = 0
    if plan_for_family:
        family_growth_year = st.sidebar.slider("Family Growth Year", 1, 20, 5, 1)
        family_growth_expense = st.sidebar.number_input("Family Growth Expense (₹/month)", value=50000, step=1000, format="%d")

    results = simulate_retirement_savings(
        initial_investment,
        initial_monthly_contribution,
        annual_return_rate,
        inflation_rate,
        years_to_retirement,
        annual_income_growth_rate,
        plan_for_family,
        family_growth_year,
        family_growth_expense
    )

    params = {
        "Initial Investment": f"₹{initial_investment/10000000:.2f} Cr",
        "Initial Monthly Contribution": f"₹{initial_monthly_contribution/100000:.2f} Lakhs",
        "Annual Return Rate": f"{annual_return_rate:.1%}",
        "Inflation Rate": f"{inflation_rate:.1%}",
        "Years to Retirement": years_to_retirement,
        "Annual Income Growth": f"{annual_income_growth_rate:.1%}",
    }
    if plan_for_family:
        params["Family Growth Year"] = family_growth_year
        params["Family Expense"] = f"₹{family_growth_expense/100000:.2f} Lakhs/month"

    # Generate and display the plots
    portfolio_value_fig = create_portfolio_value_plot(results)
    contribution_fig = create_contribution_plot(results)

    st.plotly_chart(portfolio_value_fig, use_container_width=True)
    st.plotly_chart(contribution_fig, use_container_width=True)

    st.header("Simulation Parameters")
    for key, value in params.items():
        st.text(f"{key}: {value}")

    st.header("Final Values")
    final_nominal = results['Nominal Value (Cr)'].iloc[-1]
    final_real = results['Real Value (Cr)'].iloc[-1]
    final_contribution = results['Monthly Contribution (Lakhs)'].iloc[-1]
    st.text(f"Nominal Value: ₹{final_nominal:.2f} Cr")
    st.text(f"Real Value (adjusted for inflation): ₹{final_real:.2f} Cr")
    st.text(f"Final Monthly Contribution: ₹{final_contribution:.2f} Lakhs")

if __name__ == "__main__":
    main()

