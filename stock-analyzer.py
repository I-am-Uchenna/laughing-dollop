import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np


def fetch_historical_data(symbol, period):
    """Fetches historical stock data for a given symbol and period."""
    try:
        ticker = yf.Ticker(symbol)
        historical_data = ticker.history(period=period)
        if historical_data.empty:
            st.warning(f"No data found for symbol: {symbol} with period: {period}. Please check the symbol and time period.")
            return None
        else:
            return historical_data
    except Exception as e:
        st.error(f"An error occurred while fetching data for {symbol}: {e}")
        return None

def calculate_technical_indicators(data):
    """Calculates and adds technical indicators to the historical data."""
    if data is None or data.empty:
        return data

    # Calculate SMAs
    data['SMA_20'] = data['Close'].rolling(window=20).mean()
    data['SMA_50'] = data['Close'].rolling(window=50).mean()

    # Calculate RSI
    delta = data['Close'].diff(1)
    gain = delta.copy()
    loss = delta.copy()
    gain[gain < 0] = 0
    loss[loss > 0] = 0

    # Use pandas ewm for exponential moving average
    avg_gain = gain.ewm(span=14, adjust=False).mean()
    avg_loss = abs(loss.ewm(span=14, adjust=False).mean())

    rs = avg_gain / avg_loss
    data['RSI'] = 100 - (100 / (1 + rs))

    # Calculate MACD
    data['EMA_12'] = data['Close'].ewm(span=12, adjust=False).mean()
    data['EMA_26'] = data['Close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = data['EMA_12'] - data['EMA_26']
    data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()

    # Calculate Bollinger Bands
    data['Middle_Band'] = data['Close'].rolling(window=20).mean()
    data['Upper_Band'] = data['Middle_Band'] + (data['Close'].rolling(window=20).std() * 2)
    data['Lower_Band'] = data['Middle_Band'] - (data['Close'].rolling(window=20).std() * 2)

    # Volume Profile (Conceptual - simplified for historical data)
    # For historical data, we can calculate a simple moving average of volume
    data['Volume_SMA_20'] = data['Volume'].rolling(window=20).mean()


    # Drop rows with NaN values
    data.dropna(inplace=True)

    return data

def display_key_statistics_and_price(symbol):
    """Displays key financial statistics and current price for a symbol."""
    st.write(f"**{symbol}**")
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        # Display Key Financial Statistics
        if 'marketCap' in info and info['marketCap'] is not None:
            st.metric("Market Cap", f"${info['marketCap']:,.0f}")
        if 'fiftyTwoWeekHigh' in info and info['fiftyTwoWeekHigh'] is not None:
            st.metric("52-Week High", f"${info['fiftyTwoWeekHigh']:.2f}")
        if 'fiftyTwoWeekLow' in info and info['fiftyTwoWeekLow'] is not None:
            st.metric("52-Week Low", f"${info['fiftyTwoWeekLow']:.2f}")
        if 'averageVolume' in info and info['averageVolume'] is not None:
            st.metric("Average Volume", f"{info['averageVolume']:,.0f}")

        # Display Current Price
        if 'currentPrice' in info and info['currentPrice'] is not None:
             st.metric("Current Price", f"${info['currentPrice']:.2f}")
        elif 'regularMarketPrice' in info and info['regularMarketPrice'] is not None:
             st.metric("Current Price", f"${info['regularMarketPrice']:.2f}")
        else:
             st.warning(f"Current price information not available for {symbol}.")

    except Exception as e:
        st.warning(f"Could not retrieve financial statistics for {symbol}: {e}")


def display_fundamental_analysis(symbol):
    """Displays fundamental analysis data for a symbol."""
    st.write(f"**{symbol}**")
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        # Display P/E Ratios
        if 'trailingPE' in info and info['trailingPE'] is not None:
            st.metric("P/E Ratio (Trailing)", f"{info['trailingPE']:.2f}")
        elif 'forwardPE' in info and info['forwardPE'] is not None:
             st.metric("P/E Ratio (Forward)", f"{info['forwardPE']:.2f}")
        else:
            st.info(f"P/E Ratio information not available for {symbol}.")


        # Display EPS
        if 'trailingEPS' in info and info['trailingEPS'] is not None:
            st.metric("EPS (Trailing)", f"${info['trailingEPS']:.2f}")
        elif 'forwardEPS' in info and info['forwardEPS'] is not None:
            st.metric("EPS (Forward)", f"${info['forwardEPS']:.2f}")
        else:
            st.info(f"EPS information not available for {symbol}.")


        # Display Dividend Yield
        if 'dividendYield' in info and info['dividendYield'] is not None:
            st.metric("Dividend Yield", f"{info['dividendYield']:.2%}")
        else:
            st.info(f"Dividend Yield information not available for {symbol}.")

         # Display Balance Sheet (limited data available via ticker.info)
        if 'totalAssets' in info and info['totalAssets'] is not None:
            st.metric("Total Assets", f"${info['totalAssets']:,.0f}")
        if 'totalLiabilities' in info and info['totalLiabilities'] is not None:
            st.metric("Total Liabilities", f"${info['totalLiabilities']:,.0f}")
        if 'totalStockholderEquity' in info and info['totalStockholderEquity'] is not None:
             st.metric("Total Stockholder Equity", f"${info['totalStockholderEquity']:,.0f}")
        else:
            st.info(f"Limited Balance Sheet information available for {symbol}.")


        # Display Income Statement (limited data available via ticker.info)
        if 'revenue' in info and info['revenue'] is not None:
            st.metric("Revenue", f"${info['revenue']:,.0f}")
        if 'grossProfits' in info and info['grossProfits'] is not None:
             st.metric("Gross Profits", f"${info['grossProfits']:,.0f}")
        if 'netIncomeToCommon' in info and info['netIncomeToCommon'] is not None:
             st.metric("Net Income", f"${info['netIncomeToCommon']:,.0f}")
        else:
             st.info(f"Limited Income Statement information available for {symbol}.")


    except Exception as e:
        st.warning(f"Could not retrieve fundamental analysis data for {symbol}: {e}")


def generate_charts(historical_data_dict):
    """Generates and displays interactive charts for multiple stocks."""
    if historical_data_dict:
        st.subheader("Historical Price Trends and Technical Indicators")
        for symbol, data in historical_data_dict.items():
            st.write(f"**{symbol}**")
            if data is not None and not data.empty:
                fig = go.Figure()

                # Add Candlestick trace
                fig.add_trace(go.Candlestick(x=data.index,
                                            open=data['Open'],
                                            high=data['High'],
                                            low=data['Low'],
                                            close=data['Close'],
                                            name='Candlestick'))

                # Add closing price line trace
                fig.add_trace(go.Scatter(x=data.index,
                                        y=data['Close'],
                                        mode='lines',
                                        name='Close Price'))

                # Add technical indicator traces
                if 'SMA_20' in data.columns:
                    fig.add_trace(go.Scatter(x=data.index, y=data['SMA_20'], mode='lines', name='SMA 20'))
                if 'SMA_50' in data.columns:
                    fig.add_trace(go.Scatter(x=data.index, y=data['SMA_50'], mode='lines', name='SMA 50'))
                if 'RSI' in data.columns:
                    fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines', name='RSI', yaxis='y2'))
                if 'MACD' in data.columns:
                    fig.add_trace(go.Scatter(x=data.index, y=data['MACD'], mode='lines', name='MACD', yaxis='y3'))
                if 'Signal_Line' in data.columns:
                    fig.add_trace(go.Scatter(x=data.index, y=data['Signal_Line'], mode='lines', name='Signal Line', yaxis='y3'))
                if 'Middle_Band' in data.columns:
                    fig.add_trace(go.Scatter(x=data.index, y=data['Middle_Band'], mode='lines', name='Middle Band', line=dict(dash='dash')))
                if 'Upper_Band' in data.columns:
                    fig.add_trace(go.Scatter(x=data.index, y=data['Upper_Band'], mode='lines', name='Upper Band', line=dict(dash='dash')))
                if 'Lower_Band' in data.columns:
                    fig.add_trace(go.Scatter(x=data.index, y=data['Lower_Band'], mode='lines', name='Lower Band', line=dict(dash='dash')))

                # Add Volume trace
                if 'Volume' in data.columns:
                     fig.add_trace(go.Bar(x=data.index, y=data['Volume'], name='Volume', yaxis='y4', opacity=0.5))


                # Update layout
                fig.update_layout(
                    title=f'Historical Stock Price Analysis for {symbol}',
                    xaxis_title='Date',
                    yaxis_title='Price',
                    yaxis2=dict(title='RSI', overlaying='y', side='right', position=0.15),
                    yaxis3=dict(title='MACD', overlaying='y', side='right', position=0.05),
                    yaxis4=dict(title='Volume', overlaying='y', side='left', position=0, showgrid=False),
                    xaxis_rangeslider_visible=False # Hide range slider for better visualization
                )


                st.plotly_chart(fig)
            else:
                st.info(f"No historical data available to display charts for {symbol}.")
    else:
        st.info("Enter stock symbols and a time period to fetch data.")


# --- Streamlit App Layout ---
st.title("Real-Time Stock Market Data Analysis")

stock_symbols_input = st.text_input(
    "Enter Stock Symbols (e.g., AAPL,MSFT):", "AAPL,MSFT"
)
stock_symbols = [symbol.strip().upper() for symbol in stock_symbols_input.split(',')]

time_period = st.selectbox(
    "Select Time Period:",
    ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
)

st.write(f"Analyzing data for {stock_symbols} over {time_period}")

# Fetch data for all symbols
historical_data_dict = {}
for symbol in stock_symbols:
    data = fetch_historical_data(symbol, time_period)
    if data is not None:
        historical_data_dict[symbol] = data

# Calculate technical indicators for each stock
if historical_data_dict:
    for symbol, data in historical_data_dict.items():
        historical_data_dict[symbol] = calculate_technical_indicators(data)

# Display data, statistics, and charts
if historical_data_dict:
    st.subheader("Historical Data:")
    for symbol, data in historical_data_dict.items():
        st.write(f"Data for {symbol}:")
        st.dataframe(data)

    st.subheader("Key Financial Statistics and Current Price")
    for symbol in historical_data_dict.keys():
        display_key_statistics_and_price(symbol)

    st.subheader("Fundamental Analysis")
    for symbol in historical_data_dict.keys():
        display_fundamental_analysis(symbol)

    generate_charts(historical_data_dict)
else:
    st.info("Enter stock symbols and a time period to fetch data.")
