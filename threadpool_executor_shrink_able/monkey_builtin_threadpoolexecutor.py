"""
这个主要是为了 1/防止内置线程池，线程中的函数出错了不报错，导致以为代码没毛病。
2/有界队列

"""
import concurrent
from threadpool_executor_shrink_able.bounded_threadpoolexcutor import BoundedThreadPoolExecutor


def patch_builtin_concurrent_futeres_threadpoolexecutor():
    concurrent.futures.ThreadPoolExecutor = BoundedThreadPoolExecutor


if __name__ == '__main__':
    patch_builtin_concurrent_futeres_threadpoolexecutor()  # 如果不大猴子补丁，出错了自己完全不知道。
    from concurrent.futures import ThreadPoolExecutor

    def test_error():
        raise ValueError('测试错误')
    pool = ThreadPoolExecutor(20)
    pool.submit(test_error)
