from datetime import datetime, timedelta
import streamlit as st

# --- Cycle Predictor Class ---
class CyclePredictor:
    def __init__(self, period_ranges):
        # Sort dates and ensure each pair is in correct order
        self.period_ranges = sorted([
            (min(start, end), max(start, end)) for start, end in period_ranges if start and end
        ], key=lambda x: x[0])
        self.period_dates = [start for start, end in self.period_ranges]

    def _calculate_cycle_lengths(self):
        return [
            (self.period_dates[i+1] - self.period_dates[i]).days
            for i in range(len(self.period_dates) - 1)
        ]

    def predict_next_period(self):
        if len(self.period_dates) < 2:
            return {"error": "Please enter at least two complete periods (start + end)."}

        cycle_lengths = self._calculate_cycle_lengths()
        avg_cycle_length = sum(cycle_lengths) / len(cycle_lengths)
        last_period_start = self.period_dates[-1]
        predicted_start = last_period_start + timedelta(days=round(avg_cycle_length))

        prediction_range = [
            (predicted_start - timedelta(days=2)).strftime("%Y-%m-%d"),
            (predicted_start + timedelta(days=2)).strftime("%Y-%m-%d")
        ]

        return {
            "predicted_start_date": predicted_start.strftime("%Y-%m-%d"),
            "range": prediction_range,
            "confidence": "Moderate",
            "based_on": f"average of {len(cycle_lengths)} cycle(s)"
        }

    def get_current_phase(self, current_date=None):
        if len(self.period_dates) < 1:
            return "Insufficient data"

        if not current_date:
            current_date = datetime.today()
        else:
            current_date = datetime.strptime(current_date, "%Y-%m-%d")

        last_start = self.period_dates[-1]
        days_since_last_period = (current_date - last_start).days

        if days_since_last_period < 0:
            return "Invalid current date: before last period logged"

        if days_since_last_period <= 5:
            return f"Cycle Day {days_since_last_period + 1} — Menstrual Phase"
        elif days_since_last_period <= 12:
            return f"Cycle Day {days_since_last_period + 1} — Follicular Phase"
        elif days_since_last_period <= 15:
            return f"Cycle Day {days_since_last_period + 1} — Ovulatory Phase"
        else:
            return f"Cycle Day {days_since_last_period + 1} — Luteal Phase"

# --- Streamlit GUI ---
st.set_page_config(page_title="Cycle Tracker", layout="centered")
st.title("🩸 Menstrual Cycle Predictor — Free Version")

st.markdown("Enter at least two period start and end dates to get a prediction.")

num_periods = st.number_input("How many past periods would you like to log?", min_value=2, max_value=12, value=4, step=1)
period_ranges = []

for i in range(num_periods):
    st.markdown(f"### Period #{i+1}")
    col1, col2 = st.columns(2)
    with col1:
        start = st.date_input(f"Start Date {i+1}", key=f"start_{i}", value=None)
    with col2:
        end = st.date_input(f"End Date {i+1}", key=f"end_{i}", value=None)
    period_ranges.append((start, end))

if st.button("Predict Next Period"):
    predictor = CyclePredictor(period_ranges)
    result = predictor.predict_next_period()

    if "error" in result:
        st.error(result["error"])
    else:
        st.success(f"**Predicted Start Date:** {result['predicted_start_date']}")
        st.write(f"**Prediction Range:** {result['range'][0]} to {result['range'][1]}")
        st.caption(f"Confidence: {result['confidence']} — Based on {result['based_on']}")

        phase_today = predictor.get_current_phase()
        st.info(f"**Today’s Phase:** {phase_today}")
