from multiprocessing import Pool, cpu_count
import time


class MultiPool:
    def __init__(self):
        self.max_threads = cpu_count() - 1

    def init(self):
        mp = Pool(processes=self.max_threads)
        pool_list: list = []
        return mp, pool_list

    def add(self, mp, pool_list: list, func, args: tuple):
        pool_list.append(mp.apply_async(func, args))
        return pool_list

    def run(self, mp, pool_list: list):
        start = time.time()
        mp.close()
        mp.join()
        wait_pool_list = [res.get() for res in pool_list]
        end = time.time() - start
        print("done in {}s".format("%.2f" % end))
        return wait_pool_list
