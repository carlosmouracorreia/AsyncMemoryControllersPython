# Base code adapted from this tutorial:
# https://medium.com/capital-one-tech/python-guide-using-multiprocessing-versus-multithreading-55c4ea1788cd

import os
import time
from queue import Queue
from threading import Thread
import multiprocessing
from multiprocessing import Queue as MPQueue, Process

import requests

NUMBER_OF_THREADS = 5
q = Queue()


def download_image(download_location):
    """
    Download image from image_url.
    """
    global q

    # why do we have the while True loop here? The while True loop is used to continuously check for new image URLs
    # in the queue within the worker thread. This allows the worker thread to keep running and processing
    # new image URLs as they are added to the queue by the main thread. 
    # when do we exit the loop? when q.join() is called, which blocks the main thread until all items in the queue 
    # have been processed and marked as done using q.task_done().
    while True:
        image_url = q.get()
        res = requests.get(image_url, stream=True, verify=False)
        filename = f"{download_location}/{image_url.split('/')[-1]}.jpg"

        with open(filename, 'wb') as f:
            for block in res.iter_content(1024):
                f.write(block)

        print("Image downloaded.")
        q.task_done()

def download_image_mp(download_location, mp_queue):
    """
    Worker process for multiprocessing with queue.
    Continuously downloads images from the queue until it receives a sentinel value (None).
    """
    while True:
        image_url = mp_queue.get()
        # why do we need a sentinel value here and not in the multithreading version? In the multiprocessing version, we need a sentinel value (None) to signal the worker processes to exit because they are running in separate memory spaces and do not share the same queue.
        if image_url is None:  # Sentinel value to exit the process
            break
        
        res = requests.get(image_url, stream=True, verify=False)
        filename = f"{download_location}/{image_url.split('/')[-1]}.jpg"

        with open(filename, 'wb') as f:
            for block in res.iter_content(1024):
                f.write(block)

        print("Image downloaded.")

def download_images_with_multithreading(images):
    print("Starting function with multithreading.")

    '''
     We have a queue here to hold the image URLs that need to be downloaded. 
     The main thread will populate this queue with the image URLs, 
     and the worker threads will consume these URLs from the queue to download the images.

     We don't share the image URLs directly between threads; instead, we use the queue to manage the communication and synchronization between the main thread and the worker threads.
     This is done for efficency. If we divided the image URLs between threads, it would be less efficient because we would have to manage the division of URLs and ensure that each thread gets a fair share of the workload.
     By using a queue, we can simply add all the image URLs to the queue and let the worker threads consume them as they become available, which allows for better load balancing and more efficient use
    '''
    for image_url in images:
        q.put(image_url)

    for t in range(NUMBER_OF_THREADS):
        worker = Thread(target=download_image, args=(
            "with_multithreading_photos",))
        # why is this in deamon mode? The worker thread is set to daemon mode so that it will automatically exit when the main thread finishes. 
        # This is useful in this case because we want the worker threads to stop running once all the images have been downloaded and the main thread has completed its execution.
        #  By setting the worker threads as daemons, we ensure that they do not continue to run indefinitely after the main thread has finished, 
        # which can help prevent resource leaks and ensure that the program exits cleanly.
        worker.daemon = True
        print("Starting " + worker.name)
        worker.start()

    q.join()



def download_images_with_multiprocessing(images):
    print("Starting function with multiprocessing.")
    
    # Create a multiprocessing queue for inter-process communication
    mp_queue = MPQueue()
    jobs = []
    
    # Start worker processes
    for i in range(NUMBER_OF_THREADS):
        process = Process(
            target=download_image_mp,
            args=("with_multiprocessing_photos", mp_queue)
        )
        jobs.append(process)
        process.start()
    
    # Add images to queue for workers to download
    for image_url in images:
        mp_queue.put(image_url)
    
    # Send sentinel values to signal workers to exit
    for _ in range(NUMBER_OF_THREADS):
        mp_queue.put(None)
    
    # Wait for all processes to complete
    for j in jobs:
        j.join()



def download_images_without_multithreading(images):
    print("Starting function without multithreading or multiprocessing.")
    for image_url in images:
        res = requests.get(image_url, stream=True, verify=False)

        filename = f"without_multithreading_photos/" \
                   f"{image_url.split('/')[-1]}.jpg"

        with open(filename, 'wb') as f:
            for block in res.iter_content(1024):
                f.write(block)

        print("Image downloaded.")


def main():

    # remove warning for certificate verification when downloading images from the internet
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


    images = [
        'https://images.unsplash.com/photo-1428366890462-dd4baecf492b',
        'https://images.unsplash.com/photo-1541447271487-09612b3f49f7',
        'https://images.unsplash.com/photo-1560840067-ddcaeb7831d2',
        'https://images.unsplash.com/photo-1522069365959-25716fb5001a',
        'https://images.unsplash.com/photo-1533752125192-ae59c3f8c403',
    ]

    print("Downloading images from Internet.\n")

    # delete and create the folders for the downloaded images
    import os
    
    if os.path.exists("without_multithreading_photos"):
        # force remove the directory and its contents with one command
        os.system("rm -rf without_multithreading_photos")
    os.mkdir("without_multithreading_photos")


    if os.path.exists("with_multithreading_photos"):
        os.system("rm -rf with_multithreading_photos")
    os.mkdir("with_multithreading_photos")

    if os.path.exists("with_multiprocessing_photos"):
        os.system("rm -rf with_multiprocessing_photos")
    os.mkdir("with_multiprocessing_photos")

    start_time = time.time()
    download_images_with_multithreading(images)
    print("--- Function with multithreading took %s seconds ---\n" % (
            time.time() - start_time))
    
    start_time = time.time()
    download_images_with_multiprocessing(images)
    print("--- Function with multiprocessing took %s seconds ---\n" % (
            time.time() - start_time)) 
    

    start_time = time.time()
    download_images_without_multithreading(images)
    print("--- Function without multithreading took %s seconds ---\n" % (
            time.time() - start_time))
    
    # still can do multithreading without queeue and multiprocessing without queue


if __name__ == "__main__":
    main()