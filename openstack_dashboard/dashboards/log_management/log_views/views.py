# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import django.views
from django.views.generic import TemplateView
from horizon import exceptions
from horizon import tables
from django.utils.translation import ugettext_lazy as _
from openstack_dashboard.dashboards.log_management.log_views.log_file.log_nova import handleFile
from openstack_dashboard.dashboards.log_management.log_views import tables as log_tables
from openstack_dashboard.dashboards.log_management.config.file_config import handle_file_color
import datetime
from django.http import HttpResponse  # noqa
import json


class ChoiceValue:
    def __init__(self, name, is_selected):
        self.name = name
        self.is_selected = is_selected


class IndexView(tables.DataTableView):
    # A very simple class-based view...
    template_name = 'log_management/log_views/index.html'
    table_class = log_tables.LogTable
    page_title = _("Log Views")

    def get_data(self):
        # Add data to the context here...
        project = "NOVA"
        level = 'ALL'
        start = ''
        end = ''
        if self.request.method == 'POST':
            project = self.request.POST['project']
            level = self.request.POST['level']
            start = self.request.POST['start']
            end = self.request.POST['end']
            try:
                check_input_data(project, level, start, end)
            except ValueError, e:
                data = []
                msg = _(repr(e))
                exceptions.handle(self.request, msg)
        data = handleFile(project, level, start, end)
        return data

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        if self.request.method == 'POST':
            project = self.request.POST['project']
            level = self.request.POST['level']
            start = self.request.POST['start']
            end = self.request.POST['end']

            project_choices = []
            for choice in ['NOVA', 'NEUTRON', 'GLANCE', 'KEYSTONE']:
                if (choice == project):
                    project_choices.append(ChoiceValue(choice, 'yes'))
                else:
                    project_choices.append(ChoiceValue(choice, 'no'))

            level_choices = []
            for choice in ['ALL', 'DEBUG', 'WARNING', 'ERROR', 'INFO']:
                if (choice == level):
                    level_choices.append(ChoiceValue(choice, 'yes'))
                else:
                    level_choices.append(ChoiceValue(choice, 'no'))

            context['project_choices'] = project_choices
            context['type_choices'] = level_choices
            context['start'] = start
            context['end'] = end
            return context
        # context["agents"] = neutron_hsk_api.agent_list(request=self.request)
        else:
            context['project_choices'] = [ChoiceValue("NOVA", 'yes'),
                                          ChoiceValue("NEUTRON", 'no'),
                                          ChoiceValue("GLANCE", 'no'),
                                          ChoiceValue("KEYSTONE", 'no')
                                          ]
            context['type_choices'] = [ChoiceValue("ALL", 'yes'),
                                       ChoiceValue("DEBUG", 'no'),
                                       ChoiceValue("WARNING", 'no'),
                                       ChoiceValue("ERROR", 'no'),
                                       ChoiceValue("INFO", 'no')

                                       ]
            context['start'] = ""
            context['end'] = ""
            return context


def get_log_data(project, level, start, end):
    pass
    return []


def check_input_data(project, level, start, end):
    if project not in ['NOVA', 'NEUTRON', 'GLANCE', 'KEYSTONE']:
        raise ValueError("not valid project input")
    if level not in ['ERROR', 'INFO', 'DEBUG', 'WARNING', 'ALL']:
        raise ValueError("not valid level")
    if start != '':
        try:
            start_date = datetime.datetime.strptime(start, '%Y-%m-%dT%H:%M')
        except ValueError:
            raise ValueError("Incorrect input start date")
    else:
        start_date = ''
    if end != '':
        try:
            end_date = datetime.datetime.strptime(end, '%Y-%m-%dT%H:%M')
        except ValueError:
            raise ValueError("Incorrect input end date")
    else:
        end_date = ''
    if start_date != '' or end_date != '':
        if start_date == '' or end_date == '':
            raise ValueError("Incorrect input start_date or end date")
        else:
            if start_date > end_date:
                raise ValueError("Start date must be smaller than end date")


class LogCountView(django.views.generic.TemplateView):
    def get(self, request, *args, **kwargs):
        # response = self.render_to_response()
        try:
            project = request.GET.get('project', None)
            level = request.GET.get('level', None)
            start = request.GET.get('start', None)
            end = request.GET.get('end', None)
        except Exception:
            return HttpResponse("invalid input!",
                                status=404)

        # log_color = []
        # for color in handle_file_color.read_file():
        #     log_color.append(color.split()[1])

        if self.request.COOKIES.has_key('ERROR'):
            log_color = [self.request.COOKIES['ERROR'], self.request.COOKIES['INFO'], self.request.COOKIES['WARN'],
                         self.request.COOKIES['DEBUG']]
        else:
            log_color = ['#fe0404', '#4df919', '#faf204', '#707b7a']

        log_types = ['ERROR', 'INFO', 'WARN', 'DEBUG']
        logs_data = [
            {'y': [34, 32, 12, 10], 'x': u'2016-08-27'},
            {'y': [50, 17, 14, 23], 'x': u'2016-08-28'},
            {'y': [15, 22, 40, 34], 'x': u'2016-08-29'}
        ]
        log_info = {'log_types': log_types, 'logs_data': logs_data, 'log_color': log_color}
        return HttpResponse(json.dumps(log_info), content_type='application/json')
