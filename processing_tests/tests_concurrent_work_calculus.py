import multiprocessing
import threading
import time

NUMBER_OF_PROCESSES = 5
NUMBER_OF_ITERATIONS = 5
N = 100000000  # 100 million


def sum_all_numbers(n):
    """
    Sums all the numbers from zero to n.

    :param n: The upper bound of numbers to be summed
    :return: The sum of all the numbers from 0 to n
    """

    total_sum = sum(range(n + 1))
    return print("Sum: " + str(total_sum))


def without_multiprocessing():
    print("Starting function without multiprocessing.")
    for i in range(NUMBER_OF_ITERATIONS):
        sum_all_numbers(N)


def with_multiprocessing():
    print("Starting function with multiprocessing.")
    jobs = []

    for i in range(NUMBER_OF_PROCESSES):
        process = multiprocessing.Process(
            target=sum_all_numbers,
            args=(N,)
        )
        jobs.append(process)

    for j in jobs:
        j.start()

    for j in jobs:
        j.join()

def with_multithreading():
    print("Starting function with multithreading.")
    threads = []

    for i in range(NUMBER_OF_PROCESSES):
        thread = threading.Thread(
            target=sum_all_numbers,
            args=(N,)
        )
        threads.append(thread)

    for t in threads:
        t.start()

    for t in threads:
        t.join()


def main():
    print("Summing all numbers between 0 and " + str(N) + ".\n")

    start_time = time.time()
    without_multiprocessing()
    print("--- Function without multiprocessing took %s seconds ---\n" % (
            time.time() - start_time))

    start_time = time.time()
    with_multiprocessing()
    print("--- Function with multiprocessing took %s seconds ---" % (
            time.time() - start_time))
    
    start_time = time.time()
    with_multithreading()
    print("--- Function with multithreading took %s seconds ---" % (
            time.time() - start_time))
    


if __name__ == "__main__":
    main()

    # check with pandas, numpy, anaconda and other libraries/plaforms that use multiprocessing and multithreading to see how they are implemented and how they can be used in this code to improve performance.
    # use grafana to check the peformance of memory/cpu, within a docker container? check tutorials to see whats best
    # you know code and structure, just need to scale
    '''
    Write a readme about the differences between multiprocessing and multithreading and how its being used in this code in 4 lines.
    Multiprocessing allows for parallel execution of processes, utilizing multiple CPU cores, while multithreading
allows for concurrent execution of threads within a single process, sharing the same memory space. 
In this code, multiprocessing is used to create separate processes that execute the sum_all_numbers function independently, 
while multithreading creates threads that execute the same function concurrently within the same process.
 The performance of both approaches is measured and compared to demonstrate the differences in execution time.

 # multithreading allows for interleaving of tasks, which can be beneficial for I/O-bound tasks, that can use other threads while waiting for I/O operations to complete, allowing for parallel execution. Multiprocessing, on the other hand, is more suitable for CPU-bound tasks that require intensive computation, as it can take advantage of multiple CPU cores to execute tasks in parallel. In this code, we are summing a large range of numbers, which is a CPU-bound task, so multiprocessing may provide better performance compared to multithreading. However, the actual performance may vary based on the system's hardware capabilities and the workload size.
    '''