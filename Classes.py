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