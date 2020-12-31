import time

from redis import Redis
from threadpool_executor_shrink_able import ThreadPoolExecutorShrinkAble
from threadpool_executor_shrink_able.sharp_threadpoolexecutor import set_thread_pool_executor_shrinkable,show_current_threads_num

"""
引入redis在不同时候慢慢放入任务 和隔很久加入孺人，这样才方便测试 线程池自动扩张和减小。
"""

r = Redis(decode_responses=True)



pool = ThreadPoolExecutorShrinkAble(100)
set_thread_pool_executor_shrinkable(2, 10)
print(pool.MIN_WORKERS, pool.KEEP_ALIVE_TIME)

show_current_threads_num(1)

def f(x):
    time.sleep(0.2)
    # y = ['我' * 1000 * 1000 *100]
    y = '我' * 1000 * 1000 * 100
    print(x)


while 1:
    xx = r.blpop('test_adjust_task')
    pool.submit(f, xx[1])
