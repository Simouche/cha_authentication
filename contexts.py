try:
    from asgiref.local import Local as LocalContext
except ImportError:
    from threading import local as LocalContext


class CurrentApplicationContext:
    context = LocalContext()


class CurrentTaskContext:
    _local = None
    context = None

    @classmethod
    def init(cls):
        cls._local = LocalContext()
        cls._local.set('user', None)
        cls._local.set('referrer', None)
        cls._local.set('current_host', None)
        cls.context = cls._local.local

    @classmethod
    def release(cls):
        cls.context = None
        if cls._local is not None:
            cls._local.release()
            cls._local = None
