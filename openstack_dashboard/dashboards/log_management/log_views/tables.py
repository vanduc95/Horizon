from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from horizon import exceptions
from horizon import tables
import os

class ContainerFilter(tables.FilterAction):
    name = 'container_filter'


class DeleteLog(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Log",
            u"Delete Logs",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Log",
            u"Deleted Logs",
            count
        )

    # policy_rules = (("network", "delete_network"),)

    def delete(self, request, log_index):
        # docker_host = log_index
        try:
            arr = log_index.split(':')
            filePath = os.path.join(arr[1])
            line_index = arr[0]
            print(filePath)
            print(line_index)
            file = open(filePath, "r")
            lines = file.readlines()
            file.close()

            file_reopen = open(filePath, "w")
            count =1
            for line in lines:
                if (count!=int(line_index)):
                    file_reopen.write(line)
                count += 1
            file_reopen.close()
            msg = _('Log is Deleted ! %s')
        except Exception:
            msg = (_('Failed to remove docker host "%(host_name)s"') %
                   {"host_name": log_index})
            redirect = self.get_failure_url()
            exceptions.handle(request, msg, redirect=redirect)


class LogTable(tables.DataTable):
    time = tables.Column("time",
                         verbose_name=_("Time"))
    project = tables.Column('project',
                            verbose_name=_("Project"))
    level = tables.Column('level',
                          verbose_name=_("Level"))
    resources = tables.Column('resources',
                              verbose_name=_("Resources"))
    message = tables.Column('message',
                            verbose_name=_("Message"),truncate=30)

    def __init__(self, request, *args, **kwargs):
        super(LogTable, self).__init__(request, *args, **kwargs)

    class Meta(object):
        verbose_name = "Log Views"
        name = 'log_views'
        table_actions = (DeleteLog,)
        row_actions = ()
        prev_pagination_param= ''
        pagination_param =''


class LogData:
    def __init__(self, index, file_name, time, project, level, resources, message):
        self.id = index + ":" + file_name
        self.time = time
        self.project = project
        self.level = level
        self.resources = resources
        self.message = message
