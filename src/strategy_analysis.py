# -*- coding: utf-8 -*-
"""
Data-driven Portfolio Management Part 2: Investment Strategies Analysis

Group 4: 
Nicolás Amigo Sañudo
Gema Díaz Ferreiro
Rafael Sojo García
Stephan Wolters Eisenhardt

Python script related to the last part of the assignment and which conveys a 
detailed support for the investment analysis report

All functions serve a special purpose for an in-depth data visualization analysis
all of which are described in detail in the corresponiding docstrings.


Overview of libraries used:

pandas (pd): The pandas library is used to handle the input data as a DataFrame. 
Functions like load_file use it to read the CSV file, while other functions use 
it for filtering and grouping the data.

numpy (np): Numpy is used for numerical operations and generating sequences. 
For example, in the return_distribution_area function, it is used to create an 
evenly spaced range of values for the x-axis.

matplotlib.pyplot (plt): The pyplot module from matplotlib is used for creating 
and customizing various types of plots in the functions. Functions like 
return_distribution, return_distribution_area, and others use it to create the 
figures, set labels,  and customize the appearance of the plots.

seaborn (sns): Seaborn is used to create visually appealing statistical graphics 
in the functions. For example, return_average uses it for creating a bar plot, 
return_risk_scatter for a scatter plot, and return_risk_heatmap for a heatmap.

matplotlib.colors.LogNorm: This class is used to normalize the data using a 
logarithmic scale in the return_risk_hexbin function. It improves the visualization 
of the hexbin plot by scaling the data appropriately.

scipy.stats.gaussian_kde: This class is used to create a kernel density estimate 
using Gaussian kernels in the return_distribution_area function. It helps to 
estimate the probability density function of the returns data.

scipy.integrate.quad: This function is used to calculate the area under the 
kernel density estimate curve in the return_distribution_area function. It helps 
to quantify the area of positive and negative returns.
"""

#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LogNorm
from scipy.stats import gaussian_kde
from scipy.integrate import quad

# Portfolio mebtrics file location
metrics_file = "../metrics/portfolio_metrics.csv"

#%%
def main() -> None:
    """
    Main program entry point to execute all the analysis functions in sequence.
    
    The function loads the portfolio metrics data from a CSV file and subsequently calls
    each analysis and visualization function in order. It also includes line breaks to
    separate the output of each function for better readability.
    
    Args:
        None

    Returns:
        None

    Raises:
        None

    Example:
        >>> main()
    """
    df = load_file()
    
    functions = [
        return_distribution,
        return_distribution_area,
        return_average,
        return_risk_scatter,
        return_risk_heatmap,
        return_risk_contour,
        return_risk_hexbin,
    ]
    
    for func in functions:
        func(df)
        print('\n' * 5)
    
 #%%
def load_file() -> pd.DataFrame:
    """
    Loads the portfolio metrics data from a CSV file into a pandas DataFrame and returns it.
    
    The function reads the portfolio_metrics.csv file and creates a pandas DataFrame. The
    DataFrame can then be used as input for further analysis and visualization functions.
    
    This function also checks if the column names are correct and if the first five columns
    are integers and the last two columns are floats. If the checks fail, appropriate errors
    are raised.
    
    Args:
        None

    Returns:
        pd.DataFrame: A DataFrame containing the data from the portfolio_metrics.csv file.

    Raises:
        ValueError: If the column names do not match the expected column names.
        TypeError: If the first five columns are not integers or the last two columns are not floats.

    Notes:
        Ensure that the 'portfolio_metrics.csv' file is available in the metrics directory relative to the script.

    Example:
        >>> df = load_file()
    """
    # Read the CSV file
    df = pd.read_csv(metrics_file)

    # Check if the column names are correct
    expected_columns = ["ST", "CB", "PB", "GO", "CA", "RETURN", "VOLAT"]
    if df.columns.tolist() != expected_columns:
        raise ValueError(f"Unexpected column names. Expected: {expected_columns}, Got: {df.columns.tolist()}")

    # # Check if the first five columns are integers
    # for col in expected_columns[:5]:
    #     if not pd.api.types.is_integer_dtype(df[col]):
    #         raise TypeError(f"Column '{col}' should be of type int, but got {df[col].dtype}")

    # Check if the all columns are floats
    for col in expected_columns[-7:]:
        if not pd.api.types.is_float_dtype(df[col]):
            raise TypeError(f"Column '{col}' should be of type float, but got {df[col].dtype}")

    return df

#%%
def return_distribution(data:pd.DataFrame) -> None:
    """
    Plots the return distribution for 2020 with kernel density estimation and count per bin.

    The function creates a histogram with custom bin edges, ensuring that zero is an edge between two bins.
    It also overlays a kernel density estimate on the histogram.

    Args:
        data (pd.DataFrame): input dataframe from the original portfolio_metrics.csv file

    Returns:
        None
    
    Raises:
        None

    Notes: 
        One of the seven analysis plots used in the assigmment. 

    Example:
        >>> df = pd.read_csv("portfolio_metrics.csv")
        >>> return_distribution(df)
    """
    # Set figure size
    plt.figure(figsize=(12, 8))

    # Calculate the number of bins
    n_bins = 10  # 10 bins

    # Calculate the range of returns
    min_return = data["RETURN"].min()
    max_return = data["RETURN"].max()

    # Calculate bin width based on the total range and the number of bins
    bin_width = (max_return - min_return) / n_bins

    # Create custom bin edges
    bin_edges_neg = np.arange(0, min_return - bin_width, -bin_width)[::-1]
    bin_edges_pos = np.arange(0, max_return + bin_width, bin_width)
    bin_edges = np.concatenate((bin_edges_neg, bin_edges_pos))

    # Histogram with kernel density estimate and custom bin edges
    sns.histplot(data, x="RETURN", kde=True, bins=bin_edges, edgecolor='black', linewidth=1)

    # Title and axis labels
    plt.title(f"Return Distribution")
    plt.xlabel("Return in %")
    plt.ylabel("Kernel Density Estimate & Count")

    plt.show()
#%%
def return_distribution_area(data:pd.DataFrame) -> None:
    """
    Plots the return distribution for 2020 with kernel density estimation and areas.

    The function fits a Kernel Density Estimate (KDE) to the data and plots it. It also calculates
    the area under the KDE curve for values greater than zero and less than zero, filling those areas
    with different colors.

    Args:
        data (pd.DataFrame): input dataframe from the original portfolio_metrics.csv file

    Returns:
        None

    Raises:
        None

    Notes:
        One of the seven analysis plots used in the assignment.

    Example:
        >>> df = pd.read_csv("portfolio_metrics.csv")
        >>> return_distribution_area(df)
    """
    # Fit a Kernel Density Estimate to the data
    kde = gaussian_kde(data["RETURN"])

    # Set figure size
    plt.figure(figsize=(12, 8))

    # Plot the KDE
    x_range = np.linspace(data["RETURN"].min(), data["RETURN"].max(), 1000)
    plt.plot(x_range, kde(x_range), label='KDE')

    # Calculate the area under the KDE for values greater than zero and less than zero
    area_positive, _ = quad(kde, 0, data["RETURN"].max())
    area_negative, _ = quad(kde, data["RETURN"].min(), 0)

    # Fill the areas and add annotations
    plt.fill_between(x_range, kde(x_range), where=(x_range > 0), color='g', alpha=0.2)
    plt.fill_between(x_range, kde(x_range), where=(x_range < 0), color='r', alpha=0.2)

    plt.annotate(f"Area > 0: {area_positive:.2f}", xy=(0.6, 0.8), xycoords='axes fraction', fontsize=10, backgroundcolor='w')
    plt.annotate(f"Area < 0: {area_negative:.2f}", xy=(0.6, 0.75), xycoords='axes fraction', fontsize=10, backgroundcolor='w')

    # Add a vertical line at zero
    plt.axvline(0, color='k', linestyle='--', linewidth=1)

    # Title and axis labels
    plt.title(f"Return Distribution Area")
    plt.xlabel("Return in %")
    plt.ylabel("Kernel Density Estimate")

    plt.legend()
    plt.show()
#%%
def return_average(data:pd.DataFrame) -> None:
    """
    Plots the average positive and negative returns and their counts in a bar chart.

    The function calculates the average positive and negative returns, as well as the number of
    positive and negative returns. It then creates a bar chart to display this information, along
    with the expected value of returns.

    Args:
        data (pd.DataFrame): input dataframe from the original portfolio_metrics.csv file

    Returns:
        None

    Raises:
        None

    Notes:
        One of the seven analysis plots used in the assignment.

    Example:
        >>> df = pd.read_csv("portfolio_metrics.csv")
        >>> return_average(df)
    """
    # Calculate the average positive and negative returns
    average_positive_returns = data[data["RETURN"] > 0]["RETURN"].mean()
    average_negative_returns = data[data["RETURN"] < 0]["RETURN"].mean()

    # Calculate the number of positive and negative returns
    num_positive_returns = len(data[data["RETURN"] > 0])
    num_negative_returns = len(data[data["RETURN"] < 0])

    # Calculate the expected value of returns
    expected_value = (data["RETURN"] * (1 / len(data))).sum()

    # Create a DataFrame for the average positive and negative returns
    plot_data = pd.DataFrame({
        "Return Type": ["Average Positive Returns", "Average Negative Returns"],
        "Return": [average_positive_returns, average_negative_returns]
    })

    # Add the number of positive and negative returns to the plot_data DataFrame
    plot_data["Count"] = [num_positive_returns, num_negative_returns]

    # Create a bar plot using Seaborn
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.barplot(x="Return Type", y="Return", data=plot_data, palette=["g", "r"], alpha=0.6, ax=ax)

    # Plot the horizontal line for the expected value
    ax.axhline(expected_value, color="blue", linestyle="--", label=f"Expected Value: {expected_value / 100:.2%}")
    ax.axhline(average_positive_returns, color="green", linestyle="--", label=f"Avg. Pos. Return: {average_positive_returns / 100:.2%}")
    ax.axhline(average_negative_returns, color="red", linestyle="--", label=f"Avg. Neg. Return: {average_negative_returns / 100:.2%}")

    ax.set_ylabel("Average Return in %")
    ax.set_title("Average Positive and Negative Returns")
    ax.legend()

    # Annotate the bars with the number of positive and negative returns
    for idx, row in plot_data.iterrows():
        ax.text(idx, row["Return"] + (row["Return"] * 0.01), f"Count: {row['Count']}", ha="center", va="bottom", fontsize=10, color="k")

    plt.show()

#%%
def return_risk_scatter(data:pd.DataFrame) -> None:
    """
    Generates a scatter plot of normalized return (y-axis) and risk (volatility, x-axis)
    for all portfolios, and annotates each data point with the corresponding index.

    The function normalizes return and volatility values to make it easier to compare 
    portfolios. It also calculates the mean values for return and risk, and draws the 
    corresponding vertical and horizontal lines. The plot is divided into four quadrants,
    and the number of portfolios in each quadrant is annotated.

    Args:
        data (pd.DataFrame): input dataframe from the original portfolio_metrics.csv file

    Returns:
        None

    Raises:
        None

    Notes:
        One of the seven analysis plots used in the assignment.

    Example:
        >>> df = pd.read_csv("portfolio_metrics.csv")
        >>> return_risk_scatter(df)
    """
    # Normalize return and volatility for easy portfolio comparison
    data["RETURN"] = (data["RETURN"] - data["RETURN"].min()) / (data["RETURN"].max() - data["RETURN"].min())
    data["VOLAT"] = (data["VOLAT"] - data["VOLAT"].min()) / (data["VOLAT"].max() - data["VOLAT"].min())

    # Mean values for return and volatility
    mean_return = data["RETURN"].mean()
    mean_volatility = data["VOLAT"].mean()

    # Count data points per quadrant
    q1_count = len(data[(data["VOLAT"] > mean_volatility) & (data["RETURN"] > mean_return)])
    q2_count = len(data[(data["VOLAT"] < mean_volatility) & (data["RETURN"] > mean_return)])
    q3_count = len(data[(data["VOLAT"] < mean_volatility) & (data["RETURN"] < mean_return)])
    q4_count = len(data[(data["VOLAT"] > mean_volatility) & (data["RETURN"] < mean_return)])

    # Create a scatter plot using Seaborn
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.scatterplot(x="VOLAT", y="RETURN", data=data, alpha=0.6, ax=ax)

    ax.set_xlabel("Volatility (Risk)")
    ax.set_ylabel("Return")
    ax.set_title("Normalized Return vs. Risk (Volatility) for All Portfolios")

    # Iterate over the DataFrame and add annotations for each point's index
    for idx, row in data.iterrows():
      ax.annotate(idx, (row["VOLAT"], row["RETURN"]), textcoords="offset pixels", xytext=(7.5, 7.5), ha="center", fontsize=8) 

    # Get plot limits
    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()

    # Mean values for return and volatility         
    plt.axhline(y=mean_return, color='k', linestyle='--', linewidth=1)           
    plt.axvline(x=mean_volatility, color='k',linestyle='--', linewidth=1)

    # Annotate the count of data points in each quadrant
    ax.annotate(f"Q1: {q1_count}", xy=(x_max * 0.9, y_max * 0.9), fontsize=10, ha="center", va="center", backgroundcolor="w")
    ax.annotate(f"Q2: {q2_count}", xy=(x_min + (x_max - x_min) * 0.1, y_max * 0.9), fontsize=10, ha="center", va="center", backgroundcolor="w")
    ax.annotate(f"Q3: {q3_count}", xy=(x_min + (x_max - x_min) * 0.1, y_min + (y_max - y_min) * 0.1), fontsize=10, ha="center", va="center", backgroundcolor="w")
    ax.annotate(f"Q4: {q4_count}", xy=(x_max * 0.9, y_min + (y_max - y_min) * 0.1), fontsize=10, ha="center", va="center", backgroundcolor="w")

    # Annotate the mean return and mean volatility lines
    ax.annotate(f"Mean Return: {mean_return:.2f}", xy=(x_min, mean_return), xytext=(x_min + 0.01, mean_return + 0.03), fontsize=10, va="center", backgroundcolor="w")
    ax.annotate(f"Mean Volatility: {mean_volatility:.2f}", xy=(mean_volatility, y_min + 0.02), xytext=(mean_volatility + 0.02, y_min + 0.02), fontsize=10, ha="center", rotation=90, backgroundcolor="w")

    plt.show()
#%%
def return_risk_heatmap(data:pd.DataFrame) -> None:
    """
    Generates a heatmap of return (y-axis) vs. risk (volatility, x-axis) for different
    portfolios, visualizing the density of portfolios within each bin.

    The function creates bins for return and volatility, then calculates the number of
    portfolios within each bin. It uses this data to create a heatmap that provides a
    visual representation of the distribution of portfolios based on return and risk.

    Args:
        data (pd.DataFrame): input dataframe from the original portfolio_metrics.csv file

    Returns:
        None

    Raises:
        None

    Notes:
        One of the seven analysis plots used in the assignment.

    Example:
        >>> df = pd.read_csv("portfolio_metrics.csv")
        >>> return_risk_heatmap(df)
    """
    # Create bins for return and volatility
    data["return_bin"] = pd.cut(data["RETURN"], bins=10)
    data["volatility_bin"] = pd.cut(data["VOLAT"], bins=10)

    # Calculate the density of portfolios within each bin
    heatmap_data = data.groupby(["return_bin", "volatility_bin"]).size().unstack().fillna(0)

    # Create a heatmap using Seaborn
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(heatmap_data, cmap="YlGnBu", annot=True, fmt="g", ax=ax)

    ax.set_xlabel("Volatility (Risk)")
    ax.set_ylabel("Return")
    ax.set_title("Heatmap of Return vs. Risk (Volatility) for Different Portfolios")

    plt.show()

#%%
def return_risk_contour(data:pd.DataFrame) -> None:
    """
    Generates a contour plot of return (y-axis) vs. risk (volatility, x-axis) for different
    portfolios, visualizing the density of portfolios in a continuous manner.

    The function creates a contour plot using Seaborn's kdeplot function to estimate the
    probability density function of the joint distribution of return and risk. The plot
    provides a visual representation of the distribution of portfolios based on return
    and risk in a continuous manner, unlike the heatmap plot.

    Args:
        data (pd.DataFrame): input dataframe from the original portfolio_metrics.csv file

    Returns:
        None

    Raises:
        None

    Notes:
        One of the seven analysis plots used in the assignment.

    Example:
        >>> df = pd.read_csv("portfolio_metrics.csv")
        >>> return_risk_contour(df)
    """
    # Create a contour plot using Seaborn
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.kdeplot(x=data["VOLAT"], y=data["RETURN"], cmap="Blues", fill=True, ax=ax)

    ax.set_xlabel("Volatility (Risk)")
    ax.set_ylabel("Return")
    ax.set_title("Contour Plot of Return vs. Risk (Volatility) for Different Portfolios")

    plt.show()

#%%
def return_risk_hexbin(data:pd.DataFrame) -> None:
    """
    Generates a hexbin plot of return (y-axis) vs. risk (volatility, x-axis) for different
    portfolios, visualizing the density of portfolios using a grid of hexagons.

    The function creates a hexbin plot using Matplotlib's hexbin function to bin the
    data points in hexagonal cells. The color of each hexagon represents the log(count)
    of portfolios within that cell. A grid of hexagons is used for binning instead of
    squares to better represent the density of data points and reduce the influence of
    empty bins in between data points.

    Args:
        data (pd.DataFrame): input dataframe from the original portfolio_metrics.csv file

    Returns:
        None

    Raises:
        None

    Notes:
        One of the seven analysis plots used in the assignment.

    Example:
        >>> df = pd.read_csv("portfolio_metrics.csv")
        >>> return_risk_hexbin(df)
    """
    # Create a hexbin plot using Seaborn
    fig, ax = plt.subplots(figsize=(12, 8))
    
    hb = ax.hexbin(data["VOLAT"], data["RETURN"], gridsize=30, cmap='viridis', mincnt=1, norm=LogNorm())

    ax.set_xlabel("Volatility (Risk)")
    ax.set_ylabel("Return")
    ax.set_title("Return vs. Risk (volatility) for All Portfolios")

    # Add a colorbar to the plot
    cb = plt.colorbar(hb, ax=ax)
    cb.set_label('Log(count)')

    plt.show()

#%%
if __name__ == "__main__":
    main()
    
    
    
    
    
    
    
    
    
    
    
    
    