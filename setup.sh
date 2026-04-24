#!/usr/bin/env sh
mkdir -p ~/.streamlit/

cat > ~/.streamlit/config.toml <<EOF
[server]
headless = true
enableCORS = false
port = ${PORT:-8501}
EOF
