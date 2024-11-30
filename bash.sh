#!/bin/bash

# Run backend.py with Python 3.11
echo "Starting backend server..."
python3.11 backend.py &

# Save the backend PID
BACKEND_PID=$!

# Run main.py with Streamlit
echo "Starting Streamlit app..."
streamlit run main.py

# Stop backend server when Streamlit exits
echo "Stopping backend server..."
kill $BACKEND_PID
