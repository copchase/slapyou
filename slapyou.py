from typing import Union
import random
import dynamodb_api
import emote

# How can she slap?


CURRENCY_NAME = {
    "30080840": "OddCoin",
    "63560156": "gold"
}

def slap(caller_info: dict, target_info: dict, channel_id: str) -> list:
    output_str = []

    caller_name = caller_info["displayName"]
    caller_id = caller_info["providerId"]
    target_name = target_info["displayName"]
    target_id = target_info["providerId"]

    caller_obj = dynamodb_api.get_item(caller_id)
    target_obj = None

    caller_currency = get_user_currency(caller_obj, channel_id)
    critical = roll(0.0625)

    if roll(get_chance_from_currency(caller_currency)):
        target_obj = dynamodb_api.get_item(target_info)
        stolen_amount = steal(caller_obj, target_obj, channel_id, critical)
        if critical:
            output_str.append(f"""{caller_name} slaps {target_name} and critically hits, gaining {stolen_amount} {CURRENCY_NAME.get(channel_id, "EXP")} {emote.get_positive_emote()}!""")
        else:
            output_str.append(f"""{caller_name} slaps {target_name} and gains {stolen_amount} {CURRENCY_NAME.get(channel_id, "EXP")}!""")
    elif critical:
        output_str.append(f"""{caller_name} slaps themselves in confusion, losing all but one {CURRENCY_NAME.get(channel_id, "EXP")}! {emote.get_negative_emote()}""")
        set_user_currency(caller_obj, channel_id, 1)
    else:
        loss_amount = steal(None, caller_obj, channel_id, False)
        output_str.append(f"""{caller_name} fails to slap {target_name} and loses {loss_amount} {CURRENCY_NAME.get(channel_id, "EXP")}!""")

    return output_str


def steal(caller_obj: dict, target_obj: dict, channel_id: str, critical: bool) -> int:
    target_currency = get_user_currency(target_obj, channel_id)
    percentage = random.uniform(0.05 + critical * 0.245, 0.35 + critical * 0.35)
    stolen_amount = max(1, round(percentage * target_currency))
    return stolen_amount


def get_user_currency(user_obj: dict, channel_id: str) -> int:
    return user_obj.get("currency", {}).get(channel_id, 1)


def set_user_currency(user_obj: dict, channel_id: str, currency: int) -> None:
    if "currency" not in user_obj:
        user_obj["currency"] = {}

    user_obj["currency"][channel_id] = currency


def get_chance_from_currency(currency: int) -> float:
    a = 0.333 # Increase to elevate rate of failure growth
    # 0.333 means failure is close to 100% around 1 million currency
    b = 0.0 # Increase to reduce fail rate for all people
    c = -20.0  # Increase to move function towards third quadrant
    # aka increases the "poor person threshold from 1 to 5"
    d = 0.0  # Increase to give more fail chance for poor people
    x = float(currency)
    chance = ((x**a - c) + (d / (x - c))) - b
    return 1 - (chance / 100)


def roll(chance: Union[float, str]) -> bool:
    return random.random() < chance