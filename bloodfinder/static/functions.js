function sendreq(mob,pincode,blood_grp) {
    $.post("/api/request", {
        "phone":mob,
        "pin_code":pincode,
        "blood_group":num_to_grp(parseInt(blood_grp)),
        "high_volume":'False'
    }).done(function() {
        console.log( "req sent" );
      })
      .fail(function() {
        alert( "error" );
      })
}
function register(mob,fam_id,blood_grp) {
    blood_grp = blood_grp.toUpperCase();
    $.post("/api/register", {
        "phone":mob,
        "family_id":fam_id,
        "group":num_to_grp(blood_grp)
    }).done(function(response) {
        console.log(response);        
    }).fail(function(response) {
        console.log(response);        
    });
}
function update_status(mob,new_status) {
    $.post("/api/update", {
        "phone":mob,
        "status":new_status
    }).done(function(response) {
        console.log(response);        
    }).fail(function(response) {
        console.log(response);        
    });
}
function num_to_grp(num) {
    switch(num) {
        case 1:
            grp = "A+";break;
        case 2:
            grp = "B+";break;
        case 3:
            grp = "AB+";break;
        case 4:
            grp = "O+";break;
        case 5:
            grp = "A-";break;
        case 6:
            grp = "B-";break;
        case 7:
            grp = "AB-";break;
        case 8:
            grp = "O-";break;
        default:
         return 0;
    }
    return grp;
}