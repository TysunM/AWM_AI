        symbol=TARGET_ASSET,
        qty=TRADE_QTY,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY
    )

    try:
        trade_client.submit_order(order_data=order_data)
        print("✅ Trade executed successfully on paper uplink.\n")
    except Exception as e:
        print(f"❌ Execution failed: {e}\n")

# --- THE MAIN EXECUTION LOOP ---
while True:
    try:
        # 1. Calculate the statistical baseline
        essence_price, volatility = get_true_essence()

        # We define a "panic drop" as the price falling 2 standard deviations below the mean
        panic_threshold = essence_price - (volatility * 2)

        # 2. Read the microsecond live price from Redis (populated by your other terminal)
        live_price_str = r.get(f"live_price:{TARGET_ASSET}")

        if live_price_str is None:
            print("Awaiting live data stream in Redis...")
            time.sleep(5)
            continue

        live_price = float(live_price_str)

        # 3. Output the state
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Live: ${live_price:.2f} | Essence: ${essence_price:.2f} | Buy Threshold: ${panic_threshold:.2f}")

        # 4. The Trigger Logic
        if live_price < panic_threshold:
            reason = f"Live price (${live_price:.2f}) dropped below panic threshold (${panic_threshold:.2f})"
            execute_trade(live_price, reason)

            # Sleep for 5 minutes after a buy to prevent spamming orders during a crash
            print("System cooling down for 5 minutes to let the reaction settle...")
            time.sleep(300)
        else:
            # Check again in 10 seconds
            time.sleep(10)

    except Exception as e:
        print(f"Loop Error: {e}")
        time.sleep(10)