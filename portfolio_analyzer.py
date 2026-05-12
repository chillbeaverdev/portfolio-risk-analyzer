import streamlit as st
import yfinance as yf
import quantstats as qs
import pandas as pd
import datetime
import os

# extend pandas with quantstats functionality
qs.extend_pandas()

st.set_page_config(page_title="Quant Portfolio Analyzer", layout="wide")

# css for hovering
st.markdown("""
<style>
    /* tooltip container */
    .tooltip {
        position: relative;
        display: inline-block;
        border-bottom: 1px dotted #666;
        cursor: help;
        color: #1f77b4;
        font-weight: 500;
    }
    
    /* tooltip text */
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 300px;
        background-color: #2e2e2e;
        color: #fff;
        text-align: left;
        border-radius: 8px;
        padding: 12px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -150px;
        opacity: 0;
        transition: opacity 0.3s ease-in-out;
        font-size: 14px;
        line-height: 1.5;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* tooltip arrow */
    .tooltip .tooltiptext::after {
        content: "";
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: #2e2e2e transparent transparent transparent;
    }
    
    /* show tooltip on hover */
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    /* error message styling */
    .error-box {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 12px;
        border-radius: 4px;
        margin: 10px 0;
    }
    
    /* success animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .success-message {
        animation: fadeIn 0.5s ease-in-out;
    }
</style>
""", unsafe_allow_html=True)

# financial terms dictionary
DEFINITIONS = {
    "Sharpe Ratio": "Measures risk-adjusted return. Higher is better. A ratio above 1 is good, above 2 is very good, above 3 is excellent. It shows how much excess return you get per unit of risk.",
    "CAGR": "Compound Annual Growth Rate - the average yearly return if you held the investment. For example, 10% CAGR means your money grew by 10% per year on average.",
    "Max Drawdown": "The worst peak-to-valley decline in your portfolio. For example, -20% means at the worst point, your portfolio lost 20% from its highest value. Lower is better.",
    "Benchmark": "A standard to compare your portfolio against (e.g., SPY for S&P 500). It shows if you're beating the market or not.",
    "Volatility": "How much your returns fluctuate. Higher volatility means more ups and downs. It's a measure of risk.",
    "Returns": "The profit or loss on your investment, expressed as a percentage of the initial amount."
}

def create_tooltip(term, definition):
    """creates an html tooltip element"""
    return f"""
    <div class="tooltip">{term}
        <span class="tooltiptext">{definition}</span>
    </div>
    """

# title with tooltips
st.title("Multi-Asset Portfolio Risk Analyzer")
st.markdown("Analyze your investment portfolio's performance and risk metrics compared to a benchmark.")

# sidebar user inputs
st.sidebar.header("Portfolio Configuration")

ticker_input = st.sidebar.text_input(
    "Enter Tickers (comma separated)", 
    "AAPL, MSFT, GOOG, AMZN",
    help="Enter stock ticker symbols separated by commas (e.g., AAPL, MSFT, TSLA)"
)

weights_input = st.sidebar.text_input(
    "Enter Weights (must sum to 1.0)", 
    "0.25, 0.25, 0.25, 0.25",
    help="Enter portfolio weights for each ticker. Must sum to 1.0 (e.g., 0.25, 0.25, 0.25, 0.25)"
)

benchmark_ticker = st.sidebar.text_input(
    "Benchmark Ticker", 
    "SPY",
    help="Enter a benchmark ticker to compare against (e.g., SPY for S&P 500, QQQ for NASDAQ)"
)

start_date = st.sidebar.date_input("Start Date", datetime.date(2015, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.date.today())

# validation functions
def validate_inputs(tickers, weights, benchmark, start, end):
    """validates user inputs and returns error messages if any"""
    errors = []
    
    # check if tickers list is empty
    if len(tickers) == 0 or tickers[0] == '':
        errors.append("please enter at least one ticker symbol")
    
    # check if weights match tickers
    if len(weights) != len(tickers):
        errors.append(f"number of weights ({len(weights)}) must match number of tickers ({len(tickers)})")
    
    # check if weights sum to 1.0
    elif abs(sum(weights) - 1.0) > 0.01:
        errors.append(f"weights must sum to 1.0 (currently sum to {sum(weights):.2f})")
    
    # check if any weight is negative
    if any(w < 0 for w in weights):
        errors.append("weights cannot be negative")
    
    # check if benchmark is empty
    if not benchmark or benchmark.strip() == '':
        errors.append("please enter a benchmark ticker")
    
    # check date range
    if start >= end:
        errors.append("start date must be before end date")
    
    if end > datetime.date.today():
        errors.append("end date cannot be in the future")
    
    return errors

# data processing with error handling
@st.cache_data
def get_data(tickers, benchmark, start, end):
    """downloads stock data with error handling"""
    try:
        data = yf.download(tickers, start=start, end=end, progress=False)['Close']
        bench = yf.download(benchmark, start=start, end=end, progress=False)['Close']
        
        # check if data is empty
        if data.empty:
            return None, None, "no data found for the specified tickers and date range"
        if bench.empty:
            return None, None, "no data found for the benchmark ticker"
        
        return data, bench, None
    except Exception as e:
        return None, None, f"error downloading data: {str(e)}"

# main analysis
if st.sidebar.button("Analyze Portfolio"):
    
    # parse inputs
    try:
        tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]
        weights = [float(w.strip()) for w in weights_input.split(",")]
        weights_series = pd.Series(weights, index=tickers)
    except ValueError:
        st.error("invalid input format. please check your tickers and weights")
        st.stop()
    
    # validate inputs
    errors = validate_inputs(tickers, weights, benchmark_ticker, start_date, end_date)
    
    if errors:
        st.markdown('<div class="error-box">', unsafe_allow_html=True)
        st.markdown("### please fix the following errors:")
        for error in errors:
            st.markdown(f"• {error}")
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()
    
    # download data
    with st.spinner('downloading market data...'):
        data, bench, error = get_data(tickers, benchmark_ticker, start_date, end_date)
        
        if error:
            st.error(error)
            st.info("tip: make sure ticker symbols are correct and market data is available for your date range")
            st.stop()
    
    # calculate returns
    with st.spinner('calculating risk metrics...'):
        try:
            returns = data.pct_change().dropna()
            bench_returns = bench.pct_change().dropna()
            
            # create weighted portfolio index
            portfolio_returns = (returns * weights_series).sum(axis=1)
            
            # check if we have enough data
            if len(portfolio_returns) < 20:
                st.warning("limited data available. results may not be reliable. try a longer date range")
            
        except Exception as e:
            st.error(f"error calculating returns: {str(e)}")
            st.stop()
    
    # metrics dashboard with tooltips
    st.markdown('<div class="success-message">', unsafe_allow_html=True)
    st.subheader("Key Performance Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    sharpe = qs.stats.sharpe(portfolio_returns)
    cagr = qs.stats.cagr(portfolio_returns)
    max_dd = qs.stats.max_drawdown(portfolio_returns)
    
    with col1:
        st.markdown(create_tooltip("Sharpe Ratio", DEFINITIONS["Sharpe Ratio"]), unsafe_allow_html=True)
        st.metric("", f"{round(sharpe, 2)}")
    
    with col2:
        st.markdown(create_tooltip("CAGR", DEFINITIONS["CAGR"]), unsafe_allow_html=True)
        st.metric("", f"{round(cagr * 100, 2)}%")
    
    with col3:
        st.markdown(create_tooltip("Max Drawdown", DEFINITIONS["Max Drawdown"]), unsafe_allow_html=True)
        st.metric("", f"{round(max_dd * 100, 2)}%")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # export feature
    try:
        report_file = "portfolio_report.html"
        qs.reports.html(portfolio_returns, benchmark=bench_returns, output=report_file, title="Portfolio Tear Sheet")
        
        with open(report_file, "rb") as f:
            st.sidebar.download_button(
                label="Download Full Tear Sheet (HTML)",
                data=f,
                file_name="Portfolio_Analysis_Report.html",
                mime="text/html"
            )
        
        # explanation for the tear sheet
        with st.sidebar.expander("About the Tear Sheet"):
            st.markdown(f"""
            The tear sheet includes:
            
            • {create_tooltip("Returns", DEFINITIONS["Returns"])}: monthly and yearly performance
            
            • {create_tooltip("Volatility", DEFINITIONS["Volatility"])}: risk metrics
            
            • Drawdown charts: visual representation of losses
            
            • Rolling statistics: performance over time
            
            • Comparison to {create_tooltip("Benchmark", DEFINITIONS["Benchmark"])}
            """, unsafe_allow_html=True)
    
    except Exception as e:
        st.warning(f"could not generate downloadable report: {str(e)}")
    
    # visuals
    st.subheader("Performance Analysis")
    tab1, tab2 = st.tabs(["Returns & Benchmarking", "Risk & Drawdown"])
    
    try:
        with tab1:
            fig = qs.plots.returns(portfolio_returns, bench_returns, show=False)
            st.pyplot(fig)
            st.caption("compares your portfolio's cumulative returns against the benchmark over time")
        
        with tab2:
            fig = qs.plots.drawdown(portfolio_returns, show=False)
            st.pyplot(fig)
            st.caption("shows the depth and duration of portfolio declines from peak values")
    
    except Exception as e:
        st.error(f"error generating visualizations: {str(e)}")
    
    st.success("analysis complete. download the full report from the sidebar for detailed metrics")

# sidebar info
st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Tips")
st.sidebar.info("""
- use at least 1 year of data for reliable results

- common benchmarks are SPY (S&P 500), QQQ (NASDAQ), DIA (Dow Jones)

- sharpe ratio > 1 is considered good

- lower max drawdown = less risky portfolio
""")