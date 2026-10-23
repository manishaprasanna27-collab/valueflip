import json
import math
import uuid
from http.client import HTTPException
from urllib.error import URLError
from urllib.request import urlopen

from flask import Flask, render_template, request


app = Flask(__name__)

CURRENCIES = (
    "USD", "INR", "EUR", "GBP", "JPY", "AUD",
    "CAD", "SGD", "AED", "CHF", "CNY",
)
RATES_PER_USD = {
    "USD": 1.0000,
    "INR": 94.8684,
    "EUR": 0.8914,
    "GBP": 0.7488,
    "JPY": 158.0630,
    "AUD": 1.4308,
    "CAD": 1.4049,
    "SGD": 1.2782,
    "AED": 3.6725,
    "CHF": 0.8234,
    "CNY": 6.6791,
}
RATES_URL = "https://open.er-api.com/v6/latest/USD"


def fetch_latest_rates():
    try:
        with urlopen(RATES_URL, timeout=2) as response:
            data = json.load(response)
        live_rates = data["rates"]
        rates = {currency: float(live_rates[currency]) for currency in CURRENCIES}
        if data.get("result") != "success" or any(
            not math.isfinite(rate) or rate <= 0 for rate in rates.values()
        ):
            raise ValueError("Exchange-rate response is invalid")
        return rates, True
    except (HTTPException, URLError, OSError, ValueError, KeyError, TypeError):
        return RATES_PER_USD.copy(), False


RATES, LIVE_RATES = fetch_latest_rates()


def parse_finite_number(value):
    try:
        number = float(value.strip())
    except (AttributeError, ValueError):
        raise ValueError("Enter a valid number.") from None
    if not math.isfinite(number):
        raise ValueError("Enter a finite number.")
    return number


def convert_currency(amount, from_currency, to_currency):
    if from_currency not in CURRENCIES or to_currency not in CURRENCIES:
        raise ValueError("Choose a supported currency.")
    if amount < 0:
        raise ValueError("Enter a non-negative amount.")
    converted = amount * (RATES[to_currency] / RATES[from_currency])
    if not math.isfinite(converted):
        raise ValueError("The converted amount is too large to calculate.")
    return converted


def estimate_purchase(price, shipping, tax_rate, fee_rate, budget):
    if min(price, shipping, budget) < 0:
        raise ValueError("Costs and budget must be non-negative.")
    if not 0 <= tax_rate <= 100 or not 0 <= fee_rate <= 100:
        raise ValueError("Tax and payment fee rates must be from 0 to 100.")

    subtotal = price + shipping
    tax = subtotal * tax_rate / 100
    payment_fee = subtotal * fee_rate / 100
    total = subtotal + tax + payment_fee
    if not all(math.isfinite(value) for value in (subtotal, tax, payment_fee, total)):
        raise ValueError("The estimate is too large to calculate.")
    return {
        "price": price,
        "shipping": shipping,
        "tax": tax,
        "payment_fee": payment_fee,
        "total": total,
        "budget": budget,
        "over_budget": total > budget,
        "difference": abs(budget - total),
    }


DEFAULTS = {
    "amount": "1",
    "from_currency": "USD",
    "to_currency": "EUR",
    "product_price": "100",
    "shipping_cost": "20",
    "tax_rate": "30",
    "payment_fee": "40",
    "budget": "50",
}


@app.route("/", methods=["GET", "POST"])
def index():
    values = DEFAULTS.copy()
    values.update({key: request.form[key] for key in DEFAULTS if key in request.form})
    conversion = None
    estimate = None
    error = None

    if request.method == "POST":
        action = request.form.get("action")
        try:
            if action == "convert":
                amount = parse_finite_number(values["amount"])
                try:
                    entry_id = uuid.UUID(request.form.get("entry_id", "")).hex
                except ValueError:
                    entry_id = uuid.uuid4().hex
                conversion = {
                    "amount": amount,
                    "from_currency": values["from_currency"],
                    "to_currency": values["to_currency"],
                    "result": convert_currency(
                        amount, values["from_currency"], values["to_currency"]
                    ),
                    "entry_id": entry_id,
                }
            elif action == "estimate":
                estimate = estimate_purchase(
                    *(parse_finite_number(values[key]) for key in (
                        "product_price",
                        "shipping_cost",
                        "tax_rate",
                        "payment_fee",
                        "budget",
                    ))
                )
            else:
                error = "Choose a tool and try again."
        except ValueError as exc:
            error = str(exc)
    return render_template(
        "index.html",
        currencies=CURRENCIES,
        values=values,
        conversion=conversion,
        estimate=estimate,
        error=error,
        live_rates=LIVE_RATES,
    )


if __name__ == "__main__":
    app.run()
