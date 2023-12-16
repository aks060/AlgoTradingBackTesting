# AlgoTradingBackTesting
Trading Algorithm Backtesting.

## How to use
1. First step is to configure the `config.json` file and provide the required parameters i.e. `stockDataURL`, `scanner` and `scanningURL`. These 3 are the mandatory values to be provide to work with AlgoTradingBackTesting.
2. Now update the `getCandidate` function in `functions.selectionFunction.py` as per your requirement. This function is used to fetch the candidate Stocks on which the backtest will run.

#### So Is that all?

YES, Now switch to `AlgoTradingBackTesting` directory and run `python ./backtesting/WeekMonthBullishStockRun.py --cache --file ./backtesting/DayWeekMonthBullish.csv`

## Command Parameters supported

1. `--cache` : This parameter enables to save and use stocks data (open, close, volume etc) as cache in `backtesting/cache` folder which prevent multiple request to APIs and saves your time and money.
2. `--file <csv file>` : It will read backtesting configurations from csv file provided and can run backtest with multiple configured values.

#### That's all As of now. Please feel free to contribute more Algos or to improve project quality. Thanks :)
