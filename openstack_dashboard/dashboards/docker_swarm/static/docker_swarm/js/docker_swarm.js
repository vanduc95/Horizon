container_line_chart = {
    chart_timers: [],
    charts: [],
    setup_line_chart: function (selector) {
        var self = this;
        self.tool_tip = d3.select("body").append("div")
            .attr("class", "tooltip")
            .style("opacity", 0);
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
formatTime = d3.time.format("%H:%M:%S");

function ContainerLine(id, line, color, legend_index, data, name) {
    this.id = id;
    this.color = color;
    this.line = line;
    this.legend_index = legend_index;
    this.data = data;
    this.name = name;

};
function LineChart(selector) {
    this.chart_selector = selector;
    this.containers = [];
    this.lines = [];
    this.container_colors = ["#5942f4", "#f46b42", "#6b486b", "#a05d56", "#98abc5", "#d0743c", "#ff8c00"];
    this.legend_indexs = [0, 1, 2, 3, 4, 5, 6, 7];

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
            .interpolate("cardinal")
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

    this.set_container_list = function () {
        var self = this;
        container_url_list = $(this.chart_selector).data('container-list-url');
        return $.getJSON(container_url_list, function (data) {
            data.forEach(function (container) {
                self.containers.push(container.id);
            });
        });
    };

    //process received data
    this.process_received_containers_data = function (arguments) {
        var results = [];
        if (arguments[1] == "success") {
            results.push(arguments[0]);
        } else {
            for (var i = 0; i < arguments.length; i++) {
                results.push(arguments[i][0]);
            }
        }
        for (var i = 0; i < results.length; i++) {
            results[i].value.forEach(function (d) {
                d.x = new Date(d.x);
                d.y = d.y;
            });
        }
        return results;
    };

    // Scale the range of the data
    this.scale_domain_range = function (containers_data) {
        var combine_containers_data = [];
        for (var i = 0; i < containers_data.length; i++) {
            combine_containers_data = combine_containers_data.concat(containers_data[i].value);
        }
        this.create_x_fn.domain([d3.min(combine_containers_data, function (d) {
            return d.x;
        }), d3.max(combine_containers_data, function (d) {
            return d.x;
        })]);
        this.create_y_fn.domain([0, d3.max(combine_containers_data, function (d) {
            return d.y;
        }) * 1.25]);
    };

    this.create_chart = function () {
        this.set_chart_format();
        var self = this;
        $.when(this.set_container_list()).done(function () {
            $.when.apply($, self.containers.map(function (id) {
                var container_detail_url = $(self.chart_selector).data('container-detail-url') + "?id=" + id;
                return $.ajax(container_detail_url);
            })).done(function () {

                containers_data = self.process_received_containers_data(arguments);
                self.scale_domain_range(containers_data);

                // Adds the svg elements
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
                    .text(containers_data[0].unit);

                //add_legend_manager_element
                var legend_elements = $(self.chart_selector).parent().find('.legend');
                self.svg_legend_elements = d3.select(legend_elements.get(0))
                    .append("svg")
                    .attr("width", self.chart_format.width + self.chart_format.margin.left
                    + self.chart_format.margin.right)
                    .attr("height", 60)
                    .append("g")
                    .attr("transform",
                    "translate(5,5)");

                //create container line and container legend
                containers_data.forEach(function (container_data) {
                    self.create_container_line(container_data);
                });
                // append the rectangle to capture mouse
                self.focus_catcher = self.svg_element.append("rect");
                self.focus_catcher
                    .attr("width", self.chart_format.width)
                    .attr("height", self.chart_format.height)
                    .style("fill", "none")
                    .style("pointer-events", "all")
                    .on("mouseover", function () {
                        container_line_chart.tool_tip.style("opacity", 1);
                        self.focus.style("display", null);
                        self.focus.visible = true;
                    })
                    .on("mouseout", function () {
                        container_line_chart.tool_tip.style("opacity", 0);
                        self.focus.style("display", "none");
                        self.focus.visible = false;
                    })
                    .on("mousemove", mousemove);
                function mousemove() {
                    var mouse_x0 = d3.mouse(this)[0];
                    self.focus_x = mouse_x0;
                    self.tool_tip_x = d3.event.pageX;
                    self.tool_tip_y = d3.event.pageY;
                    self.set_tool_tip(mouse_x0);
                }
                self.focus = self.svg_element.append("g");
                self.focus.style("display", "none");
            });
        });
    };

    this.get_container_list = function () {
        var self = this;
        container_url_list = $(this.chart_selector).data('container-list-url');
        return $.getJSON(container_url_list);
    };

    this.compare_container_list = function (current_container_list, updated_container_list) {
        var CompareResult = function (removed_container_list, new_container_list) {
            this.new_container_list = new_container_list;
            this.removed_container_list = removed_container_list;
        };
        removed_container_list = [];
        new_container_list = [];
        current_container_list.forEach(function (container_id) {
            var check_exist = $.grep(updated_container_list, function (id) {
                return id == container_id;
            });
            if (check_exist.length == 0) {
                removed_container_list.push(container_id);
            }
        });
        updated_container_list.forEach(function (container_id) {
            var check_exist = $.grep(current_container_list, function (id) {
                return id == container_id;
            });
            if (check_exist.length == 0) {
                new_container_list.push(container_id);
            }
        });
        return new CompareResult(removed_container_list, new_container_list);
    };

    this.update_charts = function () {
        var self = this;
        $.when(this.get_container_list()).done(function (data) {
            var updated_container_list = [];
            data.forEach(function (container) {
                updated_container_list.push(container.id);
            });
            var compare_result = self.compare_container_list(self.containers, updated_container_list);

            //remove exited containers
            compare_result.removed_container_list.forEach(function (id) {
                var container_line = $.grep(self.lines, function (e) { return e.id == id; })[0];
                container_line.line.remove();
                container_line.line.legend.remove();
                var ctn_index = self.lines.indexOf(container_line);
                self.lines.splice(ctn_index, 1);
                var ctn_id = $.grep(self.containers, function (e) { return e == id; })[0];
                var id_index = self.containers.indexOf(ctn_id);
                self.containers.splice(id_index, 1);
            });

            // add new containers and update old containers
            //self.add_new_containers(compare_result.new_container_list);
            self.containers = self.containers.concat(compare_result.new_container_list);
            //            console.log(self.containers);
            $.when.apply($, self.containers.map(function (id) {
                var container_detail_url = $(self.chart_selector).data('container-detail-url') + "?id=" + id;
                return $.ajax(container_detail_url);
            })).done(function () {

                containers_data = self.process_received_containers_data(arguments);
                self.scale_domain_range(containers_data);
                //update xAxis and yAxis
                self.xAxis.call(self.create_xAxis_fn);
                self.yAxis.call(self.create_yAxis_fn);

                //update data for exist containers
                for (var i = 0; i < self.lines.length; i++) {
                    // console.log(containers_data[i].id);
                    var container_line = self.lines[i];
                    var new_container_data = $.grep(containers_data, function (e) {
                        return e.id == container_line.id;
                    })[0];
                    container_line.line.attr('d', self.usage_create_line_fn(new_container_data.value));
                    container_line.data = new_container_data.value;
                }
                //create new line for new container
                var data_of_new_containers =
                    self.get_data_of_new_containers(containers_data, compare_result.new_container_list);
                data_of_new_containers.forEach(function (container_data) {
                    self.create_container_line(container_data);
                });
                if (self.focus.visible == true) {
                    self.set_tool_tip(self.focus_x);
                }
            });
        })
    };
    this.set_tool_tip = function (mouse_x0) {

        var self = this;
        var x0 = self.create_x_fn.invert(mouse_x0);
        // var x0 = self.create_x_fn.invert(d3.mouse(self.focus_catcher[0][0])[0]);
        var focus = self.focus;
        focus.selectAll("*").remove();
        var tool_tip = container_line_chart.tool_tip;
        var div_text = '<span style="color:' + "red" + '">' + "now is: " + formatTime(x0) + "</span>";
        var bisectDate = d3.bisector(function (d) {
            return d.x;
        }).left;
        this.lines.forEach(function (line) {
            if (line.data[0].x <= x0) {
                var i = bisectDate(line.data, x0, 1),
                    d = line.data[i];
                focus.append("circle")
                    .attr("class", "y")
                    .style("fill", line.color)
                    .style("stroke", line.color)
                    .attr("r", 4).attr("transform",
                    "translate(" + self.create_x_fn(d.x) + "," +
                    self.create_y_fn(d.y) + ")");
                div_text += "<br/>" + '<span style="color:' + line.color + '">'
                    + line.name + " : " + Math.round(d.y * 10000) / 10000 + "</span>";
            }
            // d0 = line.data[i - 1],
            // d1 = line.data[i],
            // d = x0 - d0.x > d1.x - x0 ? d1 : d0;

        })
        tool_tip.html(div_text)
            .style("left", (self.tool_tip_x + 20) + "px")
            .style("top", (self.tool_tip_y - 80) + "px");
        // console.log(div_text);
    };
    this.get_data_of_new_containers = function (containers_data, new_container_list) {
        var data_of_new_containers = []
        containers_data.forEach(function (check_data) {
            var is_exist = $.grep(new_container_list, function (e) {
                return e == check_data.id;
            });
            if (is_exist.length > 0) {
                data_of_new_containers.push(check_data);
            }
        })
        return data_of_new_containers;
    };

    this.create_container_line = function (container_data) {
        var self = this;
        for (var i = 0; i < self.legend_indexs.length; i++) {
            var check_index = self.legend_indexs[i];
            var container_exist = $.grep(self.lines, function (e) {
                return e.legend_index == check_index;
            });
            if (container_exist.length == 0) {
                container_data.legend_index = check_index;
                break;
            }
        }
        for (var i = 0; i < self.container_colors.length; i++) {
            var color = self.container_colors[i];
            var color_is_exist = $.grep(self.lines, function (e) {
                return e.color == color;
            });
            if (color_is_exist.length == 0) {
                container_data.color = color;
                break;
            }
        }
        var container_line = self.svg_element.append("path")
            .attr("class", "line")
            .attr('stroke', container_data.color)
            .attr("d", self.usage_create_line_fn(container_data.value));
        var container_legend = self.svg_legend_elements.append("g")
            .attr("class", "legend")
            .attr("transform", "translate(" + container_data.legend_index * 150 + ",0)");

        container_line.legend = container_legend;
        container_legend.append("rect")
            .attr("x", 100 - 18)
            .attr("width", 18)
            .attr("height", 18)
            .style("fill", container_data.color);
        var container_name = function () {
            d_names = container_data.name.split(".");
            return_name = d_names[0];
            for (var i = 1; i < d_names.length - 1; i++) {
                return_name += d_names[i];
            }
            return return_name;
        };
        container_legend.append("text")
            .attr("x", 100 - 24)
            .attr("y", 9)
            .attr("dy", ".35em")
            .style("text-anchor", "end")
            .text(container_name());
        self.lines.push(new ContainerLine(container_data.id, container_line,
            container_data.color, container_data.legend_index, container_data.value, container_name()));
    };
}
container_line_chart.setup_line_chart('div[data-chart-type="container_line_chart"]');

