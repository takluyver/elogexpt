var comm = Jupyter.notebook.kernel.comm_manager.new_comm('elogexpt');
console.log(comm);

var imgelt = $('<img/>').appendTo(element);
var last_id;

// Register a handler
comm.on_msg(function(msg) {
    var data = msg.content.data;
    if (data.png) {
      imgelt[0].src = 'data:image/png;base64,'+ msg.content.data.png;
      last_id = data.last_id;
    } else {
      console.log(data);
    }
});

function add_snapshot_now(){
    var start_id = last_id - 20;
    if (start_id < 0) {
      start_id = 0;
    }
    var range = "(" + start_id + ", " + last_id + ")"
    var new_cell = Jupyter.notebook.insert_cell_below();
    new_cell.code_mirror.setValue("data = client2.show_range" + range);
    new_cell.execute();
}

Jupyter.toolbar.add_buttons_group([{
    label: 'Experiment state summary now',
    icon: 'fa-umbrella',
    callback: add_snapshot_now,
    id: 'add_summary_button'
}]);
