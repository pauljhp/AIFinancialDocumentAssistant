from .FinancialModelingPrep.tickers import Ticker
from langchain.tools import tool
import pandas as pd
from typing import Dict, Any


class FMPTools:

    @tool("Get Income Statements")
    def income_statements(ticker: str) -> pd.DataFrame:
        """helpful for getting the historical income statement of a company
        :param ticker: str
        :returns: pd.DataFrame
        """
        try:
            statement = Ticker.get_income_statements(tickers=ticker, freq="A")
            return statement
        except Exception as e:
            return f"An error has happened - this is the error message: {e}"
        
    @tool("Get Balance Sheets")
    def balance_sheet(ticker: str) -> pd.DataFrame:
        """helpful for getting the historical balance sheet of a company
        :param ticker: str
        :returns: pd.DataFrame
        """
        try:
            statement = Ticker.get_balance_sheet(tickers=ticker, freq="A")
            return statement
        except Exception as e:
            return f"An error has happened - this is the error message: {e}"
        
    @tool("Get Cashflow Statements")
    def cash_flow(ticker: str) -> pd.DataFrame:
        """helpful for getting the historical cashflow statement of a company
        :param ticker: str
        :returns: pd.DataFrame
        """
        try:
            statement = Ticker.get_cashflow(tickers=ticker, freq="A")
            return statement
        except Exception as e:
            return f"An error has happened - this is the error message: {e}"
        
    @tool("Get Ratios")
    def ratios(ticker: str) -> pd.DataFrame:
        """helpful for getting the historical standardized financial ratios 
        of a company
        :param ticker: str
        :returns: pd.DataFrame
        """
        try:
            statement = Ticker.get_financial_ratios(ticker=ticker, freq="A")
            return statement
        except Exception as e:
            return f"An error has happened - this is the error message: {e}"
        
    @tool("Get Growth")
    def growth(ticker: str) -> pd.DataFrame:
        """helpful for getting the historical growth profile of a company
        :param ticker: str
        :returns: pd.DataFrame
        """
        try:
            statement = Ticker.get_financial_growth(ticker=ticker, freq="A")
            return statement
        except Exception as e:
            return f"An error has happened - this is the error message: {e}"
        
    @tool("Get Estimates")
    def estimates(ticker: str) -> Dict[str, Any]:
        """helpful for getting the Analyst estimates of a company
        :param ticker: str
        :returns: pd.DataFrame
        """
        try:
            statement = Ticker.get_analyst_estimates(ticker=ticker)
            return statement
        except Exception as e:
            return f"An error has happened - this is the error message: {e}"
        
    @tool("Get company profile")
    def profile(ticker: str):
        """helpful for getting a broad overview of a company"""
        try:
            statement = Ticker.get_company_profile(ticker=ticker)
            return statement.to_dict()
        except Exception as e:
            return f"An error has happened - this is the error message: {e}"
        
    @tool("Get product segments")
    def prod_segment(ticker: str):
        """helpful for getting the product segment of a company"""
        try:
            statement = Ticker.get_product_segments(ticker=ticker)
            return statement
        except Exception as e:
            return f"An error has happened - this is the error message: {e}"