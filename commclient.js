// Opening the comm tells the kernel to start sending data.
var comm = Jupyter.notebook.kernel.comm_manager.new_comm('elogexpt');
console.log(comm);

// This will contain the plot pngs sent from the kernel.
var imgelt = $('<img/>').appendTo(element);
// This will contain the latest data id we have received.
var last_id;

// This runs when the kernel sends new data
comm.on_msg(function(msg) {
    var data = msg.content.data;
    if (data.png) {
      // Update the plot
      imgelt[0].src = 'data:image/png;base64,'+ msg.content.data.png;
      // Update last_id
      last_id = data.last_id;
    } else {
      console.log(data);
    }
});

// This runs when the user clicks the snapshot button
function add_snapshot_now(){
    // If the last ID we got was 70, give us data points 50-70
    var start_id = last_id - 20;
    if (start_id < 0) {
      start_id = 0;
    }
    var range = "(" + start_id + ", " + last_id + ")"
    
    // Add the code in a new cell and run it.
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
