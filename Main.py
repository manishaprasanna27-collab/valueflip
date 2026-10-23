import json
import math
import tkinter as tk
from http.client import HTTPException
from tkinter import messagebox, ttk
from urllib.request import urlopen


class CurrencyPurchaseAssistant(tk.Tk):
    CURRENCIES = (
        "USD", "INR", "EUR", "GBP", "JPY", "AUD",
        "CAD", "SGD", "AED", "CHF", "CNY",
    )

    # Static rates expressed as units of each currency per one US dollar.
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

    def __init__(self):
        super().__init__()
        self.title("Currency Converter")
        self.geometry("600x540")
        self.minsize(600, 540)
        self.rates_per_usd = self.fetch_latest_rates()

        self.configure(bg="#eef2f6")
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure(".", background="#eef2f6", foreground="#243247")
        self.style.configure("TFrame", background="#eef2f6")
        self.style.configure("TLabel", background="#eef2f6", font=("Segoe UI", 10))
        self.style.configure(
            "Header.TLabel",
            background="#eef2f6",
            foreground="#142b4a",
            font=("Segoe UI", 18, "bold"),
        )
        self.style.configure(
            "Section.TLabel",
            background="#eef2f6",
            foreground="#142b4a",
            font=("Segoe UI", 13, "bold"),
        )
        self.style.configure(
            "TLabelframe",
            background="#f8fafc",
            bordercolor="#cbd5e1",
            relief="solid",
        )
        self.style.configure(
            "TLabelframe.Label",
            background="#f8fafc",
            foreground="#142b4a",
            font=("Segoe UI", 11, "bold"),
        )
        self.style.configure(
            "TButton",
            background="#1e4775",
            foreground="white",
            font=("Segoe UI", 10, "bold"),
            padding=(10, 7),
        )
        self.style.map(
            "TButton",
            background=[("active", "#2d5d91"), ("pressed", "#163657")],
            foreground=[("disabled", "#d1d5db")],
        )
        self.style.configure("TNotebook", background="#eef2f6", borderwidth=0)
        self.style.configure(
            "TNotebook.Tab",
            background="#dce5ef",
            foreground="#243247",
            padding=(14, 8),
            font=("Segoe UI", 10, "bold"),
        )
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", "#f8fafc")],
            foreground=[("selected", "#142b4a")],
        )

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=12)

        self.home_tab = ttk.Frame(self.notebook, padding=18)
        self.converter_tab = ttk.Frame(self.notebook, padding=22)
        self.estimator_tab = ttk.Frame(self.notebook, padding=18)
        self.notebook.add(self.home_tab, text="Home")
        self.notebook.add(self.converter_tab, text="Currency Converter")
        self.notebook.add(self.estimator_tab, text="Purchase Cost Estimator")

        self.create_home_tab()
        self.create_converter_tab()
        self.create_estimator_tab()

    def create_home_tab(self):
        tab = self.home_tab
        ttk.Label(
            tab,
            text="Welcome to International Currency\n& Purchase Assistant",
            style="Header.TLabel",
            justify="center",
        ).pack(pady=(18, 8))
        ttk.Label(
            tab,
            text="Convert currencies and estimate the full cost of an international purchase.",
            justify="center",
            wraplength=510,
        ).pack(pady=(0, 26))

        cards = ttk.Frame(tab)
        cards.pack(fill="x", expand=True)
        cards.columnconfigure(0, weight=1, uniform="cards")
        cards.columnconfigure(1, weight=1, uniform="cards")

        converter_card = ttk.LabelFrame(
            cards, text="Currency Converter", padding=14
        )
        converter_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ttk.Label(
            converter_card,
            text="Convert amounts between seven commonly used currencies.",
            wraplength=210,
            justify="left",
        ).pack(anchor="w", pady=(5, 16))
        ttk.Button(
            converter_card,
            text="Open Currency Converter",
            command=lambda: self.notebook.select(self.converter_tab),
        ).pack(anchor="w")

        estimator_card = ttk.LabelFrame(
            cards, text="Purchase Cost Estimator", padding=14
        )
        estimator_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        ttk.Label(
            estimator_card,
            text="Estimate tax, payment fees, total cost, and budget status.",
            wraplength=210,
            justify="left",
        ).pack(anchor="w", pady=(5, 16))
        ttk.Button(
            estimator_card,
            text="Open Cost Estimator",
            command=lambda: self.notebook.select(self.estimator_tab),
        ).pack(anchor="w")

        ttk.Label(
            tab,
            text="Choose a tab above, enter your values, then select the action button.",
            justify="center",
            wraplength=510,
        ).pack(side="bottom", pady=(22, 4))

    def create_converter_tab(self):
        tab = self.converter_tab
        ttk.Label(
            tab, text="Currency Converter", style="Section.TLabel"
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(8, 18))

        tab.columnconfigure(1, weight=1)
        self.amount_var = tk.StringVar(value="1")
        self.from_currency_var = tk.StringVar(value="USD")
        self.to_currency_var = tk.StringVar(value="EUR")

        self.add_form_row(tab, 1, "Amount:", self.amount_var)

        ttk.Label(tab, text="From Currency:").grid(
            row=2, column=0, sticky="w", padx=(0, 16), pady=8
        )
        from_box = ttk.Combobox(
            tab,
            textvariable=self.from_currency_var,
            values=self.CURRENCIES,
            state="readonly",
            width=24,
        )
        from_box.grid(row=2, column=1, sticky="ew", pady=8)

        ttk.Label(tab, text="To Currency:").grid(
            row=3, column=0, sticky="w", padx=(0, 16), pady=8
        )
        to_box = ttk.Combobox(
            tab,
            textvariable=self.to_currency_var,
            values=self.CURRENCIES,
            state="readonly",
            width=24,
        )
        to_box.grid(row=3, column=1, sticky="ew", pady=8)

        ttk.Button(tab, text="Convert", command=self.convert_currency).grid(
            row=4, column=0, columnspan=2, pady=(8, 14)
        )
        self.conversion_result = ttk.Label(
            tab, text="Enter an amount and select Convert.", style="Section.TLabel"
        )
        self.conversion_result.grid(
            row=5, column=0, columnspan=2, sticky="w", pady=8
        )

    def create_estimator_tab(self):
        tab = self.estimator_tab
        ttk.Label(
            tab,
            text="International Purchase Cost Estimator",
            style="Section.TLabel",
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(4, 10))
        ttk.Label(
            tab,
            text="Example values are provided; replace them with your purchase details.",
            wraplength=520,
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 8))

        tab.columnconfigure(1, weight=1)
        examples = (
            ("Product Price:", "100"),
            ("Shipping Cost:", "20"),
            ("Tax Rate (%):", "30"),
            ("Payment Fee (%):", "40"),
            ("Your Budget:", "50"),
        )
        self.estimator_entries = {}
        for row, (label, value) in enumerate(examples, start=2):
            variable = tk.StringVar(value=value)
            self.estimator_entries[label] = variable
            self.add_form_row(tab, row, label, variable)

        ttk.Button(
            tab, text="Calculate Total Cost", command=self.calculate_total_cost
        ).grid(row=7, column=0, columnspan=2, pady=(10, 10))
        self.cost_result = ttk.Label(
            tab,
            text="Select Calculate Total Cost to view the estimate.",
            justify="left",
            wraplength=520,
        )
        self.cost_result.grid(
            row=8, column=0, columnspan=2, sticky="w", pady=(4, 0)
        )

    @staticmethod
    def add_form_row(parent, row, label_text, variable):
        ttk.Label(parent, text=label_text).grid(
            row=row, column=0, sticky="w", padx=(0, 16), pady=8
        )
        entry = ttk.Entry(parent, textvariable=variable)
        entry.grid(row=row, column=1, sticky="ew", pady=8)
        return entry

    @classmethod
    def fetch_latest_rates(cls):
        try:
            with urlopen(cls.RATES_URL, timeout=2) as response:
                data = json.load(response)
            live_rates = data["rates"]
            rates = {
                currency: float(live_rates[currency])
                for currency in cls.CURRENCIES
            }
            if data.get("result") != "success" or any(
                not math.isfinite(rate) or rate <= 0
                for rate in rates.values()
            ):
                raise ValueError("Exchange-rate response is invalid")
            return rates
        except (HTTPException, OSError, ValueError, KeyError, TypeError):
            return cls.RATES_PER_USD.copy()

    def convert_currency(self):
        try:
            amount = self.parse_finite_number(self.amount_var.get())
            from_currency = self.from_currency_var.get()
            to_currency = self.to_currency_var.get()
            if amount < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Enter a valid non-negative amount.",
                parent=self,
            )
            return

        converted = amount * (
            self.rates_per_usd[to_currency] / self.rates_per_usd[from_currency]
        )
        self.conversion_result.config(
            text=(
                f"{amount:,.2f} {from_currency} = "
                f"{converted:,.2f} {to_currency}"
            )
        )

    def calculate_total_cost(self):
        try:
            values = {
                label: self.parse_finite_number(variable.get())
                for label, variable in self.estimator_entries.items()
            }
            price = values["Product Price:"]
            shipping = values["Shipping Cost:"]
            tax_rate = values["Tax Rate (%):"]
            fee_rate = values["Payment Fee (%):"]
            budget = values["Your Budget:"]

            if min(price, shipping, budget) < 0:
                raise ValueError
            if not 0 <= tax_rate <= 100 or not 0 <= fee_rate <= 100:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Enter valid numbers in every field. Costs and budget must "
                "be non-negative, and percentage rates must be from 0 to 100.",
                parent=self,
            )
            return

        subtotal = price + shipping
        tax = subtotal * tax_rate / 100
        payment_fee = subtotal * fee_rate / 100
        total = subtotal + tax + payment_fee
        result = (
            f"Product price: {price:.2f}\n"
            f"Shipping: {shipping:.2f}\n"
            f"Estimated tax: {tax:.2f}\n"
            f"Payment fee: {payment_fee:.2f}\n"
            f"Estimated total: {total:.2f}\n"
        )
        if total > budget:
            result += f"\nBUDGET ALERT! Over budget by {total - budget:.2f}"
        else:
            result += f"\nWithin budget! Remaining budget: {budget - total:.2f}"
        self.cost_result.config(text=result)

    @staticmethod
    def parse_finite_number(text):
        number = float(text.strip())
        if not math.isfinite(number):
            raise ValueError
        return number


if __name__ == "__main__":
    app = CurrencyPurchaseAssistant()
    app.mainloop()
