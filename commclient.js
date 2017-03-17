var comm = Jupyter.notebook.kernel.comm_manager.new_comm('elogexpt')

console.log(comm)

// Register a handler
comm.on_msg(function(msg) {
    console.log(msg.content.data);
});
