import operator
import requests
import threading

# global variables
# search for any of these items
SEARCH_FOR = ['about me', 'alt="Home Page"', 'submit your link', 'add a link', 'add your link']
NUM_THREADS = 20
# tune it if needed, may be fractional like 0.5
MAX_WAIT_TIMEOUT_IN_SECONDS = 2


def send_get_request(chunk_of_links, results, index):
    result = []
    for link in chunk_of_links:
        try:
            html = requests.get(link, timeout=MAX_WAIT_TIMEOUT_IN_SECONDS)
        except requests.exceptions.RequestException as e:
            print(e)
            continue

        text = html.text.lower()
        if any(operator.contains(text, keyword.lower()) for keyword in SEARCH_FOR):
            print("correct link found: {0}".format(link))

            found_keyword = next(keyword for keyword in SEARCH_FOR if operator.contains(text, keyword.lower()))
            result.append("|".join([found_keyword, link]))
    results[index] = result


def gen_chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]


def scrape():
    with open("linksInput.txt", "r") as file:
        links = [line.rstrip('\n') for line in file]
        if links:
            threads = []

            chunk_size = int(len(links) / NUM_THREADS)
            results = [None] * chunk_size
            chunks = list(gen_chunks(links, chunk_size))
            print("chunks count: {0}, each chunk contains {1} links".format(len(chunks), chunk_size))
            for index, chunk in enumerate(chunks):
                t = threading.Thread(target=send_get_request, args=(chunk, results, index))
                threads.append(t)
                t.start()

            [thread.join() for thread in threads]

            if any(elem for elem in results):
                print("found something")
                with open("linksOutput.txt", "a") as output_file:
                    for result in filter(lambda x: x, results):
                        for potential_link in result:
                            print("Success: {}".format(potential_link))
                            output_file.write("%s\n" % potential_link)


if __name__ == "__main__":
    #from datetime import datetime
    #start = datetime.now()

    scrape()

    #print("time {0}".format(datetime.now()-start))
    #time 0:01:13.181662

