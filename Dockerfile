FROM python:3.9-slim

# Install Firefox, dependencies
RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg2 firefox-esr xvfb && \
    rm -rf /var/lib/apt/lists/*

# Install geckodriver
RUN GECKODRIVER_VERSION=0.35.0 && \
    wget "https://github.com/mozilla/geckodriver/releases/download/v$GECKODRIVER_VERSION/geckodriver-v$GECKODRIVER_VERSION-linux64.tar.gz" && \
    tar -xzf geckodriver-v$GECKODRIVER_VERSION-linux64.tar.gz -C /usr/local/bin && \
    chmod +x /usr/local/bin/geckodriver && \
    rm geckodriver-v$GECKODRIVER_VERSION-linux64.tar.gz

# Copy app code
WORKDIR /app
COPY . /app

# Install Python dependencies
RUN pip install -r requirements.txt

# Use virtual display (for headless Firefox)
ENV DISPLAY=:99

# Run Streamlit app with virtual display
CMD bash -c "rm -f /tmp/.X99-lock && Xvfb :99 -screen 0 1024x768x16 & streamlit run app.py --server.port=8080 --server.enableCORS=true"

