import re
import datetime
import csv
import pdb
from collections import defaultdict

TAX_YEAR = 2020

def read_csv(filename):
    transactions = []
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                transactions.append(Transaction(row))
                #transactions.append(Transaction(row[0], row[1], row[2], row[3], row[4], row[5]))
                line_count += 1
        print(f'Processed {line_count} lines.')

    return transactions


def read_csv_old(filename):
    transactions = []
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                #transactions.append(Transaction(row[0], row[1], row[2], row[3], row[4], row[5]))
                line_count += 1
        print(f'Processed {line_count} lines.')

    return transactions

def run_sanity_check(transactions):
    hashmap = defaultdict(lambda: 0)

    for transaction in transactions:
        if transaction.is_buy():
            hashmap[transaction.company] += transaction.units
        if transaction.is_sell():
            hashmap[transaction.company] -= transaction.units

        if hashmap[transaction.company] < 0:
            print(f'Errors found: more Sells than Buys. {transaction.company}, {hashmap[transaction.company]}')


def remove_date(s):                                             
    st = re.sub(r'(\d)(st|nd|rd|th)', r'\1', s)
    stripped = st.split(",", 1)[0]
    return stripped


# contains boughtDate and price
class Stock:
    def __init__(self, bought_date, price):
        self.bought_date = bought_date
        self.price = price


class Transaction:

    # 0:avg price, 1: created_at, 2: fees, 3: qty, 4: side, 5: simple+name, 6: symbol, 7: type
    # Use this function for the new format (2020)
    def __init__(self, row):
        self.date = datetime.datetime.strptime(remove_date(row[1]), '%d %b %Y') 
        self.date_str = row[1]
        self.company = row[5]
        self.price = float(row[0])
        self.action = row[4]
        self.units = float(row[3])



    def is_buy(self):
        return self.action == "B" or self.action == "buy"

    def is_sell(self):
        return self.action == "S" or self.action == "sell"

    def to_string(self):
        return "Date: %s, company: %s, action: %s, units: %s, price: %s" % (self.date, self.company, self.action, self.units, self.price)


def long_term(buy, sell):
   delta = sell.date - buy.date
   return delta.days > 365


def debug_string(sold, bought, gain_type, diff):
    print("%s, Company: %s, sold: %s, bought: %s, diff: %.2f" % (gain_type, sold.company, sold.date_str, bought.date_str, diff))


def main():
    long_term_gains = 0
    short_term_gains = 0
    transactions = read_csv("gains-losses-2020.csv")
    run_sanity_check(transactions)

    stocks = defaultdict(list)

    for transaction in transactions:
        company_stock = stocks[transaction.company]
        if transaction.is_buy():
            company_stock.append(transaction)
            company_stock.sort(key=lambda x: x.date_str)
        elif transaction.is_sell():
            num_units = transaction.units
            total_diff = 0

            # Find the FIFO buy transaction for that matching sell 
            while num_units > 0:
                num_units -= 1
                bought = company_stock[0]
                total_diff += (transaction.price - bought.price)
                bought.units -= 1
                if bought.units <= 0:
                    company_stock.pop(0)

                diff = transaction.price - bought.price

                # Only record into the counters if the date is tax year
                if transaction.date.year != TAX_YEAR:
                    continue

                # long term means greater than 1 year
                if long_term(bought, transaction):
                    debug_string(transaction,bought, "Long Term", diff)
                    long_term_gains += diff
                else:
                    debug_string(transaction, bought, "Short Term", diff)
                    short_term_gains += diff

        else:
            print("ERROR, action is not recognized!")

    print(f"short term gains: {short_term_gains}. long term gains: {long_term_gains}")

main()
