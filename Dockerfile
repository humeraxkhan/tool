FROM python:3.9-slim

# Install Firefox and dependencies
RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg2 firefox-esr xvfb && \
    rm -rf /var/lib/apt/lists/*

# Install geckodriver
ARG GECKODRIVER_VERSION=0.35.0
RUN wget "https://github.com/mozilla/geckodriver/releases/download/v${GECKODRIVER_VERSION}/geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz" && \
    tar -xzf geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz -C /usr/local/bin && \
    chmod +x /usr/local/bin/geckodriver && \
    rm geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz

# Set working directory
WORKDIR /app

# Copy app files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set virtual display environment variable
ENV DISPLAY=:99

# Run Streamlit with virtual display
CMD bash -c "rm -f /tmp/.X99-lock && Xvfb :99 -screen 0 1024x768x16 & streamlit run app.py --server.port=8080 --server.enableCORS=true"

