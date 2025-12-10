import time
import random
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

class Metrics:
    def __init__(self):
        self.request_count = 0
        self.error_count = 0

    def record_request(self, success: bool):
        self.request_count += 1
        if not success:
            self.error_count += 1

    def export(self):
        return {
            "requests_total": self.request_count,
            "errors_total": self.error_count,
        }

def handle_request(metrics: Metrics):
    success = random.random() > 0.1
    metrics.record_request(success)
    if success:
        logging.info("Request handled successfully")
    else:
        logging.error("Request failed")

def main():
    metrics = Metrics()
    for _ in range(50):
        handle_request(metrics)
        time.sleep(0.05)
    logging.info(f"Final metrics: {metrics.export()}")

if __name__ == "__main__":
    main()
