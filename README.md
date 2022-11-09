# gy-multiprocessing

## Installation

### via Github

```bash
pip install git+https://github.com/guangyu-he/gy-multiprocessing
```

### via PyPI

```
pip install gy-multiprocessing
```

## Usage

- initialize a mp pool with a dictionary of lists of processes (and their output) and their runtimes
- generate a mp object inside the loop you want to run parallel
- run the function with the given arguments and callback the mp pool

## Examples

### Multi Processing

```python
import gy_multiprocessing.multiprocessing.multi_process as gymp
import time


def your_func(a_string: int, queue):
    # NOTE! you MUST add a argument for queue and use put() method to fetch the returning value

    print(a_string)
    if a_string % 5 == 0:
        time.sleep(2)

    # NOTE! This is a MUST-have line, or the multi_processing will not end!!!
    queue.put(a_string)


if __name__ == '__main__':
    # the multiprocessing must work in a function or entrance
    # do not use it barely

    """
    # initializing the multi threading instance
    # the default max_process are your cpu max cores
    # max_process could be infinite, but performance will get suffered when the hardware is overloaded
    """
    mp = gymp.MultiProcess(max_process=8)

    # example for multithreading in the loop
    outer_loop_times = 5
    for current_loop_index in range(outer_loop_times):
        # your running arguments, must be tuple
        args = (current_loop_index,)

        """
        # adding tasks in multiprocessing pool
        """
        mp.add(your_func, args)

    # it is also possible to add task outside the loop
    mp.add(your_func, (10,))

    """
    # running tasks in multi threading pool (returned values are optional)
    """
    result = mp.run()
    print(result)
```

### Multi Threads

<b>Note: you can not use multi "children" threads inside the multi threads' method!</b> If you want to use such
structure,please consider using Multi Threads inside the Multi Processing.

```python
import gy_multiprocessing.multithreading.multi_thread as gymt
import time


def your_func(a_string):
    # your single task function

    print(a_string)
    return a_string + "!"


if __name__ == '__main__':
    # the multithreading must work in a function or entrance
    # do not use it barely

    # timing (optional)
    start = time.time()

    """
    # initializing the multi threading instance
    # the default max_threads are your cpu max cores number - 1
    # max_threads can not larger than your cpu max core number
    """
    mt = gymt.MultiThread(max_threads=4)

    # example for multithreading in the loop
    outer_loop_times = 5
    for current_loop_index in range(outer_loop_times):
        args = (str(current_loop_index),)

        """
        # adding tasks in multi threading pool
        """
        mt.add(your_func, args)

    # it is also possible to work without loop
    args = (str(1),)
    mt.add(your_func, args)
    args = (str(2),)
    mt.add(your_func, args)

    """
    # running tasks in multi threading pool (returned values are optional)
    """
    results = mt.run()
    print(results)

    # timing (optional)
    end = time.time() - start
    print("done in {}s".format("%.2f" % end))
```

2022&copy;Guangyu He, for further support please contact author. <br>
Email: <a href="mailto:me@heguangyu.net">me@heguangyu.net</a>
