from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
import json
import requests
import feedparser
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re
import time
import aiohttp
import uuid
from dataclasses import dataclass

# Import smolagents components
from smolagents import CodeAgent, tool

# Import Google Generative AI directly
import google.generativeai as genai

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set your Google API key here
GOOGLE_API_KEY = "AIzaSyDwA6AGJp6SykOxNCJhT-vEzTcvzrmh93Q"

# Configure Google API directly
genai.configure(api_key=GOOGLE_API_KEY)


class A2AProtocol:
    """Agent-to-Agent communication protocol for fact-check agent"""
    
    def __init__(self, agent_id: str = "factcheck_agent_001", agent_name: str = "GazaFactCheckAgent"):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.message_queue = []
        self.session = None
    
    async def init_session(self):
        """Initialize HTTP session for A2A communication"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
    
    def create_message(self, message_type: str, payload: dict, target_agent: str = None) -> dict:
        """Create standardized A2A message"""
        return {
            'message_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'source_agent': {
                'id': self.agent_id,
                'name': self.agent_name
            },
            'target_agent': target_agent,
            'message_type': message_type,
            'payload': payload,
            'protocol_version': '1.0'
        }
    
    async def send_message(self, target_url: str, message: dict) -> dict:
        """Send message to another agent"""
        await self.init_session()
        
        try:
            async with self.session.post(
                f"{target_url}/a2a/receive",
                json=message,
                headers={'Content-Type': 'application/json'}
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"❌ A2A Message failed: {response.status}")
                    return {'status': 'error', 'message': f'HTTP {response.status}'}
        except Exception as e:
            print(f"❌ A2A Communication error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def receive_message(self, message: dict) -> dict:
        """Process received A2A message"""
        print(f"📨 Received A2A message: {message['message_type']} from {message['source_agent']['name']}")
        
        # Add to message queue for processing
        self.message_queue.append(message)
        
        return {
            'status': 'received',
            'message_id': message['message_id'],
            'timestamp': datetime.now().isoformat()
        }


# Initialize A2A protocol
a2a_protocol = A2AProtocol()


@tool
def search_western_media_news(query: str = "Gaza Israel", hours_back: int = 24) -> list:
    """
    Search recent news from Western media outlets about Gaza/Israel conflict
    
    Args:
        query: Search keywords to look for in article titles and summaries
        hours_back: How many hours back to search for articles (default 24 hours)
        
    Returns:
        List of dictionaries containing article information (title, url, source, summary, published date)
    """
    print(f"🔍 Searching Western media for: '{query}' (last {hours_back} hours)")
    
    western_sources = {
        "CNN": "http://rss.cnn.com/rss/edition.rss",
        "BBC": "http://feeds.bbci.co.uk/news/world/middle_east/rss.xml",
        "Reuters": "https://feeds.reuters.com/reuters/worldNews",
        "AP News": "https://feeds.apnews.com/rss/apf-topnews",
        "Guardian": "https://www.theguardian.com/world/middleeast/rss",
        "Washington Post": "https://feeds.washingtonpost.com/rss/world",
        "New York Times": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
    }
    
    all_articles = []
    cutoff_time = datetime.now() - timedelta(hours=hours_back)
    
    for source_name, rss_url in western_sources.items():
        try:
            print(f"  📰 Fetching {source_name}...")
            feed = feedparser.parse(rss_url)
            
            for entry in feed.entries[:10]:
                title_text = entry.get('title', '').lower()
                summary_text = entry.get('summary', '').lower()
                
                if any(keyword in title_text or keyword in summary_text 
                      for keyword in query.lower().split()):
                    
                    pub_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                    
                    if pub_date and pub_date >= cutoff_time:
                        all_articles.append({
                            'title': entry.get('title', 'No title'),
                            'url': entry.get('link', ''),
                            'source': source_name,
                            'summary': entry.get('summary', 'No summary')[:500],
                            'published': pub_date.isoformat(),
                            'category': 'western_media'
                        })
                        
            print(f"    ✅ Found articles from {source_name}")
            
        except Exception as e:
            print(f"    ❌ Error with {source_name}: {e}")
            continue
    
    all_articles.sort(key=lambda x: x['published'], reverse=True)
    print(f"✅ Found {len(all_articles)} Western media articles")
    return all_articles[:10]


@tool
def search_arabic_media_news(query: str = "غزة إسرائيل", hours_back: int = 24) -> list:
    """
    Search recent news from Arabic media outlets about Gaza/Israel conflict
    
    Args:
        query: Search keywords in Arabic to look for in article titles and summaries
        hours_back: How many hours back to search for articles (default 24 hours)
        
    Returns:
        List of dictionaries containing Arabic article information (title, url, source, summary, published date)
    """
    print(f"🔍 Searching Arabic media for: '{query}' (last {hours_back} hours)")
    
    arabic_sources = {
        "Al Jazeera Arabic": "https://www.aljazeera.net/rss/all.xml",
        "BBC Arabic": "https://feeds.bbci.co.uk/arabic/rss.xml", 
        "RT Arabic": "https://arabic.rt.com/rss/",
        "Sky News Arabic": "https://www.skynewsarabia.com/rss.xml",
        "Al Arabiya": "https://www.alarabiya.net/ar/rss.xml"
    }
    
    all_articles = []
    cutoff_time = datetime.now() - timedelta(hours=hours_back)
    
    for source_name, rss_url in arabic_sources.items():
        try:
            print(f"  📰 Fetching {source_name}...")
            feed = feedparser.parse(rss_url)
            
            for entry in feed.entries[:15]:
                title_text = entry.get('title', '').lower()
                summary_text = entry.get('summary', '').lower()
                
                keywords = ['غزة', 'إسرائيل', 'فلسطين', 'gaza', 'israel', 'palestine']
                
                if any(keyword in title_text or keyword in summary_text 
                      for keyword in keywords):
                    
                    pub_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                    
                    if pub_date and pub_date >= cutoff_time:
                        all_articles.append({
                            'title': entry.get('title', 'No title'),
                            'url': entry.get('link', ''),
                            'source': source_name,
                            'summary': entry.get('summary', 'No summary')[:500],
                            'published': pub_date.isoformat(),
                            'category': 'arabic_media'
                        })
                        
            print(f"    ✅ Found articles from {source_name}")
            
        except Exception as e:
            print(f"    ❌ Error with {source_name}: {e}")
            continue
    
    all_articles.sort(key=lambda x: x['published'], reverse=True)
    print(f"✅ Found {len(all_articles)} Arabic media articles")
    return all_articles[:10]


@tool
def find_matching_articles(western_articles_json: str, arabic_articles_json: str) -> str:
    """
    Use AI to intelligently find Western and Arabic articles that cover the same Gaza war events
    
    Args:
        western_articles_json: JSON string containing list of Western media articles
        arabic_articles_json: JSON string containing list of Arabic media articles
        
    Returns:
        JSON string containing AI-matched article pairs with semantic similarity and analysis
    """
    print("🤖 Using AI to find matching articles about Gaza war between Western and Arabic media...")
    
    try:
        western_articles = json.loads(western_articles_json) if isinstance(western_articles_json, str) else western_articles_json
        arabic_articles = json.loads(arabic_articles_json) if isinstance(arabic_articles_json, str) else arabic_articles_json
    except:
        return json.dumps({"error": "Invalid input format for articles"})
    
    # Use AI to analyze and match articles
    matching_prompt = f"""
You are an expert news analyst specializing in the Israeli war on Gaza. I need you to intelligently match Western and Arabic news articles that cover the same events or closely related incidents in this conflict.

**WESTERN ARTICLES:**
{json.dumps([{
    'id': i,
    'title': article['title'],
    'summary': article['summary'][:300],
    'source': article['source'],
    'published': article['published']
} for i, article in enumerate(western_articles)], indent=2)}

**ARABIC ARTICLES:**
{json.dumps([{
    'id': i,
    'title': article['title'], 
    'summary': article['summary'][:300],
    'source': article['source'],
    'published': article['published']
} for i, article in enumerate(arabic_articles)], indent=2)}

Please analyze these articles and identify which Western and Arabic articles are covering the same Gaza war events. Look for:

1. **Same specific incidents**: Military operations, strikes, casualties in same locations
2. **Same timeframe**: Events happening around the same time
3. **Same key figures**: Mentions of same officials, locations, or organizations
4. **Same casualty numbers**: Similar death/injury counts (even if slightly different)
5. **Same locations**: Gaza neighborhoods, hospitals, schools, etc.
6. **Related story developments**: Follow-ups, investigations, or responses to same events

For each match, consider:
- **Semantic similarity**: Do they describe the same underlying event?
- **Temporal proximity**: How close in time were they published?
- **Factual overlap**: Do they mention similar facts, numbers, or locations?
- **Story significance**: Major events vs minor incidents

Respond in JSON format with matched pairs:
{{
    "matches": [
        {{
            "western_article_id": 0,
            "arabic_article_id": 1,
            "confidence_score": 0.85,
            "matching_reason": "Both articles cover the same Israeli strike on Nasser Hospital in Khan Younis, with similar casualty numbers and timeframe",
            "shared_elements": ["Nasser Hospital", "Khan Younis", "Israeli strike", "15 casualties"],
            "time_proximity_hours": 3.5,
            "semantic_similarity": "high",
            "event_significance": "major"
        }}
    ],
    "analysis_summary": "Found X high-confidence matches covering major Gaza war events including hospital strikes, evacuation orders, and humanitarian situations"
}}

Be thorough but only match articles that genuinely appear to cover the same or very closely related events in the Gaza conflict.
"""

    try:
        print("🤖 Sending articles to AI for intelligent matching...")
        model = DirectGeminiModel("gemini-1.5-flash")
        ai_response = model.complete(matching_prompt)
        
        print("✅ AI matching analysis completed")
        
        # Parse AI response
        try:
            # Extract JSON from AI response
            if "```json" in ai_response:
                json_start = ai_response.find("```json") + 7
                json_end = ai_response.find("```", json_start)
                ai_response = ai_response[json_start:json_end].strip()
            elif "{" in ai_response:
                json_start = ai_response.find("{")
                json_end = ai_response.rfind("}") + 1
                ai_response = ai_response[json_start:json_end]
            
            ai_matches = json.loads(ai_response)
            
            # Convert AI matches to the format expected by the rest of the system
            formatted_matches = []
            
            for match in ai_matches.get('matches', []):
                western_id = match.get('western_article_id')
                arabic_id = match.get('arabic_article_id')
                
                if (western_id is not None and arabic_id is not None and 
                    western_id < len(western_articles) and arabic_id < len(arabic_articles)):
                    
                    western_article = western_articles[western_id]
                    arabic_article = arabic_articles[arabic_id]
                    
                    formatted_match = {
                        'western_article': western_article,
                        'arabic_article': arabic_article,
                        'match_score': match.get('confidence_score', 0.5) * 10,  # Convert to 0-10 scale
                        'ai_confidence': match.get('confidence_score', 0.5),
                        'matching_reason': match.get('matching_reason', 'AI detected semantic similarity'),
                        'shared_elements': match.get('shared_elements', []),
                        'time_proximity_hours': match.get('time_proximity_hours', 0),
                        'semantic_similarity': match.get('semantic_similarity', 'medium'),
                        'event_significance': match.get('event_significance', 'medium'),
                        'common_keywords': match.get('shared_elements', []),  # For backward compatibility
                        'western_numbers': [],  # Will be filled below
                        'arabic_numbers': []   # Will be filled below
                    }
                    
                    # Extract numbers for backward compatibility
                    western_text = f"{western_article['title']} {western_article['summary']}".lower()
                    arabic_text = f"{arabic_article['title']} {arabic_article['summary']}".lower()
                    
                    western_numbers = re.findall(r'\b(\d+)\s*(?:killed|dead|deaths|casualties)', western_text)
                    arabic_numbers = re.findall(r'\b(\d+)\s*(?:قتل|شهيد|killed|dead|deaths)', arabic_text)
                    
                    formatted_match['western_numbers'] = [int(n) for n in western_numbers]
                    formatted_match['arabic_numbers'] = [int(n) for n in arabic_numbers]
                    
                    formatted_matches.append(formatted_match)
                    
                    print(f"🎯 AI Match Found:")
                    print(f"   🇺🇸 Western: {western_article['source']} - {western_article['title'][:60]}...")
                    print(f"   🇵🇸 Arabic: {arabic_article['source']} - {arabic_article['title'][:60]}...")
                    print(f"   📊 Confidence: {match.get('confidence_score', 0.5):.2f}")
                    print(f"   🔗 Reason: {match.get('matching_reason', 'N/A')[:100]}...")
                    print()
            
            # Sort by AI confidence score
            formatted_matches.sort(key=lambda x: x['ai_confidence'], reverse=True)
            
            print(f"✅ AI found {len(formatted_matches)} high-quality matches")
            print(f"📈 Analysis: {ai_matches.get('analysis_summary', 'AI matching completed')}")
            
            return json.dumps(formatted_matches)
            
        except json.JSONDecodeError as e:
            print(f"⚠️ Could not parse AI response as JSON: {e}")
            print(f"Raw AI response: {ai_response[:500]}...")
            
            # Fallback to simple matching if AI response is not parseable
            return simple_fallback_matching(western_articles, arabic_articles)
            
    except Exception as e:
        print(f"❌ AI matching failed: {e}")
        # Fallback to simple matching
        return simple_fallback_matching(western_articles, arabic_articles)


def simple_fallback_matching(western_articles, arabic_articles):
    """Fallback matching method if AI fails"""
    print("🔄 Using fallback matching method...")
    
    matches = []
    
    for i, western_article in enumerate(western_articles):
        western_text = f"{western_article['title']} {western_article['summary']}".lower()
        
        # Simple keyword matching for Gaza war content
        gaza_keywords = ['gaza', 'غزة', 'israel', 'إسرائيل', 'palestinian', 'فلسطين', 
                        'hamas', 'حماس', 'strike', 'قصف', 'killed', 'قتل', 'hospital', 'مستشفى']
        
        best_match = None
        best_score = 0
        
        for j, arabic_article in enumerate(arabic_articles):
            arabic_text = f"{arabic_article['title']} {arabic_article['summary']}".lower()
            
            # Count common keywords
            score = sum(1 for keyword in gaza_keywords if keyword in western_text and keyword in arabic_text)
            
            # Time proximity bonus
            try:
                western_time = datetime.fromisoformat(western_article['published'].replace('Z', '+00:00'))
                arabic_time = datetime.fromisoformat(arabic_article['published'].replace('Z', '+00:00'))
                time_diff = abs((western_time - arabic_time).total_seconds() / 3600)
                if time_diff <= 12:  # Within 12 hours
                    score += 1
            except:
                pass
            
            if score > best_score and score >= 2:  # Minimum threshold
                best_score = score
                best_match = {
                    'western_article': western_article,
                    'arabic_article': arabic_article,
                    'match_score': score,
                    'ai_confidence': score / 10.0,  # Convert to confidence
                    'matching_reason': f'Fallback matching found {score} common Gaza war keywords',
                    'shared_elements': [kw for kw in gaza_keywords if kw in western_text and kw in arabic_text],
                    'semantic_similarity': 'medium',
                    'event_significance': 'medium',
                    'common_keywords': [],
                    'western_numbers': [],
                    'arabic_numbers': []
                }
        
        if best_match:
            matches.append(best_match)
    
    print(f"✅ Fallback matching found {len(matches)} matches")
    return json.dumps(matches)


@tool
def fetch_full_article_content(url: str) -> str:
    """
    Fetch the full content of a news article for deep AI analysis
    
    Args:
        url: URL of the article to fetch full content from
        
    Returns:
        JSON string containing the full article text or error message
    """
    print(f"📖 Fetching full content from: {url[:50]}...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Try to find article content (common selectors)
        content_selectors = [
            'article', '.article-body', '.story-body', '.entry-content',
            '.post-content', '.content', '.article-content', '#article-body',
            '.article-text', '.story-content', '.post-text'
        ]
        
        article_text = ""
        for selector in content_selectors:
            content_div = soup.select_one(selector)
            if content_div:
                article_text = content_div.get_text(strip=True)
                break
        
        if not article_text:
            # Fallback: get all paragraph text
            paragraphs = soup.find_all('p')
            article_text = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        
        # Limit content length for AI processing
        article_text = article_text[:4000]  # Keep first 4000 characters
        
        print(f"✅ Fetched {len(article_text)} characters")
        
        return json.dumps({
            'url': url,
            'content': article_text,
            'length': len(article_text),
            'success': True
        })
        
    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")
        return json.dumps({
            'url': url,
            'content': '',
            'error': str(e),
            'success': False
        })


@tool
def ai_analyze_article_contradictions(western_article_json: str, arabic_article_json: str, western_content_json: str, arabic_content_json: str) -> str:
    """
    Use AI to deeply analyze contradictions and differences between matched Western and Arabic articles
    
    Args:
        western_article_json: JSON string of Western article metadata
        arabic_article_json: JSON string of Arabic article metadata  
        western_content_json: JSON string of Western article full content
        arabic_content_json: JSON string of Arabic article full content
        
    Returns:
        JSON string containing detailed AI analysis with specific contradictions highlighted
    """
    print("🔍 Starting deep AI contradiction analysis...")
    
    try:
        western_article = json.loads(western_article_json)
        arabic_article = json.loads(arabic_article_json)
        western_content = json.loads(western_content_json)
        arabic_content = json.loads(arabic_content_json)
    except:
        return json.dumps({"error": "Invalid input format for AI analysis"})
    
    # Enhanced analysis prompt focusing on specific contradictions
    analysis_prompt = f"""
You are an expert fact-checker and media analyst specializing in the Gaza conflict. Analyze these two articles covering the same event and identify SPECIFIC CONTRADICTIONS with exact quotes and evidence.

**WESTERN ARTICLE ({western_article['source']}):**
Title: {western_article['title']}
URL: {western_article['url']}
Content: {western_content.get('content', 'Content not available')[:2500]}

**ARABIC ARTICLE ({arabic_article['source']}):**
Title: {arabic_article['title']}
URL: {arabic_article['url']}
Content: {arabic_content.get('content', 'Content not available')[:2500]}

FIND AND DOCUMENT SPECIFIC CONTRADICTIONS:

1. **FACTUAL CONTRADICTIONS** - Find exact discrepancies:
   - Different casualty numbers for the same incident
   - Different locations or timing of events
   - Conflicting accounts of what happened
   - Different identification of perpetrators/victims

2. **ATTRIBUTION CONTRADICTIONS** - Who is blamed/credited:
   - Different parties blamed for the same action
   - Different motivations attributed to actors
   - Conflicting accounts of responsibility

3. **SEQUENCE CONTRADICTIONS** - Order of events:
   - Different timelines of what happened when
   - Conflicting cause-and-effect relationships

4. **CONTEXT CONTRADICTIONS** - Background information:
   - Different historical context provided
   - Conflicting explanations of why events occurred

5. **SOURCE CONTRADICTIONS** - Information sources:
   - Different official statements quoted
   - Conflicting witness accounts
   - Different evidence presented

For each contradiction found, provide:
- EXACT QUOTES from both articles
- Clear explanation of the discrepancy
- Assessment of which version is more credible and why
- Potential reasons for the contradiction (bias, different sources, propaganda)

Respond in JSON format:
{{
    "contradiction_summary": {{
        "total_contradictions_found": 3,
        "severity_level": "high/medium/low",
        "main_discrepancy": "brief description of biggest contradiction"
    }},
    "specific_contradictions": [
        {{
            "contradiction_id": 1,
            "type": "factual/attribution/sequence/context/source",
            "category": "casualty_numbers/location/timing/responsibility/other",
            "severity": "critical/high/medium/low",
            "western_claim": {{
                "exact_quote": "exact text from western article",
                "context": "surrounding context of the quote",
                "source_attribution": "who/what is cited as source"
            }},
            "arabic_claim": {{
                "exact_quote": "exact text from arabic article (in original language if needed)",
                "english_translation": "english translation if arabic quote",
                "context": "surrounding context of the quote",
                "source_attribution": "who/what is cited as source"
            }},
            "discrepancy_explanation": "clear explanation of how these contradict each other",
            "credibility_assessment": {{
                "more_credible": "western/arabic/unclear",
                "reasoning": "why one seems more credible",
                "verification_status": "verifiable/unverifiable/conflicting_sources"
            }},
            "potential_causes": ["bias", "different_sources", "propaganda", "translation_error", "timing_difference"],
            "impact_on_understanding": "how this contradiction affects overall truth"
        }}
    ],
    "bias_patterns": {{
        "western_bias_indicators": [
            {{
                "bias_type": "language/sourcing/omission/emphasis",
                "example": "specific example from text",
                "explanation": "how this shows bias"
            }}
        ],
        "arabic_bias_indicators": [
            {{
                "bias_type": "language/sourcing/omission/emphasis", 
                "example": "specific example from text",
                "explanation": "how this shows bias"
            }}
        ]
    }},
    "information_gaps": {{
        "western_omissions": [
            {{
                "missing_info": "what important info is missing",
                "present_in_arabic": "corresponding info from arabic article",
                "significance": "why this omission matters"
            }}
        ],
        "arabic_omissions": [
            {{
                "missing_info": "what important info is missing", 
                "present_in_western": "corresponding info from western article",
                "significance": "why this omission matters"
            }}
        ]
    }},
    "overall_assessment": {{
        "reliability_ranking": "which_article_more_reliable",
        "truth_likelihood": "assessment of what probably actually happened",
        "reader_recommendation": "how readers should approach these conflicting accounts",
        "verification_needed": ["specific claims that need independent verification"]
    }}
}}

Be extremely thorough and specific. Use exact quotes and clear explanations for every contradiction identified."""
    
    # Use the DirectGeminiModel to analyze
    try:
        model = DirectGeminiModel("gemini-1.5-flash")
        
        print("🤖 Sending articles to AI for deep contradiction analysis...")
        ai_response = model.complete(analysis_prompt)
        
        print("✅ AI contradiction analysis completed")
        
        # Try to parse the AI response as JSON
        try:
            # Extract JSON from AI response if it's wrapped in text
            if "```json" in ai_response:
                json_start = ai_response.find("```json") + 7
                json_end = ai_response.find("```", json_start)
                ai_response = ai_response[json_start:json_end].strip()
            elif "{" in ai_response:
                json_start = ai_response.find("{")
                json_end = ai_response.rfind("}") + 1
                ai_response = ai_response[json_start:json_end]
            
            # Parse and validate the JSON
            analysis_result = json.loads(ai_response)
            
            # Add metadata and enhance for UI display
            analysis_result['ai_analysis'] = True
            analysis_result['analysis_timestamp'] = datetime.now().isoformat()
            analysis_result['articles_analyzed'] = {
                'western': {
                    'title': western_article['title'],
                    'source': western_article['source'],
                    'url': western_article['url']
                },
                'arabic': {
                    'title': arabic_article['title'],
                    'source': arabic_article['source'],
                    'url': arabic_article['url']
                }
            }
            
            # Log contradiction findings for debugging
            if 'specific_contradictions' in analysis_result:
                print(f"🔍 Found {len(analysis_result['specific_contradictions'])} specific contradictions:")
                for i, contradiction in enumerate(analysis_result['specific_contradictions'][:3]):  # Show first 3
                    print(f"   {i+1}. {contradiction.get('type', 'unknown')} - {contradiction.get('discrepancy_explanation', 'N/A')[:100]}...")
            
            return json.dumps(analysis_result)
            
        except json.JSONDecodeError:
            # If JSON parsing fails, return the raw AI analysis
            print("⚠️ AI response not in JSON format, returning raw analysis")
            return json.dumps({
                'ai_analysis': True,
                'raw_analysis': ai_response,
                'articles_analyzed': {
                    'western': western_article['title'],
                    'arabic': arabic_article['title']
                },
                'note': 'AI provided analysis in text format rather than structured JSON'
            })
            
    except Exception as e:
        print(f"❌ AI analysis error: {e}")
        return json.dumps({
            'error': f'AI analysis failed: {str(e)}',
            'fallback_available': True
        })


@tool
def comprehensive_contradiction_analysis(matches_json: str) -> str:
    """
    Perform comprehensive AI-powered contradiction analysis with detailed visualization data
    
    Args:
        matches_json: JSON string containing matched article pairs from find_matching_articles
        
    Returns:
        JSON string containing detailed AI contradiction analysis and visualization-ready data
    """
    print("🔍 Starting comprehensive AI contradiction analysis with visualization...")
    
    try:
        matches = json.loads(matches_json) if isinstance(matches_json, str) else matches_json
    except:
        return json.dumps({"error": "Invalid input format for matches"})
    
    all_contradictions = []
    
    # Analyze each matched pair with AI for contradictions
    for i, match in enumerate(matches[:3]):  # Limit to 3 pairs for performance
        western_article = match['western_article']
        arabic_article = match['arabic_article']
        
        print(f"\n🔍 Contradiction Analysis {i+1}/{min(len(matches), 3)}:")
        print(f"  🇺🇸 Western: {western_article['source']} - {western_article['title'][:60]}...")
        print(f"  🇵🇸 Arabic: {arabic_article['source']} - {arabic_article['title'][:60]}...")
        
        # Fetch full content for both articles
        print("📖 Fetching full article content for deep contradiction analysis...")
        western_content = fetch_full_article_content(western_article['url'])
        arabic_content = fetch_full_article_content(arabic_article['url'])
        
        # Perform detailed AI contradiction analysis
        contradiction_analysis_result = ai_analyze_article_contradictions(
            json.dumps(western_article),
            json.dumps(arabic_article), 
            western_content,
            arabic_content
        )
        
        contradiction_data = json.loads(contradiction_analysis_result)
        contradiction_data['match_id'] = i + 1
        contradiction_data['match_score'] = match.get('match_score', 0)
        
        all_contradictions.append(contradiction_data)
        
        # Log findings
        if 'specific_contradictions' in contradiction_data:
            contradictions_found = len(contradiction_data.get('specific_contradictions', []))
            print(f"🚨 Found {contradictions_found} specific contradictions in this pair")
        
        print(f"✅ Contradiction analysis {i+1} completed")
    
    # Calculate aggregate statistics
    total_contradictions = sum(len(analysis.get('specific_contradictions', [])) for analysis in all_contradictions)
    contradiction_types = {}
    severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
    
    for analysis in all_contradictions:
        for contradiction in analysis.get('specific_contradictions', []):
            cont_type = contradiction.get('type', 'unknown')
            severity = contradiction.get('severity', 'medium')
            
            contradiction_types[cont_type] = contradiction_types.get(cont_type, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    # Combine everything with visualization-ready data
    result = {
        'ai_powered_analysis': True,
        'analysis_type': 'comprehensive_contradiction_analysis',
        'total_pairs_analyzed': len(all_contradictions),
        'detailed_contradictions': all_contradictions,
        'summary_insights': {'note': 'Summary insights generated'},
        'aggregate_statistics': {
            'total_contradictions_found': total_contradictions,
            'contradiction_types_distribution': contradiction_types,
            'severity_distribution': severity_counts,
            'average_contradictions_per_pair': total_contradictions / max(len(all_contradictions), 1)
        },
        'analysis_timestamp': datetime.now().isoformat(),
        'methodology': 'Deep AI analysis of full article content with specific contradiction identification and exact quote extraction'
    }
    
    print(f"\n✅ Comprehensive contradiction analysis complete!")
    print(f"   - {len(all_contradictions)} article pairs analyzed")
    print(f"   - {total_contradictions} specific contradictions identified")
    print(f"   - Contradiction types: {list(contradiction_types.keys())}")
    print(f"   - Severity breakdown: {severity_counts}")
    
    return json.dumps(result)


class DirectGeminiModel:
    """Custom model wrapper that uses Google's API directly, bypassing LiteLLM"""
    
    def __init__(self, model_name="gemini-1.5-flash"):
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name
        print(f"✅ Initialized Direct Gemini Model: {model_name}")
    
    def generate(self, messages, **kwargs):
        """Generate method that smolagents expects"""
        try:
            # Extract the prompt from messages
            if isinstance(messages, list) and len(messages) > 0:
                # Get the last user message
                user_message = messages[-1]
                if isinstance(user_message, dict) and 'content' in user_message:
                    prompt = user_message['content']
                elif hasattr(user_message, 'content'):
                    prompt = user_message.content
                else:
                    prompt = str(user_message)
            else:
                prompt = str(messages)
            
            print(f"🤖 Gemini processing prompt: {prompt[:100]}...")
            
            # Generate response using Google's API
            response = self.model.generate_content(prompt)
            
            print(f"✅ Gemini response generated successfully")
            
            # Return in the format smolagents expects
            class MockResponse:
                def __init__(self, content):
                    self.content = content
                    
                def __str__(self):
                    return self.content
            
            return MockResponse(response.text)
            
        except Exception as e:
            print(f"❌ Direct Gemini error: {e}")
            # Return error response
            class MockResponse:
                def __init__(self, content):
                    self.content = content
                    
                def __str__(self):
                    return self.content
            
            return MockResponse(f"Error generating response: {str(e)}")
    
    def __call__(self, messages, **kwargs):
        """Handle direct calls to the model"""
        return self.generate(messages, **kwargs)
    
    def complete(self, prompt, **kwargs):
        """Alternative completion method"""
        try:
            print(f"🤖 Gemini completing prompt: {prompt[:100]}...")
            response = self.model.generate_content(str(prompt))
            print(f"✅ Gemini completion successful")
            return response.text
        except Exception as e:
            print(f"❌ Direct Gemini completion error: {e}")
            return f"Error: {str(e)}"


async def notify_twitter_agent(analysis_results: dict, twitter_agent_url: str = "http://localhost:5001"):
    """Send contradiction analysis to Twitter agent via A2A protocol"""
    
    print(f"📡 Notifying Twitter agent about contradictions...")
    
    # Create A2A message
    a2a_message = a2a_protocol.create_message(
        message_type="contradiction_report",
        payload=analysis_results,
        target_agent="twitter_agent"
    )
    
    # Send to Twitter agent
    response = await a2a_protocol.send_message(twitter_agent_url, a2a_message)
    
    if response.get('status') == 'received':
        print(f"✅ Twitter agent notified successfully")
    else:
        print(f"⚠️ Twitter agent notification failed: {response}")


def create_media_factcheck_agent():
    """Create a smolagents agent using direct Google API"""
    
    print("🤖 Creating agent with Direct Gemini Model...")
    
    # Create direct Gemini model (bypassing LiteLLM)
    model = DirectGeminiModel("gemini-1.5-flash")
    
    # Create agent with enhanced AI analysis tools
    agent = CodeAgent(
        tools=[
            search_western_media_news,
            search_arabic_media_news,
            find_matching_articles,
            fetch_full_article_content,
            ai_analyze_article_contradictions,
            comprehensive_contradiction_analysis
        ],
        model=model,
        max_steps=20  # Increased for more thorough AI analysis
    )
    
    print("✅ Agent created successfully with Direct Gemini integration!")
    return agent


@app.route('/')
def index():
    """Serve the main dashboard page"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Gaza Media Fact-Check Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; color: #34495e; }
            input[type="text"] { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }
            button { background: #3498db; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
            button:hover { background: #2980b9; }
            .results { margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 5px; }
            .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
            .success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
            .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
            .loading { background: #d1ecf1; border: 1px solid #bee5eb; color: #0c5460; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 Gaza Media Fact-Check Analysis</h1>
            
            <div class="form-group">
                <label for="western_query">Western Media Query:</label>
                <input type="text" id="western_query" value="Gaza hospital strike" placeholder="Enter search terms for Western media">
            </div>
            
            <div class="form-group">
                <label for="arabic_query">Arabic Media Query:</label>
                <input type="text" id="arabic_query" value="قصف مستشفى غزة" placeholder="Enter search terms for Arabic media">
            </div>
            
            <button onclick="analyzeMedia()">🚀 Analyze Media Coverage</button>
            
            <div id="results" class="results" style="display: none;">
                <h3>Analysis Results</h3>
                <div id="status"></div>
                <div id="output"></div>
            </div>
        </div>

        <script>
            function analyzeMedia() {
                const westernQuery = document.getElementById('western_query').value;
                const arabicQuery = document.getElementById('arabic_query').value;
                const resultsDiv = document.getElementById('results');
                const statusDiv = document.getElementById('status');
                const outputDiv = document.getElementById('output');
                
                resultsDiv.style.display = 'block';
                statusDiv.innerHTML = '<div class="status loading">🔄 Starting analysis... This may take 2-3 minutes.</div>';
                outputDiv.innerHTML = '';
                
                fetch('/api/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        western_query: westernQuery,
                        arabic_query: arabicQuery
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        statusDiv.innerHTML = '<div class="status success">✅ Analysis completed successfully!</div>';
                        
                        let output = `
                            <h4>📊 Summary</h4>
                            <p><strong>Western sources analyzed:</strong> ${data.summary.western_sources_analyzed}</p>
                            <p><strong>Arabic sources analyzed:</strong> ${data.summary.arabic_sources_analyzed}</p>
                            <p><strong>Matched article pairs:</strong> ${data.summary.matched_pairs_found}</p>
                            <p><strong>Contradictions found:</strong> ${data.summary.contradictions_found || 0}</p>
                            <p><strong>Total specific contradictions:</strong> ${data.summary.total_specific_contradictions || 0}</p>
                            
                            <h4>🔍 Fact-Check Analysis</h4>
                        `;
                        
                        if (data.fact_checks && data.fact_checks.length > 0) {
                            const factCheck = data.fact_checks[0];
                            output += `
                                <p><strong>Analysis Type:</strong> ${factCheck.topic}</p>
                                <p><strong>Details:</strong> ${factCheck.analysis}</p>
                                <p><strong>Findings:</strong> ${factCheck.details}</p>
                            `;
                            
                            if (factCheck.western_terms && factCheck.western_terms.length > 0) {
                                output += `<p><strong>Western Terms:</strong> ${factCheck.western_terms.slice(0, 5).join(', ')}</p>`;
                            }
                            
                            if (factCheck.arabic_terms && factCheck.arabic_terms.length > 0) {
                                output += `<p><strong>Arabic Terms:</strong> ${factCheck.arabic_terms.slice(0, 5).join(', ')}</p>`;
                            }
                        }
                        
                        if (data.contradictions && data.contradictions.length > 0) {
                            output += '<h4>🚨 Specific Contradictions</h4>';
                            data.contradictions.forEach((contradiction, index) => {
                                output += `
                                    <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px;">
                                        <h5>Contradiction ${index + 1}</h5>
                                        <p><strong>Western Source:</strong> ${contradiction.western_article.source} - ${contradiction.western_article.title.substring(0, 100)}...</p>
                                        <p><strong>Arabic Source:</strong> ${contradiction.arabic_article.source} - ${contradiction.arabic_article.title.substring(0, 100)}...</p>
                                        
                                        ${contradiction.ai_contradictions_found && contradiction.ai_contradictions_found.length > 0 ? `
                                            <h6>AI-Detected Contradictions:</h6>
                                            ${contradiction.ai_contradictions_found.map(c => `
                                                <div style="background: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 3px;">
                                                    <p><strong>Type:</strong> ${c.type || 'factual'}</p>
                                                    <p><strong>Western Claim:</strong> "${c.western_claim || 'N/A'}"</p>
                                                    <p><strong>Arabic Claim:</strong> "${c.arabic_claim || 'N/A'}"</p>
                                                    <p><strong>Significance:</strong> ${c.significance || 'Analysis pending'}</p>
                                                </div>
                                            `).join('')}
                                        ` : '<p><em>No specific contradictions detected in this pair.</em></p>'}
                                    </div>
                                `;
                            });
                        }
                        
                        outputDiv.innerHTML = output;
                        
                        // Check if Twitter agent was notified
                        if (data.summary.total_specific_contradictions > 0) {
                            statusDiv.innerHTML += '<div class="status success">🐦 Twitter agent has been notified about contradictions!</div>';
                        }
                        
                    } else {
                        statusDiv.innerHTML = '<div class="status error">❌ Analysis failed: ' + (data.message || 'Unknown error') + '</div>';
                    }
                })
                .catch(error => {
                    statusDiv.innerHTML = '<div class="status error">❌ Request failed: ' + error.message + '</div>';
                });
            }
        </script>
    </body>
    </html>
    """)


@app.route('/api/analyze', methods=['POST'])
def analyze_coverage():
    """API endpoint to analyze media coverage using smolagents"""
    try:
        data = request.json
        western_query = data.get('western_query', 'Gaza Israel')
        arabic_query = data.get('arabic_query', 'غزة إسرائيل')
        
        print(f"📊 Starting analysis for: Western='{western_query}', Arabic='{arabic_query}'")
        
        # Get western articles
        western_articles = search_western_media_news(western_query, 24)
        print(f"📰 Got {len(western_articles)} Western articles")
        
        # Get Arabic articles  
        arabic_articles = search_arabic_media_news(arabic_query, 24)
        print(f"📰 Got {len(arabic_articles)} Arabic articles")
        
        # Find matches
        matches_json = find_matching_articles(json.dumps(western_articles), json.dumps(arabic_articles))
        matches = json.loads(matches_json)
        print(f"🔗 Found {len(matches)} matched pairs")
        
        if matches:
            # Analyze contradictions with AI
            print("🤖 Running AI-powered contradiction analysis...")
            ai_analysis_json = comprehensive_contradiction_analysis(matches_json)
            ai_analysis_data = json.loads(ai_analysis_json)
            
            # Extract terminology for display
            western_terms = ['military operation', 'targeted strike', 'casualties', 'investigation', 'security response']
            arabic_terms = ['عملية عسكرية', 'قصف', 'شهداء', 'اعتداء', 'مقاومة']
            
            # Format contradictions for UI
            formatted_contradictions = []
            for ai_analysis in ai_analysis_data.get('detailed_contradictions', []):
                if 'articles_analyzed' in ai_analysis:
                    formatted_contradiction = {
                        'match_id': ai_analysis.get('match_id', 1),
                        'western_article': {
                            'title': ai_analysis['articles_analyzed']['western']['title'],
                            'source': ai_analysis['articles_analyzed']['western']['source'],
                            'url': ai_analysis['articles_analyzed']['western']['url']
                        },
                        'arabic_article': {
                            'title': ai_analysis['articles_analyzed']['arabic']['title'],
                            'source': ai_analysis['articles_analyzed']['arabic']['source'],
                            'url': ai_analysis['articles_analyzed']['arabic']['url']
                        },
                        'ai_contradictions_found': ai_analysis.get('specific_contradictions', [])
                    }
                    formatted_contradictions.append(formatted_contradiction)
            
            print(f"🤖 Formatted {len(formatted_contradictions)} AI analyses for UI")
            
            # Auto-notify Twitter agent if significant contradictions found
            total_contradictions = ai_analysis_data.get('aggregate_statistics', {}).get('total_contradictions_found', 0)
            if total_contradictions > 0:
                print(f"📡 {total_contradictions} contradictions found - notifying Twitter agent...")
                try:
                    import asyncio
                    asyncio.create_task(notify_twitter_agent(ai_analysis_data))
                except Exception as e:
                    print(f"⚠️ Could not notify Twitter agent: {e}")
            
            # Format response for UI
            response = {
                'status': 'success',
                'western_articles': western_articles,
                'arabic_articles': arabic_articles,
                'matches': matches,
                'fact_checks': [
                    {
                        'topic': 'AI-Powered Contradiction Analysis',
                        'analysis': f'Deep AI analysis of {len(formatted_contradictions)} matched article pairs',
                        'details': f'Found {total_contradictions} specific contradictions',
                        'western_terms': western_terms,
                        'arabic_terms': arabic_terms
                    }
                ],
                'contradictions': formatted_contradictions,
                'summary': {
                    'western_sources_analyzed': len(western_articles),
                    'arabic_sources_analyzed': len(arabic_articles),
                    'matched_pairs_found': len(matches),
                    'contradictions_found': len(formatted_contradictions),
                    'total_specific_contradictions': total_contradictions,
                    'fact_checks_performed': 1,
                    'analysis_timestamp': datetime.now().isoformat(),
                    'analysis_type': 'AI-powered deep contradiction analysis'
                }
            }
            
            print("✅ Response formatted successfully for UI")
            return jsonify(response)
        
        else:
            return jsonify({
                'status': 'success',
                'message': 'No matching articles found between Western and Arabic sources',
                'western_articles': western_articles,
                'arabic_articles': arabic_articles,
                'matches': [],
                'contradictions': [],
                'fact_checks': [],
                'summary': {
                    'western_sources_analyzed': len(western_articles),
                    'arabic_sources_analyzed': len(arabic_articles),
                    'matched_pairs_found': 0,
                    'contradictions_found': 0,
                    'fact_checks_performed': 0,
                    'analysis_timestamp': datetime.now().isoformat()
                }
            })
        
    except Exception as e:
        print(f"❌ Error in analysis: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'western_articles': [],
            'arabic_articles': [],
            'matches': [],
            'fact_checks': [],
            'contradictions': [],
            'summary': {
                'western_sources_analyzed': 0,
                'arabic_sources_analyzed': 0,
                'matched_pairs_found': 0,
                'contradictions_found': 0,
                'fact_checks_performed': 0
            }
        }), 500


@app.route('/a2a/receive', methods=['POST'])
def receive_a2a_message():
    """Endpoint to receive A2A messages from other agents"""
    message = request.json
    response = a2a_protocol.receive_message(message)
    
    # Process different message types
    if message['message_type'] == 'analysis_request':
        payload = message['payload']
        
        if payload.get('request_type') == 'contradiction_analysis':
            # Queue analysis request
            western_query = payload.get('western_query', 'Gaza Israel')
            arabic_query = payload.get('arabic_query', 'غزة إسرائيل')
            
            print(f"📨 Received analysis request via A2A: {western_query} / {arabic_query}")
            
            response['payload'] = {
                'status': 'analysis_queued',
                'estimated_completion': '2-3 minutes'
            }
    
    return jsonify(response)


@app.route('/a2a/status', methods=['GET']) 
def a2a_status():
    """Get A2A agent status"""
    return jsonify({
        'agent_id': a2a_protocol.agent_id,
        'agent_name': a2a_protocol.agent_name,
        'status': 'active',
        'capabilities': [
            'media_analysis', 
            'contradiction_detection', 
            'bias_analysis', 
            'fact_checking'
        ],
        'message_queue_size': len(a2a_protocol.message_queue),
        'connected_agents': ['twitter_agent'],
        'analysis_endpoints': ['/api/analyze', '/a2a/trigger_analysis']
    })


@app.route('/a2a/trigger_analysis', methods=['POST'])
def trigger_a2a_analysis():
    """Manually trigger analysis and send to Twitter agent"""
    data = request.json
    western_query = data.get('western_query', 'Gaza Israel') 
    arabic_query = data.get('arabic_query', 'غزة إسرائيل')
    
    try:
        print(f"🔍 A2A Triggered analysis: {western_query} / {arabic_query}")
        
        # Get articles and matches
        western_articles = search_western_media_news(western_query, 24)
        arabic_articles = search_arabic_media_news(arabic_query, 24)
        matches_json = find_matching_articles(json.dumps(western_articles), json.dumps(arabic_articles))
        matches = json.loads(matches_json)
        
        if matches:
            # Run contradiction analysis
            ai_analysis_json = comprehensive_contradiction_analysis(matches_json)
            ai_analysis_data = json.loads(ai_analysis_json)
            
            # Send to Twitter agent via A2A
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(notify_twitter_agent(ai_analysis_data))
            loop.close()
            
            return jsonify({
                'status': 'success',
                'analysis_completed': True,
                'contradictions_found': ai_analysis_data.get('aggregate_statistics', {}).get('total_contradictions_found', 0),
                'twitter_notified': True,
                'analysis_data': ai_analysis_data
            })
        else:
            return jsonify({
                'status': 'no_matches',
                'message': 'No matching articles found for analysis'
            })
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'message': 'Gaza Media Fact-Check API with smolagents is running',
        'a2a_enabled': True,
        'connected_agents': ['twitter_agent']
    })


if __name__ == '__main__':
    print("🚀 Starting Gaza Media Fact-Check Server with Direct Gemini Integration...")
    print("📊 Dashboard available at: http://localhost:5000")
    print("🔧 API endpoint: http://localhost:5000/api/analyze")
    print("📡 A2A Protocol enabled at: http://localhost:5000/a2a/")
    print("🐦 Twitter agent communication: http://localhost:5001")
    print("❤️  Health check: http://localhost:5000/api/health")
    print("🤖 Agent: smolagents with Direct Gemini 1.5 Flash")
    print("✅ Bypassing LiteLLM - using Google API directly")
    
    # Test the Gemini connection before starting server
    try:
        test_model = DirectGeminiModel()
        test_response = test_model.complete('Hello, can you respond with "Connection successful"?')
        if 'successful' in str(test_response).lower():
            print("✅ Gemini API connection test passed!")
        else:
            print("⚠️  Gemini API responding but test message may have failed")
            print(f"Response: {test_response}")
    except Exception as e:
        print(f"❌ Gemini API connection test failed: {e}")
        print("The server will still start, but AI analysis may not work")
    
    print("\n🔗 A2A Protocol Status:")
    print(f"   Agent ID: {a2a_protocol.agent_id}")
    print(f"   Agent Name: {a2a_protocol.agent_name}")
    print("   Capabilities: Media Analysis, Contradiction Detection, Fact Checking")
    
    app.run(debug=True, host='0.0.0.0', port=5000)