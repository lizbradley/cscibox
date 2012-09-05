import os
import os.path

from ACE.Framework import Workflow

class Workflows(object):

    def __init__(self):
        self.workflows = {}

    def __str__(self):
        return '{workflows : %s}' % (self.workflows)

    __repr__ = __str__

    def add(self, workflow):
        self.workflows[workflow.get_name()] = workflow

    def remove(self, name):
        del self.workflows[name]

    def get(self, name):
        return self.workflows[name]

    def names(self):
        keys = self.workflows.keys()
        keys.sort()
        return keys

    def save(self, path):
        workflows_path =  os.path.join(path, "workflows")

        if not os.path.exists(workflows_path):
            os.mkdir(workflows_path)

        keys = self.names()

        # delete workflows no longer in self.workflows()
        items = os.listdir(workflows_path)
        to_delete = [file for file in items if not file[0:len(file)-4] in keys]
        for file in to_delete:
            os.remove(os.path.join(workflows_path, file))

        for name in keys:
            workflow = self.get(name)
            workflow.save(workflows_path)

    def load(self, path):
        workflows_path =  os.path.join(path, "workflows")

        if not os.path.exists(workflows_path):
            os.mkdir(workflows_path)

        items   = os.listdir(workflows_path)
        workflows = [item for item in items if item.endswith('.txt')]
        for name in workflows:
            workflow = Workflow(name[0:len(name)-4], None)
            workflow.load(os.path.join(workflows_path, name))
            self.add(workflow)
