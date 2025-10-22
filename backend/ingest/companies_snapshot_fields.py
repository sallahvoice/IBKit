from typing import List, pd
import yfinance as yf

def create_companies_snapshot_fields(dfs: List[pd.DataFrame]): #needs revision
    snapshots = {}
    target_company_ticker = dfs[0]["ticker"].iloc[0]

    #for target company only 
    snapshots[0][target_company_ticker]["trailing_sales"] = None
    snapshots[0][target_company_ticker]["trailing_ebit"] = None
    yf_ticker = yf.Ticker(target_company_ticker)
        #check if this method is actually available + are those fields valid
    try:
        quartrly_inc = yf_ticker.financials
        if "Total Revenue" in quartrly_inc.index:
            snapshots[0][target_company_ticker]["trailing_sales"] = quartrly_inc.loc["total Revenue"].iloc[:4].sum()

            for key in ["Operating Income", "Ebit", "EBIT"]:
                if key in quartrly_inc.index:
                    snapshots[0][target_company_ticker]["trailing_ebit"] = quartrly_inc.loc[key].iloc[:4].sum()
                    break
    except Exception:
        pass
            
    if (snapshots[ticker]["trailing_sales"] or snapshots[ticker]["trailing_ebit"]) == None:
        snapshots[ticker]["trailing_sales"] = latest.get("revenue")
        snapshots[ticker]["trailing_ebit"] = latest.get("ebit")

    snapshots[0][target_company_ticker]["last_annual_cash"] = latest.get("cashAndShortTermInvestments") #needed for target company only
    

    for df in dfs:
        ticker = df["ticker"].iloc[0]
        stmt_type = df["statement_type"].iloc[0]

        yf_ticker = yf.Ticker(ticker)
        info = ticker.info

        if ticker not in snapshots:
            snapshots[ticker] = {}

        latest = df.iloc[0].to_dict()

        snapshots[ticker]["marginal_tax_rate"] = 0.21 #make it dynamic if possible

        if stmt_type == "income_statement":
            snapshots[ticker]["last_annual_revenue"] = latest.get("revenue")
            snapshots[ticker]["last_annual_ebit"] = latest.get("ebit")
            snapshots[ticker]["last_annual_net_income"] = latest.get("netIncome")
            snapshots[ticker]["last_annual_interest_expense"] = latest.get("interestExpense")
            snapshots[ticker]["last_annual_tax_paid"] = latest.get("incomeTaxExpense")



        elif stmt_type == "balance-sheet-statement":
            snapshots[ticker]["last_annual_debt"] = latest.get("totalDebt")
            
            snapshots[ticker]["last_annual_equity"] = latest.get("totalEquity")


        elif stmt_type == "cash-flow-statement":
            snapshots[ticker]["last_annual_capex"] = latest.get("capitalExpenditure") #negative
            snapshots[ticker]["last_annual_chng_wc"] = latest.get("changeInWorkingCapital")
            snapshots[ticker]["last_annual_da"] = latest.get("depreciationAndAmortization")

        else:
            snapshots[ticker]["market_cap"] = info.get("marketCap")
            snapshots[ticker]["current_shares_outstanding"] = info.get("sharesOutstanding")
            snapshots[ticker]["current_beta"] = info.get("beta")

    return snapshots