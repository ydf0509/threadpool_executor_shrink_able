import time
from concurrent.futures import ThreadPoolExecutor
import nb_log
from threadpool_executor_shrink_able import show_current_threads_num, ThreadPoolExecutorShrinkAble

show_current_threads_num(sleep_time=5)


def f1(a):
    time.sleep(0.2)  # 可修改这个数字测试多线程数量调节功能。
    b = [666] * 1000 * 10000
    print(f'{a} 。。。。。。。')
    # raise Exception('抛个错误测试')  # 官方的不会显示函数出错你，你还以为你写的代码没毛病呢。


pool = ThreadPoolExecutorShrinkAble(200)


for i in range(300):
    time.sleep(1)  # 这里的间隔时间模拟，当任务来临不密集，只需要少量线程就能搞定f1了，因为f1的消耗时间短，
    # 不需要开那么多线程，CustomThreadPoolExecutor比ThreadPoolExecutor 优势之一。
    pool.submit(f1, str(i))

# 1/下面测试阻塞主线程退出的情况。注释掉可以测主线程退出的情况。
# 2/此代码可以证明，在一段时间后，连续长时间没任务，官方线程池的线程数目还是保持在最大数量了。而此线程池会自动缩小，实现了java线程池的keppalivetime功能。
time.sleep(1000000)
