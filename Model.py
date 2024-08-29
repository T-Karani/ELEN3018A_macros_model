import random
import matplotlib.pyplot as plt
from typing import Union

try:
    period = int(input("Welcome to the model of the economy. How many years do you wish to simulate for? "))
except:
    print("Invalid input detected. Model will be simulated over a 10 year period.")
    period = 10

interest_rate = 0.05    # initial interest rate

class ReserveBank:
    def __init__(self, name, money_supply):
        self.name = name
        self.money_supply = [money_supply] * 12 # How much money is available each month
        self.reserve_requirement = 0.025  # Initial reserve requirement


    def set_reserve_requirement(self, new_reserve_requirement):
        self.reserve_requirement = float(format(new_reserve_requirement, '.2f'))

class Government:
    def __init__(self, name, budget):
        self.name = name
        self.budget = [0] * period  # 10 years, change if necessary
        self.budget[0] = budget
        self.funds = [[0] * 12]
        self.revenue = [[0] * 12]   # 12 for months; same and for all going forward

class Household:
    def __init__(self, name, savings_rate, savings):
        self.name = name
        self.net_income = [[0] * 12]
        self.savings = savings  # cumulative savings only
        self.expenses = [[0] * 12]
        self.loan_amount = 0    # total loan amount
        self.savings_rate = savings_rate
        self.stock = 0  # total amount

    def invest_in_stock_market(self, amount):
        self.stock += amount
        self.savings -= amount  # subtract investment amount from savings        

class Company:
    def __init__(self, name, assets, investment_rate):
        self.name = name
        self.assets = assets
        self.profit = [[0] * 12]
        self.expenses = [[0] * 12]
        self.net_investments = [[0] * 12]
        self.loan_amount = 0
        self.investment_rate = investment_rate
        self.rd_expenditure = 0 # Research and development (R&D)
        self.capital_expenditure = 0    # Property, labour expansion, plant equipment, etc

    def invest_in_rd(self, amount, year, month):
        self.rd_expenditure += amount
        self.profit[year][month] = self.profit[year][month] - amount  # subtract R&D expenditure from profit        

    def invest_capital_expenditure(self, amount, year, month):
        self.capital_expenditure += amount
        self.profit[year][month] -= amount  # subtract capital expenditure from profit

class CommercialBank:
    def __init__(self, name, deposits, reserve_bank):
        self.name = name
        self.deposits = [[deposits] * 12]
        self.clients = [["", 0]]
        self.loans = [["", 0] * 3]
        self.reserves = [0] * period
        self.reserve_bank = reserve_bank

    def withdraw(self, agent: Union[Company, Household], amount, year, month):
        for client in self.clients:
            if client[0] == agent.name:
                client[1] -= float(format(amount, '.2f'))

        # act depending if company or household
        if isinstance(agent, Household):
            agent.savings -= amount
            agent.net_income[year][month] += amount
        else:
            agent.assets -= amount
            agent.profit[year][month] += amount
        self.deposits[year][month] -= amount        

    def make_deposit(self, agent: Union[Company, Household], amount, year, month):
        for client in self.clients:
            if client[0] == agent.name:
                client[1] += float(format(amount, '.2f'))
                break
            else:
                self.clients.append([agent.name, float(format(amount, '.2f'))])
        
        # act depending if company or household
        if isinstance(agent, Household):
            agent.savings += amount
            agent.net_income[year][month] -= amount
        else:
            agent.assets += amount
            agent.profit[year][month] -= amount
        self.deposits[year][month] += amount

    def make_loan(self, client: Union[Company, Household], amount, year, month):
        available_money = 0
        # calculate total money in bank
        for i, deposit in enumerate(self.deposits[year]):
            if i == 0:
                available_money = self.deposits[year][i]
            else:
                available_money = sum(self.deposits[year][:i]) + self.deposits[year][i]
                
        # decline loan if not enough money
        if available_money - self.reserves[year] < amount:
            return 0

        # give loan
        for loan in self.loans:
            if loan[0] == client:
                loan[1] += float(format(amount, '.2f'))
                break
            else:
                self.loans.append([client, float(format(amount, '.2f'))])
        self.deposits[year][month] -= float(format(amount, '.2f'))
        return float(format(amount, '.2f'))

    # change reserve amount based on reserve ratio
    def update_reserves(self, year):
        available_money = 0
        for i in range(year):
            available_money += sum(self.deposits[i])
        self.reserves[year] = float(format(available_money * self.reserve_bank.reserve_requirement, '.2f'))

# allow for repayment on loan
def payback_loan(agent: Union[Company, Household], amount, bank):
    # find correct loan to repay
    for loan in bank.loans:
        if loan[0] == agent.name:
            if loan[1] - amount > 0:
                loan[1] -= amount
            else:
                loan[1] = 0
                print(agent.name, "fully repaid the loan.\n")
                loan.clear
            break

# capitalize interest on loans
def update_loans(households, companies, commercial_banks, year, month):
    # Update loan amounts
    for household in households:
        household.loan_amount *= (1 + interest_rate / 12)  # Assuming interest is compounded monthly
        for bank in commercial_banks:
            for loan in bank.loans:
                if loan[0] == household.name:
                    loan[1] = household.loan_amount
                    break

    for company in companies:
        company.loan_amount *= (1 + interest_rate / 12)  # Assuming interest is compounded monthly
        for bank in commercial_banks:
            for loan in bank.loans:            
                if loan[0] == company.name:
                    loan[1] = company.loan_amount
                    break


def calculate_gdp(households, companies, government, year):
    gdp = 0
    for household in households:
        gdp += sum(household.expenses[year])
        gdp += household.stock
        gdp += household.loan_amount
    for company in companies:
        gdp += sum(company.net_investments[year])
    gdp += government.budget[year] - sum(government.funds[year])
    return gdp

def expectations(reserve_bank, government, households, companies, commercial_banks, years, year, month):
    duration = random.randint(1, 3)

    # Expectations formation
    def form_expectations(agent, variable):
        # Simple moving average of past values
        expectations = sum(variable[year][:month]) / (month + 1)
        return expectations

    # Decision-making based on expectations
    for company in companies:
        expected_price = form_expectations(company, company.profit)  # expect prices to rise
        if expected_price > company.profit[year][month]:
            company.investment_rate *= 0.9  # increase investment
        else:
            company.investment_rate *= 1.25

    return duration

def change_confidence_level(reserve_bank, government, households, companies, commercial_banks, years, year, month):
    duration = random.randint(1, 3)
    # Confidence variable
    confidence = random.uniform(-0.5, 0.5)

    # Overconfidence and fear
    for company in companies:
        if confidence > 0.2:
            company.investment_rate *= 1.2  # overconfident, increase investment
        elif confidence < -0.1:
            company.investment_rate *= 0.8  # fearful, reduce investment

    # Irrational behavior
    for company in companies:
        if confidence > 0.35:
            company.investment_rate *= 1.5  # herding behavior, follow the crowd
        elif confidence < -0.25:
            company.investment_rate *= 0.5  # anchoring, rely on initial information

    # Sentiment analysis
    sentiment = random.uniform(-0.3, 0.4)  # initialize sentiment to 0.5
    confidence += sentiment  # adjust confidence based on sentiment

    # News and events
    news_event = random.uniform(-0.1, 0.1)  # positive news event
    confidence += news_event  # adjust confidence based on news event

    return duration


def natural_disaster(reserve_bank, government, households, companies, commercial_banks, years, year, month):
    duration = random.randint(1, 12)
    return duration

def change_consumer_confidence(reserve_bank, government, households, companies, commercial_banks, years, year, month):
    duration = random.randint(1, 8)
    # Increase household spending
    for household in households:
        household.expenses[year][month] *= 1.2

    # Decrease household savings rate
    for household in households:
        household.savings_rate *= 0.85

    return duration

def boom(reserve_bank, government, households, companies, commercial_banks, years, year, month):
    duration = random.randint(1, 4) * 12

    # Increase consumer confidence
    savings_multiplier = 0.7
    for household in households:
        household.savings_rate *= savings_multiplier

    # Increase investment
    investments_multiplier = 1.4
    for company in companies:
        company.investment_rate *= investments_multiplier

    return duration


def recession(reserve_bank, government, households, companies, commercial_banks, years, year, month):
    duration = random.randint(1, 4) * 12
    # Decrease consumer confidence
    for household in households:
        household.savings_rate *= 1.3

    # Decrease investment
    for company in companies:
        company.investment_rate *= 0.7

    return duration

def policy_intervention(reserve_bank, government, households, companies, commercial_banks, years, year, month):
    duration = random.randint(1, 18)

    reserve_bank.set_reserve_requirement(reserve_bank.reserve_requirement * 0.92)

    for bank in commercial_banks:
        bank.reserves[year] *= reserve_bank.reserve_requirement

    # Investment incentives
    investment_incentive = 0.15
    for company in companies:
        company.investment_rate *= (1 + investment_incentive)

    return duration

def choose_shock():
    shocks = {
        'boom': boom,
        'recession': recession,
        'policy_intervention': policy_intervention,
        'change_consumer_confidence': change_consumer_confidence,
        'change_confidence_level': change_confidence_level,
        'expectations': expectations,
        'natural_disaster': natural_disaster
    }
    choice_name = random.choice(list(shocks.keys()))
    return shocks[choice_name]

shocks = []

def determine_if_shock():
    check_num = random.randint(0, 100)
    shock_num = random.randint(0, 100)

    if check_num == shock_num:
        return True
    return False

def simulate_economy(reserve_bank, government, households, companies, commercial_banks, years):
    global interest_rate
    # households take out initial loan once
    for household in households:
        borrowed_amount = commercial_banks[0].make_loan(household.name, random.uniform(300, 800), 0, 0)
        household.loan_amount = borrowed_amount

    gov_wage = 120
    company_wage = 100       

    for year in range(years): 
        # Reserve Bank sets reserve requirement based on change in interest rates
        interest_direction = random.choice([-1, 1])
        interest_change = random.uniform(0.0025, 0.01) * interest_direction
        new_interest_rate = interest_rate + interest_change

        reserve_change = interest_change / 10   # proportional change
        reserve_bank.set_reserve_requirement(reserve_bank.reserve_requirement + reserve_change)

        commercial_banks[0].update_reserves(year)

        # government budget changes
        budget_change = interest_change * 2
        if year == 0:
            new_budget = government.budget[0]
        else:
            new_budget = government.budget[year - 1] * (1 + budget_change)

        government.budget[year] = float(format(new_budget, '.2f'))

        # Create empty lists to store all data for each month of the year for each agent
        if year != 0:
            government.revenue.append([0] * 12) # unlike yearly budget, revenue is calculated monthly
            government.funds.append([0] * 12)

            for household in households:
                household.net_income.append([0] * 12)
                household.expenses.append([0] * 12)

            for company in companies:
                company.profit.append([0] * 12)
                company.net_investments.append([0] * 12)
                company.expenses.append([0]  * 12)

            commercial_banks[0].deposits.append([0] * 12)

        # Companies borrow money yearly
        for company in companies:
            borrowed_amount = commercial_banks[0].make_loan(company.name, random.uniform(1000, 2000), year, 0)
            company.loan_amount += borrowed_amount

        for month in range(12):

            tax_rate = 0.25
            # Government spends money; 5% of budget reserved to further emphasis sustainable debt / emergencies
            monthly_gov_budget = government.budget[year] * 0.95 / 12 
            
            # a household is employed by government
            monthly_gov_budget -= gov_wage
            households[0].net_income[year][month] += gov_wage

            # random government expenses
            gov_purchases = random.uniform(800, 1200)
            # inflation calculation
            if year != 0:
                gov_purchases *= 1.06 ** (year)

            shock_function = None

            if determine_if_shock():
                shock_function = choose_shock() 
                shock_duration = shock_function(reserve_bank, government, households, companies, commercial_banks, years, year, month)
                shocks.append((shock_function, shock_duration))

            if shock_function == boom:
                print("Begin of economic boom in year", year, "month", month + 1, "for", shock_duration, "months", '\n')
                gov_budget_multiplier = 1.7
                interest_rate_multiplier = 0.8
                productivity_factor = 0.05
                tax_rate_factor = -0.1
            elif shock_function == recession:
                print("Begin of economic recession in year", year, "month", month + 1, "for", shock_duration, "months", '\n')            
                gov_budget_multiplier = 0.5
                interest_rate_multiplier = 1.8
                productivity_factor = -0.1
                tax_rate_factor = 0.1
                unemployment_factor = 0.2
            elif shock_function == policy_intervention:
                print("Policy changed in year", year, "month", month + 1, "for", shock_duration, "months", '\n')
                gov_budget_multiplier = 1.7
                interest_rate_multiplier = 0.6
                tax_rate_factor = -0.15
            elif shock_function == natural_disaster:
                print("Large scale natural disaster ocurred in year", year, "month", month + 1, "for", shock_duration, "months", '\n')
                gov_expense_multiplier = 2    # infrastructure
                productivity_factor = -0.3
                household_expense_multiplier = 1.5
                company_expense_multiplier = 1.8
            else:
                gov_budget_multiplier = 1
                interest_rate_multiplier = 1
                productivity_factor = 0
                tax_rate_factor = 0                
                unemployment_factor = 0
                gov_expense_multiplier = 1
                household_expense_multiplier = 1
                company_expense_multiplier = 1

            if shock_function == change_confidence_level:
                print("Company confidence changed in year", year, "month", month + 1, "for", shock_duration, "months", '\n')
            if shock_function == change_consumer_confidence:
                print("Consumer confidence changed in year", year, "month", month + 1, "for", shock_duration, "months", '\n')
            if shock_function == expectations:
                print("Expectations changed in year", year, "month", month + 1, "for", shock_duration, "months", '\n')

            for shock, duration in shocks:
                if duration > 0:
                    new_interest_rate *= interest_rate_multiplier

                    government.budget[year] *= gov_budget_multiplier
                    gov_purchases *= gov_expense_multiplier

                    if shock_function in {expectations, change_confidence_level, change_consumer_confidence}:
                        temp_val = shock_function(reserve_bank, government, households, companies, commercial_banks, years, year, month)

            # government contracts companies for services
            monthly_gov_budget -= gov_purchases
            companies[0].profit[year][month] = gov_purchases

            for shock, duration in shocks:
                if duration > 0:
                    for company in companies:
                        company.profit[year][month] *= (1 + productivity_factor)

            government.funds[year][month] = monthly_gov_budget

            # for household employed by company
            companies[0].profit[year][month] -= company_wage
            households[1].net_income[year][month] += company_wage

            for shock, duration in shocks:
                if duration > 0:
                    for household in households:
                        household.net_income[year][month] *= (1 - unemployment_factor)

            # Government collects taxes
            for household in households:
                tax_amount = household.net_income[year][month] * (tax_rate + tax_rate_factor)
                household.net_income[year][month] -= tax_amount
                government.revenue[year][month] += tax_amount

            for company in companies:
                tax_amount = company.profit[year][month] * (tax_rate + 0.06 + tax_rate_factor)
                company.profit[year][month] -= tax_amount
                government.revenue[year][month] += tax_amount  

            # Monthly activities
            for household in households:
                # pay back loans
                payback_amount = household.loan_amount * 0.02
                payback_loan(household, payback_amount, commercial_banks[0])

                # expenses
                household.expenses[year][month] = household.net_income[year][month] * random.uniform(0.4, 0.7)

            for shock, duration in shocks:
                if duration > 0:
                    household.expenses[year][month] *= household_expense_multiplier

                companies[0].profit[year][month] +=  household.expenses[year][month] * 0.15
                government.revenue[year][month] +=  household.expenses[year][month] * 0.4
                household.net_income[year][month] = household.net_income[year][month] - household.expenses[year][month] - payback_amount

                if  household.net_income[year][month] > 0:
                    # savings
                    household_month_savings = household.net_income[year][month] * household.savings_rate
                    household.savings += household_month_savings
                    household.net_income[year][month] -= household_month_savings

                    # investments
                    stock_investment_amount = household.net_income[year][month] * 0.3  # 30% of income invested in stock market
                    household.invest_in_stock_market(stock_investment_amount)

                    # deposit ALL remaining money
                    commercial_banks[0].make_deposit(household, household.net_income[year][month], year, month)

            for company in companies:
                # pay back loans
                payback_amount = company.loan_amount * 0.07
                payback_loan(company, payback_amount, commercial_banks[0])

                # expenses
                company.expenses[year][month] = company.profit[year][month] * random.uniform(0.3, 0.5)

            for shock, duration in shocks:
                if duration > 0:
                    company.expenses[year][month] *= company_expense_multiplier
                    duration -= 1
                else:
                    shocks.remove((shock, duration))

                government.revenue[year][month] += company.expenses[year][month] * 0.5 
                company.profit[year][month] = company.profit[year][month] - company.expenses[year][month] - payback_amount

                if company.profit[year][month] > 0:
                    # investments
                    rd_investment_amount = company.profit[year][month] * 0.1  # 10% of profit invested in R&D
                    company.invest_in_rd(rd_investment_amount, year, month)

                    cap_amount = company.profit[year][month] * 0.2  # 20% of profit invested in capital expenditures
                    company.invest_capital_expenditure(cap_amount, year, month)

                    company.net_investments[year][month] = rd_investment_amount + cap_amount

                    # deposit ALL remaining money
                    commercial_banks[0].make_deposit(company, company.profit[year][month], year, month)

            # Update loan amounts
            update_loans(households, companies, commercial_banks, year, month)

        interest_rate = new_interest_rate
        # pay raises
        gov_wage *= 1.09
        company_wage *= 1.07

    # # Plot GDP over time
    gdp_values = [calculate_gdp(households, companies, government, year) for year in range(years)]
    plt.plot(range(1, years+1), gdp_values)
    plt.xlabel("Year")
    plt.ylabel("GDP")
    plt.title("GDP Over Time")
    plt.show()

# Initialize the economy with small numbers chosen for convenience
reserve_bank = ReserveBank("Central Bank", 20000)
government = Government("Government", 5000)
households = [Household("Household 1", 0.1, 400), Household("Household 2", 0.2, 600)]
companies = [Company("Company 1", 2000, 0.5)]
commercial_banks = [CommercialBank("Commercial Bank", 10000, reserve_bank)]

# Simulate the economy
simulate_economy(reserve_bank, government, households, companies, commercial_banks, period)