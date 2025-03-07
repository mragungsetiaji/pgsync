import abc
import logging

class BaseExtractor(abc.ABC):
    def __init__(self, conn_params):
        self.conn_params = conn_params
        self.logger = logging.getLogger(self.__class__.__name__)
        self._configure_logging()
        self._validate_connection_params()

    def _configure_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )

    @abc.abstractmethod
    def _validate_connection_params(self):
        pass

    @abc.abstractmethod
    async def extract_incremental(self, job_dict):
        pass

class BaseTransformer(abc.ABC):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._configure_logging()

    def _configure_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )

    @abc.abstractmethod
    def transform(self, data):
        pass

class BaseLoader(abc.ABC):
    def __init__(self, credentials):
        self.credentials = credentials
        self.logger = logging.getLogger(self.__class__.__name__)
        self._validate_credentials()

    @abc.abstractmethod
    def _validate_credentials(self):
        pass

    @abc.abstractmethod
    def upload_to_gcs(self, data, table_name):
        pass
