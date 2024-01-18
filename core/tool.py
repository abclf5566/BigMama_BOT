
def calculate_trade_decision(current_position,symbol_2, btc_signal, symbol_2_signal, symbol_2_btc_signal, az, signal_threshold):
    """
    根據BTC、symbol_2和symbol_2/BTC的信號確定交易決策。
    :param current_position: 當前持倉 ('BTC', 'symbol_2', 'USDT')。
    :param btc_signal: BTC的信號。
    :param symbol_2_signal: symbol_2的信號。
    :param symbol_2_btc_signal: symbol_2/BTC交易對的信號。
    :param az: 中性區間的閾值。
    :param signal_threshold: 信號閾值。
    :return: 新的持倉位置（'BTC'、'symbol_2'或'USDT'）。
    """

    # 當前最佳收益 中性區間判斷，如果在az中性區內且兩幣種相對於USDT都下跌，則優先處理轉換為USDT
    if -az <= btc_signal <= az and -az <= symbol_2_signal <= az:
        if current_position == 'BTC' and symbol_2_btc_signal > 0:
            return f'{symbol_2}'
        elif current_position == f'{symbol_2}' and symbol_2_btc_signal < 0:
            return 'BTC'
        else:
            return current_position

    # 如果BTC和symbol_2相對於USDT的信號都小於0，則轉換為USDT
    elif btc_signal < 0 and symbol_2_signal < 0:
        return 'USDT'
    else:
        # 根據symbol_2/BTC信號進行持倉決策
        if current_position == 'BTC' and symbol_2_btc_signal > 0:
            return f'{symbol_2}'
        elif current_position == f'{symbol_2}' and symbol_2_btc_signal < 0:
            return 'BTC'
        else:
            # 根據BTC和symbol_2相對於USDT的信號差異進行決策
            if abs(btc_signal - symbol_2_signal) > signal_threshold:

                return 'BTC' if btc_signal > symbol_2_signal else f'{symbol_2}'
            else:
                return current_position
