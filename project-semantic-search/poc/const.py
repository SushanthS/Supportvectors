#Sentence transformer model
MODEL = 'sentence-transformers/all-mpnet-base-v2'

#File Handling
CHUNK_SIZE = 512
PATH = "books"

#nlp_model
NLP_MODEL = 'en_core_web_sm'

#query result
TOP_K = 4

#logger
"""
The following are the supported levels ordered in increasing severity:
TRACE(5): low-level details of the program's logic flow.
DEBUG(10): Information that is helpful during debugging.
INFO(20): Confirmation that the application is behaving as expected.
SUCCESS(25): Indicates an operation was successful.
WARNING(30): Indicates an issue that may disrupt the application in the future.
ERROR(40): An issue that needs your immediate attention but won't terminate the program.
CRITICAL(50): A severe issue that can terminate the program, like "running out of memory".
Loguru defaults to DEBUG as minimum level
"""
LOG_LEVEL = "INFO"


