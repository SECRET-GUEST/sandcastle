import sys
import time
import threading

class Spinner:
    def __init__(self):
        self.loading = False
        self.loading_thread = None
        self.message = ""

    def loading_spinner(self):
        """Animates the spinner while the loading flag is active"""
        symbols = ['\\', '-', '/', '|']
        i = 0
        while self.loading:
            sys.stdout.write(f'\r{symbols[i % len(symbols)]} {self.message} {symbols[(i+2) % len(symbols)]}')
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
        sys.stdout.write('\r')
        sys.stdout.flush()

    def loading_start(self, message="Processing in progress"):
        """Starts the spinner with a custom message"""
        self.message = message
        self.loading = True
        self.loading_thread = threading.Thread(target=self.loading_spinner)
        self.loading_thread.start()

    def loading_stop(self, final_message=None):
        """Stops the spinner and displays the final message with spacing"""
        self.loading = False
        self.loading_thread.join()
        sys.stdout.write("\r" + " " * (len(self.message) + 10) + "\r")
        sys.stdout.flush()
        final_msg = final_message if final_message else f"{self.message} completed"
        print(f"\n✅ {final_msg}\n")
