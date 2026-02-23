import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# Load data
data = pd.read_csv("data/weather_history.csv")

if len(data) < 10:
    print("⚠ Not enough data. Collect more weather history.")
    exit()

values = data[["temp","humidity","rainfall"]].values

# Normalize
scaler = MinMaxScaler()
scaled = scaler.fit_transform(values)

# Create sequences
X, y = [], []
seq_len = 5

for i in range(seq_len, len(scaled)):
    X.append(scaled[i-seq_len:i])
    y.append(scaled[i,2])  # rainfall target

X, y = np.array(X), np.array(y)

# Build model
model = Sequential()
model.add(LSTM(32, return_sequences=True, input_shape=(seq_len,3)))
model.add(LSTM(32))
model.add(Dense(1))

model.compile(optimizer="adam", loss="mse")

model.fit(X, y, epochs=8, verbose=0)

print("✅ LSTM trained")

# Predict next rainfall
last_seq = np.expand_dims(scaled[-seq_len:], axis=0)
pred = model.predict(last_seq, verbose=0)

predicted_rain = float(pred[0][0]) * 10

# Save prediction
with open("predicted_rain.txt","w") as f:
    f.write(str(round(predicted_rain,2)))

print(f"🌧 Predicted Rainfall: {round(predicted_rain,2)} mm")
