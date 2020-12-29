import time
from concurrent.futures import ThreadPoolExecutor
import nb_log
from threadpool_executor_shrink_able.sharp_threadpoolexecutor2 import show_current_threads_num, ThreadPoolExecutorShrinkAble

show_current_threads_num(sleep_time=5)


def f1(a):
    time.sleep(0.2)  # 可修改这个数字测试多线程数量调节功能。
    # b = [666] * 1000 * 10000
    print(f'{a} 。。。。。。。')
    # raise Exception('抛个错误测试')  # 官方的不会显示函数出错你，你还以为你写的代码没毛病呢。
    return a * 10


pool = ThreadPoolExecutorShrinkAble(20)


futures = pool.map(f1,[i for i in range(100)])
for fut in futures:
    print(fut)

time.sleep(1000000)
