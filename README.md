### DISCORD STOCKS BOT

The Bot designed for the Discord Platform that provides information of the specific stocks through diferent discord channels.

It supports the following functionalities:
  
   - Provides data(between 1030 and 1630 IST, Mon-Fri) and daily stock updates (at 0700 IST, Mon-Fri).

   - '!' is the prefix of the bot. '!' must be called before the command to call the bot.(Eg.!commands)

- The bot supports 8 query commands:

  - **!commands**: Displays all the working commands in the discord bot

  - **!get-list**: Displays a list of predefined stock companies.

  -  **!prev-stock-data [stock_company]**: Retrieves and displays the previous day's stock data for a specified company. It also generates and sends a plot.

  - **!daily-trade-updates [stock_company]**: Sends a daily trade update plot for a specified company.

  - **!stock-history [company1] [company2] ...**: Sends a historical plot for one or more specified companies.

  - **!stock-history-bw-dates [company] [start_date] [end_date]**: Sends a historical plot for a specified company within a specified date range.

  - **!create-channel [channel_name]**: Creates a new text channel (admin-only command).

  - **!current-stock-value [company_name]**:Displays the real time stock value for an particular company.
