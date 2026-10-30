from tavily import TavilyClient
import os

api_key = os.getenv("tavily_key")
client = TavilyClient(api_key=api_key)


def web_search(query, time_range=None, topic=None):
    response = client.search(
        query=query,
        search_depth="advanced",
        max_results=5,
        include_raw_content=True,
        include_answer="advanced",
        topic=topic,
        time_range=time_range,
    )

    result = {
        "query": query,
        "summary": response.get("answer", ""),
        "sources": []
    }

    for source in response["results"][:2]:  # Limit to the first 2 sources
        raw = source.get("raw_content") or source.get("content", "")

        result["sources"].append({
            "title": source["title"],
            "url": source["url"],
            "content": raw[:500]    
        })

    return result