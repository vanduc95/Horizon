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

from horizon import views
from openstack_dashboard.dashboards.log_management.config.file_config import handle_file_color
from horizon import exceptions


class IndexView(views.APIView):
    # A very simple class-based view...
    template_name = 'log_management/config/index.html'

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        try:
            context = self.get_data(request, context, *args, **kwargs)
        except Exception:
            exceptions.handle(request)
        response = self.render_to_response(context)
        max_age = 365 * 24 * 60 * 60  # one year
        try:
            if 'save' in self.request.POST:
                response.set_cookie('ERROR', self.request.POST['ERROR'], max_age=max_age)
                response.set_cookie('INFO', self.request.POST['INFO'], max_age=max_age)
                response.set_cookie('WARN', self.request.POST['WARN'], max_age=max_age)
                response.set_cookie('DEBUG', self.request.POST['DEBUG'], max_age=max_age)

            elif 'default' in self.request.POST:
                response.set_cookie('ERROR', '#fe0404', max_age=max_age)
                response.set_cookie('INFO', '#4df919', max_age=max_age)
                response.set_cookie('WARN', '#faf204', max_age=max_age)
                response.set_cookie('DEBUG', '#707b7a', max_age=max_age)
        except Exception:
            pass

        return response

    def get_data(self, request, context, *args, **kwargs):
        # Add data to the context here...
        return context

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        if self.request.COOKIES.has_key('ERROR'):
            context['ERROR'] = self.request.COOKIES['ERROR']
            context['INFO'] = self.request.COOKIES['INFO']
            context['WARN'] = self.request.COOKIES['WARN']
            context['DEBUG'] = self.request.COOKIES['DEBUG']

        else:
            context['ERROR'] = '#fe0404'
            context['INFO'] = '#4df919'
            context['WARN'] = '#faf204'
            context['DEBUG'] = '#707b7a'

        try:
            if 'save' in self.request.POST:
                context['ERROR'] = self.request.POST['ERROR']
                context['INFO'] = self.request.POST['INFO']
                context['WARN'] = self.request.POST['WARN']
                context['DEBUG'] = self.request.POST['DEBUG']

            elif 'default' in self.request.POST:
                context['ERROR'] = '#fe0404'
                context['INFO'] = '#4df919'
                context['WARN'] = '#faf204'
                context['DEBUG'] = '#707b7a'
        except Exception:
            pass

        # try:
        #     if self.request.method == 'GET':
        #         if 'save' in self.request.GET:
        #             error = self.request.GET['ERROR']
        #             info = self.request.GET['INFO']
        #             warn = self.request.GET['WARN']
        #             debug = self.request.GET['DEBUG']
        #             handle_file_color.write_file(error, info, warn, debug)
        #         elif 'default' in self.request.GET:
        #             handle_file_color.write_file("#fc0404", "#4df919", "#faf204", "#707b7a")
        # except Exception:
        #     pass
        #
        # color = handle_file_color.read_file()
        # context['ERROR'] = color[0].split()[1]
        # context['INFO'] = color[1].split()[1]
        # context['WARN'] = color[2].split()[1]
        # context['DEBUG'] = color[3].split()[1]

        return context
