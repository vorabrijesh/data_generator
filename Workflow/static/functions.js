function fetchPendingJobs() {

    //alert('kali1');

    //document.getElementById("id_login").innerHTML = "KaliKali"; //This won't work, some bug?

    //sanity test
    //document.getElementById("id_login").value = "KaliKali"; //this works!

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {

        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("id_pending").innerHTML = this.responseText;
        }
    };

    nodeid = document.getElementById("id_login").value;

    xhttp.open("GET", "http://localhost:5000/getjobs?nodeid="+nodeid, true);
    xhttp.send();

} //fetchPendingJobs
function renderJob() {
    //alert('logic starting');
    selected_job = "None";
    choices = document.getElementsByName("job_name");
    for (var i = 0; i < choices.length; i++) {
        if (choices[i].checked) {
            selected_job = choices[i].value;
        }
    }
    // alert(selected_job);

    //raise ajax query
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {

        if (this.readyState == 4 && this.status == 200) {
            // one more request to implement wf_renderer in views.py.
            document.getElementById("render_job").innerHTML =this.responseText;
        }
    };

    xhttp.open("GET", "http://localhost:5000/renderjob?jobid=" + selected_job, true);
    xhttp.send();
} //renderJob

function submitNode(){
    //raise ajax query
    var xhttp = new XMLHttpRequest();
    
    xhttp.onreadystatechange = function() {

        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("render_job").innerHTML = this.responseText;            
        }  
    };
    var tab = document.getElementById('render_table');
    var rowLength = tab.rows.length;
    
    var ops = '{';
    var cbs = '{';
    var rbs = '{';
    var op_t = false;
    var cb_t = false;
    var rb_t = false;
    var dis_inp= document.getElementsByTagName('input');
    //console.log(dis)
    var input_len = dis_inp.length;
    for(var i=0;i<input_len;i++){
        dis_inp[i].removeAttribute('disabled');
    }
    var dis_sel = document.getElementsByTagName('select');
    var sel_len = dis_sel.length;
    if(sel_len > 0){
    for(var i=0;i<sel_len;i++){
        dis_sel[i].removeAttribute('disabled');
        }    
    }
    for (i = 1; i < rowLength; i++){
        var Cells = tab.rows[i].cells;
        var n = Cells[0].children[0].name;
        var cell = Cells[1].children[0];
        if(cell.id=='options'){
        op_t = true;
        var opts = cell.options;
        var arr = [];
        for(var option of opts){
                arr.push(option.value);
            }
        ops = ops + '"' + n + '":' + JSON.stringify(arr) + ',';
        }
        if(cell.id=='checkboxes'){
            cb_t = true;
            var c = cell.children;
            var arr1 = [];
            for(var ch of c){
                if(ch.tagName == 'LABEL'){
                arr1.push(ch.innerHTML);
                }
            }
            //console.log(arr1)
            cbs = cbs + '"' + n + '":' + JSON.stringify(arr1) + ',';
        }
        if(cell.id.includes('radiobuttons')){
            rb_t = true;
            var r = cell.children;
            var arr2 = [];
            for(var rb of r){
                if(rb.tagName == 'LABEL'){
                arr2.push(rb.innerHTML);
                }
            }
            //console.log(arr2)
            rbs = rbs + '"' + n + '":' + JSON.stringify(arr2) + ',';
        }
    }
    ops = ops + '}';
    cbs = cbs + '}';
    rbs = rbs + '}';
    var formData = new FormData(document.getElementById("render_form"));
    if(op_t)
    formData.append('selection', ops);
    if(cb_t)
    formData.append('checkbox', cbs);
    if(rb_t)
    formData.append('radio', rbs);

    xhttp.open("POST", "http://localhost:5000/wfe/wf/strsubmit", true);
    xhttp.send(formData);

    //click refresh
    fetchPendingJobs()
}
function addjob(){
    //raise ajax query
    var xhttp = new XMLHttpRequest();
    
    xhttp.onreadystatechange = function() {

        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("render_table").innerHTML = this.responseText;            
        }  
    };
    var tab = document.getElementById('render_table');
    var rowLength = tab.rows.length;
    
    var ops = '{';
    var cbs = '{';
    var rbs = '{';
    var op_t = false;
    var cb_t = false;
    var rb_t = false;
    var dis_inp= document.getElementsByTagName('input');
    //console.log(dis)
    var input_len = dis_inp.length;
    for(var i=0;i<input_len;i++){
        dis_inp[i].removeAttribute('disabled');
    }
    var dis_sel = document.getElementsByTagName('select');
    var sel_len = dis_sel.length;
    if(sel_len > 0){
    for(var i=0;i<sel_len;i++){
        dis_sel[i].removeAttribute('disabled');
        }    
    }
    for (i = 1; i < rowLength; i++){
        var Cells = tab.rows[i].cells;
        var n = Cells[0].children[0].name;
        var cell = Cells[1].children[0];
        if(cell.id=='options'){
        op_t = true;
        var opts = cell.options;
        var arr = [];
        for(var option of opts){
                arr.push(option.value);
            }
        ops = ops + '"' + n + '":' + JSON.stringify(arr) + ',';
        }
        if(cell.id=='checkboxes'){
            cb_t = true;
            var c = cell.children;
            var arr1 = [];
            for(var ch of c){
                if(ch.tagName == 'LABEL'){
                arr1.push(ch.innerHTML);
                }
            }
            //console.log(arr1)
            cbs = cbs + '"' + n + '":' + JSON.stringify(arr1) + ',';
        }
        if(cell.id.includes('radiobuttons')){
            rb_t = true;
            var r = cell.children;
            var arr2 = [];
            for(var rb of r){
                if(rb.tagName == 'LABEL'){
                arr2.push(rb.innerHTML);
                }
            }
            //console.log(arr2)
            rbs = rbs + '"' + n + '":' + JSON.stringify(arr2) + ',';
        }
    }
    ops = ops + '}';
    cbs = cbs + '}';
    rbs = rbs + '}';
    var formData = new FormData(document.getElementById("render_form"));
    if(op_t)
    formData.append('selection', ops);
    if(cb_t)
    formData.append('checkbox', cbs);
    if(rb_t)
    formData.append('radio', rbs);

    xhttp.open("POST", "http://localhost:5000/wfe/wf/strsubmit", true);
    xhttp.send(formData);

}
