docker run -it -v "F:/Kursmaterial/AdvancedHCI/scalabel/scalabel/local-data:/opt/scalabel/local-data" -p 8686:8686 -p 6379:6379 scalabel/www node app/dist/main.js --config app/config/default_config.yml --max-old-space-size=8192