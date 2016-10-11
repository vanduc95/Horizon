group_bar_chart = {
    BarChart: function (html_element, query) {
        var self = this;
        self.html_element = html_element;
        var jquery_element = $(html_element);
        self.url = jquery_element.data('url');
        self.jquery_element = jquery_element;
        self.final_url = self.url + query;
        // console.log(self.final_url);

        self.legend_element = jquery_element.data('legend-selector')
        self.width = jquery_element.data('chart-width');
        self.height = jquery_element.data('chart-height');
        self.color = d3.scale.ordinal()
            .range(["#98abc5", "#8a89a6", "#7b6888", "#6b486b", "#a05d56", "#d0743c", "#ff8c00"]);

        self.refresh = function () {
            var self = this;
            horizon.ajax.queue({
                url: self.final_url,
                success: function (data) {
                    // Clearing the old chart data.
                    self.jquery_element.empty();
                    $(self.legend_element).empty();
                    self.log_types = data.log_types;
                    self.logs_data = data.logs_data;
                    self.render();
                },
                error: function () {
                    $(self.html_element).html(gettext('No data available.'));
                    $(self.legend_element).empty();
                    $(self.legend_element).css('height', '');
                    horizon.alert('error', gettext('An error occurred. Please try again later.'));
                },
                complete: function () {
                    // self.finish_loading();
                }
            });
        };
        self.render = function () {
            var margin = {top: 20, right: 20, bottom: 30, left: 60},
                width = self.width - margin.left - margin.right,
                height = self.height - margin.top - margin.bottom;

            var x0 = d3.scale.ordinal()
                .rangeRoundBands([0, width], .1);

            var x1 = d3.scale.ordinal();

            var y = d3.scale.linear()
                .range([height, 0]);

            var xAxis = d3.svg.axis()
                .scale(x0)
                .orient("bottom");

            var yAxis = d3.svg.axis()
                .scale(y)
                .orient("left")
                .tickFormat(d3.format(".2"));

            var svg = d3.select(self.html_element).append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
                .append("g")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

            var log_levels = self.log_types;

            self.logs_data.forEach(function (d) {
                d.logs_count = log_levels.map(function (name, index) {
                    return {name: name, value: +d.y[index]};
                });
            });
            x0.domain(self.logs_data.map(function (d) {
                return d.x;
            }));
            x1.domain(self.log_types).rangeRoundBands([0, x0.rangeBand()]);
            y.domain([0, d3.max(self.logs_data, function (d) {
                return d3.max(d.logs_count, function (d) {
                    return d.value;
                });
            })]);

            svg.append("g")
                .attr("class", "x axis")
                .attr("transform", "translate(0," + height + ")")
                .call(xAxis);

            svg.append("g")
                .attr("class", "y axis")
                .call(yAxis)
                .append("text")
                .attr("transform", "rotate(-90)")
                .attr("y", 6)
                .attr("dy", ".71em")
                .style("text-anchor", "end")
                .text("Numbers");

            var state = svg.selectAll(".state")
                .data(self.logs_data)
                .enter().append("g")
                .attr("class", "state")
                .attr("transform", function (d) {
                    return "translate(" + x0(d.x) + ",0)";
                });

            state.selectAll("rect")
                .data(function (d) {
                    return d.logs_count;
                })
                .enter().append("rect")
                .attr("width", x1.rangeBand())
                .attr("x", function (d) {
                    return x1(d.name);
                })
                .attr("y", function (d) {
                    return y(d.value);
                })
                .attr("height", function (d) {
                    return height - y(d.value);
                })
                .style("fill", function (d) {
                    return self.color(d.name);
                });

            var legend = svg.selectAll(".legend")
                .data(self.log_types.slice().reverse())
                .enter().append("g")
                .attr("class", "legend")
                .attr("transform", function (d, i) {
                    return "translate(0," + i * 20 + ")";
                });

            legend.append("rect")
                .attr("x", width - 18)
                .attr("width", 18)
                .attr("height", 18)
                .style("fill", self.color);

            legend.append("text")
                .attr("x", width - 24)
                .attr("y", 9)
                .attr("dy", ".35em")
                .style("text-anchor", "end")
                .text(function (d) {
                    return d;
                });

        };
    }
};


$("#btn-log-filter").click(function () {
    var project = $("select[name='project']").val(),
        level = $("select[name='level']").val(),
        start = $("input[name='start']").val(),
        end = $("input[name='end']").val();
    var data_query = '?project =' + project + "&&level=" + level + '&&start=' + start + "&&end=" + end;
    var chart = new group_bar_chart.BarChart('div[data-chart-type="bar_log"]', data_query);
    chart.refresh();
});

init_group_bar_chart = function () {
    var project = $("select[name='project']").val(),
        level = $("select[name='level']").val(),
        start = $("input[name='start']").val(),
        end = $("input[name='end']").val();
    var data_query = '?project =' + project + "&&level=" + level + '&&start=' + start + "&&end=" + end;
    var chart = new group_bar_chart.BarChart('div[data-chart-type="bar_log"]', data_query);
    chart.refresh();

}
init_group_bar_chart();