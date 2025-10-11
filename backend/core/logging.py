import json
import logging


class JsonFormatter(logging.Formatter):
    """Custom formatter to include extra fields in JSON format."""
    
    def format(self, record):
        # Create base log entry
        log_entry = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }
        
        # Add any extra fields dynamically
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 'msecs', 
                          'relativeCreated', 'thread', 'threadName', 'processName', 'process']:
                log_entry[key] = value
        
        return json.dumps(log_entry)


def setup_logging():
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)
