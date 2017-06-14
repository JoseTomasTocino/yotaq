import time
import random
import logging

import redis
import dill


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main_worker():

    # Configure our redis client                                                                                              
    r = redis.Redis(
        host='localhost',
        port=6379
    )

    while True:
        # Wait until there's an element in the 'tasks' queue                                                                  
        key, data = r.brpop('tasks')

        # Deserialize the task                                                                                                
        d_fun, d_args = dill.loads(data)

        # Run the task                                                                                                        
        d_fun(*d_args)


if __name__ == '__main__':
    main_worker()
