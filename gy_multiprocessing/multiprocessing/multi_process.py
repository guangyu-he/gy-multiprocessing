# loading multiprocessing package
from multiprocessing import Process, cpu_count, get_context

# importing relevant types
from multiprocessing.context import Process as ProcessType
from types import FunctionType, MethodType

# importing necessary modules
import time
import inspect
import warnings


class MultiProcess:

    def __init__(self, max_process: int = cpu_count(), silent: bool = False):
        """
        Args:
            max_process (int, optional): the maximum number of parallel running processes. Defaults to max CPU core
            silent (bool, optional): whether to silence logs. Defaults to False.

        Using Process method from multiprocessing to process the multiprocessing tasks
        """

        # error handling
        if type(max_process) is not int:
            raise TypeError(f"Wrong type of max process '{max_process}', must be an integer!")
        if max_process == 0:
            print(f"max process is set to 0: multiprocessing will not be used.")
        if max_process > cpu_count():
            warnings.warn("too much sub processes, performance may get influenced!")
        if isinstance(silent, bool) is False:
            raise TypeError(f"Wrong type of silent '{silent}', must be a boolean!")

        # set max processing pool equals to the cpu core number
        self.max_process: int = max_process

        # show log in console
        self.silent: bool = silent

        # see if there is a queue object in user function parameters
        self.has_queue_param: bool = True

        # see if there is a valid queue.put() method
        self.has_queue_put: bool = True

        # use to store the multiprocessing processes
        self.mp_pool_list: list[dict] = []

        # use to store the result from each process when multiprocessing is not used
        self.non_mp_result: list = []

    class _NoneQueue:
        """
        A class to replace queue when multiprocessing is not used, and avoid error when calling queue.put()
        """

        def put(*args):
            pass

    def test(self, func, args: tuple) -> bool:
        """
        Testing the function and arguments to see if they are suitable for multiprocessing
        Args:
            func (function): the function to be called
            args (tuple): the arguments to be passed to the function
        Returns:
            bool: whether the function and arguments are suitable for multiprocessing
        """
        test_passed: bool = True

        if not isinstance(func, FunctionType) and not isinstance(func, MethodType):
            print("Wrong type of func, must be a FunctionType!")
            test_passed = False
        if not isinstance(args, tuple):
            print("Wrong type of args, must be a tuple!")
            test_passed = False

        parameters = inspect.signature(func).parameters
        if "queue" not in parameters and self.max_process > 0:
            print(f"queue parameter not found in '{func.__name__}'")
            test_passed = False

        return test_passed

    def add(self, func, args: tuple, process_name: str = ""):
        """
        Args:
            func (function): the function to be called
            args (tuple): the arguments to be passed to the function
            process_name (str, optional): the name of the process. Defaults to "".

        Adding a task into the multi threading pool
        """

        # TODO! func: FunctionType in PyCharm will warns:
        # TODO! Expected type 'FunctionType', got '(a_string: Any) -> None' instead

        # error handling
        if not isinstance(func, FunctionType) and not isinstance(func, MethodType):
            raise TypeError("Wrong type of func, must be a FunctionType!")
        if not isinstance(args, tuple):
            raise TypeError("Wrong type of args, must be a tuple!")
        if not isinstance(process_name, str):
            raise TypeError("Wrong type of process name, must be a str!")

        # check if there is a queue parameter in the user function
        parameters = inspect.signature(func).parameters
        if "queue" not in parameters:
            self.has_queue_param = False

        if self.max_process == 0:
            # if max process is set to 0, multiprocessing will not be used

            # initialize time and result
            current_time = time.time()

            if self.has_queue_param:
                # there is queue parameter in the func, but multiprocessing is not used
                # then set up a fake queue object to avoid error when calling queue.put()
                args = args + (self._NoneQueue,)

            # execute the function
            get_result = func(*args)

            # store the result from the function
            self.non_mp_result.append(get_result)

            time_cost = time.time() - current_time
            if not self.silent:
                if process_name != "":
                    process_name = f"process: '{process_name}'"
                else:
                    process_name = "process"
                print(
                    f"{process_name} done in {format(time_cost, '.1f')}s with result {get_result}")
        else:
            if not self.test(func, args):
                raise Exception("Function and arguments are not suitable for multiprocessing!")

            # a get context method for get return value
            # NOTE! a q.put() method must include in the called func and its args
            queue_instance = get_context('spawn').Queue()

            # initialize multiprocessing for core loop function
            process: ProcessType = Process(target=func, args=args + (queue_instance,))
            # set dict inside the process list
            process_list_dict: dict = {'process': process, 'start_time': int, 'process_result': queue_instance,
                                       'process_name': process_name}
            self.mp_pool_list.append(process_list_dict)

    def each_process_func(self, list_of_processes: list) -> list:
        for processing_index, each_processing_process in enumerate(list_of_processes):

            # check each process
            current_time = time.time()
            time_cost = current_time - each_processing_process['start_time']

            # initialize the result
            get_result = None

            if each_processing_process['process'].exitcode is None:
                # the process is still alive
                continue

            # the following code is for the process is done
            elif each_processing_process['process'].exitcode == 0:
                # the process is done successfully
                try:
                    # if the process is not alive, use a small timeout to see if there is a valid non-empty queue
                    get_result = each_processing_process['process_result'].get(timeout=0.05)
                except Exception as e:
                    if repr(e) == "Empty()":
                        # script finds no queue.put() method in the user function
                        self.has_queue_put = False
                        get_result = None
            elif each_processing_process['process'].exitcode == 1:
                # means there is an error occurred in this process
                get_result = f"{each_processing_process['process_name'] + ' '}FAILED"
            else:
                # the process is done with an unknown error
                # shutdown the process and raise an error
                each_processing_process['process'].kill()
                list_of_processes.pop(processing_index)
                raise Exception(f"Unknown error occurred in process: {each_processing_process['process'].name}")

            if not self.silent:
                print(
                    f"process: {str(each_processing_process['process'].name)} done in {format(time_cost, '.1f')}s with {each_processing_process['process_name']} and result {get_result}") \
                    if each_processing_process['process_name'] != "" \
                    else print(
                    f"process: {str(each_processing_process['process'].name)} done in {format(time_cost, '.1f')}s with result {get_result}")

            # saving the result into the full process list, corresponding to the process name
            for process_index, each_process in enumerate(self.mp_pool_list):
                if each_processing_process['process'].name == each_process['process'].name:
                    self.mp_pool_list[process_index]['process_result'] = get_result

            # as long as the process is done, kill it
            each_processing_process['process'].kill()

            # remove the stopped task from processing list
            list_of_processes.pop(processing_index)

            # everytime the loop find a finished process, break the loop and return the list
            # then let the outer while loop to check if there is any process left
            # if there is still process alive, the outer while loop will continue give process to
            # the internal for loop
            break

        return list_of_processes

    def run(self) -> list:
        """
        Returns:
            the result list of returned value from each tasks

        Run all the processes
        """

        if self.max_process == 0:
            # not using multiprocessing at all
            return self.non_mp_result

        else:
            # initializing a processing list with max length of max_process
            processing_list: list = []

            if len(self.mp_pool_list) <= self.max_process:
                # if the number of tasks is less than max_process number
                for process_index, each_process in enumerate(self.mp_pool_list):
                    # put all tasks in the pool
                    processing_list.append(each_process)
                    each_process['start_time'] = time.time()
                    each_process['process'].start()

                while processing_list:
                    processing_list = self.each_process_func(processing_list)

            else:
                # if the number of tasks is more than max_process number
                for pool_index, each_process in enumerate(self.mp_pool_list):
                    if len(processing_list) < self.max_process:
                        # if there is less than max_process number of tasks in the pool
                        # add a new task in it
                        processing_list.append(each_process)
                        each_process['start_time'] = time.time()
                        each_process['process'].start()
                    while processing_list:

                        if len(processing_list) < self.max_process and pool_index != len(self.mp_pool_list) - 1:
                            # if all tasks are in the pool then wait until all tasks are finished
                            # or break the loop to add a new task in the pool
                            break

                        processing_list = self.each_process_func(processing_list)

            if not self.has_queue_put:
                warnings.warn("You may miss the queue.put() method in your function. The results may not correct!")

            return [res['process_result'] for res in self.mp_pool_list]
