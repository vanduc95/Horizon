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


class IndexView(views.APIView):
    # A very simple class-based view...
    template_name = 'log_management/config/index.html'

    def get_data(self, request, context, *args, **kwargs):
        # Add data to the context here...
        return context

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        try:
            if self.request.method == 'GET':
                if 'save' in self.request.GET:
                    error = self.request.GET['ERROR']
                    info = self.request.GET['INFO']
                    warn = self.request.GET['WARN']
                    debug = self.request.GET['DEBUG']
                    handle_file_color.write_file(error, info, warn, debug)
                elif 'default' in self.request.GET:
                    handle_file_color.write_file("#fc0404", "#4df919", "#faf204", "#707b7a")
        except Exception:
            pass

        color = handle_file_color.read_file()
        context['ERROR'] = color[0].split()[1]
        context['INFO'] = color[1].split()[1]
        context['WARN'] = color[2].split()[1]
        context['DEBUG'] = color[3].split()[1]

        return context
