import pandas as pd
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

# Load your CSV
df = pd.read_csv('student_data.csv')

# Select features (simpler but effective)
features = ['studytime', 'failures', 'absences', 'G1', 'G2']
X = df[features]
y = df['G3']

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = LinearRegression()
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print(f"MAE: {mean_absolute_error(y_test, y_pred):.2f}")

# Save model
joblib.dump(model, 'student_model.pkl')
print("Model saved as student_model.pkl")