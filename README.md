# Currency & Purchase Assistant

A responsive Flask web version of the Currency Converter and Purchase Cost Estimator desktop app. It includes the same 11 currencies, rate fallback, conversion calculation, purchase breakdown, and budget comparison.

## Run locally

1. Install Python 3.9 or newer.
2. In a terminal, change to this folder:

   ```powershell
   cd "C:\path\to\Currency-Converter-master"
   ```

3. Create and activate a virtual environment (recommended):

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Install Flask:

   ```powershell
   pip install -r requirements.txt
   ```

5. Start the web app:

   ```powershell
   python app.py
   ```

6. Open the local address printed in the terminal, usually `http://127.0.0.1:5000`.

## Features

- Convert between USD, INR, EUR, GBP, JPY, AUD, CAD, SGD, AED, CHF, and CNY. The app tries to load current rates from the existing USD-based rate endpoint and uses the desktop app's built-in rates when the request fails. The status at the top of the page indicates which rates are in use.
- Estimate purchase price, shipping, tax, and payment fees, then compare the total with your budget. Tax and payment fees are calculated on product price plus shipping, matching the original application.
- Use the swap control to exchange the selected currencies. The layout adapts to mobile and desktop screens.
- Review up to 10 recent conversions in the converter history. History is saved in this browser only and can be cleared with the **Clear** button.

Exchange rates are indicative and may differ from the rate offered by your bank or provider. An internet connection is only needed to retrieve live rates.

## Tests

Run the focused application tests with:

```powershell
python -m unittest discover -s tests
```
