from multiprocessing import Process, cpu_count, get_context
from multiprocessing.context import Process as ProcessType
import time
from types import FunctionType, MethodType
import warnings


class MultiProcess:

    def __init__(self, max_process: int = cpu_count()):
        """
        Args:
            max_process (int, optional): the maximum number of parallel running processes. Defaults to max CPU core

        Using Process method from multiprocessing to process the multiprocessing tasks
        """

        # error handling
        if type(max_process) is not int:
            raise TypeError("Wrong type of max_threads, must be an integer!")
        if max_process == 0:
            raise IndexError("max_threads are set to be 0!")
        if max_process > cpu_count():
            warnings.warn("too much sub processes, performance may get influenced!")

        # set max processing pool equals to the cpu core number
        self.max_process = max_process

        self.mp_pool_list: list[dict] = []

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
            raise TypeError("Wrong type of process_name, must be a str!")

        # a get context method for get return value
        # NOTE! a q.put() method must include in the called func and its args
        queue_instance = get_context('spawn').Queue()

        # initialize multiprocessing for core loop function
        process: ProcessType = Process(target=func, args=args + (queue_instance,))
        # set dict inside the process list
        process_list_dict = {'process': process, 'start_time': int, 'process_result': queue_instance,
                             'process_name': process_name}
        self.mp_pool_list.append(process_list_dict)

    def run(self) -> list:
        """
        Returns:
            the result list of returned value from each tasks

        Run all the processes
        """

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
                time.sleep(0.05)
                for processing_index, each_processing_process in enumerate(processing_list):
                    if not each_processing_process['process'].is_alive():
                        # check each process
                        current_time = time.time()
                        time_cost = current_time - each_processing_process['start_time']
                        get_result = each_processing_process['process_result'].get()
                        print(
                            f"process: {str(each_processing_process['process'].name)} done in: {format(time_cost, '.1f')}s with {each_processing_process['process_name']} and result {get_result}") \
                            if each_processing_process['process_name'] != "" \
                            else print(
                            f"process: {str(each_processing_process['process'].name)} done in: {format(time_cost, '.1f')}s with result {get_result}")
                        # remove the stopped task from processing list
                        processing_list.pop(processing_index)
                        for process_index, each_process in enumerate(self.mp_pool_list):
                            if each_processing_process['process'].name == each_process['process'].name:
                                self.mp_pool_list[process_index]['process_result'] = get_result
        else:
            # if the number of tasks is more than max_process number
            for process_index, each_process in enumerate(self.mp_pool_list):
                if len(processing_list) < self.max_process:
                    # if there is less than max_process number of tasks in the pool
                    # add a new task in it
                    processing_list.append(each_process)
                    each_process['start_time'] = time.time()
                    each_process['process'].start()
                while processing_list:

                    if len(processing_list) < self.max_process and process_index != len(self.mp_pool_list) - 1:
                        # if all tasks are in the pool then wait until all tasks are finished
                        # or break the loop to add a new task in the pool
                        break
                    else:
                        time.sleep(0.05)

                    for processing_index, each_processing_process in enumerate(processing_list):
                        if not each_processing_process['process'].is_alive():
                            # check each process
                            current_time = time.time()
                            time_cost = current_time - each_processing_process['start_time']
                            get_result = each_processing_process['process_result'].get()
                            print(
                                f"process: {str(each_processing_process['process'].name)} done in: {format(time_cost, '.1f')}s with {each_processing_process['process_name']} and result {get_result}") \
                                if each_processing_process['process_name'] != "" \
                                else print(
                                f"process: {str(each_processing_process['process'].name)} done in: {format(time_cost, '.1f')}s with result {get_result}")
                            # remove the stopped task from processing list
                            processing_list.pop(processing_index)
                            for process_index, each_process in enumerate(self.mp_pool_list):
                                if each_processing_process['process'].name == each_process['process'].name:
                                    self.mp_pool_list[process_index]['process_result'] = get_result

        return [res['process_result'] for res in self.mp_pool_list]
