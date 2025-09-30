# Channel Monitoring Guide

This guide explains how to set up and use the automated YouTube channel monitoring system.

## Overview

The channel monitoring system automatically:
- Scans YouTube channels for new videos daily
- Applies configurable filters to videos
- Adds qualifying videos to the processing queue
- Processes videos gradually to avoid rate limiting
- Forwards processed video data to n8n workflows

## Quick Start

### 1. Add a Channel

```bash
# Basic channel addition
youtube-chat channel add https://www.youtube.com/@channelname

# With filters and custom interval
youtube-chat channel add https://www.youtube.com/@channelname \
  --check-interval 24 \
  --no-shorts \
  --min-duration 300 \
  --include-keywords "tutorial,guide"
```

### 2. Start Background Service

```bash
# Start the monitoring service
youtube-chat service start --daemon

# Check service status
youtube-chat service status
```

### 3. Monitor Progress

```bash
# View statistics
youtube-chat stats

# Check service logs
youtube-chat service logs --lines 50
```

## Channel Management

### Adding Channels

**Basic Addition:**
```bash
youtube-chat channel add https://www.youtube.com/@channelname
```

**With Filters:**
```bash
youtube-chat channel add https://www.youtube.com/@channelname \
  --check-interval 12 \
  --no-shorts \
  --no-live \
  --min-duration 300 \
  --max-duration 3600 \
  --include-keywords "AI,machine learning,tutorial" \
  --exclude-keywords "shorts,live,stream"
```

**Supported URL Formats:**
- `https://www.youtube.com/@channelname`
- `https://www.youtube.com/channel/UC...`
- `https://www.youtube.com/c/channelname`
- `https://www.youtube.com/user/username`

### Listing Channels

```bash
# List all channels
youtube-chat channel list

# List only active channels
youtube-chat channel list --active-only
```

### Updating Channels

```bash
# Update check interval
youtube-chat channel update CHANNEL_ID --check-interval 6

# Enable/disable monitoring
youtube-chat channel update CHANNEL_ID --active
youtube-chat channel update CHANNEL_ID --inactive

# Update multiple settings
youtube-chat channel update CHANNEL_ID \
  --check-interval 12 \
  --active
```

### Removing Channels

```bash
# Remove a channel (with confirmation)
youtube-chat channel remove CHANNEL_ID

# Force removal without confirmation
youtube-chat channel remove CHANNEL_ID --force
```

## Filtering System

### Duration Filters

```bash
# Minimum duration (5 minutes)
--min-duration 300

# Maximum duration (1 hour)
--max-duration 3600

# Exclude YouTube Shorts (< 60 seconds)
--no-shorts
```

### Content Filters

```bash
# Include only videos with specific keywords
--include-keywords "python,programming,tutorial"

# Exclude videos with specific keywords
--exclude-keywords "shorts,live,stream,music"

# Exclude live streams
--no-live
```

### Quality Filters

```bash
# Minimum view count
--min-views 1000

# Date range (for bulk import)
--date-from 2025-01-01
--date-to 2025-12-31
```

### Filter Examples

**Educational Content:**
```bash
youtube-chat channel add https://www.youtube.com/@educhannel \
  --min-duration 600 \
  --include-keywords "tutorial,lesson,course,guide" \
  --exclude-keywords "shorts,music,gaming" \
  --no-shorts
```

**Tech Reviews:**
```bash
youtube-chat channel add https://www.youtube.com/@techchannel \
  --min-duration 300 \
  --max-duration 1800 \
  --include-keywords "review,unboxing,comparison" \
  --min-views 5000
```

**Programming Content:**
```bash
youtube-chat channel add https://www.youtube.com/@codechannel \
  --min-duration 900 \
  --include-keywords "python,javascript,coding,programming" \
  --exclude-keywords "shorts,live,music" \
  --no-shorts \
  --no-live
```

## Manual Scanning

### Scan All Channels

```bash
# Scan all active channels
youtube-chat channel scan --all

# Force scan (ignore last check time)
youtube-chat channel scan --all --force
```

### Scan Specific Channel

```bash
# Scan specific channel
youtube-chat channel scan --channel-id CHANNEL_ID

# Force scan specific channel
youtube-chat channel scan --channel-id CHANNEL_ID --force
```

### Scan Results

The scan command returns:
- **Total videos found**: Raw count from YouTube API
- **After filtering**: Videos remaining after applying filters
- **New videos**: Videos not already in database
- **Queued for processing**: Videos added to processing queue
- **Skipped**: Videos already in database

## Background Service

### Service Management

```bash
# Start service in daemon mode
youtube-chat service start --daemon

# Start service in foreground (for debugging)
youtube-chat service start

# Stop service
youtube-chat service stop

# Check service status
youtube-chat service status

# View service logs
youtube-chat service logs --lines 100
```

### Service Schedule

**Default Schedule:**
- **Channel scanning**: Daily at 8:00 AM
- **Video processing**: Every 2 hours
- **Health checks**: Every 30 minutes
- **Cleanup**: Daily at midnight

**Customizing Schedule:**
Edit the configuration in `config/default_config.yaml`:
```yaml
service:
  channel_scan_hour: 8      # Hour to scan channels
  processing_interval: 2    # Hours between processing
  health_check_interval: 30 # Minutes between health checks
```

### Service Status Information

The status command shows:
- **Service state**: Running/stopped
- **PID file location**: Process ID file path
- **Log file location**: Service log file path
- **Scheduled jobs**: Next run times for each job
- **Queue statistics**: Current queue status
- **Processing limits**: Daily quota usage

## Rate Limiting Integration

### How It Works

1. **Channel scanning** finds new videos and adds them to the database
2. **Videos are queued** for processing with smart scheduling
3. **Processing respects limits**: Maximum 5 videos per day
4. **Smart distribution**: Videos spread throughout the day
5. **Automatic backoff**: On rate limiting, delays increase exponentially

### Queue Management

```bash
# View queue status
youtube-chat service status

# View processing statistics
youtube-chat stats

# View processing history
youtube-chat history --limit 20
```

### Processing Timeline

**Example for 5 videos/day:**
- Video 1: Processed immediately
- Video 2: Processed ~5 hours later
- Video 3: Processed ~5 hours after that
- Video 4: Processed ~5 hours after that
- Video 5: Processed ~4 hours after that
- Next day: Quota resets, cycle repeats

## Monitoring and Analytics

### Statistics

```bash
# Comprehensive statistics
youtube-chat stats
```

Shows:
- **Channel statistics**: Active/total channels
- **Video statistics**: Total/processed/pending videos
- **Processing rate**: Success rate and daily quota usage
- **Recent activity**: Videos processed in last 24 hours

### History

```bash
# View processing history
youtube-chat history --limit 50

# View channel-specific history
youtube-chat history --channel-id CHANNEL_ID --limit 20
```

### Logs

```bash
# View recent service logs
youtube-chat service logs --lines 100

# Follow logs in real-time
youtube-chat service logs --follow

# View logs from specific time
youtube-chat service logs --since "2025-09-30 08:00:00"
```

## Best Practices

### Channel Selection

1. **Choose quality channels** with regular, valuable content
2. **Use appropriate filters** to avoid noise (shorts, live streams)
3. **Set reasonable intervals** (24 hours for most channels)
4. **Monitor quota usage** to stay within limits

### Filter Configuration

1. **Start broad, then narrow** - Add filters gradually
2. **Use keyword filters** to focus on relevant content
3. **Set duration limits** to exclude very short/long videos
4. **Test with dry-run** before committing to settings

### Service Management

1. **Run as daemon** for continuous monitoring
2. **Monitor logs regularly** for issues
3. **Check statistics** to track performance
4. **Restart service** if issues persist

### Quota Management

1. **Monitor daily usage** with `youtube-chat stats`
2. **Adjust MAX_VIDEOS_PER_DAY** based on needs
3. **Use filters effectively** to reduce processing load
4. **Consider API quota limits** when adding many channels

## Troubleshooting

### Common Issues

**No new videos found:**
- Check if channel has posted recently
- Verify filters aren't too restrictive
- Use `--force` flag to ignore last check time

**Videos not processing:**
- Check service is running: `youtube-chat service status`
- Review rate limiting: `youtube-chat stats`
- Check logs: `youtube-chat service logs`

**Service won't start:**
- Check for existing instances
- Review logs for errors
- Ensure database isn't locked

**High failure rate:**
- Rate limiting is working correctly
- Videos will be processed gradually
- Check logs for specific errors

### Getting Help

1. Check service status and logs
2. Review statistics for quota usage
3. Test manual scanning
4. Check API key configuration
5. Consult the main troubleshooting guide

## Advanced Configuration

### Custom Scheduling

Edit `config/default_config.yaml` to customize:
- Scan times and intervals
- Processing frequency
- Health check intervals
- Cleanup schedules

### Database Optimization

The system automatically:
- Cleans up old queue entries
- Optimizes database performance
- Maintains indexes for fast queries

### Integration with n8n

Configure automatic forwarding:
```bash
youtube-chat n8n configure http://your-n8n-server/webhook/endpoint
```

Processed videos will be automatically sent to your n8n workflow with:
- Video metadata (title, description, duration, etc.)
- Full transcript text
- Processing timestamp
- Channel information
