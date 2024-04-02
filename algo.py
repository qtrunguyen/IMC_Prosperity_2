import collections
from datamodel import OrderDepth, TradingState, Order
from typing import List

class Trader:

    position = {'AMETHYSTS': 0, 'STARFRUIT': 0}
    POSITION_LIMIT = {'AMETHYSTS' : 40, 'STARFRUIT' : 20}
    
    def compute_orders(self, product, order_depth, acc_bid, acc_ask):
        orders: List[Order] = []

        sell_ord = collections.OrderedDict(sorted(order_depth.sell_orders.items()))
        buy_ord = collections.OrderedDict(sorted(order_depth.buy_orders.items(), reverse=True))

        cur_pos = self.position[product]

        for ask, vol in sell_ord.items():
            if ask < acc_bid and cur_pos < self.POSITION_LIMIT[product]:
                order_for = min(-vol, self.POSITION_LIMIT[product] - cur_pos)
                cur_pos += order_for
                orders.append(Order(product, ask, order_for))

        for bid, vol in buy_ord.items():
            if bid > acc_ask and cur_pos > -self.POSITION_LIMIT[product]:
                order_for = max(-vol, -self.POSITION_LIMIT[product] - cur_pos)
                cur_pos += order_for
                orders.append(Order(product, bid, order_for))

        return orders

    def run(self, state: TradingState):
        result = {}
        
        for product in state.order_depths:
            if product == 'AMETHYSTS':
                acc_bid, acc_ask = 10000, 10000 

                order_depth: OrderDepth = state.order_depths[product]
                orders: List[Order] = []
                
                orders = self.compute_orders(product, order_depth, acc_bid, acc_ask)

                result[product] = orders

        traderData = "SAMPLE"
        conversions = 1
        return result, conversions, traderData