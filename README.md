# yotaq - Your Own Task Queue for Python

So you need a task queue for your Python project. Sure you could check [celery](http://www.celeryproject.org/), and after three months trying to understand the basic configuration options you'll be good to go. Or you could use a simpler task queue like [huey](https://github.com/coleifer/huey) or [rq](http://python-rq.org/).

Why don't you try building **your own** task queue? Well, now you can!

First, we'll use [redis](https://redis.io/) as our message broker. There's no need to install redis, we'll use docker so we keep our environment clean. Open a terminal and run:

    docker run -p 6379:6379 redis
    
There you go. Now let's create a Python virtual environment to handle our dependencies, which are the redis python library and [dill](https://pypi.python.org/pypi/dill):

    virtualenv env
    source env/bin/activate
    pip install redis dill
    
Pretty good. Our python code will use _dill_ to serialize the functions to be run and redis to store the tasks. 

## The client

The _client_ will issue the tasks to be enqueued, so open up an editor, create a file called `client.py`. There, we'll define the _task_ that will be sent to the workers, for example:

```python
import random
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def do_something(arg1, arg2):
    """ Dummy function that just waits a random amount of time """

    logger.info("Performing task with arg1=%s and arg2=%s", arg1, arg2)
    time.sleep(random.uniform(0.0, 1))
```

Now we need to configure our redis client:

    import redis
    
    r = redis.Redis(
        host='localhost',
        port=6379
    )
    
Once that's done, we're ready to generate and enqueue some tasks:

    import dill
    
    # Generate N tasks
    NUM_TASKS = 100
    logger.info("Generating %i tasks", NUM_TASKS)

    for i in range(NUM_TASKS):

        # Generate two random arguments                                                                                       
        a1 = random.randrange(0, 100)
        a2 = random.randrange(0, 100)

        # Serialize the task and its arguments                                                                                
        data = dill.dumps((do_something, [a1, a2]))

        # Store it in the message broker                                                                                      
        r.rpush('tasks', data)

# The worker

The _worker_ will do the work (who would've guessed?) by keeping an eye on the task queue and fetching the available tasks to run. Pretty simple. So open up an editor to create our `worker.py` file and write the following:

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

Boom! You're done! Run some workers with:

    python worker.py
    
You can even run them in other machines, such scaling, very distributed. And then run the client to create some tasks.

    python client.py
    
How's that for less than 50 lines of code?
