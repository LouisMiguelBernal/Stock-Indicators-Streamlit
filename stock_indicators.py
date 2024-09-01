import streamlit as st
import pandas as pd
import yfinance as yf 
import plotly.graph_objects as go
import plotly.express as px  # Import plotly.express for line charts
from alpha_vantage.fundamentaldata import FundamentalData
from stocknews import StockNews

# Set the page title and layout
st.set_page_config(page_title='Quant Lab', layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    /* Space below the title */
    .main > div {
        padding-top: 30px;  /* Adjust this value to control the space below the title */
    }

    /* Style the tabs */
    .stTabs [role="tablist"] button {
        font-size: 1.2rem;  /* Larger font for the tabs */
        padding: 12px 24px;  /* Add padding for wider space */
        margin-right: 10px;  /* Space between tabs */
        border-radius: 8px;  /* Rounded corners for a modern look */
        background-color: #00704A;  /* Primary color (e.g., #00704A for Starbucks green) */
        color: white;  /* White text for the tab labels */
    }

    /* Style for active tab */
    .stTabs [role="tablist"] button:focus, .stTabs [role="tablist"] button[aria-selected="true"] {
        background-color: #005a36;  /* Darker shade for active tab */
        color: white;  /* White text for active tab */
    }

    /* Adjust the tab content spacing */
    .stTabs [role="tabpanel"] {
        padding-top: 30px;  /* Adjust this value to control the space between tab content */
    }
    </style>
    """, unsafe_allow_html=True)

st.title('Quant Lab')

# Create Tabs for different sections of the dashboard
tabs = st.tabs(['Trading Dashboard'])
trading_dashboard = tabs[0]  # Unpack the tuple

# Trading Dashboard Tab
with trading_dashboard:
    st.markdown('### Trading Dashboard')

    # Create columns for the inputs on the landing page
    col1, col2, col3 = st.columns(3)

    # Place the ticker input and date selection in the columns
    with col1:
        ticker = st.text_input('Enter Stock Ticker:')

    with col2:
        start_date = st.date_input('Start Date')

    with col3:
        end_date = st.date_input('End Date')

    # Check if ticker is entered before proceeding
    if ticker:
        try:
            # Download stock data from Yahoo Finance
            stock = yf.download(ticker, start=start_date, end=end_date)

            # Ensure stock data is retrieved successfully
            if not stock.empty:
                # Calculate technical indicators
                stock['SMA50'] = stock['Adj Close'].rolling(window=50).mean()
                stock['SMA200'] = stock['Adj Close'].rolling(window=200).mean()

                # Bollinger Bands (20-day moving average + standard deviation bands)
                stock['20SMA'] = stock['Adj Close'].rolling(window=20).mean()
                stock['Upper Band'] = stock['20SMA'] + (stock['Adj Close'].rolling(window=20).std() * 2)
                stock['Lower Band'] = stock['20SMA'] - (stock['Adj Close'].rolling(window=20).std() * 2)

                # Calculate RSI (Relative Strength Index)
                delta = stock['Adj Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                stock['RSI'] = 100 - (100 / (1 + rs))

                # Create Candlestick Chart
                candlestick_trace = go.Candlestick(x=stock.index,
                                                   open=stock['Open'],
                                                   high=stock['High'],
                                                   low=stock['Low'],
                                                   close=stock['Adj Close'],
                                                   name='Candlestick',
                                                   increasing_line_color='green',
                                                   decreasing_line_color='red')

                # Add SMA 50 and SMA 200 to the chart
                sma50_trace = go.Scatter(x=stock.index,
                                         y=stock['SMA50'],
                                         mode='lines',
                                         name='SMA 50',
                                         line=dict(color='blue'))

                sma200_trace = go.Scatter(x=stock.index,
                                          y=stock['SMA200'],
                                          mode='lines',
                                          name='SMA 200',
                                          line=dict(color='yellow'))

                # Add Bollinger Bands to the chart
                upper_band_trace = go.Scatter(x=stock.index,
                                              y=stock['Upper Band'],
                                              mode='lines',
                                              name='Upper Band',
                                              line=dict(color='white'))

                lower_band_trace = go.Scatter(x=stock.index,
                                              y=stock['Lower Band'],
                                              mode='lines',
                                              name='Lower Band',
                                              line=dict(color='grey'))

                # Combine all traces in a single figure
                fig = go.Figure(data=[candlestick_trace, sma50_trace, sma200_trace, upper_band_trace, lower_band_trace])

                # Update layout
                fig.update_layout(
                    title=f'{ticker} Chart',
                    xaxis_title='Date',
                    yaxis_title='Price',
                    width=1700,
                    height=700,
                )

                st.plotly_chart(fig)

                # Add RSI below the main chart
                rsi_trace = go.Scatter(x=stock.index, y=stock['RSI'], mode='lines', name='RSI', line=dict(color='brown'))
                fig_rsi = go.Figure(data=[rsi_trace])

                # Update RSI layout
                fig_rsi.update_layout(
                    title='RSI (14)',
                    xaxis_title='Date',
                    yaxis_title='RSI',
                    width=1700,
                    height=300,
                    yaxis=dict(range=[0, 100])  # RSI typically ranges from 0 to 100
                )

                st.plotly_chart(fig_rsi)
            else:
                st.error("No data found for the given ticker and date range. Please try again.")

        except Exception as e:
            st.error(f"An error occurred: {e}")

    else:
        st.info("Please enter a stock ticker to start.")
