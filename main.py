import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
from bdshare import get_hist_data
from datetime import datetime
import pandas as pd


def plot_efficient_frontier():
    stock_A_ticker = stock_A_entry.get().upper()
    stock_B_ticker = stock_B_entry.get().upper()

    # Retrived data from bdshare library
    stock_A = get_hist_data('2024-06-01', datetime.now(), stock_A_ticker)[['ycp']]
    stock_B = get_hist_data('2024-06-01', datetime.now(), stock_B_ticker)[['ycp']]

    if stock_A.empty or stock_B.empty:
        error_label.config(text="Wrong tickers. No data found")


    # Rename columns
    stock_A.rename(columns={'ycp': 'ACI'}, inplace=True)
    stock_B.rename(columns={'ycp': 'GP'}, inplace=True)

    merged_stock = pd.concat([stock_A, stock_B], axis=1)

    merged_stock.index = pd.to_datetime(merged_stock.index)
    merged_stock = merged_stock.astype(float)
    merged_stock.sort_values(by=['date'], inplace=True)

    merged_df_return = (merged_stock / merged_stock.shift(1) - 1)

    # Weights
    weights_of_port_A = np.linspace(0,1,num=100)
    weights_of_port_B = 1 - weights_of_port_A
    weights = pd.DataFrame({"Weight_A":(weights_of_port_A),"Weights_B":weights_of_port_B})

    weights_array = weights.to_numpy()

    cov_matrix = merged_df_return.cov().to_numpy() * 250
    mean_returns = merged_df_return.mean().to_numpy() * 250

    portfolio_vola = np.array([np.sqrt(np.dot(w.T, np.dot(cov_matrix, w))) for w in weights_array])

    portfolio_return = np.dot(weights_array, mean_returns)

    # Creating columns for Portfolio return and volatility
    weights["Portfolio Returns"] = portfolio_return * 100
    weights["Portfolio Volatility"] = portfolio_vola * 100

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(weights['Portfolio Volatility'],weights['Portfolio Returns'], color='b')
    ax.set_title("Efficent frontier")
    ax.set_xlabel("Portfolio Volatility")
    ax.set_ylabel("Rate of Return")
    ax.grid(True)

    global canvas
    
    if canvas:
        canvas.get_tk_widget().destroy()

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10)

    error_label.config(text="")


###########

root = tk.Tk()
root.geometry("800x600")
root.title("Efficient Frontier Plot")
root.resizable(False,False)

canvas = None

##### Widgets
tk.Label(root, text="Enter stock A of DSE's companies tickers (ACI,GP, LANKABAFIN, etc...)").pack()
stock_A_entry = tk.Entry(root)
stock_A_entry.pack()

tk.Label(root, text="Enter stock B of DSE's companies tickers (ACI,GP, LANKABAFIN, etc...)").pack()
stock_B_entry = tk.Entry(root)
stock_B_entry.pack()

tk.Button(root,text="Show plots", command=plot_efficient_frontier).pack(pady=10)

tk.Button(root,text="Exit", command=lambda:root.destroy()).place(x=10,y=10)

error_label = tk.Label(root, text="", fg="red")
error_label.pack()

##############

root.mainloop()