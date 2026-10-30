from tools.communication_tools import search_emails

result = search_emails.invoke({
    "query": 'from:nse-direct@nse.co.in subject:"Trades executed at NSE"',
    "after": "2026-08-30",
    "before": "2026-09-01",
    "max_results": 5,
})

print(result)