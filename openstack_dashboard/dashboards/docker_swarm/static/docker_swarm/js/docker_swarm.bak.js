/* Additional JavaScript for chart_dashboard. */
// setup  ajax and handle select_date event


container_line_chart = {
    chart_timers: [],
    charts: [],
    setup_line_chart: function (selector) {
        var self = this;
        $(selector).each(function () {
            var chart = this;
            var new_chart = new LineChart(chart);
            new_chart.create_chart();
            self.charts.push(new_chart);
            setInterval(function () {
                new_chart.update_charts();
            }, 1000);
        });
    },
};

function ContainerLine(container_id, line, color) {
    this.container_id = container_id;
    this.color = color;
    this.line = line;

};
function LineChart(selector) {
    this.chart_selector = selector;
    this.containers = [];
    this.lines = [];
    this.container_colors = ["#98abc5", "#8a89a6", "#7b6888", "#6b486b", "#a05d56", "#d0743c", "#ff8c00"];

    this.set_chart_format = function () {
        this.chart_format = {};
        var self = this,
            format = this.chart_format;
        format.margin = { top: 30, right: 20, bottom: 30, left: 50 },
            format.width = 1000 - format.margin.left - format.margin.right,
            format.height = 500 - format.margin.top - format.margin.bottom;
        // Set the ranges
        self.create_x_fn = d3.time.scale().range([0, format.width]);
        self.create_y_fn = d3.scale.linear().range([format.height, 0]);
        self.usage_create_line_fn = d3.svg.line()
            .interpolate("basis")
            .x(function (d) {
                //console.log(self.create_x_fn(d.x));
                return self.create_x_fn(d.x);
            })
            .y(function (d) {
                return self.create_y_fn(d.y);
            });
        // Define the axes create function
        self.create_xAxis_fn = d3.svg.axis().scale(self.create_x_fn)
            .orient("bottom").ticks(5).tickFormat(d3.time.format("%H:%M:%Ss"));
        self.create_yAxis_fn = d3.svg.axis().scale(self.create_y_fn)
            .orient("left").ticks(10);
    };

    this.get_container_list = function () {
        var self = this;
        container_url_list = $(this.chart_selector).data('container-list-url');
        return $.getJSON(container_url_list, function (data) {
            self.containers = data;
        });
    };

    this.create_chart = function () {
        this.set_chart_format();
        var self = this;
        $.when(this.get_container_list()).done(function () {
            $.when.apply($, self.containers.map(function (container_id) {
                var container_detail_url = $(self.chart_selector).data('container-detail-url') + "?id=" +
                    container_id.id;
                return $.ajax(container_detail_url);
            })).done(function () {
                var results = [];
                for (var i = 0; i < arguments.length; i++) {
                    results.push(arguments[i][0]);
                }
                for (var i = 0; i < results.length; i++) {
                    results[i].value.forEach(function (d) {
                        d.x = new Date(d.x);
                        d.y = d.y;
                    });
                    results[i].color = self.container_colors[i];
                }
                // Adds the svg canvas
                self.svg_element = d3.select($(self.chart_selector).get(0))
                    .append("svg")
                    .attr("width", self.chart_format.width + self.chart_format.margin.left
                    + self.chart_format.margin.right)
                    .attr("height", self.chart_format.height + self.chart_format.margin.top
                    + self.chart_format.margin.bottom)
                    .append("g")
                    .attr("transform",
                    "translate(" + self.chart_format.margin.left + ","
                    + self.chart_format.margin.top + ")");
                // Scale the range of the data
                var combine_containers_data = [];
                for (var i = 0; i < results.length; i++) {
                    combine_containers_data = combine_containers_data.concat(results[i].value);
                }
                self.create_x_fn.domain([d3.min(combine_containers_data, function (d) {
                    return d.x;
                }), d3.max(combine_containers_data, function (d) {
                    return d.x;
                })]);
                self.create_y_fn.domain([0, d3.max(combine_containers_data, function (d) {
                    return d.y;
                }) * 1.25]);
                //draw line and push line to LineChart Object
                results.forEach(function (d) {
                    var container_line = self.svg_element.append("path")
                        .attr("class", "line")
                        .attr('stroke', d.color)
                        .attr("d", self.usage_create_line_fn(d.value));
                    self.lines.push(new ContainerLine(d.id, container_line, d.color));
                });
                console.log(self.chart_format.height);
                // Add the X Axis
                self.xAxis = self.svg_element.append("g")
                    .attr("class", "x axis")
                    .attr("transform", "translate(0," + self.chart_format.height + ")")
                    .call(self.create_xAxis_fn);
                // Add the Y Axis
                self.yAxis = self.svg_element.append("g")
                    .attr("class", "y axis")
                    .call(self.create_yAxis_fn);
                //Add yAxis unit
                self.yAxis
                    .append("text")
                    .attr("transform", "rotate(-90)")
                    .attr("y", 6)
                    .attr("dy", ".71em")
                    .style("text-anchor", "end")
                    .text(results[0].unit);

                //add_legend
                var legend_elements = $(self.chart_selector).parent().find('.legend');
                self.svg_legend_elements = d3.select(legend_elements.get(0))
                    .append("svg")
                    .attr("width", self.chart_format.width + self.chart_format.margin.left
                    + self.chart_format.margin.right)
                    .attr("height", 60)
                    .append("g")
                    .attr("transform",
                    "translate(5,5)");
                var legend_space_index = 0;
                results.forEach(function (d) {
                    var container_legend = self.svg_legend_elements.append("g")
                        .attr("class", "legend")
                        .attr("transform", "translate(" + legend_space_index * 150 + ",0)");
                    legend_space_index += 1;
                    var container_line = $.grep(self.lines, function (e) { return e.id == d.id; });
                    container_line.legend = container_legend;
                    container_legend.append("rect")
                        .attr("x", 100 - 18)
                        .attr("width", 18)
                        .attr("height", 18)
                        .style("fill", d.color);
                    container_legend.append("text")
                        .attr("x", 100 - 24)
                        .attr("y", 9)
                        .attr("dy", ".35em")
                        .style("text-anchor", "end")
                        .text(function () {
                            d_names = d.name.split(".");
                            return_name = d_names[0];
                            for (var i = 1; i < d_names.length - 1; i++) {
                                return_name += d_names[i];
                            }
                            return return_name;
                        });
                });

            });
        });
    };

    this.update_charts = function () {
        var self = this;
        $.when.apply($, self.containers.map(function (container_id) {
            var container_detail_url = $(self.chart_selector).data('container-detail-url') + "?id=" + container_id.id;
            return $.ajax(container_detail_url);
        })).done(function () {
            var results = [];
            for (var i = 0; i < arguments.length; i++) {
                arguments[i][0].value.forEach(function (d) {
                    d.x = new Date(d.x);
                });
                arguments[i][0].color = self.container_colors[i];
                results.push(arguments[i][0]);
            }
            var combine_containers_data = [];
            for (var i = 0; i < results.length; i++) {
                for (var j = 0; j < results[i].value.length; j++) {
                    combine_containers_data.push(results[i].value[j]);
                }
            }
            self.create_x_fn.domain([d3.min(combine_containers_data, function (d) {
                return d.x;
            }), d3.max(combine_containers_data, function (d) {
                return d.x;
            })]);
            self.create_y_fn.domain([0, d3.max(combine_containers_data, function (d) {
                return d.y;
            }) * 1.25]);
            self.xAxis
                // change the x axis
                .call(self.create_xAxis_fn);
            self.yAxis  // change the y axis
                .call(self.create_yAxis_fn);
            console.log(self.lines);
            for (var i = 0; i < results.length; i++) {
                console.log(self.lines);
                console.log(results[i].id);
                var container_line = $.grep(self.lines, function (e) { 
                    return e.container_id == results[i].id; 
                })[0];
                container_line.line.attr('d', self.usage_create_line_fn(results[i].value));
            }
        });

    }

}
container_line_chart.setup_line_chart('div[data-chart-type="container_line_chart"]');
