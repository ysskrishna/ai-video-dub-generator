from models.enums import JobErrorCode

class JobProcessingException(Exception):
    def __init__(self, error_code: JobErrorCode = JobErrorCode.UNKNOWN_ERROR):
        super().__init__(error_code.value)
        self.error_code = error_code