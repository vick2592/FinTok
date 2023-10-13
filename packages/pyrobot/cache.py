class Cache:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Cache, cls).__new__(cls)
            cls._instance.data = {}
        return cls._instance

    def set(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data.get(key, None)
