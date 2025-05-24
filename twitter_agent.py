import tweepy
import json
import hashlib
import uuid
from datetime import datetime
from typing import Dict, List
from flask import Flask, request, jsonify
import google.generativeai as genai

# Twitter API Configuration - REPLACE WITH YOUR NEW REGENERATED KEYS
TWITTER_API_KEY = "dJOTaKkBZZ5qtqWCDTkrQ0AAH"
TWITTER_API_SECRET = "d3o0d5LSuv5AUm2V14STmh0EHU0CWVuFWS5d62iP6u1bsN8Vfw" 
TWITTER_ACCESS_TOKEN = "your_new_access_token_after_regeneration"
TWITTER_ACCESS_TOKEN_SECRET = "your_new_access_token_secret_after_regeneration"
TWITTER_BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAJrj1wEAAAAAR%2BIkmOrpJancLK8o6T79BQwh84g%3DqgrtYSnwVJpBB5dQrDbZ5IkUULm7uzduoYWR43jc1EQ2t5nAhs"

# Configure Google API
GOOGLE_API_KEY = "AIzaSyDwA6AGJp6SykOxNCJhT-vEzTcvzrmh93Q"
genai.configure(api_key=GOOGLE_API_KEY)

# Configure Twitter API v2
print("🔧 Initializing Twitter client...")
try:
    twitter_client = tweepy.Client(
        bearer_token=TWITTER_BEARER_TOKEN,
        consumer_key=TWITTER_API_KEY,
        consumer_secret=TWITTER_API_SECRET,
        access_token=TWITTER_ACCESS_TOKEN,
        access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
        wait_on_rate_limit=True
    )
    
    # Test connection and permissions
    print("🧪 Testing Twitter API connection...")
    try:
        user = twitter_client.get_me()
        print(f"✅ Connected to Twitter as: @{user.data.username}")
        
        # Test if we can access user info (basic read permission)
        print("✅ Read permissions: OK")
        
        # The real test is when we try to post - we'll handle that in the posting function
        print("🔥 Twitter client initialized successfully!")
        print("🔄 Write permissions will be tested when posting...")
        
    except tweepy.Unauthorized as e:
        print(f"❌ Twitter authentication failed: {e}")
        print("🔧 TROUBLESHOOTING:")
        print("   1. Check your API keys are correct")
        print("   2. Make sure you regenerated keys after changing permissions")
        print("   3. Wait 10-15 minutes after regenerating keys")
        print("   4. Verify app permissions are 'Read and Write'")
        twitter_client = None
        
    except Exception as e:
        print(f"❌ Twitter connection error: {e}")
        twitter_client = None
        
except Exception as e:
    print(f"❌ Twitter client initialization failed: {e}")
    print("🔄 Running in simulation mode")
    twitter_client = None


class TwitterThreadCreator:
    """Simple Twitter thread creator without smolagents"""
    
    def __init__(self):
        self.agent_id = "twitter_agent_001"
        self.agent_name = "TwitterContradictionBot"
    
    def format_contradiction_for_twitter(self, contradiction_data: dict) -> List[dict]:
        """Format contradiction analysis for Twitter consumption"""
        print("📱 Formatting contradiction data for Twitter...")
        
        twitter_reports = []
        
        # Process detailed contradictions
        for detailed_analysis in contradiction_data.get('detailed_contradictions', []):
            if 'articles_analyzed' in detailed_analysis:
                
                # Extract main discrepancy
                main_discrepancy = detailed_analysis.get('contradiction_summary', {}).get(
                    'main_discrepancy', 'Media discrepancy detected'
                )
                
                # Extract contradictions
                contradictions = detailed_analysis.get('specific_contradictions', [])
                severity = detailed_analysis.get('contradiction_summary', {}).get('severity_level', 'medium')
                
                report = {
                    'report_id': f"CR_{hashlib.md5(str(detailed_analysis).encode()).hexdigest()[:8]}",
                    'main_headline': f"Media Contradiction Alert: {main_discrepancy[:100]}...",
                    'western_source': {
                        'outlet': detailed_analysis['articles_analyzed']['western']['source'],
                        'title': detailed_analysis['articles_analyzed']['western']['title'],
                        'url': detailed_analysis['articles_analyzed']['western']['url'],
                        'key_claim': self.extract_western_claim(contradictions)
                    },
                    'arabic_source': {
                        'outlet': detailed_analysis['articles_analyzed']['arabic']['source'],
                        'title': detailed_analysis['articles_analyzed']['arabic']['title'],
                        'url': detailed_analysis['articles_analyzed']['arabic']['url'],
                        'key_claim': self.extract_arabic_claim(contradictions)
                    },
                    'contradiction_summary': main_discrepancy,
                    'severity': severity,
                    'contradictions': contradictions,
                    'hashtags': self.generate_hashtags(severity, main_discrepancy)
                }
                
                twitter_reports.append(report)
        
        print(f"📱 Created {len(twitter_reports)} Twitter-ready reports")
        return twitter_reports
    
    def extract_western_claim(self, contradictions: List[dict]) -> str:
        """Extract main Western claim from contradictions"""
        if contradictions:
            return contradictions[0].get('western_claim', {}).get('exact_quote', '')[:200]
        return "Western media report"
    
    def extract_arabic_claim(self, contradictions: List[dict]) -> str:
        """Extract main Arabic claim from contradictions"""
        if contradictions:
            arabic_claim = contradictions[0].get('arabic_claim', {})
            return arabic_claim.get('english_translation', arabic_claim.get('exact_quote', ''))[:200]
        return "Arabic media report"
    
    def generate_hashtags(self, severity: str, discrepancy: str) -> List[str]:
        """Generate relevant hashtags"""
        base_tags = ['#FactCheck', '#MediaBias', '#Gaza', '#NewsAnalysis']
        
        if severity == 'critical':
            base_tags.append('#CriticalContradiction')
        elif severity == 'high':
            base_tags.append('#SignificantDiscrepancy')
        
        if 'casualt' in discrepancy.lower():
            base_tags.append('#CasualtyReporting')
        
        return base_tags
    
    def create_twitter_thread(self, report: dict, style: str = "engaging") -> List[dict]:
        """Create Twitter thread from contradiction report"""
        print(f"🧵 Creating Twitter thread in {style} style...")
        
        thread_tweets = []
        
        # Tweet 1: Main headline
        if style == "urgent":
            tweet1 = f"🚨 MEDIA CONTRADICTION ALERT 🚨\n\n{report['main_headline']}\n\n🧵 Thread below 👇"
        elif style == "engaging":
            tweet1 = f"🔍 Something doesn't add up in Gaza coverage...\n\n{report['main_headline']}\n\nLet's break this down 🧵"
        else:  # factual
            tweet1 = f"📊 Media Analysis Alert\n\n{report['main_headline']}\n\nDetailed analysis thread:"
        
        thread_tweets.append({
            'tweet_number': 1,
            'content': tweet1,
            'character_count': len(tweet1)
        })
        
        # Tweet 2: Western source
        western_claim = report['western_source']['key_claim'][:150]
        tweet2 = f"2/ 🇺🇸 WESTERN SOURCE: {report['western_source']['outlet']}\n\n\"{western_claim}...\"\n\n🔗 {report['western_source']['url']}"
        
        thread_tweets.append({
            'tweet_number': 2,
            'content': tweet2,
            'character_count': len(tweet2)
        })
        
        # Tweet 3: Arabic source  
        arabic_claim = report['arabic_source']['key_claim'][:150]
        tweet3 = f"3/ 🇵🇸 ARABIC SOURCE: {report['arabic_source']['outlet']}\n\n\"{arabic_claim}...\"\n\n🔗 {report['arabic_source']['url']}"
        
        thread_tweets.append({
            'tweet_number': 3,
            'content': tweet3,
            'character_count': len(tweet3)
        })
        
        # Tweet 4: Contradiction analysis
        tweet4 = f"4/ ⚡ CONTRADICTION DETECTED:\n\n{report['contradiction_summary']}\n\nSeverity: {report['severity'].upper()}"
        
        thread_tweets.append({
            'tweet_number': 4,
            'content': tweet4,
            'character_count': len(tweet4)
        })
        
        # Tweet 5: Call to action with hashtags
        hashtags = ' '.join(report['hashtags'])
        if style == "urgent":
            tweet5 = f"5/ 🎯 WHAT THIS MEANS:\n\nReaders deserve consistent, accurate reporting. Always cross-reference multiple sources.\n\n{hashtags}"
        elif style == "engaging":
            tweet5 = f"5/ 💭 TAKEAWAY:\n\nThis is why media literacy matters. Different sources, different stories.\n\nWhat do you think? 🤔\n\n{hashtags}"
        else:  # factual
            tweet5 = f"5/ 📋 ANALYSIS COMPLETE:\n\nRecommendation: Seek additional sources for verification.\n\n{hashtags}"
        
        thread_tweets.append({
            'tweet_number': 5,
            'content': tweet5,
            'character_count': len(tweet5)
        })
        
        print(f"🧵 Created {len(thread_tweets)}-tweet thread")
        return thread_tweets
    
    def post_twitter_thread(self, tweets: List[dict], dry_run: bool = True) -> dict:
        """Post Twitter thread about media contradictions"""
        print(f"🐦 {'Simulating' if dry_run else 'Posting'} Twitter thread...")
        
        if dry_run:
            # Simulate posting
            results = {
                'status': 'simulated',
                'tweets_posted': len(tweets),
                'simulation_results': [
                    {
                        'tweet_number': tweet['tweet_number'],
                        'simulated_tweet_id': f"sim_{hash(tweet['content']) % 10000000000000000000}",
                        'content': tweet['content'],
                        'character_count': tweet['character_count'],
                        'status': 'would_post_successfully'
                    }
                    for tweet in tweets
                ],
                'posted_at': datetime.now().isoformat()
            }
            
            print(f"✅ Simulated posting {len(tweets)} tweets")
            
            # Show the simulated tweets
            for tweet in results['simulation_results']:
                print(f"\n🐦 SIMULATED TWEET {tweet['tweet_number']}:")
                print(f"Content: {tweet['content']}")
                print(f"Characters: {tweet['character_count']}/280")
                print("-" * 50)
            
            return results
        
        else:
            # Actually post to Twitter
            posted_tweets = []
            reply_to_id = None
            
            try:
                for tweet in tweets:
                    if twitter_client:
                        # Post tweet
                        response = twitter_client.create_tweet(
                            text=tweet['content'],
                            in_reply_to_tweet_id=reply_to_id
                        )
                        
                        tweet_id = response.data['id']
                        reply_to_id = tweet_id  # Next tweet replies to this one
                        
                        posted_tweets.append({
                            'tweet_number': tweet['tweet_number'],
                            'tweet_id': tweet_id,
                            'content_preview': tweet['content'][:50] + "...",
                            'status': 'posted_successfully',
                            'url': f"https://twitter.com/user/status/{tweet_id}"
                        })
                        
                        print(f"✅ Posted tweet {tweet['tweet_number']}: {tweet_id}")
                        
                        # Rate limiting delay
                        import time
                        time.sleep(2)
                    else:
                        # Simulate if no Twitter client
                        posted_tweets.append({
                            'tweet_number': tweet['tweet_number'],
                            'tweet_id': f"sim_{hash(tweet['content']) % 1000000}",
                            'content_preview': tweet['content'][:50] + "...",
                            'status': 'simulated_no_api'
                        })
                
                results = {
                    'status': 'posted' if twitter_client else 'simulated',
                    'tweets_posted': len(posted_tweets),
                    'posting_results': posted_tweets,
                    'thread_url': posted_tweets[0]['url'] if posted_tweets and twitter_client else "",
                    'posted_at': datetime.now().isoformat()
                }
                
                print(f"🎉 Successfully {'posted' if twitter_client else 'simulated'} {len(posted_tweets)}-tweet thread!")
                return results
                
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Twitter posting error: {error_msg}")
                
                # Provide specific guidance for common errors
                if "401" in error_msg or "Unauthorized" in error_msg:
                    print("🔧 AUTHENTICATION ERROR - FIX NEEDED:")
                    print("   1. Go to developer.twitter.com")
                    print("   2. Select your app")
                    print("   3. Settings → App Permissions → 'Read and Write'")
                    print("   4. Keys and Tokens → Regenerate API Key & Secret")
                    print("   5. Keys and Tokens → Regenerate Access Token & Secret")
                    print("   6. Copy ALL NEW keys to twitter_agent.py")
                    print("   7. Wait 10-15 minutes, then restart system")
                    print("   ⚠️  OLD KEYS WON'T WORK AFTER REGENERATING!")
                elif "403" in error_msg or "oauth1 app permissions" in error_msg.lower():
                    print("🔧 PERMISSION ERROR:")
                    print("   App permissions might not be set correctly")
                    print("   Make sure it's 'Read and Write', not just 'Read'")
                elif "429" in error_msg:
                    print("🔧 RATE LIMIT:")
                    print("   Twitter is rate limiting. Wait 15 minutes.")
                
                return {
                    'status': 'error',
                    'error': error_msg,
                    'tweets_posted': len(posted_tweets),
                    'partial_results': posted_tweets,
                    'fix_instructions': 'Check console output for specific fix instructions'
                }
    
    def process_contradiction_and_tweet(self, contradiction_data: dict, style: str = "engaging", dry_run: bool = True):
        """Process contradiction data and create Twitter thread"""
        print(f"🤖 Processing contradiction data for Twitter...")
        
        # Format data for Twitter
        twitter_reports = self.format_contradiction_for_twitter(contradiction_data)
        
        if not twitter_reports:
            print("⚠️ No contradiction reports to process")
            return {"status": "no_data", "message": "No contradictions found to tweet about"}
        
        results = []
        
        # Create threads for each report
        for report in twitter_reports[:2]:  # Limit to 2 reports to avoid spam
            print(f"🧵 Creating thread for report: {report['report_id']}")
            
            # Create thread
            tweets = self.create_twitter_thread(report, style)
            
            # Post thread
            posting_result = self.post_twitter_thread(tweets, dry_run)
            
            results.append({
                'report_id': report['report_id'],
                'thread_created': True,
                'posting_result': posting_result
            })
        
        return {
            'status': 'success',
            'threads_created': len(results),
            'results': results
        }


# Initialize Twitter agent
twitter_creator = TwitterThreadCreator()

# Flask app for A2A communication
app = Flask(__name__)

@app.route('/a2a/receive', methods=['POST'])
def receive_a2a_message():
    """Endpoint to receive A2A messages"""
    message = request.json
    
    print(f"📨 Received A2A message: {message['message_type']}")
    
    # Process the message
    if message['message_type'] == 'contradiction_report':
        # Process Twitter posting
        contradiction_data = message['payload']
        
        print("🐦 Received contradiction report, creating Twitter thread...")
        try:
            result = twitter_creator.process_contradiction_and_tweet(
                contradiction_data, 
                style="engaging", 
                dry_run=False  # Set to False for real posting
            )
            print(f"✅ Twitter thread result: {result['status']}")
            
            response = {
                'status': 'received',
                'message_id': message['message_id'],
                'timestamp': datetime.now().isoformat(),
                'processing_result': result
            }
            
        except Exception as e:
            print(f"❌ Error creating Twitter thread: {e}")
            response = {
                'status': 'error',
                'message_id': message['message_id'],
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    else:
        response = {
            'status': 'received',
            'message_id': message['message_id'],
            'timestamp': datetime.now().isoformat()
        }
    
    return jsonify(response)

@app.route('/a2a/status', methods=['GET'])
def a2a_status():
    """Get A2A agent status"""
    return jsonify({
        'agent_id': twitter_creator.agent_id,
        'agent_name': twitter_creator.agent_name,
        'status': 'active',
        'capabilities': ['contradiction_reporting', 'twitter_posting', 'thread_creation'],
        'twitter_client_status': 'configured' if twitter_client else 'simulation_mode',
        'version': 'simple_no_smolagents'
    })

@app.route('/test_thread', methods=['POST'])
def test_thread():
    """Test endpoint to create a sample Twitter thread"""
    sample_data = {
        'detailed_contradictions': [{
            'articles_analyzed': {
                'western': {
                    'title': 'Israeli Strike Kills 15 in Gaza Hospital Area',
                    'source': 'CNN',
                    'url': 'https://example.com/western'
                },
                'arabic': {
                    'title': 'قصف إسرائيلي يستهدف مستشفى غزة ويقتل 23 مدنياً',
                    'source': 'Al Jazeera Arabic',
                    'url': 'https://example.com/arabic'
                }
            },
            'specific_contradictions': [{
                'western_claim': {'exact_quote': '15 casualties reported in targeted operation'},
                'arabic_claim': {
                    'exact_quote': '23 مدني قتلوا في القصف',
                    'english_translation': '23 civilians killed in bombing'
                }
            }],
            'contradiction_summary': {
                'severity_level': 'high',
                'main_discrepancy': 'Major discrepancy in casualty numbers: 8-person difference'
            }
        }],
        'aggregate_statistics': {
            'total_contradictions_found': 1
        }
    }
    
    try:
        result = twitter_creator.process_contradiction_and_tweet(sample_data, style="engaging", dry_run=True)
        return jsonify({
            'status': 'success',
            'message': 'Test thread created successfully',
            'result': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    print("🐦 Starting Simple Twitter Contradiction Agent...")
    print("📡 A2A Protocol enabled")
    print("🔧 Available at: http://localhost:5001")
    print("🧵 Thread creation: /test_thread")
    print("📨 A2A endpoint: /a2a/receive")
    print("📊 Status: /a2a/status")
    
    if not twitter_client:
        print("⚠️  Running in SIMULATION MODE (no real Twitter posting)")
        print("   Add your Twitter API keys to enable real posting")
    else:
        print("🔥 REAL TWITTER POSTING ENABLED!")
    
    app.run(debug=True, host='0.0.0.0', port=5001)