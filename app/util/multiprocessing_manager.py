import multiprocessing

class PoolManager:
    pool = None

    @classmethod
    def create_pool(cls, num_workers=None):
        if cls.pool is None:
            num_workers = num_workers or multiprocessing.cpu_count()
            cls.pool = multiprocessing.Pool(num_workers)
        return cls.pool

    @classmethod
    def terminate_pool(cls):
        if cls.pool is not None:
            cls.pool.terminate()
            cls.pool.close()
            cls.pool = None

    @classmethod
    def get_pool(cls):
        return cls.pool
