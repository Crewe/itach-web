import logging
import sys
import uvicorn
from .itachweb import app
from itachweb.config.config import log_path, settings


def main():
    FORMAT = '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
    logging.basicConfig(filename=log_path(), level=logging.INFO, format=FORMAT)
    config = uvicorn.Config(
        "itachweb.__main__:app",
        port=settings()["server_port"],
        host=settings()["server_host"],
        log_level="info",
    )
    server = uvicorn.Server(config)
    server.run()


if __name__ == "__main__":
    sys.exit(main())
