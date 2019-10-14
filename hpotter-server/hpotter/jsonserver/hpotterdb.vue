<html>
<head>
<meta charset="utf-8"/>
<script type="text/javascript"
        charset="utf8"
        src="https://cdn.jsdelivr.net/npm/vue">
</script>

<script type="text/javascript"
     charset="utf8"
    src="https://code.jquery.com/jquery-1.12.4.js">
</script>

<link rel="stylesheet"
     type="text/css"
     href="https://cdn.datatables.net/1.10.16/css/jquery.dataTables.css">

<script type="text/javascript"
     charset="utf8"
     src="https://cdn.datatables.net/1.10.16/js/jquery.dataTables.js">
</script>

<!--
[{"proto": 6, "created_at": "2017-11-22T19:39:01", "destPort": 2300, "destIP": null, "sourcePort": 55320, "sourceIP": null, "id": 1}, {"proto": 6, "created_at": "2017-11-26T23:17:33", "destPort": 2300, "destIP": null, "sourcePort": 60848, "sourceIP": null, "id": 2}]
-->

<script>
$(document).ready(function() {
    $('#example').dataTable( {
        ajax: {
            url: 'http://localhost:8081',
            dataSrc: ''
        },
        "columns": [
            { "data": "proto" },
            { "data": "created_at" },
            { "data": "destPort" },
            { "data": "sourcePort" },
            { "data": "sourceIP" },
            { "data": "id" },
        ]
    } );
} );
</script>

</head>

<body>
<div id="honeypot">
    <p>{{ message }}</p>
    <button v-on:click="SourceIPButton">Source IP</button>
</div>
    <div class="content">
        <table id="example" class="display" width="100%" cellspacing="0">
            <thead>
                <tr>
                    <th>Protocol</th>
                    <th>Created at</th>
                    <th>Destination Port</th>
                    <th>Source Port</th>
                    <th>Source IP Address</th>
                    <th>ID</th>
                </tr>
            </thead>
            <tfoot>
                <tr>
                    <th>Protocol</th>
                    <th>Created at</th>
                    <th>Destination Port</th>
                    <th>Source Port</th>
                    <th>Source IP Address</th>
                    <th>ID</th>
                </tr>
            </tfoot>
        </table>
    </div>
</body>
<script src="functions.js"></script>