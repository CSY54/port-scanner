import socket, signal
from concurrent.futures import ThreadPoolExecutor, as_completed
from argparse import ArgumentParser
from time import time

is_exit = False
threads = []

def handler(signum, frame):
    global is_exit
    print('\nCtrl+C pressed, scanner stopping...')
    for thread in threads:
        if not thread.running():
            thread.cancel()
    is_exit = True

def check(ip, port, timeout, res):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(timeout)

    try:
        sock.connect((ip, port))
        res[port] = True
    except:
        res[port] = False

def run(ip, timeout, thread_cnt):
    global is_exit, threads
    res = {}
    executer = ThreadPoolExecutor(max_workers=thread_cnt)

    start_time = time()

    for port in range(65536):
        if is_exit:
            break 
        threads.append(executer.submit(check, ip, port, timeout, res))

    for thread in as_completed(threads):
        pass

    open_cnt = 0
    print('Opened ports:')
    for port in range(65536):
        try:
            if res[port]:
                open_cnt += 1
                print(str(port).rjust(5))
        except:
            break
    print(f'{open_cnt} ports are open in total')

    end_time = time()
    print('Scanning finished in {} seconds'.format(end_time - start_time))

def main():
    parser = ArgumentParser()
    parser.add_argument('--ip', help='IP address you want to scan')
    parser.add_argument('-t', '--timeout', help='Timeout', default='3')
    parser.add_argument('-T', '--threads', help='Number of threads to use', default='128')

    args = parser.parse_args()
    if args.ip == None:
        print('Must provide ip address')
        exit()
    run(args.ip, int(args.timeout), int(args.threads))

if __name__ == '__main__':
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    main()
