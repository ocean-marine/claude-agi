#!/bin/bash

# Nintendo stock price research script
echo "=== Nintendo Stock Price Research ==="
echo "Date: $(date '+%Y-%m-%d %H:%M:%S JST')"
echo ""

# Search for Nintendo stock price in Japanese
echo "Searching for Nintendo stock price..."
curl -s --compressed \
  --get \
  --data-urlencode "q=任天堂 株価 7974 今日&count=10&freshness=pd&country=JP&search_lang=ja" \
  -H "Accept: application/json" \
  -H "X-Subscription-Token: ${BRAVE_API_KEY}" \
  "https://api.search.brave.com/res/v1/web/search" > nintendo_search_jp.json

# Also search in English for more comprehensive data
echo "Searching for Nintendo stock price in English..."
curl -s --compressed \
  --get \
  --data-urlencode "q=Nintendo stock price 7974.T today&count=10&freshness=pd" \
  -H "Accept: application/json" \
  -H "X-Subscription-Token: ${BRAVE_API_KEY}" \
  "https://api.search.brave.com/res/v1/web/search" > nintendo_search_en.json

echo "Search completed. Results saved to JSON files."