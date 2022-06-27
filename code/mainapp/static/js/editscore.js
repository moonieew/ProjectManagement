


var dataidvalue = [];
var gradesemester = {};






$("#class_selected").on('change', function (e) {

    var optionSelected = $("option:selected", this);
    var valueSelected = this.value;
    // alert(valueSelected);
    var url = '/editscore';
    var form = $('<form action="' + url + '" method="post">' +
        '<input type="text" name="idSelected" value="' + valueSelected + '" />' +
        '</form>');
    var data = $('')
    $('body').append(form);
    form.submit();
});


$(".check").on('change', function (e) {
    console.log("here");
    var message, x;
    x = document.getElementById(e.target.id).value;
    if (x == "") err = "Input is empty";
    if (isNaN(x)) err = "Input is not a number";
    x = Number(x);
    if (x < 0) err = "Input is too low";
    if (x > 10) err = "Input is too high";
    if (x >= 0 && x <= 10) err = ""

    if (err != "") {
        document.getElementById(e.target.id).style.color = "red";
        alert(err);
        return;
    }
    else {
        dataidvalue.push({ id: e.target.id, value: x })
        document.getElementById(e.target.id).style.color = "black";
    }
    console.log("heree");

});



$('#saveandsubmit').on('click', function (e) {
    console.log(dataidvalue)

    fetch('/api/data_id_score', {
        method: 'POST', // or 'PUT'
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(dataidvalue),
    }).then(response => response.json())
        .then(data => {

            console.log('Success:', data);
            alert("Saved Changes");
            location.reload();
        })
        .catch((error) => {
            console.error('Error:', error);
            alert("Can't save changes");
        });

});
