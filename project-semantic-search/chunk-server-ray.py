#  -------------------------------------------------------------------------------------------------
#   Copyright (c) 2023.  SupportVectors AI Lab
#   This code is part of the training material, and therefore part of the intellectual property.
#   It may not be reused or shared without the explicit, written permission of SupportVectors.
#  #
#   Use is limited to the duration and purpose of the training at SupportVectors.
#  #
#   Author: Asif Qamar
#  -------------------------------------------------------------------------------------------------
#
import logging as log
from logging.handlers import SysLogHandler

import ray
from ray import serve
from starlette.requests import Request

from datetime import datetime

from svlearn.config.configuration import ConfigurationMixin
from svlearn.utils.compute_utils import get_port
from svlearn.text.text_chunker import ChunkText

log.basicConfig(format='%(asctime)s - %(filename)s:%(lineno)d %(levelname)s - %(message)s',level=log.INFO)
logger = log.getLogger()
logger.addHandler(SysLogHandler('/dev/log'))

@serve.deployment(
    # specify the number of GPU's available; zero if it is run on cpu
    ray_actor_options={"num_gpus": 0},
    # the number of instances of the  deployment in the cluster
    autoscaling_config={"min_replicas": 0, "max_replicas": 1},
    # the concurrency of the deployment
    #max_concurrent_queries=100,
)
class CleanChunkModel:
    """
    This class is the entry point for the clean/chunk service.
    """
    def __init__(self):
        super().__init__()
        self.chunker = ChunkText()

    async def __call__(self, request: Request):
        """
        This method is called when the service is invoked, and it returns the chunks of the text.
        :param request: the request object, with the text to be chunked
        :return: the chunks of the text, as a list inside a json object
        """
        log.info(f"Received request: {request}")
        log.info(f"similarity_threshold: {self.chunker.similarity_threshold}")
        log.info(f"chunk_size: {self.chunker.chunk_size}")
        payload = await request.json()
        text = payload['text']
        tid = payload['id']
        #chunks = text
        start_time = datetime.now()
        chunks = self.chunker.create_chunks(text)
        end_time = datetime.now()
        text_chunk_time = end_time - start_time
        
        log.info(f"Returning chunks: {len(chunks)}, {text_chunk_time.total_seconds()}")
        return {'id': tid, 'chunks': chunks, 'chunk_time':  (text_chunk_time.total_seconds()*1000)+(text_chunk_time.microseconds/1000)}


if __name__ == '__main__':
    #ray.init(address='ray://localhost:10001')
    ray.init()

    mixin = ConfigurationMixin()
    config = mixin.load_config()
    #url = config['services']['clean_chunk']
    #port = get_port(url)

    entrypoint = CleanChunkModel.bind()  # bind() comes from the decorator
    #serve.run(entrypoint, port=port, host="0.0.0.0", route_prefix="/chunker")
    serve.run(target=entrypoint, blocking=True, name="chunker", route_prefix="/chunker")
    log.info(f"Started serving CleanChunkModel")
