import threading
import time
import uvicorn

class Server(uvicorn.Server):
    """
    Custom Server class based on uvicorn.Server.

    This class extends uvicorn.Server and overrides certain methods for custom behavior.

    """
    def install_signal_handlers(self):
        """
        Override to disable signal handlers installation.

        This method disables the installation of signal handlers.

        """
        pass

    def run_in_thread(self):
        """
        Run the server in a separate thread.

        This method starts the server in a separate thread and waits for it to start.

        """
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
        while not self.started:
            time.sleep(1e-3)

    def close(self):
        """
        Close the server gracefully.

        This method sets a flag to exit the server and joins the server thread.

        """
        self.should_exit = True
        self.thread.join()