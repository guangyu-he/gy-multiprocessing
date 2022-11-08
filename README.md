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

#### no returned value from the function required

```python
import gy_multiprocessing.multiprocessing as gymp


def your_func(a_string: str):
    print(a_string)


if __name__ == '__main__':
    mp_pool = gymp.init()
    outer_loop_times = 10  # for example
    for current_loop_index in range(outer_loop_times):
        # your number of loop tasks that want to run parallel
        # optional arguments:
        # process_name: the name of the process
        # max_threads: the number of max parallel processes
        # process_log: whether to show the process pool log when process is running to the end
        mp = gymp.multi_process.MultiProcess(mp_pool, outer_loop_times, current_loop_index)

        # your running arguments, must be tuple
        args = (str(outer_loop_times),)

        # run function using arguments and get callback mp_pool
        mp_pool = mp.run(your_func, args)
```

#### need to check the returned value from the function

```python
import gy_multiprocessing.multiprocessing as gymp


def your_func(a_string: str, queue):
    # NOTE! you must add a argument for queue and use put() method to fetch the returning value
    queue.put(a_string)


if __name__ == '__main__':
    mp_pool = gymp.init()
    outer_loop_times = 10  # for example
    for current_loop_index in range(outer_loop_times):
        # your number of loop tasks that want to run parallel
        # using withqueue method to show returned value in the console

        # optional arguments:
        # process_name: the name of the process
        # max_threads: the number of max parallel processes
        # process_log: whether to show the process pool log when process is running to the end
        mp = gymp.multi_process_withqueue.MultiProcess(mp_pool, outer_loop_times, current_loop_index)

        # your running arguments, must be tuple
        args = (str(outer_loop_times),)

        # run function using arguments and get callback mp_pool
        # returned value will be shown after each process is done
        mp_pool = mp.run(your_func, args)
```

### Multi Threads

<b>Note: you can not use multi "children" threads inside the multi threads method!</b> If you want to use such
structure,
please consider using Multi Threads inside the Multi Processing.

```python
import gy_multiprocessing as gymp


def your_func(a_string):
    print(a_string)


if __name__ == '__main__':

    mt = gymp.multithreading.multi_thread.MultiThread()
    pool, pool_list = mt.init()
    outer_loop_times = 10  # for example
    for current_loop_index in range(outer_loop_times):
        # your number of loop tasks that want to run using max cpu threads - 1
        args = (str(outer_loop_times),)
        pool_list = mt.add(pool, pool_list, your_func, args)
    mt.run(pool, pool_list)
```

2022&copy;Guangyu He, for further support please contact author. <br>
Email: <a href="mailto:me@heguangyu.net">me@heguangyu.net</a>
