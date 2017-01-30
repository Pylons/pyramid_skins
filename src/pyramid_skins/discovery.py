import logging
import sys
import threading


logger = logging.getLogger("pyramid_skins")

PY2 = sys.version_info[0] == 2


def string(s):
    if isinstance(s, str):
        return s
    if PY2:
        return s.encode('utf-8')
    return s.decode('utf-8')


class Discoverer(threading.Thread):
    run = None

    def __init__(self):
        super(Discoverer, self).__init__()
        self.paths = {}

    def watch(self, path, handler):
        if self.run is None:  # pragma: nocover
            raise ImportError(
                "Must have either ``MacFSEvents`` (on Mac OS X) or "
                "``pyinotify`` (Linux) to enable runtime discovery.")

        self.paths[path] = handler

        # thread starts itself
        if not self.isAlive():
            self.daemon = True
            self.start()

    try:
        import fsevents
    except ImportError:  # pragma: nocover
        pass
    else:
        def run(self):  # pragma: nocover
            logger.info("Starting FS event listener.")

            def callback(subpath, subdir):
                for path, handler in self.paths.items():
                    path = string(path)
                    if subpath.startswith(path):
                        config = handler.configure()
                        config.commit()

            stream = self.fsevents.Stream(callback, *(string(x) for x in self.paths))
            observer = self.fsevents.Observer()
            observer.schedule(stream)
            observer.run()
            observer.unschedule(stream)
            observer.stop()
            observer.join()

    try:
        import pyinotify
    except ImportError:  # pragma: nocover
        pass
    else:
        wm = pyinotify.WatchManager()

        def run(self):  # pragma: nocover
            self.watches = []
            mask = self.pyinotify.IN_CREATE

            for path in self.paths:
                wdd = self.wm.add_watch(path, mask, rec=True)
                self.watches.append(wdd)

            class Event(self.pyinotify.ProcessEvent):
                def process_IN_CREATE(inst, event):
                    subpath = event.path
                    for path, handler in self.paths.items():
                        if subpath.startswith(path):
                            config = handler.configure()
                            config.commit()

            handler = Event()
            notifier = self.pyinotify.Notifier(self.wm, handler)
            notifier.loop()
            for wdd in self.watches:
                self.wm.rm_watch(wdd.values())
            notifier.stop()
            notifier.join()
