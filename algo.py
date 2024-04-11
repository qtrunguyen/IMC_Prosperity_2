import collections
from statistics import stdev
from datamodel import OrderDepth, TradingState, Order
from typing import List

class Trader:

    position = {'AMETHYSTS': 0, 'STARFRUIT': 0}
    POSITION_LIMIT = {'AMETHYSTS' : 20, 'STARFRUIT' : 20}

    STARFRUIT_SMA = 27
    STARFRUIT_DEV = 1

    def calc_mid_price(self, order_depth):
        sell_ord = collections.OrderedDict(sorted(order_depth.sell_orders.items()))
        buy_ord = collections.OrderedDict(sorted(order_depth.buy_orders.items(), reverse=True))

        best_bid, best_ask = 0, 0
        for price, vol in sell_ord.items():
            best_bid = price
            break

        for price, vol in buy_ord.items():
            best_ask = price
            break

        return (best_bid + best_ask) / 2
    

    def compute_orders_starfruit(self, product, order_depth, acc_bid, acc_ask):
        orders: List[Order] = []

        sell_ord = collections.OrderedDict(sorted(order_depth.sell_orders.items()))
        buy_ord = collections.OrderedDict(sorted(order_depth.buy_orders.items(), reverse=True))

        cur_pos = self.position[product]

        for ask, vol in sell_ord.items():
            if (ask < acc_bid or (cur_pos < 0 and ask == acc_bid)) and cur_pos < 20:
                order_for = min(-vol, 20 - cur_pos)
                cur_pos += order_for
                orders.append(Order(product, ask, order_for))

        for bid, vol in buy_ord.items():
            if (bid > acc_ask or (cur_pos > 0 and bid == acc_ask)) and cur_pos > -20:
                order_for = max(-vol, -20 - cur_pos)
                cur_pos += order_for
                orders.append(Order(product, bid, order_for))

        self.position[product] = cur_pos

        return orders

    def run(self, state: TradingState):
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))
        result = {}
        
        starfruit_midpr_cache = []
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            if product == 'AMETHYSTS':
                spread = 1
                open_spread = 3
                start_trading = 0
                position_limit = 20
                position_spread = 15
                current_position = state.position.get(product,0)
                order_depth: OrderDepth = state.order_depths[product]
                orders: list[Order] = []
                    
                if state.timestamp >= start_trading:
                    if len(order_depth.sell_orders) > 0:
                        best_ask = min(order_depth.sell_orders.keys())
                        
                        if best_ask <= 10000-spread:
                            best_ask_volume = order_depth.sell_orders[best_ask]
                        else:
                            best_ask_volume = 0
                    else:
                        best_ask_volume = 0
                         
                    if len(order_depth.buy_orders) > 0:
                        best_bid = max(order_depth.buy_orders.keys())
                    
                        if best_bid >= 10000+spread:
                            best_bid_volume = order_depth.buy_orders[best_bid]
                        else:
                            best_bid_volume = 0 
                    else:
                        best_bid_volume = 0
                    
                    if current_position - best_ask_volume > position_limit:
                        best_ask_volume = current_position - position_limit
                        open_ask_volume = 0
                    else:
                        open_ask_volume = current_position - position_spread - best_ask_volume
                        
                    if current_position - best_bid_volume < -position_limit:
                        best_bid_volume = current_position + position_limit
                        open_bid_volume = 0
                    else:
                        open_bid_volume = current_position + position_spread - best_bid_volume
                        
                    if -open_ask_volume < 0:
                        open_ask_volume = 0         
                    if open_bid_volume < 0:
                        open_bid_volume = 0

                    if -best_ask_volume > 0:
                        orders.append(Order(product, best_ask, -best_ask_volume))
                    if -open_ask_volume > 0:
                        orders.append(Order(product, 10000 - open_spread, -open_ask_volume))

                    if best_bid_volume > 0:
                        orders.append(Order(product, best_bid, -best_bid_volume))
                    if open_bid_volume > 0:
                        orders.append(Order(product, 10000 + open_spread, -open_bid_volume))
                        
                result[product] = orders
                

            if product == "STARFRUIT":  
                cur_mid_price = self.calc_mid_price(order_depth)  
                starfruit_midpr_cache.append(cur_mid_price)       

                if len(starfruit_midpr_cache) < self.STARFRUIT_SMA:
                    # This is just random number assign for the first few timestamps that didn't have enough historial data points
                    acceptable_price = -0.00023852 * state.timestamp + 5001.4524794
                    acc_bid, acc_ask = acceptable_price, acceptable_price
   
                else:
                    mid_price_rolling = sum(starfruit_midpr_cache) / len(starfruit_midpr_cache)
                    
                    # print(f"Mid_price_rolling at {state.timestamp} is {mid_price_rolling}")

                    acc_bid = mid_price_rolling - stdev(starfruit_midpr_cache) * self.STARFRUIT_DEV
                    acc_ask = mid_price_rolling + stdev(starfruit_midpr_cache) * self.STARFRUIT_DEV
                
                    starfruit_midpr_cache.pop(0)

                orders = self.compute_orders_starfruit(product, order_depth, acc_bid, acc_ask)

                result[product] = orders

        traderData = "SAMPLE"
        conversions = 1
        return result, conversions, traderData