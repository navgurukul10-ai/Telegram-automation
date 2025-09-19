# Advanced Telegram Crawler

A sophisticated Telegram crawler designed to discover job opportunities while respecting API limits and maintaining human-like behavior.

## Features

### Core Functionality
- **Human-like Rate Limiting**: Emulates slow human sessions to avoid getting banned
- **Comprehensive State Tracking**: Tracks joined groups, read messages, pending tasks with deduplication
- **Dual Storage**: Stores data to both Elasticsearch and CSV files for redundancy
- **Session Management**: Graceful session token management without reauth on every run
- **Auth Failure Handling**: Logs auth failures without auto-retry (requires manual OTP intervention)

### Advanced Features
- **Simulation Mode**: Stubs Telegram APIs for fast testing and API call analysis
- **ML Pipeline**: Classifies messages based on job post scores using machine learning
- **Phone Number Tracking**: Identifies and tracks phone numbers that post high-quality jobs
- **Group Scoring**: Assigns job discovery scores to groups based on their last 100 messages
- **Proxy Support**: Rotates API calls across two assigned proxies (optional)
- **Daily Limits**: Respects daily limits (10 groups per account, 40 total per day)

### Data Export
- **CSV Files**: Exports all data to CSV files for easy analysis
- **Elasticsearch**: Stores structured data in Elasticsearch for advanced querying
- **Dashboard**: Generates HTML reports for viewing results

## File Structure

```
final-telegram-automation/
├── config.py                 # Configuration management
├── rate_limiter.py          # Human-like rate limiting
├── ml_pipeline.py            # Machine learning for job classification
├── elasticsearch_client.py   # Elasticsearch integration
├── simulation_mode.py        # Simulation mode for testing
├── advanced_crawler.py       # Main crawler implementation
├── dashboard.py              # Dashboard for viewing results
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── README.md                # This file
├── data/                    # Data storage directory
│   ├── groups.csv          # Groups data
│   ├── messages.csv        # Messages data
│   ├── phones.csv          # Phone numbers data
│   └── jobs.csv            # Job listings data
├── logs/                   # Log files
└── sessions/               # Telegram session files
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd final-telegram-automation
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Telegram API credentials
   ```

4. **Setup Elasticsearch (Optional)**
   ```bash
   # Install Elasticsearch locally
   # Or use Docker:
   docker run -d --name elasticsearch -p 9200:9200 -e "discovery.type=single-node" elasticsearch:8.11.0
   ```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Telegram API Configuration
ACCOUNT_1_PHONE=+1234567890
ACCOUNT_1_API_ID=your_api_id_1
ACCOUNT_1_API_HASH=your_api_hash_1

# Crawler Configuration
GROUPS_PER_ACCOUNT_PER_DAY=10
MESSAGES_PER_GROUP=100
SIMULATION_MODE=True

# Rate Limiting
MIN_DELAY=2.0
MAX_DELAY=8.0
MESSAGE_DELAY=1.0
GROUP_JOIN_DELAY=5.0

# Elasticsearch Configuration
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
```

### Universal Groups

Create a `universal_groups.json` file with the groups you want to crawl:

```json
[
  {
    "link": "https://t.me/jobs_mumbai",
    "category": "jobs",
    "priority": "high"
  },
  {
    "link": "https://t.me/tech_jobs_delhi",
    "category": "tech",
    "priority": "medium"
  }
]
```

## Usage

### Running the Crawler

1. **Simulation Mode (Recommended for testing)**
   ```bash
   python advanced_crawler.py
   ```

2. **Real Mode (Production)**
   ```bash
   # Set SIMULATION_MODE=False in .env
   python advanced_crawler.py
   ```

### Viewing Results

1. **Generate Dashboard Report**
   ```bash
   python dashboard.py
   ```

2. **View CSV Files**
   - `data/groups.csv`: Groups joined with job scores
   - `data/messages.csv`: All messages with ML classifications
   - `data/phones.csv`: Phone numbers with job posting statistics
   - `data/jobs.csv`: Extracted job listings

3. **Query Elasticsearch**
   ```python
   from elasticsearch_client import es_client
   
   # Search for jobs
   jobs = await es_client.search_jobs({
       "technologies": ["python", "javascript"],
       "location": "remote",
       "fresher_friendly": True,
       "min_job_score": 0.7
   })
   ```

## Key Components

### Rate Limiter
- Implements human-like delays between API calls
- Prevents getting banned by Telegram
- Configurable delays for different operations

### ML Pipeline
- Classifies messages as job posts using machine learning
- Extracts phone numbers, technologies, locations
- Calculates job scores and group scores
- Identifies fresher-friendly and remote jobs

### Simulation Mode
- Stubs Telegram API calls for testing
- Runs 100x faster than real mode
- Tracks API call statistics
- Perfect for development and testing

### Data Storage
- **CSV Files**: Human-readable data export
- **Elasticsearch**: Structured data for advanced querying
- **Logs**: Comprehensive activity logging

## Daily Workflow

1. **Morning**: Crawler joins up to 40 groups (10 per account)
2. **Processing**: Reads 100 messages from each group
3. **ML Analysis**: Classifies messages and extracts job data
4. **Storage**: Saves data to CSV and Elasticsearch
5. **Evening**: Generates dashboard report

## Monitoring

### Logs
- All activities are logged to `logs/crawler.log`
- Structured logging with different log levels
- Error tracking and performance metrics

### Statistics
- Groups joined per day
- Messages processed
- Job posts found
- High-score phone numbers identified
- API call statistics (in simulation mode)

## Safety Features

- **Rate Limiting**: Prevents API abuse
- **Error Handling**: Graceful failure handling
- **Session Management**: Persistent sessions
- **Deduplication**: Avoids duplicate processing
- **Daily Limits**: Respects Telegram's limits

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Check API credentials in `.env`
   - Ensure phone numbers are in international format
   - Manual OTP intervention may be required

2. **Elasticsearch Connection Issues**
   - Ensure Elasticsearch is running
   - Check connection settings in `.env`
   - Crawler will fall back to CSV-only mode

3. **Rate Limiting Issues**
   - Increase delays in configuration
   - Reduce daily limits
   - Check logs for rate limit warnings

### Debug Mode

Enable debug logging:
```bash
# Set LOG_LEVEL=DEBUG in .env
python advanced_crawler.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test in simulation mode
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Disclaimer

This tool is for educational and research purposes only. Please respect Telegram's Terms of Service and use responsibly. The authors are not responsible for any misuse of this software.
