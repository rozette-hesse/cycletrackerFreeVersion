import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="Cycle Tracker", layout="centered")

# --- Helper Class ---
class CyclePredictor:
    def __init__(self, period_ranges):
        self.period_ranges = sorted(period_ranges, key=lambda x: x[0])
        self.period_start_dates = [start for start, _ in self.period_ranges]
        self.cycle_lengths = self._calculate_cycle_lengths()

    def _calculate_cycle_lengths(self):
        return [
            (self.period_start_dates[i + 1] - self.period_start_dates[i]).days
            for i in range(len(self.period_start_dates) - 1)
        ] if len(self.period_start_dates) > 1 else []

    def predict_next_period(self):
        if len(self.period_start_dates) < 2:
            return {"error": "Log at least 2 periods to predict."}

        last_period_start = self.period_start_dates[-1]
        prev_period_start = self.period_start_dates[-2]
        last_cycle_length = (last_period_start - prev_period_start).days
        predicted_start = last_period_start + timedelta(days=last_cycle_length)

        prediction_range = [
            (predicted_start - timedelta(days=2)).strftime("%Y-%m-%d"),
            (predicted_start + timedelta(days=2)).strftime("%Y-%m-%d")
        ]

        return {
            "predicted_start_date": predicted_start.strftime("%Y-%m-%d"),
            "range": prediction_range,
            "confidence": "Moderate",
            "based_on": "last known cycle length"
        }

    def get_current_phase(self, current_date=None):
        if not self.period_start_dates:
            return "Insufficient data"

        if not current_date:
            current_date = datetime.today()
        else:
            current_date = datetime.strptime(current_date, "%Y-%m-%d")

        last_start = self.period_start_dates[-1]
        days_since_last_period = (current_date - last_start).days

        if days_since_last_period < 0:
            return "Invalid date: before last period"

        if days_since_last_period <= 5:
            return f"Cycle Day {days_since_last_period + 1} — Menstrual Phase"
        elif days_since_last_period <= 12:
            return f"Cycle Day {days_since_last_period + 1} — Follicular Phase"
        elif days_since_last_period <= 15:
            return f"Cycle Day {days_since_last_period + 1} — Ovulatory Phase"
        else:
            return f"Cycle Day {days_since_last_period + 1} — Luteal Phase"

    def get_ovulation_and_fertility_window(self):
        if len(self.period_start_dates) < 2:
            return {"error": "Log at least 2 periods to calculate ovulation."}

        last_period_start = self.period_start_dates[-1]
        prev_period_start = self.period_start_dates[-2]
        last_cycle_length = (last_period_start - prev_period_start).days

        ovulation_day = last_period_start + timedelta(days=last_cycle_length - 14)
        fertile_start = ovulation_day - timedelta(days=5)
        fertile_end = ovulation_day + timedelta(days=1)  # include day after ovulation

        return {
            "ovulation_day": ovulation_day.strftime("%Y-%m-%d"),
            "fertile_window": [
                fertile_start.strftime("%Y-%m-%d"),
                fertile_end.strftime("%Y-%m-%d")
            ]
        }

# --- Streamlit App ---
st.title("Menstrual Cycle Tracker — Free Version")

num_periods = st.number_input("How many past periods would y
