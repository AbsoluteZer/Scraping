from ddgs import DDGS
import re


def check_content_for_matches(text: str,filter:list) -> tuple:
    """
    Check if any filter words appear in the given text.
    
    Args:
        text: Text to check
        
    Returns:
        tuple: (bool, list) - Whether matches were found and list of matched words
    """
    text = text.lower()
    matches = []
    
    for word in filter:
        # Convert filter word to pattern that matches whole words only
        pattern = r'\b' + re.escape(word.lower()) + r'\b'
        if re.search(pattern, text):
            matches.append(word)
    
    return bool(matches), matches

def search_duckduckgo(query,filter):
    """
    Search DuckDuckGo for a query and check both title and body text.
    
    Args:
        query: Search term to look for
        
    Returns:
        bool: True if filter words found, False otherwise
    """
    try:
        # Create DuckDuckGo search instance
        with DDGS() as ddgs:
            # Get search results
            results = list(ddgs.text(query, max_results=20))
            print(f"  🔍 DuckDuckGo search for '{query}' returned {len(results)} results")
            
            # Check each result
            if results:
                for result in results:
                    title = result.get('title', '')
                    body = result.get('body', '')
                    
                    # Check title
                    title_found, title_matches = check_content_for_matches(title,filter)
                    if title_found:
                        print(f"  ✅ Found in title: {', '.join(title_matches)}")
                        print(f"  � Title: {title}")
                        return True
                    
                    # Check body
                    body_found, body_matches = check_content_for_matches(body,filter)
                    if body_found:
                        print(f"  ✅ Found in body: {', '.join(body_matches)}")
                        print(f"  📄 Body excerpt: {body[:200]}...")
                        return True
            
            print("  ❌ No keyword found in search results")
            return False
                
    except Exception as e:
        print(f"  ⚠️ Error searching '{query}': {str(e)}")
        return False
    
def save_data(array:list,data:bool):
    """
    Save True/False from searchduckduck go into array
    """
    array.append(data)
