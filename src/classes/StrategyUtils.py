class StrategyUtils():
    
    @staticmethod
    def calculateMA(pricelist, days=50):
        sum = 0
        count = 0
        for i in pricelist[::-1]:
            if count >= days:
                break
            sum += i[4]
            count += 1
        return round(sum / days, 2)