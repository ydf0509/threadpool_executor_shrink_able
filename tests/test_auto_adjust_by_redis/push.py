import time

from redis import Redis


r = Redis()


for j in range(100):
    for i in range(10):
        print('推送', i + j)
        r.lpush('test_adjust_task',i+j)
    time.sleep(16)  # 测试  12 和 3

