import logging

def main():
    l = HacktribeAppLog()

class HacktribeAppLog:
    def __init__(self):
        logging.basicConfig(filename="hacktribe-app.log", filemode='w',
                            format='%(levelname)s: %(message)s',
                            level=logging.DEBUG)

        console_log = logging.StreamHandler()
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_log.setFormatter(console_formatter)
        console_log.setLevel(logging.INFO)
        logging.getLogger().addHandler(console_log)


if __name__ == "__main__":
    main()
