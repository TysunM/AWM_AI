    "consecutive_wins": 0,
    "consecutive_losses": 0,
    "total_violations": 0,
    "last_update": str(datetime.now())
}

def load_karma():
    if not os.path.exists(KARMA_FILE):
        with open(KARMA_FILE, 'w') as f:
            json.dump(DEFAULT_KARMA, f)
        return DEFAULT_KARMA
    with open(KARMA_FILE, 'r') as f:
        return json.load(f)

def save_karma(data):
    data["last_update"] = str(datetime.now())
    with open(KARMA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def apply_punishment(reason):
    karma = load_karma()
    karma["consecutive_wins"] = 0
    karma["consecutive_losses"] += 1
    karma["total_violations"] += 1

    # Escalating Punishment
    if karma["total_violations"] >= 3:
        karma["status"] = "EXILE"
        karma["conviction_multiplier"] = 0.0
    else:
        karma["status"] = "RESTRICTED"
        karma["conviction_multiplier"] = 0.5 # Cuts cap from 20% to 10%

    save_karma(karma)
    print(f"🚨 PUNISHMENT TRIGGERED: {reason} | STATUS: {karma['status']}")

def apply_reward():
    karma = load_karma()
    karma["consecutive_wins"] += 1
    karma["consecutive_losses"] = 0

    # Reward for discipline: Earn back Zen status after 3 clean sessions
    if karma["consecutive_wins"] >= 3 and karma["status"] != "ZEN":
        karma["status"] = "ZEN"
        karma["conviction_multiplier"] = 1.0
        karma["total_violations"] = max(0, karma["total_violations"] - 1)
        print(f"🌟 REWARD: STATUS RESTORED TO ZEN.")

    save_karma(karma)