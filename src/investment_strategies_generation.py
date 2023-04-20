"""
Data-driven Portfolio Management
Part 2: Investment Strategies Generation

Group 4:
Nicolás Amigo Sañudo
Gema Díaz Ferreiro
Rafael Sojo García
Stephan Wolters Eisenhardt

Python script related to the second investment strategies generation part of the assigment.
The code contains some context-specific function to facilitate the readibility,
but the main structure is within  if __name__ == "__main__"

All functions serve a special purpose for an in-depth data visualization analysis
all of which are described in detail in the corresponiding docstrings.


Overview of libraries used:

pandas (pd): The pandas library is used to handle the input data as a DataFrame.
Functions like load_file use it to read the CSV file, while other functions use
it for filtering and grouping the data.

math: The math library is used to compute the standard deviation in order to
calculate the volatility.

itertools: The itertools library is used to generate all possible combinations
of percentages for the five assets in the investment portfolio.
"""

import math
import pandas as pd
import itertools

STARTDATE_STR = "01/01/2020"
ENDDATE_STR = "12/31/2020"

def portfolio_allocation():
    """
    Function to generate the portfolio with all of the percentage combinations for the
    different assets.

    Args:
        None
    Returns:
        None
    Raises:
        None
    """
    percentage = [1.0, 0.8, 0.6, 0.4, 0.2, 0.0]

    # Generate all the possible combinations
    combinations = list(itertools.product(percentage, repeat=5))

    # Check if every row sums 100%
    portfolio = []
    for row in combinations:
        if sum(row) == 1.0:
            portfolio.append(row)

    df = pd.DataFrame(portfolio, columns=['ST', 'CB', 'PB', 'GO', 'CA'])
    df.to_csv('portfolio_allocations.csv', index=False)


def load_data():
    """
    Function used to load the data all the date. This include the portfolio generated
    in the function portfolio_allocation() and the data for the different assets generated
    during the web scrapping part.

    Args:
        None
    Returns:
        assets_dict: which contains the Data and Price for each asset.
        portfolio_data: which contains the percentage combination for
        each asset.
        cost: which contains the cost percentage applied to the invested
        capital of each asset.
    Rises:
        None
    """
    portfolio_data = pd.read_csv("portfolio_allocations.csv")

    cash = pd.read_csv("usdollar.csv", delimiter=',', header=0)
    gold = pd.read_csv("spdr-gold-trust.csv",  delimiter=',', header=0)
    stocks = pd.read_csv("amundi-msci-wrld-ae-c.csv",  delimiter=',', header=0)
    corporate_bonds = pd.read_csv("ishares-global-corporate-bond-$-historical-data.csv",  delimiter=',', header=0)
    public_bonds = pd.read_csv("db-x-trackers-ii-global-sovereign-5.csv",  delimiter=',', header=0)

    assets_dict = {"ST": stocks,
                   "CB": corporate_bonds,
                   "PB": public_bonds,
                   "GO": gold,
                   "CA": cash}

    # Cost of invested capital for each asset
    cost = {"ST": 0.004,
            "CB": 0.002,
            "PB": 0.002,
            "GO": 0.001,
            "CA": 0.0}

    return assets_dict, portfolio_data, cost


def process_df(asset):
    """
    Function to some preprocessing to the assets data.

    This function convert the Date string into a Datetime and it deletes the % in
    Change %, if it existed, and it converts it into a float

    Args:
        asset: the data for the asset (date and price)
    Returns:
        None
    Raises:
        None
    """
    # Preprocessing
    asset["Date"] = pd.to_datetime(asset['Date'])
    asset['Change %'] = asset['Change %'].astype(str).map(lambda x: x.rstrip('%'))
    asset['Change %'] = asset['Change %'].astype(str).astype(float)


def fill_missing_dates(asset):
    """
    This functions fills the missing dates for the assets.

    The price for the dates with no associated price are filled. To fill them, we take
    the closest value.

    Args:
        asset: the data for the asset (date and price)
    Returns:
        None
    Rises:
        None
    """
    dates = pd.date_range(start=STARTDATE_STR, end=ENDDATE_STR)
    df_dates = pd.DataFrame({'Date': dates})
    df_merged = pd.merge(df_dates, asset, on='Date', how='left')
    df_merged = df_merged.fillna(method='ffill').fillna(method='bfill')

    return df_merged


def return_value(portfolio_data, assets, cost, investment):
    """
    This function computes the return values for each portfolio.

    To do so, it uses every line of the portfolio_allocations.csv and it iterates through
    the assets and computes the value depending on the price of it and the amount invested
    in that asset (which is bases on the percentage shown in the portfolio)

    Args:
        portfolio_data: it contains all of the percentage combinations for the different
        assets.
        assets: the data of all the asset (date and price)
        cost: cost percentage applied to the invested capital of each asset.
        investment: amount of money invested
    Returns:
        portfolio_date: portfolio data updated with the return value
    Raises:
        None
    """
    # We create the column to store the return values
    portfolio_data = portfolio_data.assign(RETURN=0)

    for index, portfolioRow in portfolio_data.iterrows():

        current_value = 0
        buy_amount = 0

        for key, value in assets.items():
            # Money invested * weight of each asset
            invested = investment * portfolioRow[key]
            shares = invested / assets[key][assets[key]['Date'] == STARTDATE_STR]['Price'].iloc[0]

            if key == "CA":  # cash
                buy_amount += (shares * (assets[key][assets[key]['Date'] == STARTDATE_STR]['Price'].iloc[0] / 100)) - (invested * cost[key])
                current_value += shares * (shares * assets[key][assets[key]['Date'] == ENDDATE_STR]['Price'].iloc[0] / 100)

            buy_amount += (shares * assets[key][assets[key]['Date'] == STARTDATE_STR]['Price'].iloc[0]) - (invested * cost[key])
            current_value += shares * assets[key][assets[key]['Date'] == ENDDATE_STR]['Price'].iloc[0]

        portfolio_return = ((current_value - buy_amount) / buy_amount) * 100
        portfolio_data.loc[index, "RETURN"] = portfolio_return

    portfolio_data.to_csv('portfolio_metrics.csv', index=False)

    return portfolio_data


def volatility_metric(portfolio_data, assets, investment):
    """
    This function computes the volatility values for each portfolio.

    To do so, it uses every line of the portfolio_allocations.csv and it iterates through
    the assets and computes the value depending on the price of it and the amount invested
    in that asset (which is bases on the percentage shown in the portfolio)

    Args:
        portfolio_data: it contains all of the percentage combinations for the different
        assets.
        assets: the data of all the asset (date and price)
        investment: amount of money invested
    Returns:
        None
    Raises:
        None
    """

    portfolio_data = portfolio_data.assign(VOLAT=0)

    volatility_col = []
    for i, portfolioRow in portfolio_data.iterrows():
        values = pd.Series([], dtype="float64")
        for asset in list(assets.keys()):
            df_asset = assets.get(asset)

            invested = investment * portfolioRow[asset]
            shares = invested / assets[asset][assets[asset]['Date'] == STARTDATE_STR]['Price'].iloc[0]

            if portfolioRow[asset] != 0:
                values = pd.concat([values, shares * df_asset.loc[(df_asset['Date'] >= STARTDATE_STR) & (df_asset['Date'] <= ENDDATE_STR)]['Price']])
        mean = values.mean()
        sd = math.sqrt((values.apply(lambda value: pow((value - mean), 2))).sum() / len(values))
        if mean != 0:
            volatility = ((sd / mean) * 100)
        else:
            volatility = 0
        volatility_col.append(volatility)

    portfolio_data["VOLAT"] = volatility_col

    portfolio_data.to_csv('portfolio_metrics.csv', index=False)


if __name__ == '__main__':
    # We use a 100$ investing.
    investment = 100

    portfolio_allocation()

    assets, portfolio_data, cost = load_data()

    process_df(assets.get("ST"))
    assets["ST"] = fill_missing_dates(assets["ST"])

    process_df(assets.get("CB"))
    assets["CB"] = fill_missing_dates(assets["CB"])

    process_df(assets.get("PB"))
    assets["PB"] = fill_missing_dates(assets["PB"])

    process_df(assets.get("GO"))
    assets["GO"] = fill_missing_dates(assets["GO"])

    process_df(assets.get("CA"))
    assets["CA"] = fill_missing_dates(assets["CA"])


    portfolio_data = return_value(portfolio_data, assets, cost, investment)

    volatility_metric(portfolio_data, assets, investment)



