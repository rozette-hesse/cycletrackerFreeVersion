from datetime import datetime, timedelta
import streamlit as st

class CyclePredictor:
    def __init__(self, period_ranges):
        # Sort ranges by start date
        self.period_ranges = sorted(period_ranges, key=lambda x: x[0])
        self.period_dates = [start for start, end in self.period_ranges]
        self.cycle_lengths = self._calculate_cycle_lengths()

    def _calculate_cycle_lengths(self):
        return [
            (self.period_dates[i+1] - self.period_dates[i]).days
            for i in range(len(self.period_dates) - 1)
        ] if len(self.period_dates) > 1 else []

    def predict_next_period(self):
        if len(self.period_dates) < 2:
            return {
                "error": "Not enough data. Please log at least 2 cycles."
            }

        last_period_start = self.period_dates[-1]
        prev_period_start = self.period_dates[-2]
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
        if len(self.period_dates) < 1:
            return "Insufficient data"

        if not current_date:
            current_date = datetime.today()

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

# Streamlit app
st.title("Cycle Predictor")

st.write("Log your recent period start and end dates below:")

period_ranges = []

for i in range(1, 6):
    st.markdown(f"### Period #{i}")
    start = st.date_input(f"Start Date {i}", key=f"start_{i}")
    end = st.date_input(f"End Date {i}", key=f"end_{i}")
    if start and end:
        start_dt = datetime.combine(min(start, end), datetime.min.time())
        end_dt = datetime.combine(max(start, end), datetime.min.time())
        period_ranges.append((start_dt, end_dt))

if len(period_ranges) >= 2:
    predictor = CyclePredictor(period_ranges)
    prediction = predictor.predict_next_period()
    today = datetime.today()
    phase = predictor.get_current_phase(today)

    st.subheader("Prediction Result")
    st.write(f"**Predicted Next Period:** {prediction.get('predicted_start_date')}")
    st.write(f"**Range:** {prediction.get('range')}")
    st.write(f"**Confidence:** {prediction.get('confidence')}")
    st.write(f"**Based on:** {prediction.get('based_on')}")

    st.subheader("Current Phase")
    st.write(f"**Today:** {today.strftime('%Y-%m-%d')} — {phase}")
else:
    st.warning("Please enter at least two period start and end date pairs to generate predictions.")
