pip install threadpool_executor_shrink_able





史上最强的python线程池。

最智能的可自动实时调节线程数量的线程池。此线程池和官方concurrent.futures的线程池 是鸭子类关系，所以可以一键替换类名 或者 import as来替换类名。
对比官方线程池，有4个创新功能或改进。 

1、主要是不仅能扩大，还可自动缩小(官方内置的ThreadpoolExecutor不具备此功能，此概念是什么意思和目的，可以百度java ThreadpoolExecutor的KeepAliveTime参数的介绍)，

2、非常节制的开启多线程，例如实例化一个最大100线程数目的pool，每隔2秒submit一个函数任务，而函数每次只需要1秒就能完成，实际上只需要调节增加到1个线程就可以，不需要慢慢增加到100个线程
官方的线程池不够智能，会一直增加到最大线程数目，此线程池则不会。

3、线程池任务的queue队列，修改为有界队列

4、此线程池运行函数出错时候，直接显示线程错误，官方的线程池则不会显示错误，例如函数中写1/0,任然不现实错误。

5.有线程池BoundedThreadPoolExecutor改善线程报错和有界队列。

6.patch_builtin_concurrent_futeres_threadpoolexecutor 支持给内置线程池打猴子补丁的方式，一键替换项目中所有原有的Thredpoolexecutor

7.以上是对比concurrent.futures 内置线程池，在博客园和csdn搜索 python自定义线程池这几个关键字，有上百篇博客实现线程池，但总共样子也就两三种，全部是抄袭来抄袭去，而且还很难调用，必须在程序末尾加join啥的，没有任何创意，中国博客园网友真的是很偷懒。

用法例子：

```python
import time
from nb_log import nb_print
from threadpool_executor_shrink_able import ThreadPoolExecutorShrinkAble

def f1(a):
    time.sleep(0.2)  # 可修改这个数字测试多线程数量调节功能。
    
    nb_print(f'{a} 。。。。。。。')
    
    # raise Exception('抛个错误测试')  # 官方的不会显示函数出错你，你还以为你写的代码没毛病呢。


pool = ThreadPoolExecutorShrinkAble(200)

# pool = ThreadPoolExecutor(200)  # 测试对比官方自带

for i in range(300):

    time.sleep(0.3)  # 这里的间隔时间模拟，当任务来临不密集，只需要少量线程就能搞定f1了，因为f1的消耗时间短，不需要开那么多线程，CustomThreadPoolExecutor比ThreadPoolExecutor 优势之一。
    
    pool.submit(f1, str(i))

# 1/下面测试阻塞主线程退出的情况。注释掉可以测主线程退出的情况。

# 2/此代码可以证明，在一段时间后，连续长时间没任务，官方线程池的线程数目还是保持在最大数量了。
# 而此线程池会自动缩小，实现了java线程池的keppalivetime功能。

time.sleep(1000000)
```

## 对比网上线程池
1

(https://www.cnblogs.com/shenwenlong/p/5604687.html)
```

#!/usr/bin/env python
# -*- coding:utf-8 -*-
#!/usr/bin/env python
# -*- coding:utf-8 -*-

import queue
import threading
import contextlib
import time

StopEvent = object()


class ThreadPool(object):

    def __init__(self, max_num):
        self.q = queue.Queue()#存放任务的队列
        self.max_num = max_num#最大线程并发数

        self.terminal = False#如果为True 终止所有线程，不再获取新任务
        self.generate_list = [] #已经创建的线程
        self.free_list = []#闲置的线程

    def run(self, func, args, callback=None):
        """
        线程池执行一个任务
        :param func: 任务函数
        :param args: 任务函数所需参数
        :param callback: 任务执行失败或成功后执行的回调函数，回调函数有两个参数1、任务函数执行状态；2、任务函数返回值（默认为None，即：不执行回调函数）
        :return: 如果线程池已经终止，则返回True否则None
        """

        if len(self.free_list) == 0 and len(self.generate_list) < self.max_num: #无空闲线程和不超过最大线程数
            self.generate_thread() # 创建线程
        w = (func, args, callback,)#保存参数为元组
        self.q.put(w)#添加到任务队列

    def generate_thread(self):
        """
        创建一个线程
        """
        t = threading.Thread(target=self.call)
        t.start()

    def call(self):
        """
        循环去获取任务函数并执行任务函数
        """
        current_thread = threading.currentThread#获取当前线程对象
        self.generate_list.append(current_thread)#添加到已创建线程里

        event = self.q.get() #获取任务
        while event != StopEvent: #如果不为停止信号

            func, arguments, callback = event#分别取值，
            try:
                result = func(*arguments) #运行函数，把结果赋值给result
                status = True   #运行结果是否正常
            except Exception as e:
                status = False #不正常
                result = e  #结果为错误信息

            if callback is not None: # 是否有回调函数
                try:
                    callback(status, result) #执行回调函数
                except Exception as e:
                    pass

            if self.terminal: # 默认为False ，如果调用terminal方法
                event = StopEvent #停止信号
            else:
                # self.free_list.append(current_thread) #执行完毕任务，添加到闲置列表
                # event = self.q.get()    #获取任务
                # self.free_list.remove(current_thread) #获取到任务之后，从闲置里删除
                with self.worker_state(self.free_list,current_thread):
                    event = self.q.get()


        else:
            self.generate_list.remove(current_thread) #如果收到终止信号，就从已创建的列表删除

    def close(self): #终止线程
        num = len(self.generate_list) #获取总已创建的线程
        while num:
            self.q.put(StopEvent) #添加停止信号，有几个线程就添加几个
            num -= 1

    # 终止线程（清空队列）
    def terminate(self):

        self.terminal = True #更改为True，

        while self.generate_list: #如果有已创建线程存活
            self.q.put(StopEvent) #有几个就发几个信号
        self.q.empty()  #清空队列
    @contextlib.contextmanager
    def worker_state(self,free_list,current_thread):
        free_list.append(current_thread)
        try:
            yield
        finally:
            free_list.remove(current_thread)
import time

def work(i):
    print(i)

pool = ThreadPool(10)
for item in range(50):
    pool.run(func=work, args=(item,))
pool.terminate()
pool.close()

```

调用方式伤不起

主要原因是用非搜狐线程，要么程序很快结束，要么就一直while 1循环程序结束不了，造成需要这样调用。
```
pool = ThreadPool(10)

for item in range(50):

    pool.run(func=work, args=(item,))
    
pool.terminate()

pool.close()


```

2 网上线程池之二

(https://www.cnblogs.com/tkqasn/p/5711593.html)

仍然是采用非守护线程，导致调用方式伤不起。啥pool.close pool.join都需要，无法随时提交任务。

```
   pool=ThreadPool(5)
    # pool.Deamon=True#需在pool.run之前设置
    for i in range(1000):
        pool.run(func=Foo,args=(i,),callback=Bar)
    pool.close()
    pool.join()
    # pool.terminate()
```


源码
```

import threading
import contextlib
from Queue import Queue
import time

class ThreadPool(object):
    def __init__(self, max_num):
        self.StopEvent = 0#线程任务终止符，当线程从队列获取到StopEvent时，代表此线程可以销毁。可设置为任意与任务有区别的值。
        self.q = Queue()
        self.max_num = max_num  #最大线程数
        self.terminal = False   #是否设置线程池强制终止
        self.created_list = [] #已创建线程的线程列表
        self.free_list = [] #空闲线程的线程列表
        self.Deamon=False #线程是否是后台线程

    def run(self, func, args, callback=None):
        """
        线程池执行一个任务
        :param func: 任务函数
        :param args: 任务函数所需参数
        :param callback:
        :return: 如果线程池已经终止，则返回True否则None
        """

        if len(self.free_list) == 0 and len(self.created_list) < self.max_num:
            self.create_thread()
        task = (func, args, callback,)
        self.q.put(task)

    def create_thread(self):
        """
        创建一个线程
        """
        t = threading.Thread(target=self.call)
        t.setDaemon(self.Deamon)
        t.start()
        self.created_list.append(t)#将当前线程加入已创建线程列表created_list

    def call(self):
        """
        循环去获取任务函数并执行任务函数
        """
        current_thread = threading.current_thread()   #获取当前线程对象·
        event = self.q.get()    #从任务队列获取任务
        while event != self.StopEvent:   #判断获取到的任务是否是终止符

            func, arguments, callback = event#从任务中获取函数名、参数、和回调函数名
            try:
                result = func(*arguments)
                func_excute_status =True#func执行成功状态
            except Exception as e:
                func_excute_status = False
                result =None
                print '函数执行产生错误', e#打印错误信息

            if func_excute_status:#func执行成功后才能执行回调函数
                if callback is not None:#判断回调函数是否是空的
                    try:
                        callback(result)
                    except Exception as e:
                        print '回调函数执行产生错误', e  # 打印错误信息


            with self.worker_state(self.free_list,current_thread):
                #执行完一次任务后，将线程加入空闲列表。然后继续去取任务，如果取到任务就将线程从空闲列表移除
                if self.terminal:#判断线程池终止命令，如果需要终止，则使下次取到的任务为StopEvent。
                    event = self.StopEvent
                else: #否则继续获取任务
                    event = self.q.get()  # 当线程等待任务时，q.get()方法阻塞住线程，使其持续等待

        else:#若线程取到的任务是终止符，就销毁线程
            #将当前线程从已创建线程列表created_list移除
            self.created_list.remove(current_thread)

    def close(self):
        """
        执行完所有的任务后，所有线程停止
        """
        full_size = len(self.created_list)#按已创建的线程数量往线程队列加入终止符。
        while full_size:
            self.q.put(self.StopEvent)
            full_size -= 1

    def terminate(self):
        """
        无论是否还有任务，终止线程
        """
        self.terminal = True
        while self.created_list:
            self.q.put(self.StopEvent)

        self.q.queue.clear()#清空任务队列

    def join(self):
        """
        阻塞线程池上下文，使所有线程执行完后才能继续
        """
        for t in self.created_list:
            t.join()


    @contextlib.contextmanager#上下文处理器，使其可以使用with语句修饰
    def worker_state(self, state_list, worker_thread):
        """
        用于记录线程中正在等待的线程数
        """
        state_list.append(worker_thread)
        try:
            yield
        finally:
            state_list.remove(worker_thread)






if __name__ == '__main__':
    def Foo(arg):
        return arg
        # time.sleep(0.1)

    def Bar(res):
        print res

    pool=ThreadPool(5)
    # pool.Deamon=True#需在pool.run之前设置
    for i in range(1000):
        pool.run(func=Foo,args=(i,),callback=Bar)
    pool.close()
    pool.join()
    # pool.terminate()

    print "任务队列里任务数%s" %pool.q.qsize()
    print "当前存活子线程数量:%d" % threading.activeCount()
    print "当前线程创建列表:%s" %pool.created_list
    print "当前线程创建列表:%s" %pool.free_list

详细代码，
```

可以去博客园搜索任意自定义线程池，由于没使用守护线程实现，调用都很麻烦。
