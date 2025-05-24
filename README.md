# Gaza Media Fact-Check Multi-Agent System 🔍📊

## Overview

A sophisticated multi-agent system designed to analyze and fact-check media coverage of Gaza-related news by comparing Western and Arabic media sources. The system automatically detects contradictions and discrepancies between different media narratives and can automatically generate Twitter threads to highlight these findings.

## 🎯 Key Features

### 🤖 Multi-Agent Architecture
- **Fact-Check Agent** (Port 5000): Main analysis engine with web dashboard
- **Twitter Agent** (Port 5001): Automated Twitter thread creation for contradictions
- **A2A Communication**: Real-time agent-to-agent communication protocol

### 📰 Media Analysis Capabilities
- **Western Media Sources**: CNN, BBC, Reuters, AP News, Guardian, Washington Post, New York Times
- **Arabic Media Sources**: Al Jazeera Arabic, BBC Arabic, RT Arabic, Sky News Arabic, Al Arabiya
- **Smart Article Matching**: AI-powered matching of related articles across language barriers
- **Deep Content Analysis**: Full article content extraction and analysis
- **Contradiction Detection**: Advanced AI analysis to identify factual contradictions

### 🐦 Automated Social Media Integration
- **Twitter Thread Generation**: Automatic creation of fact-check threads
- **Multiple Styles**: Urgent, engaging, and factual presentation styles
- **Smart Formatting**: Optimized for Twitter's character limits
- **Hashtag Generation**: Contextual hashtag creation based on severity and content

### 🌐 Web Dashboard
- **Real-time Analysis**: Live fact-checking interface
- **Visual Results**: Rich, interactive display of contradictions
- **Source Comparison**: Side-by-side comparison of Western vs Arabic sources
- **Export Capabilities**: Save and share analysis results

## 🏗️ System Architecture

```
┌─────────────────────┐    A2A Protocol    ┌─────────────────────┐
│   Fact-Check Agent  │◄──────────────────►│   Twitter Agent     │
│   (Port 5000)       │                    │   (Port 5001)       │
│                     │                    │                     │
│ ├── RSS Feed Parser │                    │ ├── Thread Creator  │
│ ├── AI Analyzer     │                    │ ├── Twitter API     │
│ ├── Web Dashboard   │                    │ └── A2A Receiver    │
│ └── A2A Transmitter │                    │                     │
└─────────────────────┘                    └─────────────────────┘
        │                                            │
        ▼                                            ▼
┌─────────────────────┐                    ┌─────────────────────┐
│   External APIs     │                    │   Twitter Platform  │
│ ├── Google Gemini   │                    │ ├── API v2          │
│ ├── RSS Feeds       │                    │ └── Tweet Posting   │
│ └── News Sources    │                    │                     │
└─────────────────────┘                    └─────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** with pip installed
2. **Google Gemini API Key** (for AI analysis)
3. **Twitter API Keys** (for automated posting - optional)

### Installation & Setup

1. **Clone/Download the project** to your local machine

2. **Install Python dependencies**:
   ```bash
   pip install flask flask-cors requests feedparser beautifulsoup4 smolagents google-generativeai tweepy aiohttp
   ```

3. **Configure API Keys**:
   
   **Google Gemini API** (Required):
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Update `GOOGLE_API_KEY` in both `app.py` and `twitter_agent.py`

   **Twitter API** (Optional - for live posting):
   - Create a Twitter Developer account and app
   - Update the Twitter credentials in `twitter_agent.py`:
     ```python
     TWITTER_API_KEY = "your_api_key"
     TWITTER_API_SECRET = "your_api_secret"
     TWITTER_ACCESS_TOKEN = "your_access_token"
     TWITTER_ACCESS_TOKEN_SECRET = "your_access_token_secret"
     TWITTER_BEARER_TOKEN = "your_bearer_token"
     ```

4. **Start the system**:
   ```bash
   python setup.py
   ```

### Alternative Manual Start

If you prefer to start agents individually:

```bash
# Terminal 1 - Fact-Check Agent
python app.py

# Terminal 2 - Twitter Agent  
python twitter_agent.py
```

## 📖 Usage Guide

### Web Dashboard (Recommended)

1. Open your browser and go to: `http://localhost:5000`
2. Enter search terms:
   - **Western Query**: "Gaza hospital strike" (English)
   - **Arabic Query**: "قصف مستشفى غزة" (Arabic)
3. Click "Start Analysis" and wait for results
4. Review contradictions, differences, and source comparisons
5. If contradictions are found, the Twitter agent will automatically create threads

### API Usage

#### Analyze Media Coverage
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "western_query": "Gaza Israel conflict",
    "arabic_query": "الصراع في غزة",
    "hours_back": 24
  }'
```

#### Check System Health
```bash
curl http://localhost:5000/api/health
```

#### A2A Communication Status
```bash
# Fact-Check Agent Status
curl http://localhost:5000/a2a/status

# Twitter Agent Status  
curl http://localhost:5001/a2a/status
```

#### Trigger Analysis via A2A
```bash
curl -X POST http://localhost:5000/a2a/trigger_analysis \
  -H "Content-Type: application/json" \
  -d '{
    "western_query": "Gaza humanitarian aid",
    "arabic_query": "المساعدات الإنسانية في غزة"
  }'
```

## 🔧 Configuration Options

### Analysis Parameters

- **Hours Back**: How far back to search for articles (default: 24 hours)
- **Article Limit**: Maximum articles per source (configurable in code)
- **Matching Threshold**: AI similarity threshold for article matching
- **Contradiction Sensitivity**: Severity levels for contradiction detection

### Twitter Settings

- **Dry Run Mode**: Test thread creation without posting (default: enabled)
- **Thread Styles**: 
  - `urgent`: Alert-style threads with 🚨 emphasis
  - `engaging`: Conversational style with questions
  - `factual`: Professional, neutral tone
- **Auto-posting**: Enable/disable automatic thread posting

### A2A Protocol

- **Message Queue**: Configurable message retention
- **Retry Logic**: Automatic retry for failed communications
- **Protocol Version**: Standardized message format

## 📊 Output Examples

### Contradiction Detection

```json
{
  "contradiction_found": true,
  "severity": "high",
  "western_claim": "Hospital strike kills 500 civilians",
  "arabic_claim": "Israeli airstrike targets medical facility with 200 casualties",
  "analysis": "Significant discrepancy in casualty numbers and framing of incident"
}
```

### Twitter Thread Output

```
🔍 Something doesn't add up in Gaza coverage...

Media Contradiction Alert: Casualty count discrepancy in hospital incident reporting

Let's break this down 🧵

2/ 🇺🇸 WESTERN SOURCE: CNN
"Hospital strike kills 500 civilians according to Hamas health ministry..."

3/ 🇵🇸 ARABIC SOURCE: Al Jazeera Arabic  
"Israeli airstrike targets medical facility with 200 casualties confirmed..."

4/ ⚡ CONTRADICTION DETECTED:
Significant discrepancy in casualty numbers and attribution sources

Severity: HIGH

5/ 💭 TAKEAWAY:
This is why media literacy matters. Different sources, different stories.

What do you think? 🤔

#FactCheck #MediaBias #Gaza #NewsAnalysis
```

## 🔍 Technical Deep Dive

### AI Analysis Pipeline

1. **RSS Feed Parsing**: Multi-source news aggregation
2. **Content Extraction**: Full article text retrieval
3. **Semantic Matching**: AI-powered article pairing across languages
4. **Contradiction Analysis**: Deep linguistic and factual comparison
5. **Severity Assessment**: Automated rating of discrepancy importance
6. **Report Generation**: Structured output for human and machine consumption

### A2A Communication Protocol

The system implements a standardized Agent-to-Agent communication protocol:

```python
{
  'message_id': 'uuid',
  'timestamp': 'ISO timestamp',
  'source_agent': {'id': 'agent_id', 'name': 'agent_name'},
  'target_agent': 'target_agent_id',
  'message_type': 'contradiction_alert|status_update|analysis_request',
  'payload': {...},
  'protocol_version': '1.0'
}
```

### Error Handling & Resilience

- **Graceful Degradation**: System continues operating if one agent fails
- **Retry Logic**: Automatic retry for failed API calls
- **Fallback Modes**: Alternative analysis methods if primary fails
- **Rate Limiting**: Respect for external API limits
- **Circuit Breakers**: Automatic service protection

## 🔒 Security & Privacy

### API Key Management
- **Environment Variables**: Store sensitive keys outside code
- **Key Rotation**: Regular API key updates recommended
- **Access Control**: Limit API permissions to minimum required

### Data Handling
- **No Persistent Storage**: Articles processed in memory only
- **Anonymized Logging**: No personal data in logs
- **CORS Protection**: Web dashboard security headers
- **Rate Limiting**: Protection against abuse

### Twitter Integration
- **Dry Run Default**: Safe testing without actual posting
- **Content Review**: Manual review option before posting
- **Account Safety**: Separate bot account recommended

## 🛠️ Development & Customization

### Adding New Media Sources

```python
# In app.py - Western sources
western_sources = {
    "Your News Source": "https://example.com/rss.xml"
}

# In app.py - Arabic sources  
arabic_sources = {
    "Your Arabic Source": "https://example.com/arabic-rss.xml"
}
```

### Custom Analysis Tools

```python
@tool
def your_custom_analysis_tool(param: str) -> str:
    """Your custom analysis function"""
    # Your analysis logic
    return result
```

### Twitter Thread Customization

```python
def create_custom_thread_style(self, report: dict) -> List[dict]:
    """Create custom Twitter thread style"""
    # Your custom thread formatting
    return thread_tweets
```

### A2A Message Types

```python
# Custom message types
message_types = [
    'contradiction_alert',
    'analysis_request', 
    'status_update',
    'custom_notification'  # Your custom type
]
```

## 🧪 Testing

### Manual Testing

1. **System Health Check**:
   ```bash
   curl http://localhost:5000/api/health
   curl http://localhost:5001/a2a/status
   ```

2. **Sample Analysis**:
   ```bash
   python setup.py  # Runs built-in test
   ```

3. **Twitter Thread Test**:
   ```bash
   curl -X POST http://localhost:5001/test_thread \
     -H "Content-Type: application/json" \
     -d '{"test": true}'
   ```

### A2A Communication Test

The setup script automatically tests:
- Agent startup and health
- A2A message exchange
- Sample analysis pipeline
- Twitter notification flow

## 🐛 Troubleshooting

### Common Issues

**"Google API Key Invalid"**
- Verify API key is correct
- Check Google AI Studio quotas
- Ensure Gemini API is enabled

**"Twitter Authentication Failed"**  
- Regenerate Twitter API keys
- Wait 10-15 minutes after regeneration
- Verify app permissions are "Read and Write"
- Check rate limits

**"No Articles Found"**
- Try broader search terms
- Increase `hours_back` parameter
- Check RSS feed availability
- Verify internet connection

**"A2A Communication Failed"**
- Ensure both agents are running
- Check port availability (5000, 5001)
- Verify firewall settings
- Review agent logs

### Debug Mode

Enable verbose logging by modifying the agents:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Log Locations

- **Fact-Check Agent**: Console output from `python app.py`
- **Twitter Agent**: Console output from `python twitter_agent.py`
- **Setup Script**: Console output from `python setup.py`

## 📈 Performance Optimization

### Speed Improvements
- **Parallel Processing**: RSS feeds fetched concurrently
- **Caching**: Article content cached during analysis
- **Connection Pooling**: Reused HTTP connections
- **Batch Processing**: Multiple articles analyzed together

### Resource Management
- **Memory Usage**: Articles processed in batches
- **API Rate Limits**: Automatic throttling and backoff
- **Connection Limits**: Configurable concurrent connections
- **Timeout Handling**: Graceful timeout management

## 🔮 Future Enhancements

### Planned Features
- **Multi-language Support**: Support for more languages beyond Arabic/English
- **Historical Analysis**: Long-term trend analysis of media bias
- **Social Media Integration**: Facebook, Instagram, TikTok analysis
- **Real-time Monitoring**: Continuous monitoring with webhooks
- **Advanced Visualizations**: Interactive charts and graphs
- **Machine Learning**: Improved contradiction detection with custom models

### Integration Possibilities
- **Slack/Discord Bots**: Real-time notifications
- **Email Alerts**: Automated contradiction reports
- **Database Storage**: Persistent analysis history
- **API Gateway**: Enterprise-grade API management
- **Mobile App**: React Native or Flutter mobile interface

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch
3. Follow existing code style
4. Add tests for new features
5. Submit pull request

### Code Style
- **Python**: PEP 8 compliance
- **JavaScript**: ES6+ standards
- **HTML/CSS**: Modern web standards
- **Documentation**: Comprehensive docstrings

### Testing Guidelines
- **Unit Tests**: Test individual functions
- **Integration Tests**: Test A2A communication
- **End-to-End Tests**: Full pipeline testing
- **Performance Tests**: Load and stress testing

## 📄 License

This project is open source. See LICENSE file for details.

## 🙏 Acknowledgments

- **Google Gemini AI**: Advanced language model capabilities
- **Twitter API**: Social media integration platform
- **RSS Feed Providers**: News sources for analysis
- **Flask Framework**: Web application backbone
- **Smolagents**: AI agent framework
- **Open Source Community**: Libraries and tools used

## 📞 Support

### Getting Help
- **Documentation**: Check this README first
- **Issues**: Create GitHub issues for bugs
- **Discussions**: Use GitHub discussions for questions
- **Email**: Contact project maintainers

### Reporting Bugs
Please include:
- System information (OS, Python version)
- Error messages and logs
- Steps to reproduce
- Expected vs actual behavior

### Feature Requests
- Use GitHub issues with "enhancement" label
- Provide detailed use case description
- Include mockups or examples if applicable

---

**⚠️ Important Notes:**

1. **Ethical Use**: This tool is designed for media literacy and fact-checking. Use responsibly and always verify findings with primary sources.

2. **API Costs**: Google Gemini API usage may incur charges. Monitor your usage and set appropriate limits.

3. **Twitter Compliance**: Ensure your use of the Twitter integration complies with Twitter's Terms of Service and API usage policies.

4. **Accuracy Disclaimer**: AI analysis may contain errors. Always perform human verification of important findings.

5. **Legal Considerations**: Be aware of copyright and fair use laws when analyzing and sharing news content.

---

*Built with ❤️ for media transparency and fact-checking* 