from multiprocessing import Process


def f(name):
    print('hello', name)


p1 = Process(target=f, args=('bob',))
p1.start()
# p.join()

p2 = Process(target=f, args=('bob',))
p2.start()
# p.join()

p3 = Process(target=f, args=('bob',))
p3.start()
# p.join()
