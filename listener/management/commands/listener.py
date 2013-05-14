from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from listener.models import *
from multiprocessing import Process, Queue, Lock
import redis, subprocess, time

class Command(BaseCommand):
	""" This is command for redis dispatchin """
    args = ''
    help = ''
    processes = []

    def __del__(self):
        for p in self.processes:
            p.join()

    def handle(self, *args, **options):
        self.stdout.write("LISTENER: Listening to cloud deployment commands from Redis.")
        self.pool = redis.ConnectionPool(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0, password=settings.REDIS_PASSWORD)
        self.r = redis.Redis(connection_pool=self.pool)
        self.pubsub = self.r.pubsub()
        self.pubsub.subscribe('cloud')

        for item in self.pubsub.listen():
            if item['type'] == 'message':
                p = Process(target=self.dispatch, args=(item['data'],))
                self.processes.append(p)
                p.start()

    def dispatch(self, command):
        # check format
        data = command.decode("utf-8").split(':')
        cid = data[0]
        distro_shortname = data[-1].split('_')[-1]
        try:
            platform = DeployPlatforms.objects.get(shortname=distro_shortname)
            self.stdout.write("deploying " + platform.shortname)
        except Exception:
            self.r.set(cid, 'failed')
            return

        # run beescale-cli
        beescale_cli = settings.CG_PATH
        credsfile_fullpath = settings.CG_CREDSFILE
        platform_id = platform.platform_id
        try:
            create = subprocess.Popen([beescale_cli, '-c', credsfile_fullpath, 'create', platform_id], stdout=subprocess.PIPE)
            iid = create.communicate()[0].decode("utf-8")
            start = subprocess.Popen([beescale_cli, '-c', credsfile_fullpath, 'start', str(iid)], stdout=subprocess.PIPE)
            self.r.set(cid, 'starting system')
            while True:
                check = subprocess.Popen([beescale_cli, '-c', credsfile_fullpath, 'instance', str(iid)], stdout=subprocess.PIPE)
                out, err = check.communicate()
                if any(state in out.decode("utf-8") for state in ['pending', 'meta']):
                    self.stdout.write("NY")
                    time.sleep(15)
                    continue
                else:
                    break
            self.stdout.write("toggling vnc")
            togglevnc = subprocess.Popen([beescale_cli, '-c', credsfile_fullpath, 'togglevnc', str(iid)], stdout=subprocess.PIPE)
            self.r.set(cid, 'starting vnc')
            while True:
                checkvnc = subprocess.Popen([beescale_cli, '-c', credsfile_fullpath, 'vncstate', str(iid)], stdout=subprocess.PIPE)
                out, err = checkvnc.communicate()
                if any(state in out.decode("utf-8") for state in ['deactivated']):
                    self.stdout.write("NY")
                    time.sleep(15)
                    continue
                else:
                    break
            # retrieve info about server
            instance_data = subprocess.Popen([beescale_cli, '-c', credsfile_fullpath, 'instance_data', str(iid)], stdout=subprocess.PIPE)
            out, err = instance_data.communicate()
            deployed_message='deployed' + '_' + out.decode('utf-8')
            self.stdout.write(deployed_message)
            self.r.set(cid, deployed_message)
        except Exception:
            pass
        #self.r.set(cid, '')
