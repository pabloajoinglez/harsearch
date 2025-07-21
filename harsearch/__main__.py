#!/usr/bin/env python3
import argparse
import json
import re
import sys
from typing import Dict, List, Optional, Union

# Color handling for cross-platform compatibility
try:
    import colorama
    colorama.init()
    GREEN = colorama.Fore.GREEN
    BLUE = colorama.Fore.BLUE
    RESET = colorama.Style.RESET_ALL
except ImportError:
    # Fallback if colorama is not installed
    GREEN = BLUE = RESET = ""

class HARSearch:
    def __init__(self, har_file: str, pattern: str, is_regex: bool, 
                 search_type: str, field: str, context_chars: int = 50):
        """
        Initialize the HAR search tool.
        
        Args:
            har_file: Path to the HAR file
            pattern: String or regex pattern to search for
            is_regex: Whether the pattern is a regex
            search_type: 'req' or 'res' (request or response)
            field: 'url', 'headers', or 'text'
            context_chars: Number of context characters to show around matches
        """
        self.har_file = har_file
        self.pattern = pattern
        self.is_regex = is_regex
        self.search_type = search_type
        self.field = field
        self.context_chars = context_chars
        
        # Compile regex if needed
        if self.is_regex:
            try:
                self.regex = re.compile(pattern, re.IGNORECASE)
            except re.error as e:
                print(f"Invalid regular expression: {e}")
                sys.exit(1)
    
    def load_har_file(self) -> Dict:
        """Load and parse the HAR file."""
        try:
            with open(self.har_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: File '{self.har_file}' not found.")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Error: '{self.har_file}' is not a valid JSON file.")
            sys.exit(1)
    
    def search_in_text(self, text: str, url: str) -> List[str]:
        """
        Search for matches in text with context.
        
        Args:
            text: The text to search in
            url: The URL associated with the text
            
        Returns:
            List of formatted match strings
        """
        matches = []
        search_text = text if text else ""
        
        if self.is_regex:
            # Find all regex matches
            for match in self.regex.finditer(search_text):
                start, end = match.span()
                # Get context around the match
                context_start = max(0, start - self.context_chars)
                context_end = min(len(search_text), end + self.context_chars)
                context = search_text[context_start:context_end]
                
                # Highlight the matched part
                highlighted = (
                    context[:start - context_start] +
                    BLUE + match.group() + RESET +
                    context[end - context_start:]
                )
                
                matches.append(f"{GREEN}URL: {url}{RESET}\n{highlighted}")
        else:
            # Simple string search
            start_pos = 0
            while True:
                pos = search_text.lower().find(self.pattern.lower(), start_pos)
                if pos == -1:
                    break
                
                end_pos = pos + len(self.pattern)
                # Get context around the match
                context_start = max(0, pos - self.context_chars)
                context_end = min(len(search_text), end_pos + self.context_chars)
                context = search_text[context_start:context_end]
                
                # Highlight the matched part
                highlighted = (
                    context[:pos - context_start] +
                    BLUE + search_text[pos:end_pos] + RESET +
                    context[end_pos - context_start:]
                )
                
                matches.append(f"{GREEN}URL: {url}{RESET}\n{highlighted}")
                start_pos = end_pos
        
        return matches
    
    def search_entries(self) -> List[str]:
        """Search through all entries in the HAR file."""
        har_data = self.load_har_file()
        all_matches = []
        
        if "log" not in har_data or "entries" not in har_data["log"]:
            print("Error: Invalid HAR file format - missing log or entries.")
            return []
        
        for entry in har_data["log"]["entries"]:
            url = entry["request"]["url"]
            target = entry[self.search_type]  # 'request' or 'response'
            
            if self.field == "url" and self.search_type == "request":
                # Special case for URL search
                if self.is_regex:
                    if self.regex.search(url):
                        all_matches.append(f"{GREEN}URL: {url}{RESET}\n{BLUE}{url}{RESET}")
                else:
                    if self.pattern.lower() in url.lower():
                        all_matches.append(f"{GREEN}URL: {url}{RESET}\n{BLUE}{url}{RESET}")
            elif self.field == "headers":
                # Search in headers
                headers = target.get("headers", [])
                header_text = "\n".join(f"{h['name']}: {h['value']}" for h in headers)
                all_matches.extend(self.search_in_text(header_text, url))
            elif self.field == "text":
                # Search in content text
                content = target.get("content", {}).get("text", "")
                all_matches.extend(self.search_in_text(content, url))
        
        return all_matches
    
    def print_results(self, matches: List[str]):
        """Print the search results with separators."""
        for i, match in enumerate(matches):
            print(match)
            if i != len(matches) - 1:
                print("\n" + "-" * 80 + "\n")

def main():
    parser = argparse.ArgumentParser(
        description="HAR Search Tool - Search through HTTP Archive (HAR) files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  harsearch example.har "example.com" -req -url
  harsearch example.har -r "example.*com" -req -headers
  harsearch example.har "password" -res -text -n 30
""")
    
    parser.add_argument("har_file", help="Path to the HAR file")
    parser.add_argument("pattern", help="String or regex pattern to search for")
    parser.add_argument("-r", "--regex", action="store_true", 
                        help="Treat pattern as a regular expression")
    parser.add_argument("-req", "--request", action="store_const", 
                        dest="search_type", const="request", 
                        help="Search in request fields")
    parser.add_argument("-res", "--response", action="store_const", 
                        dest="search_type", const="response", 
                        help="Search in response fields")
    parser.add_argument("-url", action="store_const", dest="field", const="url", 
                        help="Search in URL (request only)")
    parser.add_argument("-headers", action="store_const", dest="field", const="headers", 
                        help="Search in headers")
    parser.add_argument("-text", action="store_const", dest="field", const="text", 
                        help="Search in content text")
    parser.add_argument("-n", "--context", type=int, default=50,
                        help="Number of context characters to show around matches (default: 50)")
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.search_type:
        print("Error: You must specify either -req or -res")
        sys.exit(1)
    
    if not args.field:
        print("Error: You must specify one of -url, -headers, or -text")
        sys.exit(1)
    
    if args.field == "url" and args.search_type != "request":
        print("Error: -url can only be used with -req")
        sys.exit(1)
    
    # Perform the search
    har_search = HARSearch(
        args.har_file,
        args.pattern,
        args.regex,
        args.search_type,
        args.field,
        args.context
    )
    
    matches = har_search.search_entries()
    
    if not matches:
        print("No matches found.")
    else:
        #print(f"Found {len(matches)} matches:\n")
        har_search.print_results(matches)

if __name__ == "__main__":
    main()
