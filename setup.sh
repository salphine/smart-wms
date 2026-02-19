mkdir -p ~/.streamlit/
echo "\
[general]\n\
email = \"salphine@example.com\"\n\
" > ~/.streamlit/credentials.toml
echo "\
[server]\n\
headless = true\n\
enableCORS = false\n\
port = \\n\
" > ~/.streamlit/config.toml
