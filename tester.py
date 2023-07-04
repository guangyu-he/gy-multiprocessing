import time

import gy_multiprocessing as gymp


def your_func(a_string: int, queue):
    # NOTE! you MUST add a argument for queue and use put() method to fetch the returning value

    # print(a_string)
    if a_string % 5 == 0:
        raise Exception("stupid")
    if a_string % 7 == 0:
        time.sleep(5)
    else:
        time.sleep(2)

    # NOTE! This is a MUST-have line, or the multi_processing will not end!!!
    queue.put(a_string)


if __name__ == '__main__':
    # the multiprocessing must work in a function or entrance
    # do not use it barely

    """
    # initializing the multiprocessing instance
    # the default max_process are your cpu max cores
    # max_process could be infinite, but performance will get suffered when the hardware is overloaded
    """
    mp = gymp.MultiProcess(max_process=10)

    # example for multiprocessing in the loop
    outer_loop_times = 10
    for current_loop_index in range(outer_loop_times):
        # your running arguments, must be tuple
        args = (current_loop_index,)

        """
        # adding tasks in multiprocessing pool
        """
        mp.add(your_func, args, process_name=str(current_loop_index))

    # it is also possible to add task outside the loop
    mp.add(your_func, (10,))

    """
    # running tasks in multiprocessing pool (returned values are optional)
    """
    result = mp.run()
    print(result)
